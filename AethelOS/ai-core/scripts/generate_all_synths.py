import bpy
import sys
import os

out_dir = r"C:\Users\Usuario1\.gemini\antigravity\scratch\Sinergia-Bot\AethelOS\web-core\public"

def create_synth(name, color_emission, scale_mult_x, scale_mult_y, scale_mult_z):
    # Borrar todo
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Material
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.9
    bsdf.inputs['Roughness'].default_value = 0.2
    bsdf.inputs['Emission Color'].default_value = color_emission
    bsdf.inputs['Emission Strength'].default_value = 0.8

    parts = []

    def add_part(part_name, location, scale):
        bpy.ops.mesh.primitive_cube_add(location=location)
        obj = bpy.context.active_object
        obj.name = part_name
        
        # Apply scaling multipliers to make them distinct
        obj.scale = (scale[0]*scale_mult_x, scale[1]*scale_mult_y, scale[2]*scale_mult_z)
        
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        parts.append(obj)

    # Dimensiones base (Escaladas)
    add_part("Torso", (0, 0, 1.1), (0.25, 0.15, 0.35))
    add_part("Head", (0, 0, 1.6), (0.12, 0.12, 0.15))
    add_part("Neck", (0, 0, 1.45), (0.05, 0.05, 0.05))
    add_part("Arm_L", (0.35 * scale_mult_x, 0, 1.0), (0.08, 0.08, 0.35))
    add_part("Arm_R", (-0.35 * scale_mult_x, 0, 1.0), (0.08, 0.08, 0.35))
    add_part("Leg_L", (0.12 * scale_mult_x, 0, 0.35), (0.1, 0.1, 0.4))
    add_part("Leg_R", (-0.12 * scale_mult_x, 0, 0.35), (0.1, 0.1, 0.4))

    # Seleccionar y unir
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)

    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    final_obj = bpy.context.active_object
    final_obj.name = name

    # Exportar
    out_path = os.path.join(out_dir, f"{name.lower()}.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')
    print(f"Exito. {name} exportado a: {out_path}")

# Marcus (Finanzas) - Corpulento y Naranja/Oro
create_synth("Marcus_Synth", (1.0, 0.4, 0.0, 1.0), 1.3, 1.2, 1.1)

# Emma (RRHH) - Esbelta y Rosa/Violeta
create_synth("Emma_Synth", (0.8, 0.2, 0.8, 1.0), 0.8, 0.8, 0.95)

# Elena (Operaciones) - Equilibrada y Verde
create_synth("Elena_Synth", (0.2, 0.8, 0.4, 1.0), 1.0, 1.0, 1.05)
