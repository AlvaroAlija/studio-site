# Guía de contenido — studio.alvaroalija.com

Cómo poblar y mantener tu portfolio. **Regla de oro: el sitio nunca se toca para añadir contenido.** Todo el contenido vive en la carpeta `content/`; cada push a `main` publica automáticamente en [studio.alvaroalija.com](https://studio.alvaroalija.com) (~1 minuto).

## Cómo publicar un cambio

Dos formas, elige la que te sea cómoda:

**A) Desde github.com (sin instalar nada):** navega al archivo → icono del lápiz → edita → botón "Commit changes". Listo.

**B) Con git en tu máquina:**

```bash
git pull
# ... edita lo que sea en content/ ...
git add content/
git commit -m "content: nuevo post sobre X"
git push
```

Para verificar: pestaña **Actions** del repo (el workflow "Build & deploy" debe acabar en verde) y refresca el sitio.

---

## 1. Escribir un post del devlog

Crea un archivo en `content/devlog/` con nombre `AAAA-MM-DD-slug.md` (el slug será la URL: `/blog/AAAA-MM-DD-slug`). Plantilla completa:

```markdown
---
title: "Título del post"
date: 2026-09-12
tag: GODOT
excerpt: "Una o dos frases que aparecen en el listado y como entradilla."
---

Primer párrafo del cuerpo. Markdown normal: **negrita**, [enlaces](https://...), etc.

<figure>
  <div class="ph ratio-16-9" role="img" aria-label="descripción de la imagen"><span>etiqueta del placeholder</span></div>
  <figcaption>Pie de foto en monospace.</figcaption>
</figure>

```gdscript
# Los bloques de código llevan resaltado de sintaxis automático
func example() -> void:
    pass
```

Párrafo de cierre.
```

- `tag` debe ser uno de: `GODOT` | `BLENDER` | `DEVLOG` | `STORE`.
- El tiempo de lectura se calcula solo — no lo escribas.
- **Imágenes reales**: cuando tengas una, súbela junto al post (p. ej. `site/public/blog/mi-imagen.webp`) y usa `<figure><img src="/blog/mi-imagen.webp" alt="..."><figcaption>...</figcaption></figure>` en lugar del `div.ph` placeholder.

## 2. La tienda de renders (`content/renders.json`)

Cada render es un objeto del array. Campos:

| Campo | Qué es |
|---|---|
| `slug` | id-en-kebab-case, único (también es la ruta en el storage) |
| `title` | 2–3 palabras, titular de la card |
| `category` | `Environments` \| `Hard surface` \| `Product` \| `Character` — los filtros salen solos de aquí; una categoría nueva crea su chip automáticamente |
| `price` | número; `0` = gratis (badge FREE + botón Download) |
| `desc` | 1–2 frases, ~110–140 caracteres |
| `spec` | línea técnica monospace, ej. `6144×6144 · PNG + .blend` |
| `image` | URL de la imagen cuadrada de la card; `null` = placeholder rayado |
| `full` | URL de descarga (gratis) o del bundle |
| `buy` | enlace Gumroad/Stripe (de pago); `null` si es gratis |
| `updated` | fecha ISO `AAAA-MM-DD` (ordena la grid, más nuevo primero) |
| `featured` | `1`/`2`/`3` = aparece en la fila destacada de la home (orden); `null` = no |
| `featuredNote` | frase corta para la card destacada |

**Cambiar un precio o un texto = editar una línea y push.** Ese es todo el CMS.

**Renders nuevos**: cuando el pipeline de subida esté activo (fase R2 pendiente), `pipeline/upload.py` añadirá la entrada con las URLs por ti. Mientras tanto puedes añadir entradas a mano con `image: null` y se verán con placeholder.

## 3. Los juegos (`content/games.json`)

| Campo | Qué es |
|---|---|
| `slug` | id único; **debe coincidir con el slug de la URL de itch.io** (`alvaro.itch.io/<slug>`) para el sync automático |
| `title`, `status` | status: `Released` \| `In development` \| `Prototype` |
| `meta` | línea `Motor · duración · plataformas` |
| `tagline` | frase de la card del catálogo |
| `story`, `detail` | dos párrafos de la página de detalle |
| `stack` | "Built with" de la página de detalle |
| `controls` | array de `{ "key": "WASD", "act": "Move" }` |
| `cover` | imagen 16:9 de la card; `null` = placeholder |
| `shots` | array de `{ "src": url o null, "label": "texto placeholder" }` — el carrusel del detalle |
| `itchUrl` | ⚠️ pon aquí la URL real de cada juego |
| `embedUrl` | URL del embed HTML5 de itch; si existe, la página de detalle muestra el juego jugable en iframe; si es `null`, muestra el carrusel |
| `downloadUrl` | zip de escritorio; `null` = el botón lleva a itch |
| `featured` / `featuredNote` | igual que en renders |

Cuando el sync de itch.io esté activo (fase pendiente), `cover`, `itchUrl` y `embedUrl` se actualizarán solos cada noche desde tu cuenta de itch — tú solo mantienes los textos.

## 4. Fila de destacados y estadísticas

- **Destacados de la home**: pon `featured: 1|2|3` (+`featuredNote`) en cualquier render o juego. Se mezclan y ordenan solos.
- **Stats del About**: "Renders shipped" y "Games released" se calculan de los manifiestos. Los otros dos ("6 yr", "100%") están en `site/src/lib/content.ts` si algún día quieres cambiarlos.

## 5. Textos fijos (la excepción)

Los copys estructurales no son "contenido" y viven en los componentes — se cambian una vez y rara vez:

- Hero (titular, sublínea): `site/src/components/Hero.astro`
- About (párrafos): `site/src/components/AboutSection.astro`
- Contacto (blurb, **enlaces de redes** ⚠️ ahora apuntan a las homes genéricas, y **email** placeholder `hola@alvaroalija.com`): `site/src/components/ContactFooter.astro`
- Blurbs de sección (tienda/juegos): `RendersSection.astro` / `GamesSection.astro`

## 6. Lo que NO hay que hacer

- ❌ No subir al repo `.blend`, renders, `builds/` ni `.godot/` — el `.gitignore` ya lo bloquea; los binarios van a object storage (R2), git solo lleva manifiestos.
- ❌ No editar nada de `site/` para añadir contenido — si sientes esa necesidad, falta un campo en el manifiesto: dilo.
- ❌ No borrar campos de los JSON aunque estén a `null` — el build los espera.

## 7. Si algo se rompe

1. Mira **Actions** en GitHub: si el último run está en rojo, el error suele ser un JSON mal cerrado (una coma de más) o front-matter inválido en un `.md`.
2. El sitio en producción **no se rompe** mientras un build falle — se queda en la última versión buena.
3. Rollback: revertir el commit problemático (`git revert <sha>` o desde GitHub) y push.

## Pendiente de infraestructura (contexto)

- **R2 / CDN** (`cdn.alvaroalija.com`): para que las imágenes reales sustituyan a los placeholders vía `upload.py`.
- **Sync itch.io**: API key + activar variable; luego es automático.
- **Formulario de contacto**: endpoint de Formspree; mientras tanto hace fallback a abrir el correo.
- **Runner de render** en tu workstation: para lanzar renders desde GitHub Actions.
