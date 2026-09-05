---
title: "One area light is usually enough"
date: 2026-08-11
tag: BLENDER
excerpt: "A note on subtraction: most of my renders got better when I deleted lights instead of adding them."
---

The instinct with a scene that reads badly is to add a fill. Nine times out of ten what it actually needs is for the key to be moved and everything else switched off.

Dust Chapel — the free desert interior in the store — is one 4m area light, one volumetric cube, and a sun disabled for the final frame. Everything that looks like bounce is geometry doing its job.

<figure>
  <div class="ph ratio-16-9" role="img" aria-label="comparison — three lights vs one"><span>comparison — three lights vs one</span></div>
  <figcaption>Same scene, same shaders, two lights removed.</figcaption>
</figure>

```python
# quick sanity check in the console
for l in [o for o in bpy.data.objects if o.type=='LIGHT']:
    print(l.name, l.data.energy)
```

If a render only works with four lights, the shapes are not carrying it yet. Go back to blocking.
