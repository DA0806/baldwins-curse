"""
main.py — Nexo central de King Baldwin — The Leper's Curse
Estructura de Datos y Algoritmos · Checkpoint 2

La Guía 1 dice que main.py no debe tener la lógica de ninguna estructura:
importa cada módulo (inventario, armas, mascaras, historial, eventos,
mazmorra) y llama sus funciones en el orden correcto para que la partida
corra. Lo único que main.py aporta es la INTEGRACIÓN: cómo el movimiento
del rey dispara un evento de la cola, cómo queda en el historial y cómo el
deshacer rebobina de verdad la partida (backtracking).

Flujo mínimo del checkpoint, todo dentro del ciclo del menú:
    (a) al iniciar, la mazmorra se genera con la función recursiva;
    (b) el rey empieza en el Nexo de Jerusalén y se mueve entre salas conectadas;
    (c) cada movimiento queda en el historial (pila) y dispara el siguiente
        evento de la cola (popleft);
    (d) el rey puede deshacer su última acción y volver atrás de verdad;
    (e) en las salas marcadas (las más profundas) puede recoger un objeto,
        que entra al inventario del Checkpoint 1.

Decisión del equipo sobre los eventos al deshacer (explicada en el README):
cuando se deshace un movimiento, el evento que ese movimiento disparó
VUELVE AL FRENTE de la cola con appendleft y sus efectos se revierten:
deshacer rebobina la partida, no sirve para saltarse eventos.

Ejecutar:  python3 main.py
"""

from .inventario import (
    agregar_objeto, usar_objeto, soltar_objeto, mostrar_inventario,
    buscar_objeto, contar_objeto, vaciar_inventario, objeto_mas_repetido,
    reemplazar_objeto, objetos_unicos, CAPACIDAD_MAXIMA,
)
from .armas import (
    MAX_ARMAS, equipar_arma, intercambiar_armas, soltar_arma_activa,
    arma_activa,
)
from .mascaras import (
    MAX_MASCARAS, agregar_mascara, ciclar_mascara, mascara_activa,
)
from .historial import (
    apilar_accion, deshacer_ultima_accion, ver_ultima_accion,
    mostrar_historial, vaciar_historial, contar_acciones_de_tipo,
)
from .eventos import (
    encolar_evento, procesar_siguiente_evento, ver_siguiente_evento,
    reencolar_al_frente, contar_eventos_de_tipo, simular_turnos,
    crear_cola_eventos, crear_cola_turnos, turno_actual, rotar_turno,
)
from .mazmorra import (
    RAIZ, MUNDO, TESOROS, PROFUNDIDAD_MAXIMA,
    generar_mazmorra, contar_salas_por_nivel, calcular_profundidad_real,
    vecinos_de, mostrar_arbol,
)

VIDA_INICIAL = 100
CURA_POCION = 25

# Eventos reales del mapa del juego (Guía 6): al iniciar la partida se
# encolan en orden de llegada y se procesan con popleft al moverse.
EVENTOS_INICIALES = [
    "enemigo: Mameluco de Saladino tiende una emboscada (-12)",
    "mensaje: la Vera Cruz susurra: el reino aún es tuyo",
    "trampa: dardos envenenados brotan de la arena (-8)",
    "cofre: Bezante Sarraceno",
    "enemigo: Caballero Renegado del Templo bloquea el paso (-12)",
    "trampa: arena movediza en el camino del oasis (-8)",
    "cofre: Poción de Mirra",
]

# Sistema de turnos (Guía 6): al menos 3 participantes que rotan con
# popleft + append. El rey y dos enemigos del reino.
PARTICIPANTES_TURNOS = ["Rey Balduino", "Mameluco de Saladino", "Caballero Renegado"]


# ============================================================
# Estado y presentación de la partida
# ============================================================

def crear_partida():
    """Crea el estado completo de la partida integrando las tres estructuras.

    La mazmorra se genera con la función recursiva (Guía 7), los eventos
    del mapa se encolan uno por uno (Guía 6) y el historial nace vacío
    (Guía 5). Devuelve un diccionario con el estado del rey y del reino.
    """
    # --- Checkpoint 1: inventario, armas y máscaras (siguen funcionando) ---
    inventario = [
        "Vera Cruz",
        "Poción de Mirra",
        "Poción de Mirra",
        "Bezante Sarraceno",
        "Bezante Sarraceno",
    ]
    armas = ["Espada del Sepulcro", None]   # slot 0 activa, slot 1 en espera
    mascaras = [
        "Máscara del Rey Ciego",
        "Máscara de Lázaro",
        "Corona de Espinas Fundida",
    ]

    # --- Guía 7: la mazmorra se genera de forma recursiva ---
    conexiones = []
    salas = []
    salas_marcadas = []
    generar_mazmorra(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO,
                     conexiones, salas, salas_marcadas)

    # --- Guía 6: los eventos del mapa se encolan al iniciar la partida ---
    cola_eventos = crear_cola_eventos()
    for evento in EVENTOS_INICIALES:
        encolar_evento(cola_eventos, evento)

    # --- Guía 6: la fila de turnos con los 3 participantes ---
    turnos = crear_cola_turnos(PARTICIPANTES_TURNOS)

    # --- Guía 5: el historial de acciones nace vacío ---
    historial = []

    return {
        "vida": VIDA_INICIAL,
        "fase_podredumbre": 1,
        "sala": RAIZ,
        "inventario": inventario,
        "armas": armas,
        "slot_arma": 0,
        "mascaras": mascaras,
        "indice_mascara": 0,
        "mazmorra_salas": salas,
        "mazmorra_conexiones": conexiones,
        "salas_marcadas": salas_marcadas,
        "salas_saqueadas": [],
        "cola_eventos": cola_eventos,
        "turnos": turnos,
        "historial": historial,
    }


def mostrar_intro(estado):
    """Muestra la portada de la partida y la mazmorra generada recursivamente."""
    print()
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("=== CHECKPOINT 2: EL REINO RECURSIVO ===")
    print()
    print("El Nexo de Jerusalén despierta. La Vera Cruz brilla entre tus")
    print("manos y la lepra corroe tu carne. La Orden de San Lázaro te")
    print("aguarda: resucitarás una y otra vez, rey leproso, hasta recuperar")
    print("las Máscaras de la Tristeza y enfrentar al Sultán Saladino.")
    print()
    print("--- MAZMORRA GENERADA (función recursiva, Guía 7) ---")
    print("Salas del reino: " + str(len(estado["mazmorra_salas"])) +
          " · profundidad real alcanzada: " +
          str(calcular_profundidad_real(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO)))

    conteo = {}
    contar_salas_por_nivel(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO, conteo)
    partes = []
    for nivel in sorted(conteo):
        partes.append("nivel " + str(nivel) + " -> " + str(conteo[nivel]) + " salas")
    print("Salas por nivel: " + " · ".join(partes))
    print("Salas marcadas (las más profundas, con tesoro): " +
          ", ".join(estado["salas_marcadas"]))
    print()
    print("Árbol del reino:")
    mostrar_arbol(RAIZ, 0, MUNDO, estado["salas_marcadas"], TESOROS)
    print()
    print("Eventos del mapa encolados: " + str(len(estado["cola_eventos"])) +
          " (se procesan en orden de llegada, FIFO)")
    print("Fila de turnos: " + " -> ".join(estado["turnos"]))
    print()


def mostrar_estado(estado):
    """Muestra la condición del rey y del reino antes de cada decisión."""
    print()
    print("==========================================")
    print("  KING BALDWIN — THE LEPER'S CURSE")
    print("==========================================")
    print("  Estás en:", estado["sala"])
    print("  Vida:", estado["vida"],
          "· Podredumbre: fase", str(estado["fase_podredumbre"]) + "/3")
    print("  Arma activa:", arma_activa(estado["armas"], estado["slot_arma"])
          or "(puños del rey leproso)")
    print("  Máscara equipada:",
          mascara_activa(estado["mascaras"], estado["indice_mascara"])
          or "(rostro descarnado)")
    print("  Objetos en la bolsa:", len(estado["inventario"]), "/",
          str(CAPACIDAD_MAXIMA))
    print("  Turno en curso:", turno_actual(estado["turnos"]))
    print("  Eventos pendientes en la cola:", len(estado["cola_eventos"]))
    print("  Historial (acciones apiladas):", len(estado["historial"]))
    print("==========================================")


def mostrar_menu():
    """Escribe el menú principal de la partida (0 a 8)."""
    print()
    print("  1) Moverse a una sala conectada")
    print("  2) Recoger objeto de la sala (solo salas marcadas)")
    print("  3) Deshacer última acción (backtracking)")
    print("  4) Ver historial del rey")
    print("  5) Ver turnos y eventos pendientes")
    print("  6) Inventario del caballero (submenú)")
    print("  7) Armas (equipar / intercambiar / soltar)")
    print("  8) Máscaras (ciclar / recoger nueva)")
    print("  0) Abandonar el reino (salir)")


# ============================================================
# Eventos: aplicar y revertir efectos (la decisión del equipo)
# ============================================================

def extraer_daño(detalle):
    """Extrae el número de daño de un texto de evento como '... (-12)'."""
    inicio = detalle.rfind("(-")
    if inicio == -1:
        return 0
    fin = detalle.find(")", inicio)
    if fin == -1:
        return 0
    try:
        return int(detalle[inicio + 2:fin])
    except ValueError:
        return 0


def aplicar_evento(estado, evento):
    """Aplica en la partida el efecto del evento procesado de la cola.

    Devuelve (murio, con_efecto): murio es True si el rey murió y resucitó
    durante el evento; con_efecto es True si el evento dejó un efecto
    reversible en la partida (un cofre que no pudo entregar su botín porque
    la bolsa estaba llena queda registrado como evento SIN efecto).
    Los tipos de evento del juego son: enemigo (daño), trampa (daño y
    podredumbre), cofre (objeto al inventario) y mensaje (solo narración).
    """
    tipo, detalle = evento.split(": ", 1)
    con_efecto = True

    if tipo == "enemigo":
        daño = extraer_daño(detalle)
        estado["vida"] -= daño
        print("   -> El enemigo hiere al rey: -" + str(daño) +
              " de vida (te quedan " + str(estado["vida"]) + ")")

    elif tipo == "trampa":
        daño = extraer_daño(detalle)
        estado["vida"] -= daño
        if estado["fase_podredumbre"] < 3:
            estado["fase_podredumbre"] += 1
        print("   -> La trampa daña al rey: -" + str(daño) +
              " de vida (te quedan " + str(estado["vida"]) +
              ") · la lepra avanza a fase " + str(estado["fase_podredumbre"]) + "/3")

    elif tipo == "cofre":
        objeto = detalle
        if agregar_objeto(estado["inventario"], objeto):   # valida CAPACIDAD_MAXIMA
            print("   -> El botín entra a la bolsa del caballero.")
        else:
            print("   -> La bolsa está llena: el botín queda en el camino.")
            con_efecto = False      # no hay nada que revertir después

    elif tipo == "mensaje":
        print("   -> La señal fortalece la voluntad del rey leproso.")

    else:
        print("   -> (evento desconocido, el reino es extraño)")
        con_efecto = False

    if estado["vida"] <= 0:
        resucitar(estado)
        return True, False
    return False, con_efecto


def revertir_evento(estado, evento):
    """Revierte el efecto de un evento cuando se deshace el movimiento que lo disparó.

    Es el inverso exacto de aplicar_evento: el enemigo devuelve el daño,
    la trampa retrocede la podredumbre y el cofre devuelve su botín. Así
    el deshacer rebobina la partida de verdad.
    """
    tipo, detalle = evento.split(": ", 1)

    if tipo == "enemigo" or tipo == "trampa":
        daño = extraer_daño(detalle)
        estado["vida"] += daño
        print("   -> Se rebobina el daño: +" + str(daño) +
              " de vida (te quedan " + str(estado["vida"]) + ")")
        if tipo == "trampa" and estado["fase_podredumbre"] > 1:
            estado["fase_podredumbre"] -= 1
            print("   -> La podredumbre retrocede a fase " +
                  str(estado["fase_podredumbre"]) + "/3")

    elif tipo == "cofre":
        objeto = detalle
        soltar_objeto(estado["inventario"], objeto)   # quita el botín (o avisa)

    elif tipo == "mensaje":
        print("   -> El susurro se desvanece retrocediendo en el tiempo.")


def resucitar(estado):
    """La Vera Cruz revive al rey en el Nexo: cuerpo renovado, memoria nublada.

    Al resucitar, la vida y la podredumbre se reinician, el rey vuelve al
    Nexo de Jerusalén y el historial se vacía (la resurrección nubla la
    memoria reciente: ya no hay nada que deshacer). La cola de eventos y
    la fila de turnos continúan como estaban: el mundo sigue su curso.
    """
    print()
    print(">>> La Vera Cruz resplandece: la muerte no retiene al rey <<<")
    estado["vida"] = VIDA_INICIAL
    estado["fase_podredumbre"] = 1
    estado["sala"] = RAIZ
    vaciar_historial(estado["historial"])
    print(">>> Resucitas en el " + RAIZ + " con el cuerpo renovado <<<")


# ============================================================
# Movimiento: historial + evento + turno (la integración del checkpoint)
# ============================================================

def elegir_destino(estado):
    """Pide y valida la sala de destino (por número o por nombre).

    Devuelve la sala destino válida, o None si la elección es inválida.
    Cubre los casos límite: número fuera de rango (incluye 0 y negativos),
    texto que no existe y sala que existe pero NO está conectada.
    """
    vecinas = vecinos_de(estado["sala"], estado["mazmorra_conexiones"])
    print()
    print("Salas conectadas desde " + estado["sala"] + ":")
    for i, sala in enumerate(vecinas, start=1):
        etiqueta = sala
        if sala in estado["salas_marcadas"]:
            if sala in estado["salas_saqueadas"]:
                etiqueta += "  * (marcada, ya saqueada)"
            else:
                etiqueta += "  * (marcada: hay un tesoro)"
        print("  " + str(i) + ") " + etiqueta)

    eleccion = input("Elige una sala (número o nombre): ").strip()

    # Camino 1: eligió por número
    if eleccion.lstrip("-").isdigit():
        numero = int(eleccion)
        if 1 <= numero <= len(vecinas):
            return vecinas[numero - 1]
        print("Opción no válida: ese número no corresponde a ninguna sala")
        print("conectada (hay " + str(len(vecinas)) + " salas conectadas).")
        return None

    # Camino 2: eligió por nombre
    if eleccion == "":
        print("No escribiste ninguna sala: el rey se queda donde está.")
        return None
    if eleccion in estado["mazmorra_salas"]:
        if eleccion in vecinas:
            return eleccion
        print("La sala '" + eleccion + "' existe en el reino, pero NO está")
        print("conectada con tu sala actual: no puedes viajar hasta allí.")
        return None
    print("La sala '" + eleccion + "' no existe en este reino.")
    return None


def mover(estado):
    """Ejecuta el movimiento del rey: historial + evento + rotación de turno.

    Este es el corazón de la integración del Checkpoint 2:
    1. el rey cambia de sala;
    2. el movimiento queda apilado en el historial (si incluye el evento
       que disparó, para poder rebobinarlo al deshacer);
    3. se procesa el siguiente evento de la cola con popleft (si la cola
       está vacía, avisa y sigue: caso límite);
    4. la fila de turnos rota con popleft + append.
    """
    destino = elegir_destino(estado)
    if destino is None:
        return

    origen = estado["sala"]
    estado["sala"] = destino
    print()
    print("Te mueves a:", destino)

    # 1) Se dispara el siguiente evento de la cola (FIFO con popleft)
    evento = procesar_siguiente_evento(estado["cola_eventos"])
    accion = "mover: " + origen + " -> " + destino
    murio = False
    if evento is not None:
        murio, con_efecto = aplicar_evento(estado, evento)
        if con_efecto:
            accion += " (evento: " + evento + ")"
        else:
            # El evento se consumió sin efecto reversible (p. ej. cofre con
            # la bolsa llena): se registra como 'evento sin efecto' para que
            # al deshacer vuelva a la cola pero no se revierta nada.
            accion += " (evento sin efecto: " + evento + ")"
        print("   (quedan " + str(len(estado["cola_eventos"])) +
              " eventos pendientes en la cola)")

    # Si murió y resucitó, la memoria se nubla: la acción no se registra
    if murio:
        print("(La resurrección nubla la memoria: este movimiento no se registra)")
        return

    # 2) El movimiento queda apilado en el historial (LIFO)
    apilar_accion(estado["historial"], accion)

    # 3) La fila de turnos rota: el que actuó vuelve al final
    quien = rotar_turno(estado["turnos"])
    print("Turno consumido: " + quien + " · la fila queda: " +
          " -> ".join(estado["turnos"]))


def recoger_objeto(estado):
    """Recoge el tesoro de una sala marcada y lo agrega al inventario (CP1).

    Solo funciona en las salas más profundas del árbol y mientras no estén
    saqueadas. Si la bolsa está llena, agregar_objeto avisa y el tesoro
    se queda en la sala. La acción queda en el historial para poder
    deshacerla (el objeto vuelve a la sala).
    """
    sala = estado["sala"]
    if sala not in estado["salas_marcadas"]:
        print("Esta sala no está marcada: solo las salas más profundas del")
        print("reino guardan tesoros (mira las salas con * al moverte).")
        return
    if sala in estado["salas_saqueadas"]:
        print("Ya saqueaste esta sala: no queda nada que recoger aquí.")
        return

    objeto = TESOROS.get(sala)
    if objeto is None:
        print("Esta sala marcada no tiene tesoro registrado: el reino es extraño.")
        return

    print()
    print("Sala marcada: " + sala)
    if sala == "Campos de Hattin":
        print("Derrotas a la guardia del Sultán Saladino y saqueas su tienda...")
    if agregar_objeto(estado["inventario"], objeto):   # CP1: valida capacidad 6
        estado["salas_saqueadas"].append(sala)
        apilar_accion(estado["historial"], "recoger: " + objeto)
        print("La sala queda registrada como saqueada.")
    else:
        print("El tesoro permanece en la sala: libera espacio en la bolsa.")


# ============================================================
# Deshacer: rebobinar de verdad la partida (backtracking)
# ============================================================

def revertir_accion(estado, accion):
    """Revierte en el juego el efecto de una acción recién deshecha de la pila.

    Cada tipo de acción se rebobina distinto:
    - mover:  el rey vuelve a la sala de origen y, si el movimiento
              disparó un evento, el evento se des-aplica y vuelve al
              FRENTE de la cola (decisión del equipo: appendleft);
    - recoger: el objeto sale de la bolsa y la sala recupera su tesoro;
    - usar:   el objeto vuelve intacto a la bolsa (y la poción, su cura);
    - soltar: el objeto regresa del suelo a la bolsa (si hay espacio).
    """
    if ": " not in accion:
        print("   -> (acción sin efecto reversible)")
        return
    tipo, resto = accion.split(": ", 1)

    if tipo == "mover":
        ruta = resto
        evento = None
        revertir = True
        if " (evento sin efecto: " in resto:
            ruta, cola_parte = resto.split(" (evento sin efecto: ", 1)
            if cola_parte.endswith(")"):
                evento = cola_parte[:-1]
            else:
                evento = cola_parte
            revertir = False      # se consumió sin efecto: solo se re-encola
        elif " (evento: " in resto:
            ruta, cola_parte = resto.split(" (evento: ", 1)
            # quita SOLO el paréntesis de cierre del envoltorio: el evento
            # original puede terminar en "(-12)" y rstrip(")") lo dañaría
            if cola_parte.endswith(")"):
                evento = cola_parte[:-1]
            else:
                evento = cola_parte
        origen = ruta.split(" -> ", 1)[0]
        estado["sala"] = origen
        print("   -> Backtracking: vuelves a " + origen)
        if evento is not None:
            if revertir:
                revertir_evento(estado, evento)
            else:
                print("   -> El evento no dejó efecto reversible que deshacer.")
            reencolar_al_frente(estado["cola_eventos"], evento)
            print("   (quedan " + str(len(estado["cola_eventos"])) +
                  " eventos pendientes en la cola)")

    elif tipo == "recoger":
        objeto = resto
        soltar_objeto(estado["inventario"], objeto)   # quita el objeto de la bolsa
        if estado["sala"] in estado["salas_saqueadas"]:
            estado["salas_saqueadas"].remove(estado["sala"])
            print("   -> La sala recupera su tesoro: podría volver a recogerse.")

    elif tipo == "usar":
        objeto = resto
        if agregar_objeto(estado["inventario"], objeto):
            print("   -> El objeto vuelve intacto a la bolsa del caballero.")
            if objeto == "Poción de Mirra":
                estado["vida"] -= CURA_POCION
                print("   -> La cura se rebobina: -" + str(CURA_POCION) +
                      " de vida (te quedan " + str(estado["vida"]) + ")")
        else:
            print("   -> La bolsa está llena: el objeto usado no puede volver.")

    elif tipo == "soltar":
        objeto = resto
        if agregar_objeto(estado["inventario"], objeto):
            print("   -> El objeto regresa del suelo a la bolsa del caballero.")
        else:
            print("   -> La bolsa está llena: el objeto queda tirado en la sala.")

    else:
        print("   -> (tipo de acción sin reversión conocida)")


def deshacer(estado):
    """Deshace la última acción del historial y rebobina sus efectos.

    Usa deshacer_ultima_accion() de la pila (pop) y, con lo que devuelve,
    revierte el efecto real en la partida: eso es backtracking de verdad.
    Con el historial vacío, la propia pila avisa y no pasa nada (caso límite).
    """
    accion = deshacer_ultima_accion(estado["historial"])
    if accion is None:
        return
    revertir_accion(estado, accion)


# ============================================================
# Paneles de información: historial, turnos y eventos
# ============================================================

def ver_historial_rey(estado):
    """Muestra el historial completo, la última acción y conteos por tipo."""
    print()
    mostrar_historial(estado["historial"])
    ultima = ver_ultima_accion(estado["historial"])
    if ultima is not None:
        print()
        print("Última acción (sin sacarla de la pila): " + ultima)
    movimientos = contar_acciones_de_tipo(estado["historial"], "mover")
    recogidas = contar_acciones_de_tipo(estado["historial"], "recoger")
    usos = contar_acciones_de_tipo(estado["historial"], "usar")
    sueltos = contar_acciones_de_tipo(estado["historial"], "soltar")
    print()
    print("Conteo por tipo (sin modificar el historial):")
    print("  mover: " + str(movimientos) + " · recoger: " + str(recogidas) +
          " · usar: " + str(usos) + " · soltar: " + str(sueltos))


def ver_turnos_y_eventos(estado):
    """Muestra la fila de turnos (con simular_turnos) y la cola de eventos."""
    print()
    print("--- SISTEMA DE TURNOS (cola rotativa con popleft + append) ---")
    print("Fila de turnos actual: " + " -> ".join(estado["turnos"]))
    print("Turno en curso: " + str(turno_actual(estado["turnos"])))
    print()
    print("Próximos turnos (simulación de 6 rondas con simular_turnos):")
    simular_turnos(list(estado["turnos"]), 6)
    print()
    print("--- COLA DE EVENTOS (FIFO con popleft) ---")
    print("Eventos pendientes: " + str(len(estado["cola_eventos"])))
    siguiente = ver_siguiente_evento(estado["cola_eventos"])
    if siguiente is None:
        print("La cola está vacía: no hay eventos pendientes.")
    else:
        print("Próximo evento (sin sacarlo de la cola): " + siguiente)
    enemigos = contar_eventos_de_tipo(estado["cola_eventos"], "enemigo")
    trampas = contar_eventos_de_tipo(estado["cola_eventos"], "trampa")
    cofres = contar_eventos_de_tipo(estado["cola_eventos"], "cofre")
    mensajes = contar_eventos_de_tipo(estado["cola_eventos"], "mensaje")
    print("Conteo por tipo (sin modificar la cola): " + str(enemigos) +
          " enemigos · " + str(trampas) + " trampas · " + str(cofres) +
          " cofres · " + str(mensajes) + " mensajes")


# ============================================================
# Sub-menús del Checkpoint 1 (inventario, armas y máscaras)
# ============================================================

def menu_inventario(estado):
    """Sub-menú del inventario: las 10 funciones de listas del Checkpoint 1.

    Las acciones de usar y soltar objetos del rey SÍ se registran en el
    historial (son parte de las 4 acciones importantes del checkpoint) y
    por eso también se pueden deshacer. Agregar, vaciar y reemplazar son
    operaciones de mantenimiento de la bolsa y no se registran.
    """
    while True:
        inventario = estado["inventario"]
        print()
        print("  --- INVENTARIO DEL CABALLERO (listas, Checkpoint 1) ---")
        print("  1) Ver inventario")
        print("  2) Agregar objeto a la bolsa")
        print("  3) Usar objeto (consume)")
        print("  4) Soltar objeto")
        print("  5) Buscar objeto")
        print("  6) Contar objeto")
        print("  7) Vaciar inventario")
        print("  8) Objeto más repetido")
        print("  9) Reemplazar objeto")
        print("  10) Objetos únicos")
        print("  0) Volver al reino")
        sub = input("  Sub-opción: ").strip()

        if sub == "1":
            mostrar_inventario(inventario)
        elif sub == "2":
            objeto = input("  Objeto a agregar: ").strip()
            agregar_objeto(inventario, objeto)
        elif sub == "3":
            objeto = input("  Objeto a usar: ").strip()
            usado = usar_objeto(inventario, objeto)
            if usado is not None:
                if objeto == "Poción de Mirra":
                    estado["vida"] += CURA_POCION
                    print("  La Mirra alivia tu carne: +" + str(CURA_POCION) +
                          " de vida (tienes " + str(estado["vida"]) + ")")
                apilar_accion(estado["historial"], "usar: " + objeto)
        elif sub == "4":
            objeto = input("  Objeto a soltar: ").strip()
            soltado = soltar_objeto(inventario, objeto)
            if soltado is not None:
                apilar_accion(estado["historial"], "soltar: " + objeto)
        elif sub == "5":
            objeto = input("  Objeto a buscar: ").strip()
            posicion = buscar_objeto(inventario, objeto)
            if posicion is None:
                print("No tienes " + objeto + " en la bolsa.")
            else:
                print("Posición de " + objeto + ": " + str(posicion))
        elif sub == "6":
            objeto = input("  Objeto a contar: ").strip()
            print("Cantidad de " + objeto + ": " +
                  str(contar_objeto(inventario, objeto)))
        elif sub == "7":
            vaciar_inventario(inventario)
        elif sub == "8":
            mas_repetido = objeto_mas_repetido(inventario)
            if mas_repetido is None:
                print("Tu inventario está vacío")
            else:
                print("El objeto más repetido es: " + mas_repetido)
        elif sub == "9":
            viejo = input("  Objeto viejo: ").strip()
            nuevo = input("  Objeto nuevo: ").strip()
            reemplazar_objeto(inventario, viejo, nuevo)
        elif sub == "10":
            print("Objetos únicos: " + str(objetos_unicos(inventario)))
        elif sub == "0":
            return
        else:
            print("  Sub-opción no válida: elige entre 0 y 10.")


def menu_armas(estado):
    """Sub-menú de armas: cinto de 2 slots (puerto de PlayerInventory.gd)."""
    armas = estado["armas"]
    slot_arma = estado["slot_arma"]
    print()
    print("  a) Equipar un arma nueva")
    print("  b) Intercambiar slots (TAB en Godot)")
    print("  c) Soltar el arma activa (G en Godot)")
    sub = input("  Sub-opción: ").strip().lower()
    if sub == "a":
        nueva = input("  Arma a equipar: ").strip()
        equipar_arma(armas, slot_arma, nueva)
    elif sub == "b":
        estado["slot_arma"] = intercambiar_armas(armas, slot_arma)
    elif sub == "c":
        soltar_arma_activa(armas, slot_arma)
    else:
        print("  Sub-opción no válida: elige a, b o c.")


def menu_mascaras(estado):
    """Sub-menú de máscaras: The Visages of Sorrow (puerto de Godot)."""
    mascaras = estado["mascaras"]
    indice_mascara = estado["indice_mascara"]
    print()
    print("  a) Ciclar máscara (siguiente rostro)")
    print("  b) Recoger máscara nueva")
    sub = input("  Sub-opción: ").strip().lower()
    if sub == "a":
        estado["indice_mascara"] = ciclar_mascara(mascaras, indice_mascara)
    elif sub == "b":
        nueva = input("  Máscara a recoger: ").strip()
        agregar_mascara(mascaras, indice_mascara, nueva)
    else:
        print("  Sub-opción no válida: elige a o b.")


# ============================================================
# Programa principal: el ciclo del menú
# ============================================================

def main():
    """Punto de entrada del juego: crea la partida y corre el ciclo del menú."""
    estado = crear_partida()

    mostrar_intro(estado)
    input("(Presiona Enter para tomar el control del rey leproso...)")

    jugando = True   # variable lógica que controla el bucle (como en PSeInt)
    while jugando:
        mostrar_estado(estado)
        mostrar_menu()
        opcion = input("  Opción: ").strip()

        if opcion == "1":
            mover(estado)
        elif opcion == "2":
            recoger_objeto(estado)
        elif opcion == "3":
            deshacer(estado)
        elif opcion == "4":
            ver_historial_rey(estado)
        elif opcion == "5":
            ver_turnos_y_eventos(estado)
        elif opcion == "6":
            menu_inventario(estado)
        elif opcion == "7":
            menu_armas(estado)
        elif opcion == "8":
            menu_mascaras(estado)
        elif opcion == "0":
            jugando = False
            print()
            print("Abandonas el reino. La Vera Cruz se apaga... hasta la")
            print("próxima resurrección, rey leproso.")
        else:
            print()
            print("Opción no válida: elige entre 0 y 8 (texto, 0 fuera de")
            print("contexto y números negativos no son opciones del menú).")

    print()
    print("Fin de la sesión del caballero leproso.")


if __name__ == "__main__":
    main()
