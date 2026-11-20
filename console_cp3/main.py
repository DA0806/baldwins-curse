"""Consola CP3: integración de los módulos originales del equipo y la campaña.

La pila de etiquetas usa historial.py (append/pop). Una pila paralela guarda
instantáneas profundas para restaurar duplicados, orden FIFO, turno, mundo,
grafo y árbol con exactitud. La muerte conserva la regla CP2: borra el historial.
"""
from copy import deepcopy
from . import cp2, inventario, armas, mascaras, mundo
from .eventos import procesar_siguiente_evento, rotar_turno
from .historial import apilar_accion, deshacer_ultima_accion
from .grafo import Graph
from .misiones import MissionTree, NODES
from .mazmorra import RAIZ


# Estas claves son las dos pilas; no se incluyen recursivamente en cada copia.
STACK_KEYS = {"historial", "reversiones"}


def instantanea(estado):
    return deepcopy({key: value for key, value in estado.items() if key not in STACK_KEYS})


def registrar(estado, antes, etiqueta):
    if antes == instantanea(estado):
        return False
    estado["reversiones"].append(antes)
    apilar_accion(estado["historial"], etiqueta)
    return True


def crear_partida():
    estado = cp2.crear_partida()
    # En CP3 las máscaras son recompensas de las misiones, no equipo inicial.
    estado["mascaras"] = []
    estado["indice_mascara"] = 0
    graph = Graph()
    for room in estado["mazmorra_salas"]:
        graph.add_node(room)
    for first, second in estado["mazmorra_conexiones"]:
        graph.add_edge(first, second)
    graph.add_edge(RAIZ, "atrio_1")
    for first, children in mundo.CAMPAIGN_TREE.items():
        for second in children:
            graph.add_edge(first, second)
    for first, second in mundo.EXTRA_EDGES:
        graph.add_edge(first, second)
    estado.update({"grafo": graph, "misiones": MissionTree(),
                   "mundo": mundo.crear_mundo(graph.adjacency), "reversiones": []})
    estado["mundo"][RAIZ]["visitada"] = True
    return estado


def vecinos_transitables(estado, sala):
    result = estado["grafo"].neighbors(sala)
    # La puerta del Abad se abre al derrotar al campeón, como Expedition.gd.
    if sala == "capilla_2" and "mameluco" not in estado["misiones"].completed:
        result = [room for room in result if room != "capilla_3"]
    return result


def ruta(estado, destino):
    return estado["grafo"].shortest_path(
        estado["sala"], destino, lambda room: vecinos_transitables(estado, room))


def deshacer(estado):
    if not estado["historial"]:
        deshacer_ultima_accion(estado["historial"])
        return False
    etiqueta = deshacer_ultima_accion(estado["historial"])
    before = estado["reversiones"].pop()
    history, snapshots = estado["historial"], estado["reversiones"]
    estado.clear()
    estado.update(before)
    estado["historial"], estado["reversiones"] = history, snapshots
    print("Estado restaurado exactamente: " + etiqueta)
    print("El evento vuelve al frente, con su orden y turno originales.")
    return True


def resucitar(estado):
    cp2.resucitar(estado)
    estado["reversiones"].clear()
    estado["mundo"][RAIZ]["visitada"] = True


def _completar(estado, mission):
    if estado["misiones"].complete(mission):
        print("Misión completada: " + NODES[mission][1])
        return True
    return False


def elegir_destino(estado):
    neighbors = vecinos_transitables(estado, estado["sala"])
    print("Salas conectadas (0 para volver):")
    for number, room in enumerate(neighbors, 1):
        print(f"  {number}) {room} — {estado['mundo'][room]['nombre']}")
    selected = input("Destino (número o ID): ").strip()
    if selected == "0":
        return None
    if selected in neighbors:
        return selected
    if selected in estado["mundo"]:
        print("Sala conocida, pero no conectada o con puerta bloqueada.")
        return None
    try:
        number = int(selected)
    except ValueError:
        number = 0
    if 1 <= number <= len(neighbors):
        return neighbors[number - 1]
    print("Destino no válido: elige una sala conectada o 0 para volver.")
    return None


def mover(estado, destino=None):
    if destino is None:
        destino = elegir_destino(estado)
    if destino is None:
        return False
    if destino not in estado["mundo"]:
        print("Sala desconocida.")
        return False
    if destino not in vecinos_transitables(estado, estado["sala"]):
        print("Sala no conectada o puerta bloqueada.")
        return False
    antes, origen = instantanea(estado), estado["sala"]
    estado["sala"] = destino
    estado["mundo"][destino].update({"visitada": True})
    print("Te mueves a: " + destino)
    event = procesar_siguiente_evento(estado["cola_eventos"])
    if event is not None:
        # Reutiliza las reglas de daño/cofres del equipo. CP2 limpia historial al morir.
        died, _effect = cp2.aplicar_evento(estado, event)
        if died:
            estado["reversiones"].clear()
            print("La resurrección borra el historial; este movimiento no se registra.")
            return True
    who = rotar_turno(estado["turnos"])
    print("Turno consumido: " + str(who))
    if destino == "atrio_1":
        _completar(estado, "despertar")
    registrar(estado, antes, f"mover: {origen} -> {destino}")
    return True


def recoger_objeto(estado):
    sala = estado["sala"]
    treasure = estado["mundo"].get(sala, {}).get("tesoro")
    if not treasure:
        print("No queda tesoro para recoger en esta sala.")
        return False
    mission = {"osario": "rey_ciego", "cisterna": "lazaro", "desague": "corona"}.get(sala)
    if mission and not estado["misiones"].available(mission):
        print("La misión de esta máscara está bloqueada o ya completada.")
        return False
    antes = instantanea(estado)
    if mission:
        if treasure not in estado["mascaras"]:
            mascaras.agregar_mascara(estado["mascaras"], estado["indice_mascara"], treasure)
        _completar(estado, mission)
    elif not inventario.agregar_objeto(estado["inventario"], treasure):
        return False
    estado["mundo"][sala].update({"tesoro": None})
    estado["salas_saqueadas"].append(sala)
    registrar(estado, antes, "recoger: " + treasure)
    return True


def usar_objeto_rey(estado, objeto):
    if objeto not in estado["inventario"]:
        print("No tienes " + objeto)
        return False
    if objeto == "Poción de Mirra" and estado["vida"] >= cp2.VIDA_INICIAL:
        print("Ya tienes la vida completa; conservas la poción.")
        return False
    antes = instantanea(estado)
    inventario.usar_objeto(estado["inventario"], objeto)
    if objeto == "Poción de Mirra":
        estado["vida"] = min(cp2.VIDA_INICIAL, estado["vida"] + cp2.CURA_POCION)
        print("La Mirra restaura tu vida: " + str(estado["vida"]))
        if estado["sala"] == "cisterna":
            _completar(estado, "mirra")
    registrar(estado, antes, "usar: " + objeto)
    return True


def actuar_mision(estado, mission_id=None):
    tree = estado["misiones"]
    local = [mission for mission in tree.available_by_level()
             if NODES[mission][2] == estado["sala"]]
    if mission_id is None:
        if not local:
            print("No hay objetivos disponibles en esta sala; consulta el diario.")
            return False
        mission_id = local[0]
    if mission_id not in NODES:
        print("Misión desconocida.")
        return False
    if mission_id not in local:
        print("Misión bloqueada, completada o ubicada en otra sala.")
        return False
    if mission_id in ("rey_ciego", "lazaro", "corona"):
        return recoger_objeto(estado)
    if mission_id == "mirra":
        return usar_objeto_rey(estado, "Poción de Mirra")
    antes = instantanea(estado)
    if mission_id in ("renegado", "mameluco", "cruzada"):
        if armas.arma_activa(estado["armas"], estado["slot_arma"]) is None:
            print("Necesitas equipar un arma para enfrentar al guardián.")
            return False
        enemy = estado["mundo"][estado["sala"]]["enemigo"]
        damage = {"renegado": 8, "mameluco": 12, "cruzada": 20}[mission_id]
        estado["vida"] -= damage
        print(f"Combates contra {enemy}: recibes {damage} de daño.")
        rotar_turno(estado["turnos"])
        if estado["vida"] <= 0:
            resucitar(estado)
            return True
        estado["mundo"][estado["sala"]].update({"enemigo": None, "peligro": 0})
    print(NODES[mission_id][3])
    _completar(estado, mission_id)
    registrar(estado, antes, "misión: " + NODES[mission_id][1])
    if mission_id == "cruzada":
        print("El Abad cae. Cruzas la salida: La Última Cruzada ha terminado.")
    return True


def insertar_sala(estado, sala, nombre=None):
    if not _nombre_valido(sala) or not _nombre_valido(nombre or sala):
        print("ID y nombre deben contener letras; no se admiten valores vacíos.")
        return False
    antes = instantanea(estado)
    if not mundo.insertar(estado["mundo"], sala, nombre or sala):
        print("La sala ya existe o su nombre no es válido.")
        return False
    estado["grafo"].add_edge(estado["sala"], sala)
    registrar(estado, antes, "insertar: " + sala)
    print("Sala auxiliar insertada y conectada a " + estado["sala"])
    return True


def actualizar_sala(estado, sala, peligro):
    antes = instantanea(estado)
    if not mundo.actualizar_peligro(estado["mundo"], sala, peligro):
        print("Sala desconocida o peligro inválido (entero entre 0 y 3).")
        return False
    registrar(estado, antes, "actualizar: " + sala)
    print("Peligro actualizado.")
    return True


def eliminar_sala(estado, sala):
    if sala == estado["sala"]:
        print("No puedes eliminar la sala actual.")
        return False
    antes = instantanea(estado)
    if not mundo.eliminar(estado["mundo"], sala):
        print("Solo se pueden eliminar salas auxiliares existentes; la campaña está protegida.")
        return False
    estado["grafo"].remove_node(sala)
    registrar(estado, antes, "eliminar: " + sala)
    print("Sala auxiliar eliminada del diccionario y del grafo.")
    return True


def _nombre_valido(texto):
    return isinstance(texto, str) and bool(texto.strip()) and any(char.isalpha() for char in texto)


def _pedir_nombre(prompt):
    value = input(prompt + " (0 para volver): ").strip()
    if value == "0":
        return None
    if not _nombre_valido(value):
        print("Nombre no válido: escribe un nombre con letras.")
        return None
    return value


def _mutar(estado, etiqueta, function, *args):
    antes = instantanea(estado)
    function(*args)
    return registrar(estado, antes, etiqueta)


def menu_inventario(estado):
    while True:
        print("\nINVENTARIO: 1 Ver, 2 Agregar, 3 Usar, 4 Soltar, 5 Buscar, 6 Contar,")
        print("7 Vaciar, 8 Más repetido, 9 Reemplazar, 10 Únicos, 0 Volver")
        option = input("Sub-opción: ").strip()
        bag = estado["inventario"]
        if option == "0":
            return
        if option == "1":
            inventario.mostrar_inventario(bag)
        elif option in ("2", "3", "4", "5", "6"):
            item = _pedir_nombre("Objeto")
            if item is None:
                continue
            if option == "2":
                _mutar(estado, "agregar: " + item, inventario.agregar_objeto, bag, item)
            elif option == "3":
                usar_objeto_rey(estado, item)
            elif option == "4":
                _mutar(estado, "soltar: " + item, inventario.soltar_objeto, bag, item)
            elif option == "5":
                position = inventario.buscar_objeto(bag, item)
                print("No encontrado" if position is None else "Posición: " + str(position))
            else:
                print("Cantidad: " + str(inventario.contar_objeto(bag, item)))
        elif option == "7":
            _mutar(estado, "vaciar: inventario", inventario.vaciar_inventario, bag)
        elif option == "8":
            print("Más repetido: " + str(inventario.objeto_mas_repetido(bag)))
        elif option == "9":
            old = _pedir_nombre("Objeto viejo")
            if old is None:
                continue
            new = _pedir_nombre("Objeto nuevo")
            if new is not None:
                _mutar(estado, "reemplazar: " + old, inventario.reemplazar_objeto, bag, old, new)
        elif option == "10":
            print("Únicos: " + str(inventario.objetos_unicos(bag)))
        else:
            print("Sub-opción no válida: elige entre 0 y 10.")


def menu_armas(estado):
    while True:
        print("\nARMAS: a/1 Equipar, b/2 Intercambiar, c/3 Soltar, 0 Volver")
        option = input("Sub-opción: ").strip().lower()
        if option == "0":
            return
        belt, slot = estado["armas"], estado["slot_arma"]
        if option in ("a", "1"):
            name = _pedir_nombre("Arma")
            if name is not None:
                _mutar(estado, "equipar: " + name, armas.equipar_arma, belt, slot, name)
        elif option in ("b", "2"):
            antes = instantanea(estado)
            estado["slot_arma"] = armas.intercambiar_armas(belt, slot)
            registrar(estado, antes, "intercambiar: arma")
        elif option in ("c", "3"):
            _mutar(estado, "soltar: arma", armas.soltar_arma_activa, belt, slot)
        else:
            print("Sub-opción no válida: a, b, c, 1, 2, 3 o 0.")


def menu_mascaras(estado):
    while True:
        print("\nMÁSCARAS: a/1 Ciclar, b/2 Recoger nueva, 0 Volver")
        option = input("Sub-opción: ").strip().lower()
        if option == "0":
            return
        belt, index = estado["mascaras"], estado["indice_mascara"]
        if option in ("a", "1"):
            antes = instantanea(estado)
            estado["indice_mascara"] = mascaras.ciclar_mascara(belt, index)
            registrar(estado, antes, "ciclar: máscara")
        elif option in ("b", "2"):
            name = _pedir_nombre("Máscara")
            if name is not None:
                _mutar(estado, "equipar: " + name, mascaras.agregar_mascara, belt, index, name)
        else:
            print("Sub-opción no válida: a, b, 1, 2 o 0.")


def _mostrar_ruta(estado, destino):
    if destino not in estado["mundo"]:
        print("Sala desconocida.")
        return
    path = ruta(estado, destino)
    if not path:
        print("Sin ruta: sala desconectada o puerta bloqueada.")
    else:
        print("Ruta mínima BFS (" + str(len(path) - 1) + " pasos): " + " -> ".join(path))


def menu_mapa(estado):
    while True:
        print("\nMAPA: 1 Alcance BFS, 2 Exploración DFS, 3 Ruta mínima, 0 Volver")
        option = input("Sub-opción: ").strip()
        graph = estado["grafo"]
        neighbors = lambda room: vecinos_transitables(estado, room)
        if option == "0":
            return
        if option == "1":
            print("Alcance BFS: " + " -> ".join(graph.bfs(estado["sala"], neighbors)))
        elif option == "2":
            order = graph.dfs(estado["sala"], neighbors)
            print("Exploración DFS: " + " -> ".join(order))
            print("Pendientes de visitar: " + ", ".join(room for room in order
                  if not estado["mundo"][room]["visitada"]))
        elif option == "3":
            print("IDs: " + ", ".join(estado["mundo"]))
            room = _pedir_nombre("ID de destino")
            if room is not None:
                _mostrar_ruta(estado, room)
        else:
            print("Sub-opción no válida: elige entre 0 y 3.")


def menu_misiones(estado):
    while True:
        print("\nMISIONES: 1 Diario en preorden, 2 Disponibles por nivel, 3 Ruta a misión, 0 Volver")
        option = input("Sub-opción: ").strip()
        tree = estado["misiones"]
        if option == "0":
            return
        if option == "1":
            for entry in tree.preorder():
                mission = entry["id"]
                status = "COMPLETA" if mission in tree.completed else "DISPONIBLE" if tree.available(mission) else "BLOQUEADA"
                print("  " * entry["depth"] + f"[{status}] {mission}: {NODES[mission][1]} — {NODES[mission][2]}")
                print("  " * entry["depth"] + NODES[mission][3])
        elif option == "2":
            pending = tree.available_by_level()
            if not pending:
                print("No quedan misiones disponibles; la campaña está completada.")
            for mission in pending:
                print(mission + ": " + NODES[mission][1])
                _mostrar_ruta(estado, NODES[mission][2])
        elif option == "3":
            mission = _pedir_nombre("ID de misión")
            if mission is None:
                continue
            if mission not in NODES:
                print("Misión desconocida.")
            else:
                _mostrar_ruta(estado, NODES[mission][2])
        else:
            print("Sub-opción no válida: elige entre 0 y 3.")


def menu_mundo(estado):
    while True:
        print("\nMUNDO: 1 Consultar sala, 2 Actualizar peligro, 3 Insertar auxiliar,")
        print("4 Eliminar auxiliar, 5 Tesoros pendientes (filtro), 6 Resumen de peligro, 0 Volver")
        option = input("Sub-opción: ").strip()
        if option == "0":
            return
        if option in ("1", "2", "3", "4"):
            room = _pedir_nombre("ID de sala")
            if room is None:
                continue
            if option == "1":
                data = mundo.consultar_sala(estado["mundo"], room)
                print("Sala desconocida." if data is None else str(data))
            elif option == "2":
                # Aquí 0 es un dato válido: representa una sala sin peligro.
                raw = input("Peligro 0–3 (Enter para cancelar): ").strip()
                if not raw:
                    continue
                try:
                    danger = int(raw)
                except ValueError:
                    print("Peligro no válido: escribe un entero entre 0 y 3.")
                    continue
                actualizar_sala(estado, room, danger)
            elif option == "3":
                name = _pedir_nombre("Nombre de la sala auxiliar")
                if name is not None:
                    insertar_sala(estado, room, name)
            else:
                eliminar_sala(estado, room)
        elif option == "5":
            print("Tesoros pendientes: " + str(mundo.filtrar_tesoros_pendientes(estado["mundo"])))
        elif option == "6":
            print("Resumen: " + str(mundo.resumir_peligro(estado["mundo"])))
        else:
            print("Sub-opción no válida: elige entre 0 y 6.")


def mostrar_menu():
    print("\n1 Moverse  2 Recoger  3 Deshacer  4 Historial  5 Turnos y eventos")
    print("6 Inventario  7 Armas  8 Máscaras  9 Mapa  10 Misiones  11 Mundo")
    print("12 Realizar objetivo de la sala  0 Salir")


def main():
    estado = crear_partida()
    try:
        cp2.mostrar_intro(estado)
        print("CHECKPOINT 3: mapas con ciclos, árbol de misiones y diccionario del mundo.")
        print("El puente del Nexo conduce a atrio_1. Usa 10 para el diario y 12 para actuar.")
        while True:
            cp2.mostrar_estado(estado)
            mostrar_menu()
            option = input("Opción: ").strip()
            if option == "0":
                print("Abandonas el reino. Fin de la sesión.")
                return estado
            actions = {"1": mover, "2": recoger_objeto, "3": deshacer,
                       "4": cp2.ver_historial_rey, "5": cp2.ver_turnos_y_eventos,
                       "6": menu_inventario, "7": menu_armas, "8": menu_mascaras,
                       "9": menu_mapa, "10": menu_misiones, "11": menu_mundo,
                       "12": actuar_mision}
            action = actions.get(option)
            if action is None:
                print("Opción no válida: elige entre 0 y 12.")
            else:
                action(estado)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada finalizada. Abandonas el reino sin error.")
        return estado


if __name__ == "__main__":
    main()
