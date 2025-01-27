import bpy
import os
from . import clear  # Importar el archivo clear.py

bl_info = {
    "name": "FilesList",
    "blender": (3, 3, 0),
    "category": "Object",
}

# Clase para el operador de importación
class ImportFilesOperator(bpy.types.Operator):
    bl_idname = "object.import_files_operator"
    bl_label = "Importar Archivos"

    def execute(self, context):
        scene = context.scene
        selected_files = [file.path for file in scene.files_list if file.selected]

        if not selected_files:
            self.report({'ERROR'}, "No se ha seleccionado ningún archivo para importar")
            return {'CANCELLED'}

        for file_path in selected_files:
            self.import_file(file_path)

        self.report({'INFO'}, "Archivos importados correctamente")
        return {'FINISHED'}

    def import_file(self, file_path):
        if file_path.lower().endswith('.fbx'):
            bpy.ops.import_scene.fbx(filepath=file_path)
        elif file_path.lower().endswith('.obj'):
            bpy.ops.import_scene.obj(filepath=file_path)
        elif file_path.lower().endswith('.stl'):
            bpy.ops.import_mesh.stl(filepath=file_path)
        else:
            self.report({'WARNING'}, f"Archivo no soportado: {file_path}")

# Clase para el operador de limpiar archivos recientes
class ClearRecentFilesOperator(bpy.types.Operator):
    bl_idname = "object.clear_recent_files"
    bl_label = "Limpiar Archivos Recientes"

    def execute(self, context):
        clear.clear_recent_files()  # Llamar a la función desde clear.py
        self.report({'INFO'}, "Historial de archivos recientes limpiado")
        return {'FINISHED'}

# Panel principal
class FilesListPanel(bpy.types.Panel):
    bl_label = "Importar Archivos"
    bl_idname = "OBJECT_PT_fileslist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Import Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "fileslist_folder", text="Carpeta de Archivos")
        layout.operator("object.update_file_list", text="Actualizar Lista")

        layout.label(text="Archivos disponibles:")
        for file_item in scene.files_list:
            layout.prop(file_item, "selected", text=file_item.name)

        layout.operator("object.import_files_operator", text="Importar Archivos")
        layout.operator("object.clear_recent_files", text="Limpiar Archivos Recientes")

# Registrar las propiedades y clases
def register():
    bpy.utils.register_class(ImportFilesOperator)
    bpy.utils.register_class(FilesListPanel)
    bpy.utils.register_class(ClearRecentFilesOperator)
    bpy.utils.register_class(UpdateFileListOperator)
    bpy.utils.register_class(FileItem)

    bpy.types.Scene.fileslist_folder = bpy.props.StringProperty(
        name="Carpeta",
        description="Selecciona una carpeta con archivos soportados (.fbx, .obj, .stl)",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.files_list = bpy.props.CollectionProperty(type=FileItem)

def unregister():
    bpy.utils.unregister_class(ImportFilesOperator)
    bpy.utils.unregister_class(FilesListPanel)
    bpy.utils.unregister_class(ClearRecentFilesOperator)
    bpy.utils.unregister_class(UpdateFileListOperator)
    bpy.utils.unregister_class(FileItem)

    del bpy.types.Scene.fileslist_folder
    del bpy.types.Scene.files_list

if __name__ == "__main__":
    register()
