# services/table_builder.py

import math


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def safe_num(value):
    try:
        return float(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0


def split_ltm_share(value: float) -> tuple:
    ltm   = math.floor(value)
    share = round(value - ltm, 4)
    return ltm, share


# ─────────────────────────────────────────────
# DEVELOPER & SOFTWARE LISTS
# ─────────────────────────────────────────────

def get_developer_list(sw_agg: dict) -> list:
    return list({
        data["developer"]
        for data in sw_agg.values()
        if data["developer"]
    })


def get_software_list(sw_agg: dict) -> list:
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


def get_software_by_developer(sw_agg: dict, developers: list) -> list:
    return [
        {
            "software":  sw,
            "developer": data["developer"],
            "lease_lic": data["lease_lic"],
            "total_lic": data["total_lic"],
        }
        for sw, data in sw_agg.items()
        if data["developer"] in developers
        and safe_num(data["lease_lic"]) > 0
    ]


# ─────────────────────────────────────────────
# TABLE 1 — Licence Summary
# ─────────────────────────────────────────────

def build_table1(
    sw_agg:        dict,
    software_list: list,
    annual:        float = 0,
) -> list:
    rows = []
    for sw in software_list:
        if sw not in sw_agg:
            continue
        data     = sw_agg[sw]
        lease    = safe_num(data["lease_lic"])
        annual_v = safe_num(annual)
        order    = lease - annual_v if annual_v > 0 else lease

        rows.append({
            "software":  sw,
            "developer": data["developer"],
            "total_lic": safe_num(data["total_lic"]),
            "own_lic":   safe_num(data["own_lic"]),
            "lease_lic": lease,
            "annual":    annual_v,
            "order":     order,
        })
    return rows


# ─────────────────────────────────────────────
# TABLE 2 — Allocated
# ─────────────────────────────────────────────

def build_table2(
    records:       list,
    sw_agg:        dict,
    software_list: list,
    advent:        float = 0,
    onshore:       float = 0,
) -> dict:
    from core.errors import SoftwareNotFoundError

    NPP_DEPTS = {"pp", "cv", "el"}
    result    = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)

        sw_records   = [r for r in records if r["software"] == sw]
        dept_ltc     = {}
        dept_others  = {}
        total_valdel = 0

        for r in sw_records:
            dept = r["dept"].lower().strip()
            if dept not in dept_ltc:
                dept_ltc[dept]    = 0
                dept_others[dept] = 0
            dept_ltc[dept]    += safe_num(r["grand_ltc"])
            dept_others[dept] += safe_num(r.get("others", 0))
            total_valdel      += sum(
                safe_num(p.get("valdel", 0))
                for p in r["projects"].values()
            )

        # NPP = PP + CV + EL (each including others)
        npp_value = sum(
            dept_ltc.get(d, 0) + dept_others.get(d, 0)
            for d in NPP_DEPTS
            if d in dept_ltc
        )

        rows = []

        if npp_value > 0:
            rows.append({
                "label":       "NPP",
                "description": " + ".join(
                    d.upper() for d in NPP_DEPTS if d in dept_ltc
                ),
                "value": npp_value,
            })

        # PP — with PL adjustment
        pp_ltc  = dept_ltc.get("pp", 0)  + dept_others.get("pp", 0)
        pl_ltc  = dept_ltc.get("pl", 0)  + dept_others.get("pl", 0)
        own_lic = safe_num(sw_agg[sw]["own_lic"])

        if pp_ltc > 0:
            pp_value = pp_ltc + pl_ltc - own_lic if pl_ltc > 0 else pp_ltc
            rows.append({
                "label":       "PP",
                "description": "PP + PL - Own" if pl_ltc > 0 else "PP",
                "value":       pp_value,
            })

        # CV
        cv_value = dept_ltc.get("cv", 0) + dept_others.get("cv", 0)
        if cv_value > 0:
            rows.append({
                "label":       "CV",
                "description": "CV",
                "value":       cv_value,
            })

        # Valdel
        rows.append({
            "label":       "Valdel",
            "description": "Sum of all Valdel values",
            "value":       total_valdel,
        })

        # Advent
        advent_v = safe_num(advent)
        if advent_v > 0:
            rows.append({
                "label":       "Advent",
                "description": "User input",
                "value":       advent_v,
            })

        # Onshore
        onshore_v = safe_num(onshore)
        if onshore_v > 0:
            rows.append({
                "label":       "Onshore",
                "description": "User input",
                "value":       onshore_v,
            })

        # Total
        total = npp_value + total_valdel + advent_v + onshore_v
        rows.append({
            "label":       "Total",
            "description": "Sum of all",
            "value":       total,
        })

        result[sw] = {
            "developer": sw_agg[sw]["developer"],
            "rows":      rows,
        }

    return result


# ─────────────────────────────────────────────
# TABLE 3 — Required
# ─────────────────────────────────────────────

def build_table3(
    records:       list,
    sw_agg:        dict,
    software_list: list,
    annual:        float = 0,
    advent:        float = 0,
    onshore:       float = 0,
) -> dict:
    from core.errors import SoftwareNotFoundError

    result = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)

        sw_records   = [r for r in records if r["software"] == sw]
        data         = sw_agg[sw]
        lease        = safe_num(data["lease_lic"])
        annual_v     = safe_num(annual)
        order        = lease - annual_v if annual_v > 0 else lease

        total_valdel = 0
        total_pp     = 0
        total_others = 0

        for r in sw_records:
            dept = r["dept"].lower().strip()
            if dept == "pp":
                total_pp += safe_num(r["grand_ltc"])
            total_valdel += sum(
                safe_num(p.get("valdel", 0))
                for p in r["projects"].values()
            )
            total_others += safe_num(r.get("others", 0))

        cec       = total_others
        vec       = order - cec
        advent_v  = safe_num(advent)
        onshore_v = safe_num(onshore)
        total     = total_valdel + total_pp + cec + vec + advent_v + onshore_v

        rows = [
            {"label": "Valdel",  "value": total_valdel},
            {"label": "PP",      "value": total_pp},
            {"label": "CEC",     "value": cec},
            {"label": "VEC",     "value": vec},
        ]

        if onshore_v > 0:
            rows.append({"label": "Onshore", "value": onshore_v})
        if advent_v > 0:
            rows.append({"label": "Advent",  "value": advent_v})

        rows.append({"label": "Total", "value": total})

        result[sw] = {
            "developer": data["developer"],
            "order":     order,
            "rows":      rows,
        }

    return result


# ─────────────────────────────────────────────
# TABLE 4 — ISL
# ─────────────────────────────────────────────

def build_table4(
    records:       list,
    sw_agg:        dict,
    software_list: list,
) -> dict:
    from core.errors import SoftwareNotFoundError

    result = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)

        sw_records = [r for r in records if r["software"] == sw]
        rows       = []

        for r in sw_records:
            ltc_value  = safe_num(r["grand_ltc"])
            ltm, share = split_ltm_share(ltc_value)
            rows.append({
                "dept":  r["dept"],
                "ltm":   ltm,
                "share": share,
                "total": ltc_value,
            })

        total_ltm   = sum(r["ltm"]   for r in rows)
        total_share = round(sum(r["share"] for r in rows), 4)
        rows.append({
            "dept":  "TOTAL",
            "ltm":   total_ltm,
            "share": total_share,
            "total": total_ltm + total_share,
        })

        result[sw] = {
            "developer": sw_agg[sw]["developer"],
            "rows":      rows,
        }

    return result


# ─────────────────────────────────────────────
# KEYSTORE HELPERS
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
    if software not in sw_agg:
        return None

    label_clean = label.strip().lower()

    allocated_data = build_table2(
        records       = records,
        sw_agg        = sw_agg,
        software_list = [software],
        advent        = advent,
        onshore       = onshore,
    )
    if software in allocated_data:
        for row in allocated_data[software]["rows"]:
            if row["label"].strip().lower() == label_clean:
                return row["value"]

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


def get_all_label_options(
    records:  list,
    sw_agg:   dict,
    software: str,
    annual:   float = 0,
    advent:   float = 0,
    onshore:  float = 0,
) -> list:
    seen   = set()
    labels = []

    def add_label(name):
        key = name.strip().lower()
        if key not in seen:
            seen.add(key)
            labels.append(name.strip())

    sw_records = [r for r in records if r["software"] == software]
    for r in sw_records:
        add_label(r["dept"])

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
# TABLE 5 — Keystore
# ─────────────────────────────────────────────

def build_table_keystore(
    records:       list,
    sw_agg:        dict,
    software_list: list,
    annual:        float = 0,
    advent:        float = 0,
    onshore:       float = 0,
    user_values:   dict  = {},  # ← add this
) -> dict:
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
            value      = get_value_for_label(
                records  = records,
                sw_agg   = sw_agg,
                software = sw,
                label    = label,
                annual   = annual,
                advent   = advent,
                onshore  = onshore,
            )

            # If value is None → check user_values
            if value is None:
                value = user_values.get(sw, {}).get(label, {}).get(
                    list(status_map.keys())[0] if status_map else "", None
                )

            for key_id, active in status_map.items():
                # Per-key user value takes priority
                key_user_val = user_values.get(sw, {}).get(label, {}).get(key_id)
                final_value  = key_user_val if key_user_val is not None else value

                keys_list.append({
                    "label":  label,
                    "key_id": key_id,
                    "active": active,
                    "value":  final_value,
                })

        result[sw] = {
            "developer": sw_agg[sw]["developer"],
            "keys":      keys_list,
        }

    return result