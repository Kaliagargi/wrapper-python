# services/table_builder.py

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def safe_num(value):
    try:
        return float(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0


# ─────────────────────────────────────────────
# SOFTWARE LIST
# ─────────────────────────────────────────────

def get_software_list(sw_agg: dict) -> list:
    """
    Returns software names where lease_lic > 0.
    These are the ones that need to be purchased/managed.
    Used to populate dropdown in frontend.
    """
    return [
        {
            "software":  sw,
            "developer": data["developer"],
            "lease_lic": data["lease_lic"],
            "total_lic": data["total_lic"],
        }
        for sw, data in sw_agg.items()
        if safe_num(data["lease_lic"]) > 0
    ]


# ─────────────────────────────────────────────
# TABLE 1 — Licence Summary
# ─────────────────────────────────────────────

def build_table1(sw_agg: dict) -> list:
    """
    One row per software.
    Shows: Software | Total Lic | Lease Lic
    No software filter — shows all software.
    """
    rows = []
    for sw, data in sw_agg.items():
        rows.append({
            "software":  sw,
            "developer": data["developer"],
            "total_lic": safe_num(data["total_lic"]),
            "own_lic":   safe_num(data["own_lic"]),
            "lease_lic": safe_num(data["lease_lic"]),
        })
    return rows


# ─────────────────────────────────────────────
# TABLE 2 — Allocated
# ─────────────────────────────────────────────

def build_table2(records: list, sw_agg: dict, software: str, project_layout: list) -> list:
    """
    Allocated licences for selected software.
    Shows per-project LTC breakdown by dept.
    Developer | Software | Dept | per-project LTC | LTC Total | Grand Total
    """
    from core.errors import SoftwareNotFoundError

    if software not in sw_agg:
        raise SoftwareNotFoundError(software)

    # Filter records for selected software
    sw_records = [r for r in records if r["software"] == software]

    rows = []
    for r in sw_records:
        row = {
            "developer": r["developer"],
            "software":  r["software"],
            "dept":      r["dept"],
            "projects":  {},
            "ltc_total": 0,
            "grand_total": safe_num(r["total_lic"]),
        }

        ltc_total = 0
        for p in project_layout:
            ltc_v = safe_num(r["projects"].get(p["name"], {}).get("ltc", 0))
            row["projects"][p["name"]] = {
                "location": p["location"],
                "ltc":      ltc_v,
            }
            ltc_total += ltc_v

        row["ltc_total"] = ltc_total
        rows.append(row)

    return rows


# ─────────────────────────────────────────────
# TABLE 3 — Required
# ─────────────────────────────────────────────

def build_table3(records: list, sw_agg: dict, software: str) -> list:
    """
    Required licences for selected software.
    Required = Total Lic - Allocated (grand_ltc)
    Positive deficit shown in red in Excel later.
    Developer | Software | Dept | Total | Allocated | Required
    """
    from core.errors import SoftwareNotFoundError

    if software not in sw_agg:
        raise SoftwareNotFoundError(software)

    sw_records = [r for r in records if r["software"] == software]

    rows = []
    for r in sw_records:
        total_lic  = safe_num(r["total_lic"])
        allocated  = safe_num(r["grand_ltc"])
        required   = total_lic - allocated

        rows.append({
            "developer": r["developer"],
            "software":  r["software"],
            "dept":      r["dept"],
            "total_lic": total_lic,
            "allocated": allocated,
            "required":  required,
            "is_deficit": required > 0,  # flag for frontend to show red
        })

    return rows


# ─────────────────────────────────────────────
# TABLE 4 — ISL (In-Stock Licences)
# ─────────────────────────────────────────────

def build_table4(records: list, sw_agg: dict, software: str) -> list:
    """
    In-stock licences for selected software.
    Shows own_lic and lease_lic per dept.
    Developer | Software | Dept | Own Lic | Lease Lic | Total In-Stock
    """
    from core.errors import SoftwareNotFoundError

    if software not in sw_agg:
        raise SoftwareNotFoundError(software)

    sw_records = [r for r in records if r["software"] == software]

    rows = []
    for r in sw_records:
        own_lic   = safe_num(r["own_lic"])
        lease_lic = safe_num(r["lease_lic"])

        rows.append({
            "developer":    r["developer"],
            "software":     r["software"],
            "dept":         r["dept"],
            "own_lic":      own_lic,
            "lease_lic":    lease_lic,
            "total_instock": own_lic + lease_lic,
        })

    return rows

# ─────────────────────────────────────────────
# KEYSTORE HELPER — Get value for any label
# (searches Allocated table, then Required table)
# ─────────────────────────────────────────────

def get_value_for_label(
    records:  list,
    sw_agg:   dict,
    software: str,
    label:    str,
    annual:   float = 0,
    advent:   float = 0,
    onshore:  float = 0,
) -> float | None:
    """
    Searches for `label` in:
      1. Allocated table rows (NPP, PP, CV, Valdel, Advent, Onshore, Total)
      2. Required table rows  (Valdel, PP, CEC, VEC, Onshore, Advent, Total)

    Returns the matching value, or None if not found in either.
    """
    if software not in sw_agg:
        return None

    label_clean = label.strip().lower()

    # 1. Check Allocated table
    allocated_data = build_table2(
        records       = records,
        sw_agg        = sw_agg,
        software_list = [software],
        advent        = advent,
        onshore        = onshore,
    )
    if software in allocated_data:
        for row in allocated_data[software]["rows"]:
            if row["label"].strip().lower() == label_clean:
                return row["value"]

    # 2. Check Required table
    required_data = build_table3(
        records       = records,
        sw_agg        = sw_agg,
        software_list = [software],
        annual        = annual,
        advent        = advent,
        onshore       = onshore,
    )
    if software in required_data:
        for row in required_data[software]["rows"]:
            if row["label"].strip().lower() == label_clean:
                return row["value"]

    return None


# ─────────────────────────────────────────────
# KEYSTORE HELPER — Get all label options
# (real depts + Allocated labels + Required labels, union)
# ─────────────────────────────────────────────

def get_all_label_options(
    records:  list,
    sw_agg:   dict,
    software: str,
    annual:   float = 0,
    advent:   float = 0,
    onshore:  float = 0,
) -> list:
    """
    Returns a deduplicated list of all possible labels for
    a software — real dept names + Allocated row labels +
    Required row labels. Case-insensitive dedup, original
    casing preserved on first occurrence.
    """
    seen   = set()
    labels = []

    def add_label(name):
        key = name.strip().lower()
        if key not in seen:
            seen.add(key)
            labels.append(name.strip())

    # Real dept names from records
    sw_records = [r for r in records if r["software"] == software]
    for r in sw_records:
        add_label(r["dept"])

    # Allocated table labels
    allocated_data = build_table2(
        records       = records,
        sw_agg        = sw_agg,
        software_list = [software],
        advent        = advent,
        onshore       = onshore,
    )
    if software in allocated_data:
        for row in allocated_data[software]["rows"]:
            add_label(row["label"])

    # Required table labels
    required_data = build_table3(
        records       = records,
        sw_agg        = sw_agg,
        software_list = [software],
        annual        = annual,
        advent        = advent,
        onshore       = onshore,
    )
    if software in required_data:
        for row in required_data[software]["rows"]:
            add_label(row["label"])

    return labels


# ─────────────────────────────────────────────
# TABLE 5 — Keystore (updated)
# ─────────────────────────────────────────────

def build_table_keystore(
    records:       list,
    sw_agg:        dict,
    software_list: list,
    annual:        float = 0,
    advent:        float = 0,
    onshore:       float = 0,
) -> dict:
    """
    Builds a flat Keystore table per software.
    'dept'/'label' options now include real depts AND
    computed labels from Allocated/Required tables.
    """
    from core.errors import SoftwareNotFoundError
    from core.keystore import get_keys_with_status

    result = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)

        all_labels = get_all_label_options(
            records  = records,
            sw_agg   = sw_agg,
            software = sw,
            annual   = annual,
            advent   = advent,
            onshore  = onshore,
        )

        keys_list = []

        for label in all_labels:
            status_map = get_keys_with_status(sw, label)

            value = get_value_for_label(
                records  = records,
                sw_agg   = sw_agg,
                software = sw,
                label    = label,
                annual   = annual,
                advent   = advent,
                onshore  = onshore,
            )

            for key_id, active in status_map.items():
                keys_list.append({
                    "label":  label,
                    "key_id": key_id,
                    "active": active,
                    "value":  value,
                })

        result[sw] = {
            "developer": sw_agg[sw]["developer"],
            "keys":      keys_list,
        }

    return result