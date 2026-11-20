"""Smoke tests through the entry point the course uses."""

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def play(*inputs: str) -> str:
    result = subprocess.run(
        [sys.executable, "-B", "main.py"],
        cwd=ROOT,
        input="\n".join(inputs) + "\n",
        text=True,
        capture_output=True,
        timeout=8,
        check=False,
    )
    if result.returncode or "Traceback" in result.stderr:
        raise AssertionError(f"Game exited with {result.returncode}:\n{result.stderr}")
    return result.stdout


class ConsoleEntryPointTests(unittest.TestCase):
    def test_invalid_main_menu_values_and_zero_to_exit(self):
        output = play("", "texto", "-1", "999", "0").casefold()
        self.assertGreaterEqual(output.count("no válida"), 3)
        self.assertIn("fin de la sesión", output)

    def test_submenus_accept_invalid_values_without_crashing(self):
        # Exercise each submenu from a new game to isolate its input.
        for option in ("6", "7", "8", "9", "10", "11"):
            for invalid in ("texto", "-1", "999", "0"):
                with self.subTest(option=option, invalid=invalid):
                    output = play("", option, invalid, "0", "0").casefold()
                    self.assertIn("fin de la sesión", output)
                    if invalid != "0":
                        self.assertIn("no válida", output)

    def test_original_dungeon_route_with_event_and_undo(self):
        output = play("", "1", "1", "3", "0")
        self.assertIn("Desierto de Judá", output)
        self.assertIn("Nexo de Jerusalén", output)
        self.assertIn("Mameluco de Saladino", output)
        self.assertIn("Fin de la sesión", output)

    def test_eof_leaves_cleanly(self):
        output = play("", "9")
        self.assertIn("Entrada finalizada", output)

    def test_unknown_and_sealed_routes_from_the_map(self):
        output = play("", "9", "3", "fantasma", "3", "capilla_3", "0", "0")
        self.assertIn("Sala desconocida", output)
        self.assertIn("Sin ruta", output)

    def test_destinations_reject_non_decimal_and_out_of_range_input(self):
        output = play("", "1", "²", "1", "-1", "1", "9" * 4400, "1", "0", "0")
        self.assertEqual(output.count("Destino no válido"), 3)
        self.assertIn("Fin de la sesión", output)

    def test_invalid_danger_stays_in_world_menu(self):
        output = play("", "11", "2", "atrio_1", "texto",
                      "2", "atrio_1", "-1", "2", "atrio_1", "0", "6", "0", "0")
        self.assertIn("Peligro no válido", output)
        self.assertIn("peligro inválido", output)
        self.assertIn("Peligro actualizado", output)
        self.assertIn("Resumen:", output)
