bl_info = {
    "name": "R3F Scene Exporter",
    "blender": (3, 0, 0),
    "author": "Your Name",
    "description": "Export meshes, cameras, lights, and background to R3F-friendly format",
    "category": "3D View",
    "version": (1, 1),
}

import bpy
import json
import os
import subprocess
from bpy.types import Operator, Panel
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


# === Operators ===

class EXPORT_OT_r3f_scene_json(Operator):
    bl_idname = "export.r3f_scene_json"
    bl_label = "Export R3F Scene"

    def execute(self, context):
        cameras, lights, meshes = [], [], []

        blend_dir = bpy.path.abspath("//")
        export_dir = path.join(blend_dir, "viewer", "public", "exported_gltfs")
        os.makedirs(export_dir, exist_ok=True)

        for cam in bpy.data.cameras:
            cam_obj = [o for o in bpy.data.objects if o.data == cam][0]
            cameras.append(get_camera_data(cam_obj, cam))

        for light in bpy.data.lights:
            light_obj = [o for o in bpy.data.objects if o.data == light][0]
            lights.append(get_light_data(light_obj, light))

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                glb_file = export_mesh_object(obj, export_dir)
                meshes.append(glb_file)

        background_color = color_to_list(bpy.context.scene.world.color)

        data = {
            "cameras": cameras,
            "lights": lights,
            "background": background_color,
            "meshes": meshes
        }

        out_path = path.join(blend_dir, "viewer", "public", "lights_and_cameras.json")
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)

        self.report({'INFO'}, "Exported scene data.")
        return {'FINISHED'}


class EXPORT_OT_r3f_clear_folder(Operator):
    bl_idname = "export.r3f_clear"
    bl_label = "Clear Viewer Export Folder"

    def execute(self, context):
        clean_export_folder()
        self.report({'INFO'}, "Viewer export folder cleared.")
        return {'FINISHED'}


class EXPORT_OT_r3f_launch_app(Operator):
    bl_idname = "export.r3f_launch"
    bl_label = "Launch Viewer (npm run dev)"

    def execute(self, context):
        blend_dir = bpy.path.abspath("//")
        viewer_dir = path.join(blend_dir, "viewer")
        try:
            subprocess.Popen(["npm", "run", "dev"], cwd=viewer_dir)
            self.report({'INFO'}, "Viewer launched.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to launch viewer: {e}")
        return {'FINISHED'}


# === UI Panel ===

class EXPORT_PT_r3f_panel(Panel):
    bl_label = "R3F Scene Export"
    bl_idname = "EXPORT_PT_r3f_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Three.js"

    def draw(self, context):
        layout = self.layout
        layout.operator("export.r3f_launch", icon="URL")
        layout.operator("export.r3f_scene_json", icon="FILE_REFRESH")
        layout.operator("export.r3f_clear", icon="TRASH")


# === Register ===

classes = [
    EXPORT_OT_r3f_scene_json,
    EXPORT_OT_r3f_clear_folder,
    EXPORT_OT_r3f_launch_app,
    EXPORT_PT_r3f_panel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.handlers.load_post.append(clean_export_folder)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if clean_export_folder in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(clean_export_folder)


if __name__ == "__main__":
    register()
