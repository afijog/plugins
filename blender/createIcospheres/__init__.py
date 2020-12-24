bl_info = {
    "name": "Circular Array Icospheres",
    "author": "Antonio Fijo",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Creates a circular array of icospheres",
    "category": "Add Mesh",
}

import bpy

import sys, os, importlib
pathname = os.path.dirname(bpy.context.space_data.text.filepath)
if pathname not in sys.path:
   sys.path.append(pathname)

import createIcospheres
importlib.reload(createIcospheres)

def register():
    createIcospheres.register()

def unregister():
    createIcospheres.unregister()

if __name__ == "__main__":
    register()