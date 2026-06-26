import json
import math
from core.errors import SoftwareNotFoundError
def safe_num(value):
    try:
        return float(value) if value is not None else 0
    except(ValueError,TypeError):
        return 0
    
def split_ltm_share(value:float) ->tuple:
    ltm = math.floor(value)
    share = round(value-ltm,4)
    return ltm,share

def get_developer_list(sw_agg: dict) ->list:
   return list({
    data["developer"]
    for data in sw_agg.values()
    if data["developer"]
})

    
def get_software_list(sw_agg: dict) ->list:
    return[
        {
            "software":sw,
            "developer":data["developer"],
            "lease_lic":data["lease_lic"],
            "total_lic":data["total_lic"],
            "dept":data["depts"]
        }
        for sw,data in sw_agg.items()
        if safe_num(data["lease_lic"])>0
    ]
def get_software_by_developer(sw_agg: dict, developers:list) ->list:
    return[ {
            "software":sw,
            "developer":data["developer"],
            "lease_lic":data["lease_lic"],
            "total_lic":data["total_lic"],
        }
    for sw,data in sw_agg.items()
    if data["developer"] in developers and safe_num(data["lease_lic"])>0 
   ]

def build_table1(sw_agg: dict , software_list:list,annual:float = 0,advent:float=0) -> list:
    rows=[]
    advent_v = safe_num(advent)
    for sw in software_list:
        if sw not in sw_agg:
            continue
       
            
        data = sw_agg[sw]
        lease = safe_num(data["lease_lic"])
        annual_v = safe_num(annual)
        if advent_v != 0 and sw=="SMARTPLANT 3D":
            order = lease - annual_v + advent_v  if annual_v > 0 else lease
        else: 
            order = lease - annual_v  if annual_v > 0 else lease

        rows.append({
            "software":sw,
            "developer":data["developer"],
            "total_lic":data["total_lic"],
            "own_lic":safe_num(data["own_lic"]),
            "lease_lic":lease,
            "annual":annual_v,
            "advent":advent_v,
            "order_lic":order,
        })
    return rows
    
def build_table2(records: list,sw_agg: dict,software_list:list,advent:float=0,onshore:float=0) ->dict:
    from core.errors import SoftwareNotFoundError
    NPP_dept = {"el","in","me-s"}
    result ={}
    for sw in software_list:
        if sw not in sw_agg:
             raise SoftwareNotFoundError(sw)
        
        sw_records = [r for r in records if r["software"] == sw]
        data = sw_agg[sw]
        own = safe_num(data["own_lic"])

        dept_ltc={}
        total_valdel = 0

        for r in sw_records:
            dept = r["dept"].lower().strip()

            if dept not in dept_ltc:
                dept_ltc[dept]=0
            dept_ltc[dept] +=safe_num(r["grand_ltc"])
            total_valdel +=sum(
                safe_num(p.get("valdel",0))
                for p in r["projects"].values()
            )

            npp_depts_found={
                d:dept_ltc[d]
                for d in NPP_dept
                if d in dept_ltc
            }
            npp_value = sum(npp_depts_found.values())
            rows=[]
            if npp_value>0:
                rows.append({
                "label":"NPP",
                "discription":"+".join(
                    d.upper() for d in NPP_dept if d in dept_ltc
                ),
                "value":npp_value,
                
            })
            new_val = dept_ltc.get("pp", 0)
            for dept_key in ["pl","pp", "cv"]:
                if dept_key in dept_ltc:
                    if dept_key=="pl":
                        print("this is being executed")
                        if dept_ltc.get("pl",0)>0: 
                            print(dept_ltc.get("pp",0))  
                            print(dept_ltc.get("pl",0)) 
                            new_val = dept_ltc.get("pp",0)+dept_ltc.get("pl")+r.get("pp",0)+safe_num(r["others"])
                            print(new_val)
                        continue
                    
                    rows.append({
                         "label": dept_key.upper(),
                         "description": dept_key.upper(),
                         "value": new_val - own if dept_key == "pp" else dept_ltc[dept_key],})
                   
            dept_sum = sum((new_val - own) if dept_key == "pp" else dept_ltc[dept_key]for dept_key in ["pp", "cv"] if dept_key in dept_ltc
)
            advent_v = safe_num(advent)
            if advent_v>0:
                rows.append({
                    "label":"Advent",
                    "description":"User_input",
                    "value":advent_v,
                })

            onshore_v = safe_num(onshore)
            
            if onshore_v>0:
                rows.append({
                    "label":"Onshore",
                    "description":"onshore",
                    "value":onshore_v,
                })
            total = npp_value + dept_sum + advent_v + onshore_v
            rows.append({
                    "label":"Total",    
                    "description":"Sum of all",
                    "value":total,
                })
            
            result[sw] = {
                "developer" : sw_agg[sw]["developer"],
                "rows":rows,
            }

    return result

def build_table3(records:list,sw_agg:dict,software_list:list,annual:float =0,advent:float=0,onshore:float =0) ->dict:
    from core.errors import SoftwareNotFoundError
    result = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)
        
        sw_records = [r for r in records if r["software"] == sw]
        data = sw_agg[sw]

        lease = safe_num(data["lease_lic"])
        annual_v = safe_num(annual)
        order = lease-annual_v if annual_v>0 else lease

        total_valdel = 0
        total_pp=0
        total_others=0

        for r in sw_records:
            dept = r["dept"].lower().strip()
            if dept =="pp":
                total_pp +=safe_num(r["grand_ltc"])
            total_valdel+=sum(
                safe_num(p.get("valdel",0))
                for p in r["projects"].values()
            )

            total_others +=safe_num(r.get("others",0))

            cec = total_others
            vec= order-cec
            advent_v = safe_num(advent)
            onshore_v=safe_num(onshore)
            total = total_valdel+total_pp+cec+vec+advent_v+onshore_v

            rows = [
                {"label":"Valdel","value":total_valdel},
                {"label":"PP","value":total_pp},
                {"label":"CEC","value":cec},
                {"label":"VEC","value":vec},

            ]

            if onshore_v>0:
                rows.append({"label":"Onshore","value":onshore_v})
            if advent_v:
                rows.append({"label":"Advent","value":advent_v})
            rows.append({"label":"Total","value":total})

            result[sw] ={
                "developer":data["developer"],
                "order":order,
                "rows":rows
            }

    return result


def build_table4(records:list,sw_agg:dict,software_list:list) ->dict:
    from core.errors import SoftwareNotFoundError

    results={}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)
        
        sw_records = [r for r in records if r["software"] ==sw]
        rows=[]

        for r in  sw_records:
            ltc_value = safe_num(r["grand_ltc"])
            ltm,share = split_ltm_share(ltc_value)

            rows.append({
                "dept":r["dept"],
                "ltm":ltm,
                "share":share,
                "total":ltc_value,
            })
        
        total_ltm = sum(r["ltm"]  for r in rows)
        total_share = round(sum(r["share"]  for r in rows),4)

        rows.append({
            "dept":"TOTAL",
            "ltm":total_ltm,
            "share":total_share,
            "total":total_ltm+total_share
        })
        results[sw] ={
            "developer":sw_agg[sw]["developer"],
            "rows":rows,
        }
    return results
def load()-> dict:
    file_path = 'data/keystore_keys.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
            
def save(data:dict):
    file_path = 'data/keystore_keys.json'
    with open(file_path, 'w', encoding='utf-8') as feedsjson:
       json.dump(data, feedsjson, indent=2)

def keys_with_status(software:str,dept:str)->dict:
    data=load()
    dept_key=dept
    sw_data=data.get(software,{})
    dept_data=sw_data.get(dept_key,{})

    if not dept_data:
        return {}
    return {key_id:meta.get("active",True)
            for key_id,meta in dept_data.items()
    }
def toggle_key(software:str,dept:str,key_id:str)->bool:
    data=load()
    dept_key=dept.strip()
    sw_data=data.get(software,{})
    dept_data=sw_data.get(dept_key,{})

    if key_id not in dept_data:
        return False
    
    current= dept_data[key_id].get("active",True)
    dept_data[key_id]["active"]=not current
    save(data)
    return True

def keystore_calculator(records:list,software:str,dept:str,value:str)->float |None:
    NPP_dept = {"EL","IN","ME-S"}        
    sw_records = [r for r in records if r["software"] == software]
    dept_ltc={}
    for r in sw_records:
        dept_record = r["dept"].strip()
        if dept_record not in dept_ltc:
            dept_ltc[dept_record]=0
        dept_ltc[dept_record] +=safe_num(r["grand_ltc"])
        individual_val=dept_ltc[dept_record]
        print(individual_val)
        npp_depts_found={
            d:dept_ltc[d]
            for d in NPP_dept
            if d in dept_ltc
        }
        print(individual_val)
        npp_value = sum(npp_depts_found.values())
        
    print(dept)
    if software=="SMARTPLANT 3D":
        if dept=="PP":
            if "ORP" in value:
                return 13
            elif "ORP_UPI" in value:
                return 2
            else:
                return None
        
        elif dept=="NPP":
            return npp_value
       
        elif dept=="CV":
            return dept_ltc[dept]
        else:
           
            return None
    if software=="CAESAR II":
        if dept=="ME-S":
            return None
        elif dept=="NPP":
            return npp_value
        elif dept=="CV":
            return dept_ltc[dept]
        else:
            return None 
    if software=="PV-ELITE":
        if dept=="PP":
            return None
        elif dept=="NPP":
            return npp_value
        elif dept=="CV":
            return dept_ltc[dept]
        else:
            return None
    else:
        print("this is being run")
        return None

def add_key(software: str, dept: str, key_id: str, active: bool = True) -> bool:
    data     = load()
    dept_key = dept.strip()

    if software not in data:
        data[software] = {}
    if dept_key not in data[software]:
        data[software][dept_key] = {}

    dept_data = data[software][dept_key]  # ← reference, not reassign!

    if key_id in dept_data:
        return False

    dept_data[key_id] = {"active": active}
    save(data)
    return True

def build_table_keystore(
    records:       list,
    sw_agg:        dict,
    software_list: list,
    user_values:   dict = {},
    
) -> dict:
    from core.errors import SoftwareNotFoundError

    registry = load()
    result   = {}

    for sw in software_list:
        if sw not in sw_agg:
            raise SoftwareNotFoundError(sw)

        sw_registry = registry.get(sw, {})
        keys_list   = []

        # Walk EVERY label + key defined for this software in the registry,
        # so nothing the user added is silently dropped.
        for label, dept_data in sw_registry.items():
            if not isinstance(dept_data, dict):
                continue
            for key_id, meta in dept_data.items():
                active = meta.get("active", True) if isinstance(meta, dict) else True

                # Values are supplied by the frontend (derived from the tables
                # each label belongs to) and arrive here via user_values so they
                # are written into the downloaded Excel.
                value = (
                    user_values.get(sw, {})
                               .get(label, {})
                               .get(key_id, None)
                )

                keys_list.append({
                    "label":  label,
                    "key_id": key_id,
                    "active": active,
                    "value":  value,   # None → "User Input" in Excel
                })

        result[sw] = {
            "developer": sw_agg[sw]["developer"],
            "keys":      keys_list,
        }

    return result