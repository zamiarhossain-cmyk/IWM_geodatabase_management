import arcpy
import os
from collections import defaultdict, Counter

#INPUT GDBs
rawgeo_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_RawGeo.gdb" #Location of the rawgeo geodatabase
geo_gdb    = r"D:\GIS_work\BAR_BAR_Wazirpur_Geo.gdb" #Location of the geodatabase


def list_all_featureclasses(gdb):
    arcpy.env.workspace = gdb
    fcs = []

    initial_fcs = arcpy.ListFeatureClasses() or []
    fcs.extend(initial_fcs)

    datasets = arcpy.ListDatasets(feature_type="feature") or []
    for fds in datasets:
        fds_fcs = arcpy.ListFeatureClasses(feature_dataset=fds) or []
        for fc in fds_fcs:
            fcs.append(os.path.join(fds, fc))

    return fcs

def parse_name(fc_name):
    parts = fc_name.split("_")
    if len(parts) < 7:
        return None
    jl = parts[3]
    sheet = parts[4]
    layer_type = parts[-1]
    return jl, sheet, layer_type

def analyze_gdb(gdb, valid_types):
    fcs = list_all_featureclasses(gdb)
    sheet_tracker = defaultdict(list)
    type_counter = Counter()

    for fc in fcs:
        name = os.path.basename(fc)
        parsed = parse_name(name)
        if not parsed:
            continue

        jl, sheet, ltype = parsed
        if ltype in valid_types:
            type_counter[ltype] += 1
            sheet_tracker[(jl, sheet)].append(ltype)

    return type_counter, sheet_tracker

#RUN ANALYSIS
type_map = {
    "LRG": "LG",
    "MRG": "MG",
    "SRG": "SG",
    "PRG": "PG",
    "NRG": "NG"
}

reverse_map = {v: k for k, v in type_map.items()}

rawgeo_types = set(type_map.keys())
geo_types    = set(type_map.values())

rawgeo_count, rawgeo_sheets = analyze_gdb(rawgeo_gdb, rawgeo_types)
geo_count, geo_sheets       = analyze_gdb(geo_gdb, geo_types)

#REPORT COUNTS
print("\nLAYER TOTALS")
for r_type in sorted(rawgeo_types):
    g_type = type_map[r_type]
    print(f"{r_type}: {rawgeo_count[r_type]} | {g_type}: {geo_count[g_type]}")

#SHEET VALIDATION
print("\nDETAILED MISMATCH CHECK")

all_keys = set(rawgeo_sheets.keys()) | set(geo_sheets.keys())

for jl, sheet in sorted(all_keys):
    raw_types_found = rawgeo_sheets.get((jl, sheet), [])
    geo_types_found = geo_sheets.get((jl, sheet), [])

    # Raw present, Geo missing
    for r_type in raw_types_found:
        expected_g = type_map[r_type]
        if expected_g not in geo_types_found:
            print(f"MISMATCH: JL {jl} Sh {sheet} has {r_type} but is MISSING {expected_g}")

    # Geo present, Raw missing
    for g_type in geo_types_found:
        expected_r = reverse_map[g_type]
        if expected_r not in raw_types_found:
            print(f"MISMATCH: JL {jl} Sh {sheet} has {g_type} but is MISSING {expected_r}")

    # Duplicate detection
    if len(raw_types_found) != len(set(raw_types_found)):
        print(f"DUPLICATE in RAWGEO to JL {jl}, Sheet {sheet}")

    if len(geo_types_found) != len(set(geo_types_found)):
        print(f"DUPLICATE in GEO to JL {jl}, Sheet {sheet}")

print("\nCHECK COMPLETE")

