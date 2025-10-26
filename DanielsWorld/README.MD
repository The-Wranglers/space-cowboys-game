DanielsWorld — Level & encounter authoring
=========================================

This folder contains the map runtime and a small authoring workflow for placing "encounters" (dialogue events, minigames, etc.) on the map.

Files of interest
- `adventure_map.py` — Main map class. When created without a custom `encounter_generator`, it will attempt to load encounter placement from `DanielsWorld/encounters_config.py` or from a JSON/YAML config file (see below).
- `encounters_config.py` — Python-based defaults and a small generator. You can edit this file or use an external config file (`encounters.json` or `encounters.yaml`) to let designers place encounters without editing Python.

How encounter placement works
----------------------------

When an `AdventureMap` instance is created, the constructor tries the following in order:

1. If you pass a callable `encounter_generator` to the constructor, it will be used directly.
2. Otherwise, the map tries to import `DanielsWorld.encounters_config` and call `generate_encounters(screen)` from that module.
3. If the module is not present or fails, a built-in default placement is used.

External JSON/YAML configuration
--------------------------------

Designers can provide `encounters.json` or `encounters.yaml` in the `DanielsWorld/` directory. The configuration supports three placement modes:

- `placement_mode: explicit` — supply explicit positions (relative ratios 0.0–1.0)
- `placement_mode: grid` — evenly space a number of encounters in a grid
- `placement_mode: random` — randomly scatter encounters with basic spacing rules

Example `encounters.json` (explicit mode):

```json
{
	"placement_mode": "explicit",
	"explicit_positions": [
		{"x_ratio": 0.25, "y_ratio": 0.35, "type": "dialogue", "character": "Mysterious Stranger", "id": "enc0"},
		{"x_ratio": 0.75, "y_ratio": 0.60, "type": "minigame", "id": "enc1"},
		{"x_ratio": 0.50, "y_ratio": 0.80, "type": "dialogue", "character": "Lost Robot", "id": "enc2"}
	]
}
```

Example `encounters.yaml` (random mode):

```yaml
placement_mode: random
count: 6
```

Notes
- If both `encounters.json` and `encounters.yaml` exist, `encounters.json` takes precedence.
- YAML parsing requires `PyYAML` (the code will fall back to JSON if PyYAML isn't available).
- Encounter IDs, types and characters are copied into the generated list and will appear in the runtime logs.

Debugging and logs
------------------

`adventure_map.py` logs which generator was used and prints the final encounter list to stdout at initialization. This helps designers confirm placements without running the full game.

Authoring workflow suggestion
----------------------------

1. Edit `encounters.json` using the explicit format for precise control.
2. Run the map to verify positions (the logger prints encounter coordinates).
3. If you want procedural placement, set `placement_mode` to `grid` or `random` and adjust `count`.

If you want me to add a small helper script that prints encounter positions for a given resolution (without launching the full game), tell me and I will add `tools/print_encounters.py`.

Happy level designing!
