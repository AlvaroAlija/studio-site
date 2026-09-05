import rendersRaw from "../../../content/renders.json";
import gamesRaw from "../../../content/games.json";

export type RenderCategory = "Environments" | "Hard surface" | "Product" | "Character";
export type GameStatus = "Released" | "In development" | "Prototype";

export interface Render {
  slug: string;
  title: string;
  category: RenderCategory;
  price: number;
  desc: string;
  spec: string;
  image: string | null;
  full: string | null;
  buy: string | null;
  updated: string;
  featured: number | null;
  featuredNote: string | null;
}

export interface Shot {
  src: string | null;
  label: string;
}

export interface Game {
  slug: string;
  title: string;
  status: GameStatus;
  meta: string;
  tagline: string;
  story: string;
  detail: string;
  stack: string;
  controls: { key: string; act: string }[];
  cover: string | null;
  shots: Shot[];
  itchUrl: string;
  embedUrl: string | null;
  downloadUrl: string | null;
  featured: number | null;
  featuredNote: string | null;
}

export const renders: Render[] = (rendersRaw as Render[])
  .slice()
  .sort((a, b) => b.updated.localeCompare(a.updated));

export const games: Game[] = gamesRaw as Game[];

/** Filter categories are derived from the data so new ones appear automatically. */
export const renderCategories: string[] = [
  ...new Set(renders.map((r) => r.category)),
];

export interface FeaturedItem {
  kind: "3D Render" | "Game";
  title: string;
  note: string;
  href: string;
  image: string | null;
  label: string;
  order: number;
}

/** Featured row: items flagged in the manifests, renders and games mixed. */
export const featured: FeaturedItem[] = [
  ...renders
    .filter((r) => r.featured != null)
    .map<FeaturedItem>((r) => ({
      kind: "3D Render",
      title: r.title,
      note: r.featuredNote ?? r.desc,
      href: "/#renders",
      image: r.image,
      label: `render — ${r.title.toLowerCase()}`,
      order: r.featured ?? 0,
    })),
  ...games
    .filter((g) => g.featured != null)
    .map<FeaturedItem>((g) => ({
      kind: "Game",
      title: g.title,
      note: g.featuredNote ?? g.tagline,
      href: `/games/${g.slug}`,
      image: g.cover,
      label: `featured game — ${g.title.toLowerCase()}`,
      order: g.featured ?? 0,
    })),
].sort((a, b) => a.order - b.order);

/** About stats — counts computed from the manifests, not typed. */
export const stats = [
  { value: `${renders.length}`, label: "Renders shipped" },
  { value: `${games.filter((g) => g.status === "Released").length}`, label: "Games released" },
  { value: "6 yr", label: "In Blender" },
  { value: "100%", label: "Solo built" },
];

/** Reading time computed at build, not authored. */
export function readingTime(markdown: string): string {
  const words = markdown.replace(/```[\s\S]*?```/g, " ").split(/\s+/).filter(Boolean).length;
  return `${Math.max(1, Math.round(words / 200))} min read`;
}

const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

/** "28 AUG 2026" — the meta-line date format used across the devlog. */
export function formatDate(date: Date): string {
  return `${String(date.getUTCDate()).padStart(2, "0")} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()}`;
}
