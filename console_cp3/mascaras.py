
"""
mascaras.py — "The Visages of Sorrow": cinto de máscaras del rey leproso
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 1

Este es el puerto a Python (con listas) de la lógica de máscaras que ya
tenía en PlayerInventory.gd, del proyecto Godot del equipo
(github.com/DA0806/baldwins-curse):

    @export var max_carried_masks: int = 3
    var carried_masks: Array[MaskData] = []
    var active_mask_index: int = 0

Cada máscara cambia el estilo de combate del rey. En Godot el ciclado
tiene un temporizador (mask_swap_timer); acá el cambio es inmediato,
pero el comportamiento de la lista es el mismo: un buffer circular con
(índice + 1) módulo cantidad.

Así corresponden las funciones con el GDScript original:
    agregar_mascara()  <-  add_or_swap_mask()
    ciclar_mascara()   <-  cycle_mask()
    mascara_activa()   <-  get_active_mask()

Para probarlo por separado, como pide la regla 3 de la Guía 1:
    python3 mascaras.py
"""

# Igual que max_carried_masks en Godot: la mente del rey
# solo soporta tres rostros a la vez.
MAX_MASCARAS = 3


def agregar_mascara(mascaras, indice_activo, nueva_mascara):
    """Añade una máscara al cinto o reemplaza la activa si está lleno el límite.

    Puerto de add_or_swap_mask() de PlayerInventory.gd:
    - Si lleva menos de MAX_MASCARAS, la añade al cinto (si es la primera,
      queda equipada de inmediato).
    - Si ya lleva 3, la nueva reemplaza la máscara ACTIVA y la vieja cae
      al suelo.

    Devuelve la máscara soltada, o None si no se soltó nada.
    """
    if len(mascaras) < MAX_MASCARAS:
        mascaras.append(nueva_mascara)
        if len(mascaras) == 1:
            print("Te colocas " + nueva_mascara + " sobre el rostro descarnado.")
        else:
            print(nueva_mascara + " cuelga del cinto de máscaras.")
        return None

    # Límite alcanzado: intercambiar con la máscara activa
    soltada = mascaras[indice_activo]
    mascaras[indice_activo] = nueva_mascara
    print("Retiras " + soltada + ", que cae al suelo. Ahora portas " + nueva_mascara + ".")
    return soltada


def ciclar_mascara(mascaras, indice_activo):
    """Cicla entre las máscaras del cinto: buffer circular (índice + 1) módulo cantidad.

    Puerto de cycle_mask() de PlayerInventory.gd. La máscara nueva cambia
    el estilo de combate del caballero.
    Devuelve el nuevo índice activo.
    """
    if len(mascaras) == 0:
        print("El rey no porta máscaras todavía.")
        return indice_activo

    previa = mascaras[indice_activo]
    nuevo_indice = (indice_activo + 1) % len(mascaras)
    print("Retiras " + previa + ". El combate cambia: " + mascaras[nuevo_indice] + ".")
    return nuevo_indice


def mascara_activa(mascaras, indice_activo):
    """Devuelve la máscara equipada, o None si el cinto está vacío."""
    if len(mascaras) == 0 or indice_activo >= len(mascaras):
        return None
    return mascaras[indice_activo]


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de mascaras.py (Visages of Sorrow, puerto de Godot)")
    print()

    # Estado inicial: las tres máscaras del concepto del juego
    mascaras = ["Máscara del Rey Ciego", "Máscara de Lázaro", "Corona de Espinas Fundida"]
    indice_activo = 0

    print("Máscara equipada:", mascara_activa(mascaras, indice_activo))
    print("Cinto completo:", mascaras)
    print()

    # 1) Ciclar hacia adelante (buffer circular)
    indice_activo = ciclar_mascara(mascaras, indice_activo)
    indice_activo = ciclar_mascara(mascaras, indice_activo)
    indice_activo = ciclar_mascara(mascaras, indice_activo)  # vuelve a la primera

    # 2) Cinto lleno (3/3): recoger una cuarta máscara reemplaza la activa
    soltada = agregar_mascara(mascaras, indice_activo, "Máscara del Penitente")
    print("Máscara que quedó en el suelo:", soltada)
    print("Cinto actualizado:", mascaras)
