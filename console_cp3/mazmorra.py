"""
mazmorra.py — Mazmorra recursiva del Reino de Jerusalén
King Baldwin — The Leper's Curse · Estructura de Datos y Algoritmos · Checkpoint 2

Semana 7, Guía 7: la mazmorra se genera con una función RECURSIVA que tiene
un caso base y un caso recursivo claros (patrón de generar_arbol_genealogico /
generar_salas de la guía), pero con las zonas reales del mapa del equipo
(mapa_baldwin.png): el Nexo de Jerusalén como raíz, y de ahí cuelgan el
Desierto de Judá y el Egipto de Saladino; del desierto cuelgan el Castillo de
Kerak y el Oasis de los Peregrinos, y de Egipto los Campos de Hattin y la
Siria de Nur.

Estructura del árbol (profundidad 2, 7 salas, 6 conexiones):

    Nexo de Jerusalén            (nivel 0 · raíz, aquí revive la Vera Cruz)
    ├── Desierto de Judá         (nivel 1)
    │   ├── Castillo de Kerak            (nivel 2 · sala marcada: tesoro)
    │   └── Oasis de los Peregrinos      (nivel 2 · sala marcada: tesoro)
    └── Egipto de Saladino      (nivel 1)
        ├── Campos de Hattin            (nivel 2 · sala marcada: jefe/tesoro)
        └── Siria de Nur                (nivel 2 · sala marcada: tesoro)

Adaptaciones de la Guía 7 incluidas (se piden mínimo 2, traemos 3):
    1. contar_salas_por_nivel      <- contar_personas_por_generacion
    2. generar_mazmorra marca las salas más profundas (tesoros/jefes)
                                      <- generar_arbol_marcando_sin_descendencia
    3. calcular_profundidad_real   <- calcular_generaciones_totales (combina con max())

Este módulo se puede correr aparte, como pide la regla 3 de la Guía 1:
    python3 mazmorra.py
"""


# ============================================================
# El mundo del juego (tomado del mapa_baldwin.png del equipo)
# Cada sala apunta a la lista de sus salas hijas. Las salas de
# nivel 2 (las hojas) no tienen hijas registradas: ahí termina
# cada rama y por eso son las salas marcadas con tesoro.
# ============================================================

RAIZ = "Nexo de Jerusalén"
PROFUNDIDAD_MAXIMA = 2

MUNDO = {
    "Nexo de Jerusalén": ["Desierto de Judá", "Egipto de Saladino"],
    "Desierto de Judá": ["Castillo de Kerak", "Oasis de los Peregrinos"],
    "Egipto de Saladino": ["Campos de Hattin", "Siria de Nur"],
}

# Las salas más profundas quedan marcadas y guardan un tesoro real del concepto
# del juego (los mismos objetos del inventario del Checkpoint 1).
TESOROS = {
    "Castillo de Kerak": "Reliquia de San Lázaro",
    "Oasis de los Peregrinos": "Poción de Mirra",
    "Campos de Hattin": "Sello del Sultán",
    "Siria de Nur": "Bezante Sarraceno",
}


# ============================================================
# Generación recursiva (Guía 7: programa de referencia adaptado)
# ============================================================

def generar_mazmorra(sala_actual, profundidad, max_profundidad, mundo,
                     conexiones, salas, salas_marcadas):
    """Genera la mazmorra del reino de forma recursiva y marca las salas más profundas.

    Adaptación de generar_salas() y generar_arbol_marcando_sin_descendencia()
    de la Guía 7: en vez de nombres inventados como "1.1.2", las salas toman
    los nombres reales de las zonas del mapa del juego.

    Caso base:     la sala alcanza la profundidad máxima; se registra en
                   salas_marcadas (allí van los tesoros y el jefe) y se corta
                   la rama sin seguir generando.
    Caso recursivo: la sala aún no llega al fondo; por cada sala hija del
                   mundo se registra la conexión (padre -> hija) y se vuelve
                   a llamar a la función con profundidad + 1.
    """
    salas.append(sala_actual)

    if profundidad >= max_profundidad:          # CASO BASE
        salas_marcadas.append(sala_actual)      # hoja del árbol: sala del tesoro
        return

    for hija in mundo.get(sala_actual, []):     # CASO RECURSIVO
        conexiones.append((sala_actual, hija))
        generar_mazmorra(hija, profundidad + 1, max_profundidad, mundo,
                         conexiones, salas, salas_marcadas)


def contar_salas_por_nivel(sala_actual, nivel, max_profundidad, mundo, conteo):
    """Cuenta cuántas salas hay en cada nivel de la mazmorra, en un diccionario acumulador.

    Adaptación de contar_personas_por_generacion() de la Guía 7:
    usa conteo.get(nivel, 0) + 1 para no revisar si el nivel ya existía.
    No modifica la mazmorra, solo la recorre.
    """
    conteo[nivel] = conteo.get(nivel, 0) + 1

    if nivel >= max_profundidad:                # caso base: rama al fondo
        return

    for hija in mundo.get(sala_actual, []):     # caso recursivo
        contar_salas_por_nivel(hija, nivel + 1, max_profundidad, mundo, conteo)


def calcular_profundidad_real(sala_actual, nivel, max_profundidad, mundo):
    """Calcula la profundidad real de la mazmorra: el nivel más profundo alcanzado.

    Adaptación de calcular_generaciones_totales() de la Guía 7: en vez de
    llenar una lista mientras recorre, devuelve un valor que se combina con
    max() a partir de lo que le devuelven sus propias llamadas recursivas
    (el mismo patrón de factorial, que combinaba con *).

    Caso base:     la sala está en la profundidad máxima o no tiene hijas
                   registradas; esa rama termina y devuelve su nivel.
    Caso recursivo: pregunta a cada rama su profundidad y se queda con max().
    """
    hijas = mundo.get(sala_actual, [])
    if nivel >= max_profundidad or not hijas:   # casos base
        return nivel

    profundidades = []
    for hija in hijas:                          # caso recursivo
        profundidades.append(
            calcular_profundidad_real(hija, nivel + 1, max_profundidad, mundo)
        )
    return max(profundidades)                   # combina con max()


def vecinos_de(sala, conexiones):
    """Devuelve la lista de salas conectadas a una sala (sus vecinas de movimiento).

    Recorre las conexiones (padre -> hija) del árbol en ambos sentidos:
    del padre se puede bajar a las hijas y de una hija volver a subir al
    padre, para que el rey pueda regresar de una sala profunda.
    """
    vecinas = []
    for padre, hija in conexiones:
        if padre == sala and hija not in vecinas:
            vecinas.append(hija)
        elif hija == sala and padre not in vecinas:
            vecinas.append(padre)
    return vecinas


def mostrar_arbol(sala_actual, nivel, mundo, salas_marcadas, tesoros):
    """Muestra la mazmorra como árbol de sangrías, marcando las salas del fondo.

    También es recursiva: imprime la sala actual con una sangría según su
    nivel y llama a la función sobre cada hija.
    """
    sangria = "   " * nivel
    linea = sangria + sala_actual
    if sala_actual in salas_marcadas:
        linea += "   [marcada: tesoro -> " + tesoros.get(sala_actual, "?") + "]"
    print(linea)
    for hija in mundo.get(sala_actual, []):
        mostrar_arbol(hija, nivel + 1, mundo, salas_marcadas, tesoros)


# ============================================================
# Prueba del módulo por separado (regla 3, Guía 1)
# ============================================================

if __name__ == "__main__":
    print("=== KING BALDWIN — THE LEPER'S CURSE ===")
    print("Prueba de mazmorra.py (generación recursiva del reino)")
    print()

    # 1) Generar la mazmorra completa
    conexiones = []
    salas = []
    salas_marcadas = []
    generar_mazmorra(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO,
                     conexiones, salas, salas_marcadas)

    print("Salas generadas (" + str(len(salas)) + "):")
    print("  " + str(salas))
    print()
    print("Conexiones (padre -> hija):")
    for conexion in conexiones:
        print("  " + str(conexion))
    print()
    print("Salas marcadas (las más profundas):")
    print("  " + str(salas_marcadas))
    print()

    # 2) Contar salas por nivel (adaptación 1 de la Guía 7)
    conteo = {}
    contar_salas_por_nivel(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO, conteo)
    print("Salas por nivel:")
    for nivel in sorted(conteo):
        print("  nivel " + str(nivel) + " -> " + str(conteo[nivel]) + " salas")
    print()

    # 3) Profundidad real (adaptación 3 de la Guía 7)
    profundidad = calcular_profundidad_real(RAIZ, 0, PROFUNDIDAD_MAXIMA, MUNDO)
    print("Profundidad real alcanzada: " + str(profundidad))
    print()

    # 4) El árbol con sangrías
    print("Árbol del reino:")
    mostrar_arbol(RAIZ, 0, MUNDO, salas_marcadas, TESOROS)
    print()

    # 5) Vecinas de movimiento
    print("Vecinas del Nexo de Jerusalén: " + str(vecinos_de(RAIZ, conexiones)))
    print("Vecinas del Desierto de Judá:  " + str(vecinos_de("Desierto de Judá", conexiones)))
    print("Vecinas de la raíz inexistente 'Atlantis': " + str(vecinos_de("Atlantis", conexiones)))
