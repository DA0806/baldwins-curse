#!/usr/bin/env bash
# Smoke de Baldwin's Curse: importa el proyecto y lo arranca 120 iteraciones
# en modo headless. Falla si Godot devuelve un código distinto de 0 o si la
# salida contiene errores de parseo, carga o ejecución (Godot puede terminar
# con código 0 aunque un script no compile).
#
# Uso:
#   GODOT=/ruta/al/binario tools/smoke.sh              # proyecto actual
#   GODOT=/ruta/al/binario tools/smoke.sh --self-test  # demuestra que detecta una falla
#   tools/smoke.sh --project /otra/ruta                # otro directorio de proyecto
#
# No comprueba la presentación visual: headless no renderiza.
set -u

GODOT="${GODOT:-godot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$ROOT"
SELF_TEST=0
FIRST_ROOM='res://Scenes/Rooms/Atrio1.tscn'
ERROR_PATTERN='SCRIPT ERROR|^ERROR:|Parse Error|Parser Error|Failed to load|Failed loading|Cannot open file|Invalid call|Invalid access|Nonexistent function'

while [ $# -gt 0 ]; do
	case "$1" in
		--self-test) SELF_TEST=1 ;;
		--project) shift; PROJECT="$1" ;;
		*) echo "Argumento desconocido: $1" >&2; exit 2 ;;
	esac
	shift
done

if ! command -v "$GODOT" >/dev/null 2>&1; then
	echo "No encuentro Godot ('$GODOT'). Define GODOT=/ruta/al/ejecutable." >&2
	exit 2
fi

run_smoke() { # $1 = directorio de proyecto; devuelve 0 si está limpio
	local project="$1" log status=0
	log="$(mktemp -t baldwins-smoke.XXXXXX)"
	echo "== Godot $("$GODOT" --version 2>/dev/null | tail -1) · $project"
	{
		echo "--- import"
		"$GODOT" --headless --recovery-mode --path "$project" --import || status=$?
		echo "--- arranque (120 iteraciones)"
		"$GODOT" --headless --path "$project" --quit-after 120 || status=$?
		# La escena principal es el plano de entrada, que no carga la jugabilidad:
		# se arranca también la primera sala de la campaña (jugador, HUD, enemigos).
		echo "--- primera sala ($FIRST_ROOM, 120 iteraciones)"
		"$GODOT" --headless --path "$project" --quit-after 120 "$FIRST_ROOM" || status=$?
	} >"$log" 2>&1
	if [ "$status" -ne 0 ]; then
		echo "FALLA: Godot terminó con código $status (log: $log)"
		return 1
	fi
	if grep -nE "$ERROR_PATTERN" "$log"; then
		echo "FALLA: la salida contiene errores (log: $log)"
		return 1
	fi
	echo "OK: import y arranque sin errores (log: $log)"
	return 0
}

if [ "$SELF_TEST" -eq 1 ]; then
	# Copia el proyecto, rompe un script a propósito y exige que el smoke falle.
	tmp="$(mktemp -d -t baldwins-selftest.XXXXXX)"
	trap 'rm -rf "$tmp"' EXIT
	rsync -a --exclude .git --exclude .godot "$ROOT/" "$tmp/"
	printf '\nfunc _roto(:\n' >> "$tmp/Scripts/Player.gd"
	if run_smoke "$tmp"; then
		echo "SELF-TEST FALLÓ: el smoke no detectó el script roto."
		exit 1
	fi
	echo "SELF-TEST OK: el smoke detectó el script roto."
	exit 0
fi

run_smoke "$PROJECT"
