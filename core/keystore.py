# core/keystore.py

import json
import os

KEYSTORE_PATH = "data/keystore_keys.json"
os.makedirs("data", exist_ok=True)

# ─────────────────────────────────────────────
# LOAD & SAVE
# ─────────────────────────────────────────────

def _load() -> dict:
    """Load keystore from JSON file."""
    if not os.path.exists(KEYSTORE_PATH):
        return {}
    with open(KEYSTORE_PATH, "r") as f:
        return json.load(f)


def _save(data: dict):
    """Save keystore to JSON file."""
    with open(KEYSTORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

def get_keys(software: str, dept: str) -> list:
    """
    Returns active (not hidden) Key IDs 
    for a specific software + dept combination.
    """
    data = _load()
    sw_data   = data.get(software, {})
    dept_data = sw_data.get(dept.lower(), {})

    # dept_data can be list (old) or dict with hidden flag (new)
    if isinstance(dept_data, list):
        return dept_data

    # Filter out hidden keys
    return [
        k for k, meta in dept_data.items()
        if not meta.get("hidden", False)
    ]


def get_all_keys_for_software(software: str) -> dict:
    """
    Returns all active Key IDs grouped by dept
    for a specific software.
    """
    data    = _load()
    sw_data = data.get(software, {})

    result = {}
    for dept, dept_data in sw_data.items():
        if isinstance(dept_data, list):
            result[dept] = dept_data
        else:
            result[dept] = [
                k for k, meta in dept_data.items()
                if not meta.get("hidden", False)
            ]
    return result


# ─────────────────────────────────────────────
# ADD NEW KEY
# ─────────────────────────────────────────────

def add_key(software: str, dept: str, key_id: str) -> bool:
    """
    Adds a new Key ID for software + dept.
    Persists to JSON file immediately.
    Returns False if key already exists.
    """
    data = _load()

    # Create structure if not exists
    if software not in data:
        data[software] = {}
    if dept.lower() not in data[software]:
        data[software][dept.lower()] = {}

    dept_data = data[software][dept.lower()]

    # Convert list to dict if old format
    if isinstance(dept_data, list):
        data[software][dept.lower()] = {
            k: {"hidden": False} for k in dept_data
        }
        dept_data = data[software][dept.lower()]

    # Check if already exists
    if key_id in dept_data:
        if not dept_data[key_id].get("hidden", False):
            return False  # already active
        else:
            # Unhide if was hidden
            dept_data[key_id]["hidden"] = False
            _save(data)
            return True

    dept_data[key_id] = {"hidden": False}
    _save(data)
    return True


# ─────────────────────────────────────────────
# HIDE KEY (soft delete)
# ─────────────────────────────────────────────

def hide_key(software: str, dept: str, key_id: str) -> bool:
    """
    Hides a Key ID (soft delete).
    Key stays in JSON but won't show in dropdowns.
    """
    data = _load()

    dept_data = data.get(software, {}).get(dept.lower(), {})

    if isinstance(dept_data, list):
        # Convert to dict format first
        data[software][dept.lower()] = {
            k: {"hidden": k == key_id} for k in dept_data
        }
        _save(data)
        return True

    if key_id not in dept_data:
        return False

    dept_data[key_id]["hidden"] = True
    _save(data)
    return True
# core/keystore.py

import json
import os

KEYSTORE_PATH = "data/keystore_keys.json"
os.makedirs("data", exist_ok=True)


# ─────────────────────────────────────────────
# LOAD & SAVE
# ─────────────────────────────────────────────

def _load() -> dict:
    """Load keystore from JSON file. Returns {} if file doesn't exist."""
    if not os.path.exists(KEYSTORE_PATH):
        return {}
    with open(KEYSTORE_PATH, "r") as f:
        return json.load(f)


def _save(data: dict):
    """Save keystore dict back to JSON file."""
    with open(KEYSTORE_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────
# GET KEYS WITH STATUS
# ─────────────────────────────────────────────

def get_keys_with_status(software: str, dept: str) -> dict:
    """
    Returns: {"KEY_001": True, "KEY_002": False, ...}

    Handles migration from old list format to new dict format.
    """
    data = _load()
    dept_key = dept.strip().lower()

    sw_data   = data.get(software, {})
    dept_data = sw_data.get(dept_key, {})

    # Nothing exists yet
    if not dept_data:
        return {}

    # Old format → list of key names, all active by default
    if isinstance(dept_data, list):
        migrated = {k: {"active": True} for k in dept_data}

        # Save migrated format back to file
        if software not in data:
            data[software] = {}
        data[software][dept_key] = migrated
        _save(data)

        dept_data = migrated

    # New format → dict of {key_id: {"active": bool}}
    return {
        key_id: meta.get("active", True)
        for key_id, meta in dept_data.items()
    }


# ─────────────────────────────────────────────
# TOGGLE KEY ACTIVE STATUS
# ─────────────────────────────────────────────

def toggle_key(software: str, dept: str, key_id: str) -> bool:
    """
    Flips active true ↔ false for a given key.
    Returns False if key doesn't exist.
    """
    data = _load()
    dept_key = dept.strip().lower()

    sw_data   = data.get(software, {})
    dept_data = sw_data.get(dept_key, {})

    # Handle old list format
    if isinstance(dept_data, list):
        dept_data = {k: {"active": True} for k in dept_data}
        data[software][dept_key] = dept_data

    if key_id not in dept_data:
        return False

    current = dept_data[key_id].get("active", True)
    dept_data[key_id]["active"] = not current

    _save(data)
    return True


# ─────────────────────────────────────────────
# ADD NEW KEY
# ─────────────────────────────────────────────

def add_key(software: str, dept: str, key_id: str, active: bool = True) -> bool:
    """
    Adds a new Key ID for software + dept with given active status.
    Returns False if key already exists.
    """
    data = _load()
    dept_key = dept.strip().lower()

    if software not in data:
        data[software] = {}

    if dept_key not in data[software]:
        data[software][dept_key] = {}

    dept_data = data[software][dept_key]

    # Handle old list format
    if isinstance(dept_data, list):
        dept_data = {k: {"active": True} for k in dept_data}
        data[software][dept_key] = dept_data

    if key_id in dept_data:
        return False

    dept_data[key_id] = {"active": active}
    _save(data)
    return True