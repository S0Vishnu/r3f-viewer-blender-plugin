bl_info = {
    "name": "R3F Scene Exporter",
    "blender": (3, 0, 0),
    "author": "Vishnu",
    "description": "Export meshes, cameras, lights, and background to R3F-friendly format",
    "category": "3D View",
    "version": (1, 1),
    "tracker_url": "https://github.com/S0Vishnu/r3f-viewer-blender-plugin/issues",
}

import bpy
from . import r3f_handlers
from . import r3f_ui

def register():
    r3f_handlers.register()
    r3f_ui.register()
    bpy.app.handlers.load_post.append(r3f_handlers.clean_export_folder)

def unregister():
    r3f_ui.unregister()
    r3f_handlers.unregister()
    if r3f_handlers.clean_export_folder in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(r3f_handlers.clean_export_folder)
