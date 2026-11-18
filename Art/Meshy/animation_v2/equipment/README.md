# Equipo independiente — Meshy

Cinco modelos nuevos: espada, maza, guadaña, incensario y poción. Las referencias y los modelos fueron generados en Meshy con t2/n1. No se generaron variantes pagadas: la maza de prueba reutiliza la geometría de la maza con acabado frío.

Costo confirmado:120 créditos (45 referencias +75 modelos texturados). IDs, prompts, cargos y SHA-256 de GLB: manifest.json. Los modelos originales están en models/, las referencias en references/ y los renders ortográficos en renders/.

Los sprites de equipo conservan un pivote físico de agarre independiente del tamaño de iconos y recogibles. sword/mace:64×32, agarre(8,16); scythe:128×64, agarre(16,32); censer:48×64, agarre(24,8). Sprite_manifest.json registra dimensiones y hashes.

Reproducción desde la raíz del juego, sin gastar créditos:

```sh
blender --background --python tools/render_equipment_v2.py -- --render
python3 tools/render_equipment_v2.py --pack
```

La guadaña se orienta con el gancho hacia abajo y una proporción de hoja adecuada al canvas; el renderer no corta la punta. Los iconos de espada y maza se muestran en diagonal; las armas equipadas apuntan a la derecha. La poción incorpora una rampa roja apagada para distinguir el líquido de los herrajes de cobre.

Se inspeccionaron los cinco thumbnails, los renders y la galería final sprites_review.png. Las13 texturas tienen alfa binario y las cuatro texturas equipadas conservan margen en todos los bordes. La poción es un asset preparado; no activa curación, consumo ni guardado.
