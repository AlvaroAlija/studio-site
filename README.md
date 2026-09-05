# alvaro.works — portfolio + GitOps content pipeline

Portfolio site for Álvaro (3D artist in Blender, indie game dev in Godot) with a
GitOps content pipeline: the site is **never hand-edited to add content**. The
render workstation and the itch.io account are the sources of truth; git carries
manifests pointing at artifacts in object storage; a push triggers build + deploy.

## Layout

```
site/                     # Astro static site (the web app)
content/
  renders.json            # written by pipeline/upload.py on the workstation
  games.json              # synced from itch.io by pipeline/sync_itch.py
  devlog/*.md             # one markdown file per post, front-matter metadata
pipeline/
  render.py               # headless Blender render job
  upload.py               # artifact -> R2/S3 (content-versioned URLs) + manifest write
  sync_itch.py            # itch.io API -> games.json overlay
.github/workflows/
  render.yml              # workflow_dispatch on a self-hosted workstation runner
  build-deploy.yml        # push to main -> build Astro -> Cloudflare Pages
  sync-itch.yml           # nightly cron + manual dispatch
```

Git is the control plane, object storage (Cloudflare R2) is the data plane, and
itch.io hosts the playable builds. Artifact URLs are content-versioned
(`renders/<slug>/v3/card.webp`) — a new render is a new URL, never an overwrite,
so the CDN caches immutably and a manifest revert still resolves.

## Site

```bash
cd site && npm install && npm run dev
```

- Astro 5, static output, no client framework. Content collections read
  `content/devlog/*.md`; the JSON manifests are imported at build time.
- Image fields that are `null` render as labelled striped placeholders until the
  pipeline fills them.
- Filter chips, featured row, and about-stats are all derived from the
  manifests — nothing is hardcoded.
- Contact form posts to `PUBLIC_FORM_ENDPOINT` (see `site/.env.example`); with
  no endpoint configured it falls back to a mailto handoff.

## Content update flows

| Change | Action |
|---|---|
| New render | workstation renders → `upload.py` pushes artifacts + appends `renders.json` → commit → deploy |
| Game release / cover change | `sync_itch.py` (every build + nightly) overlays itch-owned fields |
| New devlog post | commit one `.md` in `content/devlog/` |
| Price or copy change | edit one line of `renders.json` — that is the entire CMS |
| Rollback | revert the commit; versioned artifact URLs keep working |

## Secrets (GitHub Actions)

`R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`,
`ITCH_API_KEY`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.
