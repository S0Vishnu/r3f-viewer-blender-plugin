import bpy
import os
import json
from mathutils import Vector
from os import path

# === Utility Functions ===

def safe_name(name: str):
    return name.replace(" ", "_").replace("-", "_")

def safe_transform(vec):
    return [round(vec.x, 4), round(vec.z, 4), round(-vec.y, 4)]  # Convert to R3F coordinate system

def color_to_list(bpy_color):
    return [round(c, 4) for c in bpy_color[:3]]

def get_camera_data(cam_obj, cam_data):
    return {
        "name": safe_name(cam_obj.name),
        "type": "PerspectiveCamera",
        "fov": cam_data.lens,
        "position": safe_transform(cam_obj.location),
        "rotation": safe_transform(cam_obj.rotation_euler)
    }

def get_light_data(light_obj, light_data):
    light_info = {
        "name": safe_name(light_obj.name),
        "type": light_data.type,
        "color": color_to_list(light_data.color),
        "intensity": light_data.energy,
        "position": safe_transform(light_obj.location),
    }

    if light_data.type == "SPOT":
        if light_obj.constraints:
            for c in light_obj.constraints:
                if c.type in {"TRACK_TO", "DAMPED_TRACK", "LOCKED_TRACK"} and c.target:
                    light_info["target"] = safe_transform(c.target.location)
                    break
        else:
            target = light_obj.location + light_obj.rotation_euler.to_matrix() @ Vector((0, 0, -1))
            light_info["target"] = safe_transform(target)

        light_info["angle"] = light_data.spot_size

    return light_info

def export_mesh_object(obj, export_dir):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    export_path = path.join(export_dir, f"{safe_name(obj.name)}.glb")
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True
    )
    obj.select_set(False)
    return safe_name(obj.name) + ".glb"

def clean_export_folder(dummy=None):
    blend_dir = bpy.path.abspath("//")
    export_dir = path.join(blend_dir, "viewer", "public")

    if os.path.exists(export_dir):
        for root, _, files in os.walk(export_dir):
            for file in files:
                if file.endswith(".glb") or file == "lights_and_cameras.json":
                    os.remove(path.join(root, file))

def register():
    pass

def unregister():
    pass
