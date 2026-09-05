---
title: "Baking Blender lightmaps that survive Godot 4"
date: 2026-08-28
tag: GODOT
excerpt: "Lightmap workflows break in the export, not the bake. Here is the settings chain I stopped fighting with."
---

Every time I moved a scene from Blender into Godot the lighting arrived flatter than I left it. The bake was fine; the transfer was not. Three things were wrong and all of them were mine.

First, the UV2 channel. Godot wants a second, non-overlapping UV set purely for lighting, and Blender's smart-unwrap gives you overlap the moment two faces share a shell. Unwrap for light before you unwrap for texture.

Second, scale. A scene authored at centimetre scale bakes at centimetre scale, and Godot's lightmapper reads the texel density as absurdly high. Set the unit system before the first bake, not after.

<figure>
  <div class="ph ratio-16-9" role="img" aria-label="diagram — UV2 channel layout"><span>diagram — UV2 channel layout</span></div>
  <figcaption>Left: overlapping shells. Right: the same mesh unwrapped for lightmaps.</figcaption>
</figure>

```python
# Blender → glTF export, the only flags that mattered
export_apply = True        # apply modifiers
export_texcoords = True    # keeps UV2 alive
export_yup = True          # Godot is Y-up
export_materials = 'EXPORT'
```

Once the chain was fixed the bake took nine minutes and I have not touched it since. Build is on itch if you want to walk the tunnel.
