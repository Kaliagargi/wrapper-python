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