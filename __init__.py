import bpy
import os

bl_info = {
    "name": "FilesList with Filter",
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

# Panel principal con filtros
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

        # Filtros para modelos
        layout.label(text="Filtros para Modelos:")
        layout.prop(scene, "filter_by_name", text="Filtrar por nombre")
        layout.prop(scene, "filter_selected_only", text="Mostrar seleccionados")

        layout.label(text="Modelos disponibles:")
        filtered_files = self.get_filtered_files(scene.files_list, scene.filter_by_name, scene.filter_selected_only)
        for file_item in filtered_files:
            layout.prop(file_item, "selected", text=file_item.name)

        layout.operator("object.import_files_operator", text="Importar Archivos")

        # Filtros para escenas .blend
        layout.label(text="Filtros para Escenas (.blend):")
        layout.prop(scene, "filter_blend_by_name", text="Filtrar por nombre")
        layout.prop(scene, "filter_blend_selected_only", text="Mostrar seleccionados")

        layout.label(text="Escenas .blend disponibles:")
        filtered_blends = self.get_filtered_files(scene.blend_files, scene.filter_blend_by_name, scene.filter_blend_selected_only)
        for blend_item in filtered_blends:
            layout.prop(blend_item, "selected", text=blend_item.name)

        layout.operator("object.open_blend_file_operator", text="Abrir Escena .blend")

    def get_filtered_files(self, files, filter_name, selected_only):
        filtered_files = files
        if filter_name:
            filtered_files = [file for file in filtered_files if filter_name.lower() in file.name.lower()]
        if selected_only:
            filtered_files = [file for file in filtered_files if file.selected]
        return filtered_files

# Operador para actualizar la lista
class UpdateFileListOperator(bpy.types.Operator):
    bl_idname = "object.update_file_list"
    bl_label = "Actualizar Lista de Archivos"

    def execute(self, context):
        scene = context.scene
        folder = scene.fileslist_folder

        if not os.path.exists(folder):
            self.report({'ERROR'}, f"La carpeta {folder} no existe")
            return {'CANCELLED'}

        scene.files_list.clear()
        scene.blend_files.clear()

        for root, dirs, files in os.walk(folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(('.fbx', '.obj', '.stl')):
                    file_item = scene.files_list.add()
                    file_item.name = file_name
                    file_item.path = file_path
                elif file_name.lower().endswith('.blend'):
                    blend_item = scene.blend_files.add()
                    blend_item.name = file_name
                    blend_item.path = file_path

        self.report({'INFO'}, "Lista de archivos actualizada")
        return {'FINISHED'}

# Operador para abrir escenas .blend
class OpenBlendFileOperator(bpy.types.Operator):
    bl_idname = "object.open_blend_file_operator"
    bl_label = "Abrir Escena .blend"

    def execute(self, context):
        scene = context.scene
        selected_blends = [file.path for file in scene.blend_files if file.selected]

        if not selected_blends:
            self.report({'ERROR'}, "No se ha seleccionado ninguna escena .blend para abrir")
            return {'CANCELLED'}

        for blend_path in selected_blends:
            try:
                bpy.ops.wm.open_mainfile(filepath=blend_path)
            except RuntimeError as e:
                if 'version' in str(e).lower() and 'too new' in str(e).lower():
                    self.report({'ERROR'}, f"No se puede abrir '{blend_path}': Este archivo fue guardado con una versión más reciente de Blender.")
                else:
                    self.report({'ERROR'}, f"Error al intentar abrir el archivo: {str(e)}")

        self.report({'INFO'}, "Escena .blend abierta correctamente")
        return {'FINISHED'}

# Clases para los archivos
class FileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)

class BlendFileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)

# Registro
def register():
    bpy.utils.register_class(ImportFilesOperator)
    bpy.utils.register_class(FilesListPanel)
    bpy.utils.register_class(UpdateFileListOperator)
    bpy.utils.register_class(OpenBlendFileOperator)
    bpy.utils.register_class(FileItem)
    bpy.utils.register_class(BlendFileItem)

    bpy.types.Scene.fileslist_folder = bpy.props.StringProperty(
        name="Carpeta",
        description="Selecciona una carpeta con archivos soportados (.fbx, .obj, .stl)",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.files_list = bpy.props.CollectionProperty(type=FileItem)
    bpy.types.Scene.blend_files = bpy.props.CollectionProperty(type=BlendFileItem)
    bpy.types.Scene.filter_by_name = bpy.props.StringProperty(
        name="Filtrar Nombre Modelos",
        description="Filtrar archivos por nombre"
    )
    bpy.types.Scene.filter_selected_only = bpy.props.BoolProperty(
        name="Mostrar Seleccionados Modelos",
        description="Mostrar solo los archivos seleccionados",
        default=False
    )
    bpy.types.Scene.filter_blend_by_name = bpy.props.StringProperty(
        name="Filtrar Nombre Escenas",
        description="Filtrar escenas .blend por nombre"
    )
    bpy.types.Scene.filter_blend_selected_only = bpy.props.BoolProperty(
        name="Mostrar Seleccionados Escenas",
        description="Mostrar solo las escenas seleccionadas",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(ImportFilesOperator)
    bpy.utils.unregister_class(FilesListPanel)
    bpy.utils.unregister_class(UpdateFileListOperator)
    bpy.utils.unregister_class(OpenBlendFileOperator)
    bpy.utils.unregister_class(FileItem)
    bpy.utils.unregister_class(BlendFileItem)

    del bpy.types.Scene.fileslist_folder
    del bpy.types.Scene.files_list
    del bpy.types.Scene.blend_files
    del bpy.types.Scene.filter_by_name
    del bpy.types.Scene.filter_selected_only
    del bpy.types.Scene.filter_blend_by_name
    del bpy.types.Scene.filter_blend_selected_only

if __name__ == "__main__":
    register()
