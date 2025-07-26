import bpy
import subprocess
import os
import json
from os import path
from bpy.types import Operator, Panel

from . import r3f_handlers

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
            cameras.append(r3f_handlers.get_camera_data(cam_obj, cam))

        for light in bpy.data.lights:
            light_obj = [o for o in bpy.data.objects if o.data == light][0]
            lights.append(r3f_handlers.get_light_data(light_obj, light))

        for obj in bpy.data.objects:
            if obj.type == "MESH":
                glb_file = r3f_handlers.export_mesh_object(obj, export_dir)
                meshes.append(glb_file)

        background_color = r3f_handlers.color_to_list(bpy.context.scene.world.color)

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
        r3f_handlers.clean_export_folder()
        self.report({'INFO'}, "Viewer export folder cleared.")
        return {'FINISHED'}

# define port checking function
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

class EXPORT_OT_r3f_launch_app(Operator):
    bl_idname = "export.r3f_launch"
    bl_label = "Launch Viewer and Server"

    def execute(self, context):
        blend_dir = bpy.path.abspath("//")
        viewer_dir = os.path.join(blend_dir, "viewer")
        server_dir = os.path.join(blend_dir, "server")

        # Ports used
        viewer_port = 4001
        server_port = 4000

        try:
            # === Viewer ===
            if not is_port_in_use(viewer_port):
                self.report({'INFO'}, "Launching Viewer...")
                node_modules_path = os.path.join(viewer_dir, "node_modules")
                if not os.path.exists(node_modules_path):
                    subprocess.check_call(["npm", "install"], cwd=viewer_dir)
                subprocess.Popen(["npm", "run", "dev"], cwd=viewer_dir)
            else:
                self.report({'INFO'}, f"Viewer already running on port {viewer_port}")

            # === Server ===
            if not is_port_in_use(server_port):
                self.report({'INFO'}, "Launching Node Server...")
                node_modules_path = os.path.join(server_dir, "node_modules")
                if not os.path.exists(node_modules_path):
                    subprocess.check_call(["npm", "install"], cwd=server_dir)
                subprocess.Popen(["npx", "ts-node", "server.ts"], cwd=server_dir)
            else:
                self.report({'INFO'}, f"Server already running on port {server_port}")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to launch apps: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


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


classes = [
    EXPORT_OT_r3f_scene_json,
    EXPORT_OT_r3f_clear_folder,
    EXPORT_OT_r3f_launch_app,
    EXPORT_PT_r3f_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
