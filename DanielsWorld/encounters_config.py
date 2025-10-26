"""Configurable encounter generator for DanielsWorld.

This module exports `generate_encounters(screen)` which returns a list of encounter
records in the form expected by AdventureMap:
    {"id": str, "pos": pygame.Vector2, "type": "dialogue"|"minigame", "character": Optional[str]}

Configuration constants provided below:
- ENCOUNTER_COUNT: integer number of encounters (ignored in explicit mode)
- PLACEMENT_MODE: 'random' | 'grid' | 'explicit'
- EXPLICIT_POSITIONS: list of tuples (x_ratio, y_ratio, type, character_or_none, id)

You can edit the constants here to change the map's encounter placement.
"""

import random
import json
from pathlib import Path

# YAML support is optional. If PyYAML is available, we'll use it to read YAML configs.
try:
    import yaml  # type: ignore
    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

# Configuration
ENCOUNTER_COUNT = 5
PLACEMENT_MODE = 'random'  # 'random', 'grid', or 'explicit'
# If explicit, give ratios (0.0-1.0) relative to the screen size
EXPLICIT_POSITIONS = [
    # (x_ratio, y_ratio, type, character, id)
    (0.25, 0.35, 'dialogue', 'Mysterious Stranger', 'enc0'),
    (0.75, 0.6, 'minigame', None, 'enc1'),
    (0.5, 0.8, 'dialogue', 'Lost Robot', 'enc2'),
]

# spacing used for random placement (minimum distance between encounters, pixels)
_MIN_DISTANCE = 120
_MARGIN = 80


def _random_positions(screen, count):
    w, h = screen.get_width(), screen.get_height()
    pts = []
    attempts = 0
    while len(pts) < count and attempts < count * 50:
        attempts += 1
        x = random.uniform(_MARGIN, w - _MARGIN)
        y = random.uniform(_MARGIN, h - _MARGIN)
        too_close = False
        for (px, py) in pts:
            dx = px - x
            dy = py - y
            if (dx*dx + dy*dy) < (_MIN_DISTANCE * _MIN_DISTANCE):
                too_close = True
                break
        # avoid placing exactly in the center where the player spawns
        cx, cy = w / 2, h / 2
        if (x - cx)**2 + (y - cy)**2 < (150**2):
            too_close = True
        if not too_close:
            pts.append((x, y))
    # if we couldn't find enough spread-out points, fill remaining with random
    while len(pts) < count:
        pts.append((random.uniform(_MARGIN, w - _MARGIN), random.uniform(_MARGIN, h - _MARGIN)))
    return pts


def _grid_positions(screen, count):
    w, h = screen.get_width(), screen.get_height()
    # choose rows/cols to be near square
    cols = int((count ** 0.5) + 0.5)
    if cols < 1:
        cols = 1
    rows = (count + cols - 1) // cols
    pts = []
    x_step = w / (cols + 1)
    y_step = h / (rows + 1)
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx >= count:
                break
            x = (c + 1) * x_step
            y = (r + 1) * y_step
            pts.append((x, y))
            idx += 1
    return pts


def generate_encounters(screen):
    """Return list of encounter dicts for the given screen."""
    import pygame
    encounters = []
    # Try to load external config (encounters.json or encounters.yaml) from the DanielsWorld folder.
    cfg = _load_external_config()
    if cfg:
        # cfg is expected to be a dict; keys may override constants.
        mode = cfg.get('placement_mode', PLACEMENT_MODE)
        if mode == 'explicit' and cfg.get('explicit_positions'):
            for tpl in cfg.get('explicit_positions'):
                # support either dict or list/tuple form
                if isinstance(tpl, dict):
                    x_ratio = tpl.get('x_ratio', 0.5)
                    y_ratio = tpl.get('y_ratio', 0.5)
                    etype = tpl.get('type', 'dialogue')
                    char = tpl.get('character')
                    eid = tpl.get('id', f"enc_exp_{len(encounters)}")
                else:
                    x_ratio, y_ratio, etype, char, eid = tpl
                x = int(screen.get_width() * float(x_ratio))
                y = int(screen.get_height() * float(y_ratio))
                rec = {"id": eid, "pos": pygame.Vector2(x, y), "type": etype}
                if char:
                    rec['character'] = char
                encounters.append(rec)
            return encounters
        # For non-explicit modes, allow count override
        cfg_count = int(cfg.get('count', ENCOUNTER_COUNT))
        cfg_mode = mode
    else:
        cfg_count = ENCOUNTER_COUNT
        cfg_mode = PLACEMENT_MODE
    if PLACEMENT_MODE == 'explicit':
        for tpl in EXPLICIT_POSITIONS:
            x_ratio, y_ratio, etype, char, eid = tpl
            x = int(screen.get_width() * x_ratio)
            y = int(screen.get_height() * y_ratio)
            rec = {"id": eid, "pos": pygame.Vector2(x, y), "type": etype}
            if char:
                rec['character'] = char
            encounters.append(rec)
        return encounters

    if cfg_mode == 'grid':
        pts = _grid_positions(screen, cfg_count)
    else:
        pts = _random_positions(screen, cfg_count)

    for i, (x, y) in enumerate(pts):
        etype = 'dialogue' if i % 2 == 0 else 'minigame'
        rec = {"id": f"enc{i}", "pos": pygame.Vector2(int(x), int(y)), "type": etype}
        if etype == 'dialogue':
            # basic default character names; projects can override by editing this file
            rec['character'] = 'Wanderer' if i % 3 else 'Strange One'
        encounters.append(rec)
    return encounters


def _load_external_config():
    """Look for encounters.json or encounters.yaml in the same directory as this file.

    Returns parsed dict or None if no config found or parse error.
    """
    base = Path(__file__).parent
    json_path = base / 'encounters.json'
    yaml_path = base / 'encounters.yaml'
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    if yaml_path.exists() and _HAS_YAML:
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    return None
