"""The reusable structures also work outside of the Baldwin map."""

from unittest import TestCase

from console_cp3.grafo import Graph
from console_cp3.misiones import MissionTree
from console_cp3.mundo import (
    actualizar_peligro,
    consultar_sala,
    eliminar,
    filtrar_tesoros_pendientes,
    insertar,
    resumir_peligro,
)


class StructuresTests(TestCase):
    def test_bfs_shortest_path_and_dfs_on_cycles_and_isolated_nodes(self):
        graph = Graph()
        for first, second in ((0, 1), (1, 2), (2, 3), (3, 0), (0, None)):
            graph.add_edge(first, second)
        graph.add_node(9)
        self.assertEqual(graph.shortest_path(None, 3), [None, 0, 3])
        self.assertEqual(graph.shortest_path(0, 2), [0, 1, 2])
        self.assertEqual(graph.shortest_path(0, 9), [])
        self.assertEqual(graph.bfs(9), [9])
        self.assertEqual(graph.dfs(99), [])
        self.assertEqual(set(graph.dfs(0)), {0, 1, 2, 3, None})

    def test_mission_guards_and_orders(self):
        missions = MissionTree()
        self.assertEqual(len(missions.preorder()), 10)
        self.assertEqual(max(row["depth"] for row in missions.preorder()), 4)
        self.assertFalse(missions.complete("cruzada"))
        self.assertFalse(missions.complete("missing"))
        self.assertTrue(missions.complete("despertar"))
        self.assertFalse(missions.complete("despertar"))
        self.assertEqual(missions.available_by_level(), ["juramento", "medico"])

    def test_world_dictionary_mutations_and_two_queries(self):
        world = {}
        self.assertIsNone(consultar_sala(world, "unmapped"))
        self.assertFalse(eliminar(world, "unmapped"))
        self.assertTrue(insertar(world, "tower", "Torre de prueba"))
        self.assertFalse(insertar(world, "tower", "Duplicado"))
        self.assertFalse(actualizar_peligro(world, "tower", -1))
        self.assertTrue(actualizar_peligro(world, "tower", 2))
        world["tower"]["tesoro"] = "Mirra"
        self.assertEqual(filtrar_tesoros_pendientes(world), {"tower": "Mirra"})
        self.assertEqual(resumir_peligro(world)["por_peligro"][2], 1)
        self.assertTrue(eliminar(world, "tower"))
        self.assertIsNone(consultar_sala(world, "tower"))
