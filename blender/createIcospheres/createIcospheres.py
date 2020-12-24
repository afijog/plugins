import bpy, math
from bpy.types import Operator
from bpy.props import (IntProperty, FloatProperty)

def createIcos(self, context):
    n = self.number
    radius = self.radius

    angle_inc = 2 * math.pi / n

    for idx in range(n):
        angle = angle_inc * idx
        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, location=(x, y, 0))
        context.object.name = f'Ico {idx}'


class CircularArrayIcospheresOperator(Operator):
    """Creates a circular array of icospheres"""
    bl_idname = "mesh.add_circular_array_icospheres"
    bl_label = "Circular Array Icospheres"
    bl_options = {'REGISTER', 'UNDO'}

    radius: FloatProperty(
        name="Radius",
        description="The radius",
        min=0.01, max=100.0,
        default=5.0,
    )
    number: IntProperty(
        name="number",
        description="The number",
        min=1, max=100,
        default=5,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        createIcos(self, context)
        return {'FINISHED'}

def addCircularArrayIcospheresOperatorButton(self, context):
    self.layout.operator(
        CircularArrayIcospheresOperator.bl_idname,
        text="Add " + CircularArrayIcospheresOperator.bl_label,
        icon='MESH_ICOSPHERE')


class CircularArrayIcospheresPanel(bpy.types.Panel):
    bl_idname = "circular.array.icospheres.panel"
    bl_label = "Circular Array Icospheres Panel"
    bl_category = "MS Plugins"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(CircularArrayIcospheresOperator.bl_idname, text = CircularArrayIcospheresOperator.__doc__)

def register():
    bpy.utils.register_class(CircularArrayIcospheresOperator)
    bpy.utils.register_class(CircularArrayIcospheresPanel)
    bpy.types.VIEW3D_MT_mesh_add.append(addCircularArrayIcospheresOperatorButton)

def unregister():
    bpy.utils.unregister_class(CircularArrayIcospheresOperator)
    bpy.utils.unregister_class(CircularArrayIcospheresPanel)
    bpy.types.VIEW3D_MT_mesh_add.remove(addCircularArrayIcospheresOperatorButton)
