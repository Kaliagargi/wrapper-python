from services.parser import parse_excel

project_layout, records, sw_agg = parse_excel("Book1.xlsx")

print(f"Projects found: {len(project_layout)}")
for p in project_layout:
   print(p) 

print(f"\nTotal records: {len(records)}")
print(f"\nSoftware found: {list(sw_agg.keys())}")
print(f"\nSample record:\n{records[0]}")