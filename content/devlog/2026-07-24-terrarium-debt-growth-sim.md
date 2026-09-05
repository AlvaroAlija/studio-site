---
title: "Terrarium Debt — the growth sim, attempt three"
date: 2026-07-24
tag: DEVLOG
excerpt: "Two rewrites in and the plants finally grow at a rate that feels like pressure rather than punishment."
---

The first version simulated every plant every tick. At forty plants the day-advance took two seconds and the whole feel of the game collapsed into waiting.

The second version batched growth into a queue but let debt compound off-screen, which meant players who explored got quietly ruined. Correct simulation, terrible game.

Attempt three simulates on demand: a plant computes its state from the last time it was observed. Cheap, deterministic, and it made the interest mechanic legible for the first time.

<figure>
  <div class="ph ratio-16-9" role="img" aria-label="ui capture — the ledger panel"><span>ui capture — the ledger panel</span></div>
  <figcaption>The ledger is the only HUD element in the game.</figcaption>
</figure>

```gdscript
func state_at(day: int) -> Growth:
    var elapsed := day - last_seen
    return _project(cached, elapsed)  # no per-tick loop
```

Next post: what happens when the terrarium reclaims a room you were standing in.
