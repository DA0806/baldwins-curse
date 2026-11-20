"""
historial.py — Pila del historial de acciones del rey leproso
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 2

Semana 5, Guía 5: el historial de acciones es una PILA (LIFO) porque la
acción más reciente es siempre la primera que hay que deshacer: eso es
exactamente el backtracking del rey por el reino.

Contiene las 3 funciones del programa de referencia de la Guía 5
(apilar_accion, deshacer_ultima_accion, ver_ultima_accion), una función
para mostrar el historial completo de la más reciente a la más antigua,
una para vaciarlo (la usa la resurrección de la Vera Cruz), y las 4
funciones de "Tu turno" ya adaptadas a las acciones reales del juego:

    - deshacer_multiples       (deshace varias acciones seguidas)
    - contar_acciones_de_tipo  (cuenta acciones por tipo, sin modificar)
    - invertir_historial       (invierte con una pila auxiliar)
    - deshacer_hasta_tipo      (deshace hasta encontrar un tipo)

Las acciones del juego tienen la forma "tipo: detalle", por ejemplo:
    "mover: Nexo de Jerusalén -> Desierto de Judá (evento: trampa: ...)"
    "recoger: Reliquia de San Lázaro"
    "usar: Poción de Mirra"
    "soltar: Bezante Sarraceno"

Por eso las funciones de tipo usan startswith(tipo), como en la guía.

Este módulo se puede correr aparte, como pide la regla 3 de la Guía 1:
    python3 historial.py
"""


# ============================================================
# Programa de referencia (Guía 5) — 3 funciones base
# ============================================================

def apilar_accion(historial, accion):
    """Registra una acción nueva en el historial (push con append)."""
    historial.append(accion)
    print("Acción registrada: " + accion)


def deshacer_ultima_accion(historial):
    """Quita y devuelve la acción más reciente del historial (pop).

    Si el historial está vacío avisa y devuelve None en vez de cerrarse
    con error: ese es el caso límite 'deshacer sin historial'.
    """
    if len(historial) == 0:
        print("No hay nada que deshacer: el historial está vacío.")
        return None
    accion = historial.pop()
    print("Deshaciendo: " + accion)
    return accion


def ver_ultima_accion(historial):
    """Consulta la última acción sin quitarla del historial (peek)."""
    if len(historial) == 0:
        return None
    return historial[-1]


def mostrar_historial(historial):
    """Muestra el historial completo, de la acción MÁS RECIENTE a la más antigua.

    Recorre la pila de arriba hacia abajo (del final de la lista al
    principio), que es el orden natural de una pila LIFO: lo último que
    hizo el rey aparece primero.
    """
    if len(historial) == 0:
        print("El historial está vacío: el rey aún no ha actuado.")
        return
    print("--- HISTORIAL DEL REY (más reciente primero) ---")
    for i in range(len(historial) - 1, -1, -1):
        print("[" + str(i + 1) + "] " + historial[i])
    print("(total de acciones: " + str(len(historial)) + ")")


def vaciar_historial(historial):
    """Vacía el historial por completo (lo usa la resurrección de la Vera Cruz).

    Cuando el rey muere y resucita, su memoria reciente se nubla: la pila
    queda vacía y ya no hay nada que deshacer hasta que vuelva a actuar.
    """
    historial.clear()
    print("El historial del rey queda en blanco.")


# ============================================================
# TU TURNO (Guía 5) — 4 funciones nuevas, adaptadas al juego
# ============================================================

def deshacer_multiples(historial, cantidad):
    """Deshace varias acciones seguidas, hasta 'cantidad' veces o hasta que se vacíe.

    Reutiliza deshacer_ultima_accion() en cada vuelta y corta con break
    si el historial se vacía antes de completar la cantidad pedida.
    """
    for i in range(cantidad):
        if len(historial) == 0:
            print("Ya no hay más acciones que deshacer.")
            break
        deshacer_ultima_accion(historial)


def contar_acciones_de_tipo(historial, tipo):
    """Cuenta cuántas acciones del historial empiezan con cierto tipo, sin modificarlo.

    Recorre con un for normal (sin pop) y usa startswith(tipo), igual que
    en la guía: el historial queda exactamente igual después de la llamada.
    """
    contador = 0
    for accion in historial:
        if accion.startswith(tipo):
            contador += 1
    return contador


def invertir_historial(historial):
    """Invierte el orden del historial usando una pila auxiliar.

    El vaciado con pop() y el rellenado con un for normal (sin pop)
    invierten el orden UNA sola vez. Si el paso del rellenado usara
    pop() de nuevo, las dos inversiones se cancelarían y el historial
    quedaría igual que al principio.
    """
    pila_auxiliar = []
    while len(historial) > 0:
        pila_auxiliar.append(historial.pop())
    for accion in pila_auxiliar:          # for normal: NO usar pop() aquí
        historial.append(accion)
    print("Historial invertido: la acción más antigua ahora es la más reciente.")


def deshacer_hasta_tipo(historial, tipo_objetivo):
    """Deshace repetidamente hasta encontrar y deshacer una acción de cierto tipo.

    Combina un ciclo while con una condición de parada: si el tipo nunca
    aparece, el historial se vacía y avisa en vez de quedarse en un ciclo
    infinito.
    """
    while len(historial) > 0:
        accion = deshacer_ultima_accion(historial)
        if accion.startswith(tipo_objetivo):
            print("Se llegó al tipo buscado: " + tipo_objetivo)
            return
    print("Se vació el historial sin encontrar el tipo: " + tipo_objetivo)


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# Con las acciones REALES del juego, no las genéricas de la guía.
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de historial.py con acciones reales del reino")
    print()

    historial = []

    # 1) Registrar acciones reales del juego (Guía 5: apilar_accion)
    apilar_accion(historial, "mover: Nexo de Jerusalén -> Desierto de Judá (evento: enemigo: Mameluco de Saladino tiende una emboscada (-12))")
    apilar_accion(historial, "mover: Desierto de Judá -> Castillo de Kerak (evento: mensaje: la Vera Cruz susurra: el reino aún es tuyo)")
    apilar_accion(historial, "recoger: Reliquia de San Lázaro")
    apilar_accion(historial, "usar: Poción de Mirra")
    print()

    # 2) Consultar la última sin sacarla (peek)
    print("Última acción (sin sacarla): " + str(ver_ultima_accion(historial)))
    print()

    # 3) Mostrar el historial completo, de la más reciente a la más antigua
    mostrar_historial(historial)
    print()

    # 4) Contar acciones de un tipo sin modificar el historial
    movimientos = contar_acciones_de_tipo(historial, "mover")
    print("Acciones de tipo 'mover': " + str(movimientos))
    print("Historial sin cambios: " + str(len(historial)) + " acciones siguen en la pila")
    print()

    # 5) Deshacer varias de una vez (se piden 2, hay 4)
    deshacer_multiples(historial, 2)
    mostrar_historial(historial)
    print()

    # 6) Deshacer hasta encontrar un tipo que sí existe ("mover")
    deshacer_hasta_tipo(historial, "mover")
    print("Historial restante: " + str(historial))
    print()

    # 7) Deshacer hasta un tipo que NO existe ("volar"): debe vaciarse y avisar
    apilar_accion(historial, "soltar: Bezante Sarraceno")
    deshacer_hasta_tipo(historial, "volar")
    print()

    # 8) Invertir el historial con pila auxiliar
    apilar_accion(historial, "mover: Nexo de Jerusalén -> Egipto de Saladino")
    apilar_accion(historial, "recoger: Sello del Sultán")
    print("Antes de invertir: " + str(historial))
    invertir_historial(historial)
    print("Después de invertir: " + str(historial))
    print()

    # 9) Caso límite: deshacer con el historial vacío
    vaciar_historial(historial)
    deshacer_ultima_accion(historial)
    deshacer_multiples(historial, 3)
    mostrar_historial(historial)
