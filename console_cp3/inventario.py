"""
inventario.py — Lista de objetos del caballero leproso
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 1

Semana 3, Guía 3: las 6 funciones del programa de referencia más las 4 de
"Tu turno", ya trabajando con los objetos reales del reino leproso
(Vera Cruz, Poción de Mirra, Bezantes Sarracenos y compañía).

Este módulo se puede correr aparte, como pide la Guía 1:
    python3 inventario.py
"""


CAPACIDAD_MAXIMA = 6


# ============================================================
# Similar a la guia 3 — 6 funciones base
# ============================================================

def agregar_objeto(inventario, objeto):
    """Agrega un objeto si hay espacio disponible."""
    if len(inventario) >= CAPACIDAD_MAXIMA:
        print("Inventario lleno, no se pudo agregar " + objeto)
        return False
    inventario.append(objeto)
    print("Agregaste: " + objeto)
    return True


def usar_objeto(inventario, nombre):
    """Usa (consume) un objeto y lo quita del inventario."""
    if nombre not in inventario:
        print("No tienes " + nombre)
        return None
    inventario.remove(nombre)
    print("Usaste: " + nombre)
    return nombre


def soltar_objeto(inventario, nombre):
    """Suelta (descarta) un objeto sin usar su efecto."""
    if nombre not in inventario:
        print("No tienes " + nombre + " para soltar")
        return None
    inventario.remove(nombre)
    print("Soltaste: " + nombre)
    return nombre


def mostrar_inventario(inventario):
    """Muestra cada objeto con su posición."""
    if not inventario:
        print("Tu inventario está vacío")
        return
    print("--- Inventario ---")
    for indice, objeto in enumerate(inventario):
        print("[" + str(indice) + "] " + objeto)


def buscar_objeto(inventario, nombre):
    """Devuelve la posición del objeto, o None si no está."""
    if nombre in inventario:
        return inventario.index(nombre)
    return None


def contar_objeto(inventario, nombre):
    """Cuenta cuántas veces aparece un objeto."""
    return inventario.count(nombre)


# ============================================================
# TU TURNO (Guía 3) — 4 funciones nuevas
# ============================================================

def vaciar_inventario(inventario):
    """Suelta todos los objetos del inventario, uno por uno, hasta dejarlo vacío."""
    while len(inventario) > 0:
        # Siempre soltar el primero: la lista se acorta en cada paso.
        soltar_objeto(inventario, inventario[0])
    print("Inventario vaciado por completo")


def objeto_mas_repetido(inventario):
    """Devuelve el nombre del objeto que más se repite en el inventario."""
    if not inventario:
        return None
    mas_repetido = inventario[0]          # empezar asumiendo el primero
    for objeto in inventario:
        if contar_objeto(inventario, objeto) > contar_objeto(inventario, mas_repetido):
            mas_repetido = objeto
    return mas_repetido


def reemplazar_objeto(inventario, nombre_viejo, nombre_nuevo):
    """Cambia un objeto viejo por uno nuevo: suelta el viejo y agrega el nuevo."""
    if nombre_viejo not in inventario:
        print("No tienes " + nombre_viejo + " para reemplazar")
        return False
    # El orden importa: primero soltar (libera espacio) y después agregar.
    soltar_objeto(inventario, nombre_viejo)
    agregar_objeto(inventario, nombre_nuevo)
    return True


def objetos_unicos(inventario):
    """Devuelve una lista nueva con cada objeto una sola vez, sin duplicados."""
    unicos = []
    for objeto in inventario:
        if objeto not in unicos:
            unicos.append(objeto)
    return unicos


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# Usé los objetos reales del juego en vez del ejemplo
# genérico de "Espada / Escudo / Poción" de la guía.
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de inventario.py con objetos del reino leproso")
    print()

    inventario = []

    # 1) Agregar objetos reales del juego
    agregar_objeto(inventario, "Vera Cruz")
    agregar_objeto(inventario, "Poción de Mirra")
    agregar_objeto(inventario, "Poción de Mirra")
    agregar_objeto(inventario, "Bezante Sarraceno")
    agregar_objeto(inventario, "Bezante Sarraceno")
    agregar_objeto(inventario, "Bezante Sarraceno")

    # 2) Recorrer
    mostrar_inventario(inventario)

    # 3) Buscar y contar
    print("Posición de la Vera Cruz: " + str(buscar_objeto(inventario, "Vera Cruz")))
    print("Bezantes en el inventario: " + str(contar_objeto(inventario, "Bezante Sarraceno")))

    # 4) Usar y soltar
    usar_objeto(inventario, "Poción de Mirra")
    soltar_objeto(inventario, "Bezante Sarraceno")

    # 5) Las cuatro funciones nuevas de "Tu turno"
    print("El objeto más repetido es: " + str(objeto_mas_repetido(inventario)))
    print("Objetos únicos: " + str(objetos_unicos(inventario)))
    reemplazar_objeto(inventario, "Bezante Sarraceno", "Reliquia de San Lázaro")

    # 6) Vaciar por completo
    vaciar_inventario(inventario)
    mostrar_inventario(inventario)
