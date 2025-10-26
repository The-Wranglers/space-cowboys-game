"""
Small helpers to normalize and denormalize UI coordinates/radii relative to a reference size.
Used so UI elements maintain relative placement when the window is resized.

Functions:
- get_ref_size(bg_image, screen): if bg_image present return its size else screen size
- set_encounters_normalized(enc_list, ref_size): annotate each encounter dict with '_pos_norm'
- recalc_encounter_positions(enc_list, screen, ref_size): update enc['pos'] to absolute values for current screen
- normalize_point, denormalize_point
- normalize_radius, denormalize_radius

Design: non-destructive; keeps original absolute 'pos' and adds a '_pos_norm' key for stored ratios.
"""
from typing import Iterable, Tuple
import pygame

def get_ref_size(bg_image, screen) -> Tuple[int, int]:
    """Return reference size (width, height). Prefer background image if present."""
    try:
        if bg_image is not None:
            return bg_image.get_size()
    except Exception:
        pass
    return (screen.get_width(), screen.get_height())


def normalize_point(x: float, y: float, ref_size: Tuple[int, int]) -> Tuple[float, float]:
    rw, rh = ref_size
    if rw <= 0 or rh <= 0:
        return (0.0, 0.0)
    return (x / rw, y / rh)


def denormalize_point(x_ratio: float, y_ratio: float, screen: pygame.Surface) -> Tuple[int, int]:
    sw, sh = screen.get_width(), screen.get_height()
    return (int(sw * x_ratio), int(sh * y_ratio))


def normalize_radius(radius: float, ref_size: Tuple[int, int]) -> float:
    # store radius as fraction of the larger dimension
    rw, rh = ref_size
    biggest = max(1, rw, rh)
    return radius / biggest


def denormalize_radius(radius_ratio: float, screen: pygame.Surface) -> int:
    sw, sh = screen.get_width(), screen.get_height()
    biggest = max(1, sw, sh)
    return max(1, int(radius_ratio * biggest))


def set_encounters_normalized(enc_list: Iterable[dict], ref_size: Tuple[int, int]):
    """Annotate encounter dicts with '_pos_norm' and optional '_radius_norm'.

    Each encounter is expected to have a 'pos' key that is a pygame.Vector2 or (x,y).
    The function is non-destructive: it writes into each dict a '_pos_norm' tuple (x_ratio,y_ratio).
    """
    for enc in enc_list:
        pos = enc.get('pos')
        if pos is None:
            continue
        try:
            if hasattr(pos, 'x') and hasattr(pos, 'y'):
                x, y = float(pos.x), float(pos.y)
            else:
                x, y = float(pos[0]), float(pos[1])
        except Exception:
            continue
        enc['_pos_norm'] = normalize_point(x, y, ref_size)
        # if a radius value is present store normalized radius
        r = enc.get('radius')
        if r is not None:
            enc['_radius_norm'] = normalize_radius(float(r), ref_size)


def recalc_encounter_positions(enc_list: Iterable[dict], screen: pygame.Surface, ref_size: Tuple[int,int]):
    """Using stored '_pos_norm' values, update each encounter's 'pos' to an absolute pygame.Vector2 for the current screen size."""
    for enc in enc_list:
        norm = enc.get('_pos_norm')
        if norm:
            try:
                x, y = denormalize_point(norm[0], norm[1], screen)
                enc['pos'] = pygame.Vector2(x, y)
            except Exception:
                pass
        # if radius normalization present, update runtime 'radius' as well
        rnorm = enc.get('_radius_norm')
        if rnorm is not None:
            try:
                enc['radius'] = denormalize_radius(rnorm, screen)
            except Exception:
                pass
