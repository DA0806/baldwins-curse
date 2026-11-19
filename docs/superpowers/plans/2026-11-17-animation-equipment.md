# Animation and independent equipment Implementation Plan

> **For agentic workers:** execute in parallel under the approved task split.

**Goal:** expressive layered character animation and coherent equipment.
**Architecture:** Meshy source props + existing character rigs, offline Blender render body sheets and hand pose data, one visual clock synchronized to existing combat phases.
**Tech Stack:** Godot4.7.2, Blender4.5.9, Pillow, Meshy.
**Spec:** ../specs/2026-11-17-animation-equipment-design.md

## Global Constraints
640×360, original damage/reach/timings/save schema; body/weapon separate. Dash/potion assets only. Meshy budget<=129.

## Review Focus
- Weapon accepted during attack cannot change on inventory swap.
- Mirroring and grip remain coherent.
- Hitbox controls damage, not animation.
- Body/collision/hurtbox share floor after scale changes.
- Pickup/HUD sizes independent.

### Task1 — Props (equipment_assets)
- [x] Generate five references/models120credits; inspect and export pinned-grip equipment, HUD/world sprites, sources.
### Task2 — Character renders (root)
- [x] Render body-only clips at4x, generate pose metadata, pack sheets and preview motion.
### Task3 — Player/pickups (historical_references)
- [x] Behavior tests red→green; one animation clock, phase clips, frozen weapon, world textures, dash asset wiring.
### Task4 — Enemies/boss (final_art_review)
- [x] Behavior tests red→green; phase clips/weapon layer, scaled collision/hurtbox anchored to existing floor.
### Task5 — Integration (root)
- [x] Import, all six stage suites and targeted presentation tests, real game captures, visual review.
- [x] Commit feat, verify HEAD, push branch; PR only after approval.
