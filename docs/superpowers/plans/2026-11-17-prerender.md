# Prerendered sprites Implementation Plan

> **For agentic workers:** execute with superpowers:executing-plans; documentation/QA may run in parallel as authorized by the user.

**Goal:** integrate Meshy-derived character sprites while retaining gameplay.
**Architecture:** original reference images → Meshy t2.5/n1 → humanoid rig → controlled Blender orthographic renders → PNG sheets retaining existing cell contracts.
**Tech Stack:** Meshy, Blender 4.5, Pillow, Godot 4.7.2.
**Spec:** ../specs/2026-11-17-prerender-design.md

## Global Constraints
640×360, integer nearest; Baldwin 128×128 pivot(32,127), custodian96×48 pivot(48,47), acolyte64×48 pivot(32,47), abbot224×128 pivot(112,120). Keep frame/state mappings, damage windows and collisions.

## Review Focus
- Horizontal flip retains body origin.
- Foot contact stable across standing frames.
- Active sword/scythe occupies real hitbox.
- Vulnerability distinct by pose and seal.
- Small dark characters remain readable against rooms.

### Task 1: Sources
- [x] Generate and inspect four original references.
- [x] Generate four textured 12000-face models and retain task IDs.
- [x] Rig humanoids and obtain base walking/idle/action clips where needed.
- [x] Inspect thumbnails and local mesh/rig structure.

### Task 2: Render/integrate
Files: tools/render_characters.py, Art/Meshy/prerendered/, Sprites/Characters/Baldwin/*.png, Sprites/Enemies/{custodio,custodio_sellado,acolito}.png, Sprites/Bosses/abad.png.
- [x] Pose actual model geometry; render orthographic facing right.
- [x] Build exact horizontal strips using fixed transforms, no individual frame recentering.
- [x] Reproduce attack/recovery/seal/censer semantics with readable shapes.
- [x] Inspect contact sheets, alpha and hitbox overlays, then install.

### Task 3: Verify/document
Files: docs/arte_prerenderizado.md, docs/arte.md, docs/assets.md.
- [x] Record historical references, actual task IDs, cost and source locations.
- [x] Run Godot import and stage4/5/6 tests; capture representative rooms.
- [x] Fresh agent reviews final art/contracts and fixes material issues.
- [x] Commit feat: assets prerenderizados, verify current HEAD, push codex branch. PR only after user approval; no PR has been opened.
