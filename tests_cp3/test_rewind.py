"""Regression checks for the original checkpoint's undo and FIFO contract."""

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from console_cp3.main import crear_partida, deshacer, mover


class RewindTests(TestCase):
    def test_movement_and_its_event_are_one_reversible_action(self):
        with redirect_stdout(StringIO()), patch("builtins.input", return_value="1"):
            state = crear_partida()
            keys = ("vida", "fase_podredumbre", "sala", "inventario", "cola_eventos", "turnos")
            before = {key: deepcopy(state[key]) for key in keys}
            mover(state)
            self.assertNotEqual(state["sala"], before["sala"])
            self.assertLess(state["vida"], before["vida"])
            self.assertEqual(
                list(state["cola_eventos"]), list(before["cola_eventos"])[1:]
            )
            deshacer(state)
            for key, value in before.items():
                with self.subTest(field=key):
                    self.assertEqual(state[key], value)
            self.assertFalse(state["historial"])

    def test_undo_empty_history_leaves_game_running(self):
        with redirect_stdout(StringIO()) as output:
            state = crear_partida()
            deshacer(state)
        self.assertFalse(state["historial"])
        self.assertTrue(output.getvalue().strip())
