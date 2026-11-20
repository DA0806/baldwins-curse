"""End-to-end mission and map scenarios through the console game's commands."""

from contextlib import redirect_stdout
from io import StringIO
from unittest import TestCase

from console_cp3.main import (
    actuar_mision,
    actualizar_sala,
    crear_partida,
    deshacer,
    eliminar_sala,
    insertar_sala,
    mover,
    recoger_objeto,
    ruta,
    usar_objeto_rey,
)


class CampaignTests(TestCase):
    def test_all_ten_missions_and_sealed_final_chamber(self):
        with redirect_stdout(StringIO()) as output:
            state = crear_partida()
            missions = state["misiones"]

            def go(*rooms):
                for room in rooms:
                    mover(state, room)
                    self.assertEqual(state["sala"], room, output.getvalue())

            def objective(mission):
                actuar_mision(state, mission)
                self.assertIn(mission, missions.completed, output.getvalue())

            go("atrio_1")
            if "despertar" not in missions.completed:
                objective("despertar")
            go("atrio_2")
            objective("juramento")
            go("torre")
            objective("medico")
            go("atrio_2", "atrio_1", "osario")
            recoger_objeto(state)
            self.assertIn("rey_ciego", missions.completed, output.getvalue())
            go("cripta_1", "atrio_3")
            objective("renegado")
            go("cripta_1", "cripta_2", "cisterna")
            recoger_objeto(state)
            self.assertIn("lazaro", missions.completed, output.getvalue())
            usar_objeto_rey(state, "Poción de Mirra")
            self.assertIn("mirra", missions.completed, output.getvalue())
            go("cripta_2", "cripta_1", "osario", "desague")
            recoger_objeto(state)
            self.assertIn("corona", missions.completed, output.getvalue())
            go("cripta_3", "cripta_4", "capilla_1", "capilla_2")
            mover(state, "capilla_3")
            self.assertEqual(state["sala"], "capilla_2")
            objective("mameluco")
            go("capilla_3")
            objective("cruzada")
            self.assertEqual(set(missions.completed), set(missions.NODES))

    def test_undo_mission_restores_dependents_and_item(self):
        with redirect_stdout(StringIO()):
            state = crear_partida()
            mover(state, "atrio_1")
            if "despertar" not in state["misiones"].completed:
                actuar_mision(state, "despertar")
            mover(state, "atrio_2")
            actuar_mision(state, "juramento")
            for room in ("atrio_1", "osario"):
                mover(state, room)
            expected_loot = state["mundo"]["osario"]["tesoro"]
            recoger_objeto(state)
            self.assertIsNone(state["mundo"]["osario"]["tesoro"])
            self.assertTrue(state["misiones"].available("renegado"))
            deshacer(state)
            self.assertEqual(state["mundo"]["osario"]["tesoro"], expected_loot)
            self.assertTrue(state["misiones"].available("rey_ciego"))
            self.assertFalse(state["misiones"].available("renegado"))

    def test_auxiliary_room_updates_graph_and_rewinds_deletion(self):
        with redirect_stdout(StringIO()):
            state = crear_partida()
            origin = state["sala"]
            self.assertTrue(insertar_sala(state, "archivo", "Archivo perdido"))
            self.assertFalse(insertar_sala(state, "archivo", "Duplicado"))
            self.assertTrue(actualizar_sala(state, "archivo", 2))
            self.assertEqual(ruta(state, "archivo"), [origin, "archivo"])
            self.assertTrue(eliminar_sala(state, "archivo"))
            self.assertNotIn("archivo", state["mundo"])
            self.assertEqual(ruta(state, "archivo"), [])
            deshacer(state)
            self.assertEqual(state["mundo"]["archivo"]["peligro"], 2)
            self.assertEqual(ruta(state, "archivo"), [origin, "archivo"])
            self.assertFalse(eliminar_sala(state, origin))
