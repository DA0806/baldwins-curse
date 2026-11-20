"""Árbol de misiones trasladado fielmente de Scripts/Rooms/MissionTree.gd."""
from collections import deque

ROOT = "despertar"
# id: (padre, título, sala, objetivo). El orden conserva el árbol del juego.
NODES = {
    "despertar": ("", "El Despertar del Rey", "atrio_1", "Vuelve a la vida en el Atrio del Voto."),
    "juramento": ("despertar", "El Juramento de la Vera Cruz", "atrio_2", "Presta juramento junto al brasero."),
    "rey_ciego": ("juramento", "Máscara del Rey Ciego", "osario", "Recoge la máscara en la galería baja."),
    "renegado": ("rey_ciego", "Caballero Renegado", "atrio_3", "Vence al caballero de la puerta."),
    "lazaro": ("juramento", "Máscara de Lázaro", "cisterna", "Recoge la máscara sobre las ménsulas."),
    "mirra": ("lazaro", "Poción de Mirra", "cisterna", "Bebe mirra cuando te falte vida."),
    "medico": ("despertar", "Consejo del Médico Real", "torre", "Lee el consejo del médico al pie de la Torre."),
    "corona": ("medico", "Corona de Espinas Fundida", "desague", "Recoge la corona en el último descenso."),
    "mameluco": ("corona", "Mameluco de Saladino", "capilla_2", "Derrota al campeón que guarda la capilla."),
    "cruzada": ("mameluco", "La Última Cruzada", "capilla_3", "Vence al Abad y cruza la salida."),
}


class MissionTree:
    ROOT, NODES = ROOT, NODES

    def __init__(self):
        self.completed = {}
        self.children = {}
        for mission, (parent, *_rest) in NODES.items():
            self.children.setdefault(parent, []).append(mission)

    def __eq__(self, other):
        return isinstance(other, MissionTree) and self.completed == other.completed and self.children == other.children

    def available(self, mission):
        if mission not in NODES or mission in self.completed:
            return False
        parent = NODES[mission][0]
        return not parent or parent in self.completed

    def complete(self, mission):
        if not self.available(mission):
            return False
        self.completed[mission] = True
        return True

    def preorder(self):
        result = []
        def visit(mission, depth):
            result.append({"id": mission, "depth": depth})
            for child in self.children.get(mission, []):
                visit(child, depth + 1)
        visit(ROOT, 0)
        return result

    def available_by_level(self):
        queue, result = deque([ROOT]), []
        while queue:
            mission = queue.popleft()
            if self.available(mission):
                result.append(mission)
            queue.extend(self.children.get(mission, []))
        return result
