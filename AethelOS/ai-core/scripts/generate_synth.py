import bpy
import sys
import os

# Borrar todo
bpy.ops.wm.read_factory_settings(use_empty=True)

# Limpiar escena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Material Sintético AethelOS (Azul Brillante Holográfico/Metálico)
mat = bpy.data.materials.new(name="Aethel_Synth_Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.1, 0.2, 0.4, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['Emission Color'].default_value = (0.2, 0.6, 1.0, 1.0)
bsdf.inputs['Emission Strength'].default_value = 0.5

parts = []

def add_part(name, location, scale):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    parts.append(obj)

# Dimensiones base del Synth
# Torso
add_part("Torso", (0, 0, 1.1), (0.25, 0.15, 0.35))
# Cabeza
add_part("Head", (0, 0, 1.6), (0.12, 0.12, 0.15))
# Cuello
add_part("Neck", (0, 0, 1.45), (0.05, 0.05, 0.05))
# Brazo Izquierdo
add_part("Arm_L", (0.35, 0, 1.0), (0.08, 0.08, 0.35))
# Brazo Derecho
add_part("Arm_R", (-0.35, 0, 1.0), (0.08, 0.08, 0.35))
# Pierna Izquierda
add_part("Leg_L", (0.12, 0, 0.35), (0.1, 0.1, 0.4))
# Pierna Derecha
add_part("Leg_R", (-0.12, 0, 0.35), (0.1, 0.1, 0.4))

# Seleccionar todas las partes
bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)

bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

final_obj = bpy.context.active_object
final_obj.name = "Travis_Synth"

# Exportar a GLB
out_path = r"C:\Users\Usuario1\.gemini\antigravity\scratch\Sinergia-Bot\AethelOS\web-core\public\travis_synth.glb"
bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

print("Exito. Travis Synth exportado a:", out_path)
