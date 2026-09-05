#!/usr/bin/env python3
"""Push a finished render to object storage and append it to renders.json.

GitOps contract:
  * Artifact paths are content-versioned (renders/<slug>/v<N>/...) — a new
    render is a NEW URL, never an overwrite, so the CDN caches immutably and
    a manifest revert still resolves to a valid artifact.
  * This script only writes the manifest; committing and pushing (the build
    trigger) is left to the caller / workflow step.

Requires: boto3 (works against Cloudflare R2 via its S3-compatible endpoint),
Pillow for the WebP card. Credentials come from the environment:
  R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET

    python3 pipeline/upload.py --slug kelp-cathedral --title "Kelp Cathedral" \
        --category Environments --price 24 --spec "6144×6144 · PNG + .blend" \
        --desc "Submerged gothic hall..." --image out/kelp-cathedral.png \
        --extra out/kelp-cathedral.blend
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "content" / "renders.json"
CDN_BASE = os.environ.get("CDN_BASE_URL", "https://cdn.alvaro.works")
CARD_SIZE = 1200  # square WebP card generated for the store grid

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_manifest() -> list[dict]:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{MANIFEST} is not valid JSON: {exc}") from exc
    if not isinstance(data, list):
        raise RuntimeError(f"{MANIFEST} must contain a JSON array")
    return data


def next_version(entries: list[dict], slug: str) -> int:
    """Versions are derived from existing artifact URLs so they never collide."""
    pattern = re.compile(rf"/renders/{re.escape(slug)}/v(\d+)/")
    versions = [0]
    for entry in entries:
        for field in ("image", "full"):
            url = entry.get(field) or ""
            match = pattern.search(url)
            if match:
                versions.append(int(match.group(1)))
    return max(versions) + 1


def make_card(source: Path, dest: Path) -> None:
    """Generate the square WebP card image used by the store grid."""
    from PIL import Image  # imported lazily so --dry-run works without Pillow

    with Image.open(source) as im:
        im = im.convert("RGB")
        side = min(im.size)
        left = (im.width - side) // 2
        top = (im.height - side) // 2
        im = im.crop((left, top, left + side, top + side))
        im = im.resize((CARD_SIZE, CARD_SIZE), Image.LANCZOS)
        im.save(dest, "WEBP", quality=88)


def upload_file(local: Path, key: str) -> str:
    """Upload one file to the bucket; returns its public CDN URL."""
    import boto3

    endpoint = os.environ["R2_ENDPOINT_URL"]
    bucket = os.environ["R2_BUCKET"]
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    )
    content_type = {
        ".png": "image/png",
        ".webp": "image/webp",
        ".blend": "application/octet-stream",
        ".zip": "application/zip",
    }.get(local.suffix.lower(), "application/octet-stream")
    client.upload_file(
        str(local), bucket, key,
        ExtraArgs={"ContentType": content_type, "CacheControl": "public, max-age=31536000, immutable"},
    )
    return f"{CDN_BASE}/{key}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", required=True,
                        choices=["Environments", "Hard surface", "Product", "Character"])
    parser.add_argument("--price", required=True, type=float, help="0 means free")
    parser.add_argument("--desc", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--image", required=True, type=Path, help="Full-resolution PNG")
    parser.add_argument("--extra", type=Path, default=None, help="Optional .blend / bundle to ship")
    parser.add_argument("--buy", default=None, help="Gumroad/Stripe link for paid items")
    parser.add_argument("--dry-run", action="store_true", help="Skip uploads, print the manifest entry")
    args = parser.parse_args()

    if not SLUG_RE.fullmatch(args.slug):
        print(f"error: slug must be url-safe kebab-case, got {args.slug!r}", file=sys.stderr)
        return 1
    if not args.image.is_file():
        print(f"error: image not found: {args.image}", file=sys.stderr)
        return 1
    if args.price > 0 and not args.buy and not args.dry_run:
        print("error: paid items need --buy (Gumroad/Stripe link)", file=sys.stderr)
        return 1

    try:
        entries = load_manifest()
        version = next_version(entries, args.slug)
        prefix = f"renders/{args.slug}/v{version}"

        card = args.image.with_name(f"{args.slug}-card.webp")
        if args.dry_run:
            image_url = f"{CDN_BASE}/{prefix}/card.webp"
            full_url = f"{CDN_BASE}/{prefix}/{args.image.name}"
        else:
            make_card(args.image, card)
            image_url = upload_file(card, f"{prefix}/card.webp")
            full_url = upload_file(args.image, f"{prefix}/{args.image.name}")
            if args.extra is not None:
                if not args.extra.is_file():
                    raise RuntimeError(f"--extra file not found: {args.extra}")
                full_url = upload_file(args.extra, f"{prefix}/{args.extra.name}")

        entry = {
            "slug": args.slug,
            "title": args.title,
            "category": args.category,
            "price": int(args.price) if args.price == int(args.price) else args.price,
            "desc": args.desc,
            "spec": args.spec,
            "image": image_url,
            "full": full_url,
            "buy": args.buy,
            "updated": date.today().isoformat(),
            "featured": None,
            "featuredNote": None,
        }

        # Replace an existing entry for the slug (metadata update) or append.
        replaced = False
        for i, existing in enumerate(entries):
            if existing.get("slug") == args.slug:
                entry["featured"] = existing.get("featured")
                entry["featuredNote"] = existing.get("featuredNote")
                entries[i] = entry
                replaced = True
                break
        if not replaced:
            entries.append(entry)

        if args.dry_run:
            print(json.dumps(entry, indent=2, ensure_ascii=False))
            return 0

        MANIFEST.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except KeyError as exc:
        print(f"error: missing environment variable {exc}", file=sys.stderr)
        return 1
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"{'updated' if replaced else 'added'} {args.slug} (v{version}) in {MANIFEST}")
    print("commit and push content/renders.json to trigger the deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
