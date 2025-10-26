"""
Simple player profile system.
Encapsulates loading/saving a JSON-backed profile and provides helpers for choices and world flags.
"""
from pathlib import Path
import json
from typing import Any, Dict


class PlayerProfile:
    def __init__(self, data_dir: Path = None):
        self.root = Path(__file__).resolve().parents[1]
        self.data_dir = data_dir or (self.root / "data")
        self.path = self.data_dir / "player_profile.json"
        self.data: Dict[str, Any] = {"choices": {}, "flags": {}}
        self.load()

    def load(self):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
        except Exception:
            # keep defaults on error
            self.data = {"choices": {}, "flags": {}}

    def save(self):
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    # Choices
    def get_choice(self, encounter_idx: int):
        return self.data.get("choices", {}).get(str(encounter_idx))

    def set_choice(self, encounter_idx: int, selected_index: int, text: str):
        self.data.setdefault("choices", {})[str(encounter_idx)] = {"selected": selected_index, "text": text}
        self.save()

    def choices(self):
        return self.data.get("choices", {})

    # Flags (world state)
    def get_flag(self, key: str, default=None):
        return self.data.get("flags", {}).get(key, default)

    def set_flag(self, key: str, value: Any):
        self.data.setdefault("flags", {})[key] = value
        self.save()

    def clear(self):
        self.data = {"choices": {}, "flags": {}}
        self.save()

    # Account linking (web profile)
    def set_account(self, account_dict: Dict[str, Any]):
        self.data.setdefault('account', {})
        self.data['account'] = account_dict
        self.save()

    def get_account(self):
        return self.data.get('account')
