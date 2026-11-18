# Animación con personalidad y equipo independiente

Estado: aprobado por Felipe el 17 de noviembre de 2026; producir e integrar el lote.

## Intención y enfoque
Conservar el acabado prerenderizado de Meshy y la abadía funeraria. El usuario pidió armas independientes: se adopta cuerpo sin arma más capa de arma, ambos sincronizados por cuadro y por fase real de combate. Frente a generar una hoja completa por combinación (duplica cuerpos y dificulta nuevos ítems), las capas permiten nuevas armas y mantienen el anclaje a la mano. Un personaje 3D en tiempo real ampliaría el alcance innecesariamente.

## Personalidad y cuadros
Baldwin: reposo8 con respiración contenida y peso del juramento; andar16 con pisada firme; salto10 con impulso/apogeo/caída; daño6; muerte12; ataque espada16 con tajo ágil; ataque maza20 con carga de hombro, impacto pesado y recuperación; Dash12 con compresión, extensión y frenado. Los conteos son objetivos iniciales: la lectura y los tiempos reales gobiernan la distribución.
Custodios: reposo vigilante, paso pesado, anticipación clara, tajo y recuperación en secuencias de varios cuadros. Acólito: balanceo de incensario y lanzamiento deliberado. Abad: autoridad lenta en reposo, barrido bajo y convocatoria claramente diferentes, recuperación vulnerable y agotamiento con poses distintas. Dar cuadros intermedios reales, no repetir o interpolar solamente un PNG. Reutilizar rigs y locomoción Meshy existentes; calibrar la cadencia al desplazamiento para reducir deslizamiento de pies. Dash se entrega con12cuadros y una referencia de duración0,20s para la integración futura.

## Armas y poción
Generar en Meshy una espada medieval, maza de la Cripta (la maza de prueba reutiliza su geometría con otro acabado), guadaña del Abad, incensario y poción: cinco modelos texturados con referencias propias. Acero frío, marfil, cuero y cobre, con formas grandes legibles. Poción de vidrio grueso con líquido rojo apagado, tapón y collar de cobre, silueta distinta de las máscaras. Entregar modelo, icono y sprite de mundo; el arma equipada tiene su propia capa.
Baldwin elige gesto según el arma del ataque aceptado, incluso si cambia la selección después. Dividir espada en6/4/6cuadros y maza en8/4/8 para preparación/activo/recuperación; ajustar velocidad de cada clip al tiempo real del ataque. Un solo reloj visual gobierna cuerpo y arma. Usar el tag existente combo_animation_tag para elegir gesto. Sincronizar preparación/activo/recuperación con MeleeAttack; evitar daño visual adelantado y arma doble. Espada y maza deben sentirse diferentes conservando sus valores actuales. Equipo de enemigos también queda como capa separada al producir sus cuadros.

## Escalas
Referencia de altura erguida: Baldwin64px, custodios~60px, acólito~56px, Abad~88px. Conservar posición de pies y revisar cuerpo/colisión juntos cuando cambie la altura. Los objetivos de altura se validan contra las escenas, y se mantienen alineados cuerpo, colisión y hurtbox sin mover el apoyo en el suelo. Iconos64×64 se ajustan al espacio del HUD, no definen tamaño físico: máscara en mundo~16–20px, poción~12–16px, espada~28–36px y maza~22–28px en recogibles; equipo en mano se calibra al cuerpo y al alcance propio. No escalar la zona de daño por el PNG.

## Límites
Resolución lógica640×360, cámara y paleta actuales; esta pasada no migra a720p. Dash y poción se entregan preparados para las mecánicas futuras: sin tecla de dash, invulnerabilidad, consumo, curación ni modificación del guardado todavía. La corrección de máscaras afecta tamaño de recogible e iconos; no añade un cambio de máscara visible en la cara. La poción se entrega como asset, no exige animación de beber. Conservar estadísticas, alcance y tiempos de armas, máscaras y jefe. No añadir combos o armas jugables nuevas.

## Coste previsto
Cinco referencias(45créditos)+cinco modelos inteligentes texturados(75)=120créditos. Hasta tres clips de animación adicionales(9créditos): presupuesto previsto129. Reutilizar fuentes existentes y animaciones incluidas. No regenerar variantes pagadas por resultados deficientes sin consultar. Saldo consultado4252.

## Entrega y pruebas
Sprites/capas, anclajes reproducibles, fuentes GLB, poses Dash y poción listas para integrar, galería animada antes/después y capturas de juego con espada y maza. Verificar ambas orientaciones, cancelación por daño/muerte, congelación del arma aceptada, correspondencia de fases y escalas de pickup/HUD. Actualizar tests que fijan cuadro4 como único golpe; añadir pruebas que comprueben comportamiento real de fases/capas. Ejecutar etapas1–6 y pruebas específicas de presentación. Rama nueva codex/animation-equipment, commit feat, verificación, push y aprobación antes de PR.
