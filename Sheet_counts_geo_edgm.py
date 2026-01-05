import arcpy
import os

#INPUT GDB PATHS
geo_gdb  = r"D:\GIS_work\BAR_BAR_Wazirpur_Geo.gdb" #Location of the geo geodatabase
edgm_gdb = r"D:\GIS_work\BAR_BAR_Wazirpur_MG.gdb" #Location of the edgematch geodatabase


def get_mg_layers(gdb):
    arcpy.env.workspace = gdb
    mg_layers = []

    for fc in arcpy.ListFeatureClasses() or []:
        if fc.endswith("_MG"):
            mg_layers.append(fc)

    for fds in arcpy.ListDatasets(feature_type="feature") or []:
        for fc in arcpy.ListFeatureClasses(feature_dataset=fds) or []:
            if fc.endswith("_MG"):
                mg_layers.append(os.path.join(fds, fc))

    return sorted(mg_layers)

#COLLECT MG LAYERS
geo_mg  = get_mg_layers(geo_gdb)
edgm_mg = get_mg_layers(edgm_gdb)

#COUNTS
print("MG LAYER COUNT")
print(f"Geo GDB  MG count : {len(geo_mg)}")
print(f"Edgm GDB MG count : {len(edgm_mg)}")

#NAME COMPARISON
geo_set  = set(os.path.basename(fc) for fc in geo_mg)
edgm_set = set(os.path.basename(fc) for fc in edgm_mg)

missing_in_edgm = geo_set - edgm_set
extra_in_edgm   = edgm_set - geo_set

print("\nCOMPARISON RESULT")

if not missing_in_edgm and not extra_in_edgm:
    print("MG layers are EXACTLY the same in Geo and Edgm GDB")
else:
    print("MG layers mismatch detected")

    if missing_in_edgm:
        print("\nMissing in Edgm GDB:")
        for fc in sorted(missing_in_edgm):
            print("  ", fc)

    if extra_in_edgm:
        print("\nExtra in Edgm GDB:")
        for fc in sorted(extra_in_edgm):

            print("  ", fc)
