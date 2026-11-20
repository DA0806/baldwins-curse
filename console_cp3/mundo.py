"""Diccionario de salas: consulta segura, edición y consultas del reino."""
from .mazmorra import TESOROS, MUNDO, RAIZ

# Árbol y pasajes de Expedition.gd; se mantienen también las siete salas CP2.
CAMPAIGN_TREE = {
    "atrio_1": ["atrio_2", "osario"], "atrio_2": ["atrio_3", "torre"],
    "atrio_3": ["cripta_1"], "osario": ["desague"],
    "cripta_1": ["cripta_2"], "cripta_2": ["cripta_3", "cisterna"],
    "cripta_3": ["cripta_4"], "cripta_4": ["capilla_1"],
    "capilla_1": ["capilla_2"], "capilla_2": ["capilla_3"],
}
EXTRA_EDGES = [("osario", "cripta_1"), ("cisterna", "cripta_4"),
               ("torre", "atrio_3"), ("desague", "cripta_3")]
ENEMIES = {"atrio_3": "Caballero Renegado", "capilla_2": "Mameluco de Saladino",
           "capilla_3": "Abad"}
TREASURES = {"osario": "Máscara del Rey Ciego", "cisterna": "Máscara de Lázaro",
             "desague": "Corona de Espinas Fundida"}


CAMPAIGN_ROOMS = set(CAMPAIGN_TREE) | {child for children in CAMPAIGN_TREE.values() for child in children}
CP2_ROOMS = {RAIZ} | set(MUNDO) | {child for children in MUNDO.values() for child in children}


def room_name(room):
    if room in CP2_ROOMS:
        return room
    if room == "desague":
        return "Desagüe"
    if "_" not in room:
        return room.capitalize()
    name, number = room.split("_", 1)
    return name.capitalize() + " · " + number


def crear_mundo(salas):
    world = {}
    for room in salas:
        enemy = ENEMIES.get(room)
        world[room] = {
            "nombre": room_name(room), "tipo": "campaña" if room in CAMPAIGN_ROOMS else "reino CP2",
            "peligro": 3 if enemy else 1, "visitada": False,
            "tesoro": TESOROS.get(room, TREASURES.get(room)),
            "enemigo": enemy, "auxiliar": False,
        }
    return world


def consultar_sala(mundo, sala):
    return mundo.get(sala)


def actualizar_peligro(mundo, sala, peligro):
    room = mundo.get(sala)
    if room is None or type(peligro) is not int or not 0 <= peligro <= 3:
        return False
    room.update({"peligro": peligro})
    return True


def insertar(mundo, sala, nombre):
    if not sala.strip() or sala in mundo or not nombre.strip():
        return False
    mundo[sala] = {"nombre": nombre, "tipo": "auxiliar", "peligro": 0,
                   "visitada": False, "tesoro": None, "enemigo": None, "auxiliar": True}
    return True


def eliminar(mundo, sala):
    room = mundo.get(sala)
    if room is None or not room["auxiliar"]:
        return False
    del mundo[sala]
    return True


def filtrar_tesoros_pendientes(mundo):
    """Consulta 1: localizar botín aún disponible sin mutar el diccionario."""
    return {key: room["tesoro"] for key, room in mundo.items() if room.get("tesoro")}


def resumir_peligro(mundo):
    """Consulta 2: planificar por peligro y medir salas visitadas."""
    levels = {level: 0 for level in range(4)}
    visited = 0
    for room in mundo.values():
        levels[room.get("peligro", 0)] += 1
        visited += bool(room.get("visitada", False))
    return {"por_peligro": levels, "visitadas": visited, "total": len(mundo)}
