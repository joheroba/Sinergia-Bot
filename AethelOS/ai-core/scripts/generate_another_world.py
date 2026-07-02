import bpy
import bmesh
import mathutils
import os

out_dir = r"C:\Users\Usuario1\.gemini\antigravity\scratch\Sinergia-Bot\AethelOS\web-core\public"

def create_polygonal_human(name, color_emission, thickness, height_scale):
    # Borrar todo
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Material Flat Shaded Another World
    mat = bpy.data.materials.new(name=f"{name}_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
    bsdf.inputs['Emission Color'].default_value = color_emission
    bsdf.inputs['Emission Strength'].default_value = 0.6
    bsdf.inputs['Roughness'].default_value = 0.8 # Sin brillo, totalmente mate

    # Crear cubo base (Torso)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.2))
    obj = bpy.context.active_object
    obj.name = name
    
    # Escalar torso
    obj.scale = (0.4 * thickness, 0.2 * thickness, 0.5 * height_scale)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Tolerancia para encontrar caras
    def get_face(normal):
        for f in bm.faces:
            if (f.normal - normal).length < 0.1:
                return f
        return None

    # Extruir Cuello y Cabeza
    top_face = get_face(mathutils.Vector((0, 0, 1)))
    if top_face:
        ret = bmesh.ops.extrude_discrete_faces(bm, faces=[top_face])
        new_face = ret['faces'][0]
        bmesh.ops.translate(bm, vec=(0, 0, 0.1), verts=new_face.verts)
        bmesh.ops.scale(bm, vec=(0.5, 0.5, 1), verts=new_face.verts) # Cuello más delgado
        # Cabeza
        ret = bmesh.ops.extrude_discrete_faces(bm, faces=[new_face])
        head_face = ret['faces'][0]
        bmesh.ops.translate(bm, vec=(0, 0, 0.3), verts=head_face.verts)
        bmesh.ops.scale(bm, vec=(2.5, 2.5, 1), verts=head_face.verts) # Cabeza más ancha

    # Brazos
    for side in [1, -1]:
        side_face = get_face(mathutils.Vector((side, 0, 0)))
        if side_face:
            # Hombro
            ret = bmesh.ops.extrude_discrete_faces(bm, faces=[side_face])
            shoulder = ret['faces'][0]
            bmesh.ops.translate(bm, vec=(0.2*side, 0, 0), verts=shoulder.verts)
            # Brazo hacia abajo
            ret = bmesh.ops.extrude_discrete_faces(bm, faces=[shoulder])
            arm = ret['faces'][0]
            # Rotar la cara hacia abajo
            bmesh.ops.rotate(bm, verts=arm.verts, cent=arm.calc_center_median(), matrix=mathutils.Matrix.Rotation(1.57 * side, 3, 'Y'))
            bmesh.ops.translate(bm, vec=(0.1*side, 0, -0.6 * height_scale), verts=arm.verts)
            bmesh.ops.scale(bm, vec=(0.5, 0.5, 1), verts=arm.verts) # Brazo más delgado en la muñeca

    # Piernas
    bottom_face = get_face(mathutils.Vector((0, 0, -1)))
    if bottom_face:
        # Dividir la cara inferior en dos para las piernas
        # Simplificación: Extruimos todo hacia abajo y luego escalamos para simular piernas unidas (estilo retro poligonal abstracto)
        ret = bmesh.ops.extrude_discrete_faces(bm, faces=[bottom_face])
        leg = ret['faces'][0]
        bmesh.ops.translate(bm, vec=(0, 0, -1.0 * height_scale), verts=leg.verts)
        bmesh.ops.scale(bm, vec=(0.8, 0.8, 1), verts=leg.verts)

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Modificadores para dar look orgánico poligonal (Another World)
    # 1. Subdivision Surface (Redondea)
    subdiv = obj.modifiers.new(name="Subdiv", type='SUBSURF')
    subdiv.levels = 2
    bpy.ops.object.modifier_apply(modifier="Subdiv")
    
    # 2. Decimate (Reduce drásticamente polígonos para look retro)
    decimate = obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = 0.08  # Muy low poly
    bpy.ops.object.modifier_apply(modifier="Decimate")

    # Asegurar Flat Shading
    bpy.ops.object.shade_flat()

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Exportar
    out_path = os.path.join(out_dir, f"{name.lower()}.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')
    print(f"Exito. {name} exportado a: {out_path}")

# Travis (Soporte) - Azul
create_polygonal_human("Travis_Synth", (0.0, 0.5, 1.0, 1.0), 1.0, 1.0)
# Marcus (Finanzas) - Corpulento y Naranja/Oro
create_polygonal_human("Marcus_Synth", (1.0, 0.4, 0.0, 1.0), 1.4, 1.1)
# Emma (RRHH) - Esbelta y Rosa/Violeta
create_polygonal_human("Emma_Synth", (0.8, 0.2, 0.8, 1.0), 0.7, 0.95)
# Elena (Operaciones) - Equilibrada y Verde
create_polygonal_human("Elena_Synth", (0.2, 0.8, 0.4, 1.0), 0.9, 1.05)
