
"""
armas.py — Cinto de 2 slots de armas del rey leproso
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 1

Esto es el puerto a Python (con listas) del sistema de armas que ya
tenía en PlayerInventory.gd, del proyecto Godot del equipo
(github.com/DA0806/baldwins-curse):

    @export var weapons: Array[WeaponData] = [null, null]   # 2 slots
    @export var active_weapon_slot: int = 0                 # 0 = principal

Así corresponden las funciones con el GDScript original:
    equipar_arma()        <-  equip_or_swap_weapon()
    intercambiar_armas()  <-  switch_active_weapon_slot()   (tecla TAB)
    soltar_arma_activa()  <-  drop_active_weapon()          (tecla G)

Para probarlo por separado, como pide la regla 3 de la Guía 1:
    python3 armas.py
"""

# Igual que en Godot: el rey solo puede portar 2 armas.
# Slot 0 = arma principal (activa) · Slot 1 = arma en espera.
MAX_ARMAS = 2


def equipar_arma(armas, slot_activo, nueva_arma):
    """Equipa un arma: si hay un slot libre lo usa, si no, intercambia con el slot activo.

    Sigue la regla de equip_or_swap_weapon() de PlayerInventory.gd:
    1. Si la principal está ocupada y la secundaria vacía, la nueva arma
       va a la secundaria. El rey no suelta nada.
    2. Si los dos slots están ocupados, se reemplaza el arma ACTIVA:
       la vieja cae al suelo del Nexo y se devuelve para quien la invoque.

    Devuelve el arma soltada, o None si no se soltó nada.
    """
    if len(armas) >= MAX_ARMAS and armas[0] is not None and armas[1] is None:
        # Caso 1: hueco en el cinto secundario
        armas[1] = nueva_arma
        print(nueva_arma + " cuelga de tu cinto, en espera.")
        return None

    # Caso 2: reemplazar el arma del slot activo
    arma_vieja = armas[slot_activo]
    armas[slot_activo] = nueva_arma
    if arma_vieja is None:
        print("Empuñas " + nueva_arma + ".")
    else:
        print("Empuñas " + nueva_arma + ". " + arma_vieja + " cae al suelo del Nexo.")
    return arma_vieja


def intercambiar_armas(armas, slot_activo):
    """Intercambia la posición entre el arma principal y la secundaria.

    Puerto de switch_active_weapon_slot() (tecla TAB en Godot).
    Devuelve el nuevo slot activo (0 o 1).
    """
    nuevo_slot = 1 - slot_activo
    if armas[nuevo_slot] is None:
        print("El otro slot está vacío: sigues con " + str(armas[slot_activo]) + ".")
        return slot_activo
    print("Cambias al slot " + str(nuevo_slot + 1) + ": ahora empuñas " + armas[nuevo_slot] + ".")
    return nuevo_slot


def soltar_arma_activa(armas, slot_activo):
    """Suelta el arma activa (cae al suelo del Nexo) y vacía su slot.

    Puerto de drop_active_weapon() (tecla G en Godot).
    Devuelve el arma soltada, o None si no había arma.
    """
    arma = armas[slot_activo]
    if arma is None:
        print("No empuñas ningún arma que soltar.")
        return None
    armas[slot_activo] = None
    print("Soltaste: " + arma)
    return arma


def arma_activa(armas, slot_activo):
    """Devuelve el nombre del arma activa (o None si el slot está vacío)."""
    return armas[slot_activo]


def arma_en_espera(armas):
    """Devuelve el nombre del arma en espera (o None si el slot está vacío)."""
    return armas[1 - 0] if len(armas) > 1 else None


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de armas.py (cinto de 2 slots, puerto de Godot)")
    print()

    # Estado inicial: la Espada del Sepulcro empuñada, cinto secundario vacío
    armas = ["Espada del Sepulcro", None]
    slot_activo = 0

    print("Arma activa:", arma_activa(armas, slot_activo))
    print()

    # 1) Equipar un arma con hueco libre -> va al slot secundario
    equipar_arma(armas, slot_activo, "Cimitarra Saqueada")

    # 2) Intercambiar slots (TAB en Godot)
    slot_activo = intercambiar_armas(armas, slot_activo)

    # 3) Cinto lleno: equipar una tercera arma reemplaza la activa
    arma_caida = equipar_arma(armas, slot_activo, "Mangual del Penitente")
    print("Arma que quedó en el suelo:", arma_caida)

    # 4) Soltar el arma activa (G en Godot)
    soltar_arma_activa(armas, slot_activo)
    print("Arma activa ahora:", arma_activa(armas, slot_activo) or "(slot vacío)")
