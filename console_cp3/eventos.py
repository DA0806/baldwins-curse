"""
eventos.py — Cola de eventos del reino y sistema de turnos
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 2

Semana 6, Guía 6: los eventos del mapa forman una COLA (FIFO) con
collections.deque porque deben suceder en orden de llegada: el primer
peligro programado del reino es el primero que se procesa. El sistema de
turnos también es una cola rotativa: el que juega vuelve al final de la
fila (popleft + append).

Contiene las 3 funciones del programa de referencia de la Guía 6
(encolar_evento, procesar_siguiente_evento, ver_siguiente_evento), un par
de funciones propias del juego (reencolar_al_frente para la decisión de
deshacer, y las colas de turnos), y las 4 funciones de "Tu turno" ya
adaptadas a los eventos reales del juego:

    - procesar_multiples_eventos  (procesa varios seguidos)
    - contar_eventos_de_tipo      (cuenta por tipo, sin modificar)
    - invertir_cola               (invierte con una pila auxiliar)
    - simular_turnos              (reparte turnos en ciclo)

Los eventos del juego tienen la forma "tipo: detalle", por ejemplo:
    "enemigo: Mameluco de Saladino tiende una emboscada (-12)"
    "trampa: dardos envenenados brotan de la arena (-8)"
    "cofre: Bezante Sarraceno"
    "mensaje: la Vera Cruz susurra: el reino aún es tuyo"

Por eso las funciones de tipo usan startswith(tipo), como en la guía.

Este módulo se puede correr aparte, como pide la regla 3 de la Guía 1:
    python3 eventos.py
"""

from collections import deque


# ============================================================
# Programa de referencia (Guía 6) — 3 funciones base
# ============================================================

def crear_cola_eventos():
    """Crea la cola de eventos del mapa vacía (un deque nuevo)."""
    return deque()


def encolar_evento(cola_eventos, evento):
    """Registra un evento nuevo al final de la cola (enqueue con append)."""
    cola_eventos.append(evento)
    print("Evento encolado: " + evento)


def procesar_siguiente_evento(cola_eventos):
    """Quita y devuelve el evento más antiguo de la cola (dequeue con popleft).

    Si la cola está vacía avisa y devuelve None en vez de cerrarse con
    error: ese es el caso límite 'procesar evento con la cola vacía'.
    """
    if len(cola_eventos) == 0:
        print("No hay eventos pendientes.")
        return None
    evento = cola_eventos.popleft()
    print("Procesando: " + evento)
    return evento


def ver_siguiente_evento(cola_eventos):
    """Consulta el evento más antiguo sin quitarlo de la cola (peek)."""
    if len(cola_eventos) == 0:
        return None
    return cola_eventos[0]


def reencolar_al_frente(cola_eventos, evento):
    """Devuelve un evento ya procesado al FRENTE de la cola (appendleft).

    Decisión del equipo para el deshacer: cuando el rey deshace un
    movimiento, el evento que ese movimiento disparó vuelve a quedar
    pendiente y es el PRÓXIMO en volverse a procesar. Así deshacer no
    sirve para saltarse eventos: el peligro regresa al frente.
    """
    cola_eventos.appendleft(evento)
    print("El evento vuelve al frente de la cola: seguirá pendiente.")
    print("   -> " + evento)


# ============================================================
# Sistema de turnos (Guía 6): cola rotativa con popleft + append
# ============================================================

def crear_cola_turnos(participantes):
    """Convierte la lista de participantes del combate en una cola de turnos."""
    return deque(participantes)


def turno_actual(turnos):
    """Devuelve quién tiene el turno ahora (el frente de la fila), sin rotar."""
    if len(turnos) == 0:
        return None
    return turnos[0]


def rotar_turno(turnos):
    """Rota la fila de turnos: el que juega sale del frente y vuelve al final.

    popleft() saca al participante que actúa y append() lo devuelve al
    final para que espere su siguiente turno: la fila nunca se vacía y el
    ciclo se repite cada N movimientos (N = cantidad de participantes).
    Devuelve el participante que tomó el turno.
    """
    if not turnos:
        print("No hay participantes en la fila de turnos.")
        return None
    actual = turnos.popleft()
    turnos.append(actual)
    return actual


def simular_turnos(personajes, rondas):
    """Reparte turnos en ciclo: el que juega vuelve al final de la fila.

    Función de la Guía 6 adaptada al juego: crea su propia cola a partir
    de la lista de personajes (no modifica la cola real de la partida) y
    muestra cómo se repite el orden de turnos ronda tras ronda.
    """
    turnos = deque(personajes)
    if not turnos:
        print("No hay participantes para simular.")
        return
    for numero_ronda in range(1, rondas + 1):
        actual = turnos.popleft()
        print("Ronda " + str(numero_ronda) + ": le toca a " + actual)
        turnos.append(actual)


# ============================================================
# TU TURNO (Guía 6) — 4 funciones nuevas, adaptadas al juego
# ============================================================

def procesar_multiples_eventos(cola_eventos, cantidad):
    """Procesa varios eventos seguidos, hasta 'cantidad' veces o hasta que se vacíe.

    Reutiliza procesar_siguiente_evento() en cada vuelta y corta con
    break si la cola se vacía antes de completar la cantidad pedida.
    """
    for i in range(cantidad):
        if len(cola_eventos) == 0:
            print("Ya no hay más eventos que procesar.")
            break
        procesar_siguiente_evento(cola_eventos)


def contar_eventos_de_tipo(cola_eventos, tipo):
    """Cuenta cuántos eventos de la cola empiezan con cierto tipo, sin modificarla.

    Recorre el deque con un for normal (sin popleft), exactamente igual
    que recorreríamos una lista: la cola queda igual después de llamarla.
    """
    contador = 0
    for evento in cola_eventos:
        if evento.startswith(tipo):
            contador += 1
    return contador


def invertir_cola(cola_eventos):
    """Invierte el orden de la cola usando una pila auxiliar (una lista normal).

    La primera vuelta vacía la cola con popleft() (sale el más antiguo)
    y la segunda vuelve a encolar sacando de la pila con pop() (sale el
    último apilado). Combinar un vaciado FIFO con un rellenado LIFO
    invierte el orden UNA sola vez, sin cancelarse.
    """
    pila_auxiliar = []
    while len(cola_eventos) > 0:
        pila_auxiliar.append(cola_eventos.popleft())
    while len(pila_auxiliar) > 0:
        cola_eventos.append(pila_auxiliar.pop())
    print("Cola invertida: el último evento en llegar sería el próximo en salir.")


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# Con los eventos REALES del juego, no los genéricos de la guía.
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de eventos.py con eventos reales del reino")
    print()

    # 1) Encolar los eventos reales del mapa del juego
    cola = crear_cola_eventos()
    encolar_evento(cola, "enemigo: Mameluco de Saladino tiende una emboscada (-12)")
    encolar_evento(cola, "mensaje: la Vera Cruz susurra: el reino aún es tuyo")
    encolar_evento(cola, "trampa: dardos envenenados brotan de la arena (-8)")
    encolar_evento(cola, "cofre: Bezante Sarraceno")
    print()

    # 2) Consultar el siguiente sin sacarlo (peek)
    print("Siguiente evento (sin sacarlo): " + str(ver_siguiente_evento(cola)))
    print()

    # 3) Procesar varios seguidos (se piden 2)
    procesar_multiples_eventos(cola, 2)
    print("Cola restante: " + str(list(cola)))
    print()

    # 4) Contar eventos de un tipo sin modificar la cola
    trampas = contar_eventos_de_tipo(cola, "trampa")
    cofres = contar_eventos_de_tipo(cola, "cofre")
    print("Trampas pendientes: " + str(trampas) + " · Cofres pendientes: " + str(cofres))
    print("Cola sin cambios: " + str(list(cola)))
    print()

    # 5) Reencolar al frente (la decisión del equipo para el deshacer)
    reencolar_al_frente(cola, "mensaje: la Vera Cruz susurra: el reino aún es tuyo")
    print("Cola con el evento al frente: " + str(list(cola)))
    procesar_siguiente_evento(cola)   # vuelve a salir el mismo evento
    print()

    # 6) Invertir la cola con pila auxiliar
    print("Antes de invertir: " + str(list(cola)))
    invertir_cola(cola)
    print("Después de invertir: " + str(list(cola)))
    print()

    # 7) Sistema de turnos: 3 participantes reales del juego
    print("--- SISTEMA DE TURNOS (cola rotativa) ---")
    participantes = ["Rey Balduino", "Mameluco de Saladino", "Caballero Renegado"]
    turnos = crear_cola_turnos(participantes)
    print("Fila inicial: " + str(list(turnos)))
    for i in range(5):
        quien = rotar_turno(turnos)
        print("Movimiento " + str(i + 1) + " -> turno de: " + quien + " · fila queda: " + str(list(turnos)))
    print()

    # 8) Simular turnos con la función de la Guía 6 (no toca la cola real)
    print("Simulación de 6 rondas con simular_turnos:")
    simular_turnos(participantes, 6)
    print()

    # 9) Caso límite: procesar con la cola vacía
    cola_vacia = crear_cola_eventos()
    procesar_siguiente_evento(cola_vacia)
    procesar_multiples_eventos(cola_vacia, 4)
    print("Siguiente evento de una cola vacía: " + str(ver_siguiente_evento(cola_vacia)))
