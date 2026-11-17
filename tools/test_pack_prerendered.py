"""Integration checks for the prerender packer's file and alpha contracts."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


TOOL = Path(__file__).with_name("pack_prerendered.py")
SHEETS = [
    *(('baldwin', name, 128, 128, count, f'Characters/Baldwin/{name}.png')
      for name, count in [('Idle', 4), ('Walk', 8), ('Jump', 6), ('Attack', 5), ('Dead', 6), ('Hurt', 2)]),
    ('custodio', 'poses', 96, 48, 4, 'Enemies/custodio.png'),
    ('custodio_sellado', 'poses', 96, 48, 4, 'Enemies/custodio_sellado.png'),
    ('acolito', 'poses', 64, 48, 4, 'Enemies/acolito.png'),
    ('abad', 'poses', 224, 128, 9, 'Bosses/abad.png'),
]


class PackTests(unittest.TestCase):
    # Create independent inputs with transparent magenta outside ivory shapes.
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.frames = self.root / 'frames'
        self.output = self.root / 'output'
        for actor, action, width, height, count, destination in SHEETS:
            folder = self.frames / actor / action
            folder.mkdir(parents=True)
            image = Image.new('RGBA', (width * 4, height * 4), (255, 0, 255, 0))
            bottom = height if actor != 'abad' else 121
            ImageDraw.Draw(image).rectangle((80, (height - 38) * 4, 175, bottom * 4 - 1), fill=(229, 214, 179, 255))
            for frame in range(count):
                image.save(folder / f'{frame:03}.png')
            original = self.root / 'Sprites' / destination
            original.parent.mkdir(parents=True, exist_ok=True)
            Image.new('RGBA', (width * count, height), (100, 120, 140, 255)).save(original)

    # Run the actual CLI so installation and validation exercise real files.
    def run_tool(self, *arguments):
        return subprocess.run([sys.executable, str(TOOL), '--project-root', str(self.root),
                               '--frames-dir', str(self.frames), '--output-dir', str(self.output), *arguments],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Catch accidental installation, recentering, bad alpha math and backup replacement.
    def test_pack_preserves_anchor_and_requires_explicit_install(self):
        original = self.root / 'Sprites/Characters/Baldwin/Idle.png'
        original_bytes = original.read_bytes()
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(original.read_bytes(), original_bytes)
        with Image.open(self.output / 'Characters/Baldwin/Idle.png') as packed:
            self.assertEqual(packed.size, (512, 128))
            frame = packed.crop((0, 0, 128, 128))
            self.assertEqual(frame.getchannel('A').getbbox(), (20, 90, 44, 128))
            colors = [pixel[:3] for pixel in frame.getdata() if pixel[3]]
            self.assertTrue(all(r > 190 and g > 175 and 100 < b < 210 for r, g, b in colors))
            self.assertEqual(set(packed.getchannel('A').getdata()), {0, 255})
        self.assertTrue((self.output.parent / 'gallery.png').is_file())
        self.assertTrue((self.output.parent / 'comparison.png').is_file())
        result = self.run_tool('--install')
        self.assertEqual(result.returncode, 0, result.stderr)
        backup = self.root / 'Art/Meshy/prerendered/before/Characters/Baldwin/Idle.png'
        self.assertEqual(backup.read_bytes(), original_bytes)
        self.assertNotEqual(original.read_bytes(), original_bytes)
        original.write_bytes(b'replaced after first install')
        result = self.run_tool('--install')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(backup.read_bytes(), original_bytes)

    # Reject actual clipped geometry before writing a partial batch.
    def test_clipped_frame_stops_all_output(self):
        path = self.frames / 'acolito/poses/000.png'
        with Image.open(path) as source:
            image = source.copy()
        ImageDraw.Draw(image).rectangle((0, 20, 8, 30), fill=(229, 214, 179, 255))
        image.save(path)
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('clip', result.stderr.lower())
        self.assertFalse(self.output.exists())

    # Reject missing frames and RGB inputs instead of silently converting them.
    def test_incomplete_and_non_rgba_inputs_are_rejected(self):
        path = self.frames / 'abad/poses/008.png'
        path.unlink()
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        Image.new('RGB', (896, 512), 'white').save(path)
        result = self.run_tool()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('RGBA', result.stderr)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
