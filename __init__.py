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
        # Listar los archivos seleccionados
        selected_files = [file.path for file in scene.files_list if file.selected]

        if not selected_files:
            self.report({'ERROR'}, "No se ha seleccionado ningún archivo para importar")
            return {'CANCELLED'}

        # Importar los archivos seleccionados
        for file_path in selected_files:
            self.import_file(file_path)

        self.report({'INFO'}, "Archivos importados correctamente")
        return {'FINISHED'}

    def import_file(self, file_path):
        # Importar el archivo según su extensión
        if file_path.lower().endswith('.fbx'):
            bpy.ops.import_scene.fbx(filepath=file_path)
        elif file_path.lower().endswith('.obj'):
            bpy.ops.import_scene.obj(filepath=file_path)
        elif file_path.lower().endswith('.stl'):
            bpy.ops.import_mesh.stl(filepath=file_path)
        else:
            self.report({'WARNING'}, f"Archivo no soportado: {file_path}")

# Panel principal con área de filtro
class FilesListPanel(bpy.types.Panel):
    bl_label = "Importar Archivos"
    bl_idname = "OBJECT_PT_fileslist"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Import Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Campo para seleccionar la carpeta
        layout.prop(scene, "fileslist_folder", text="Carpeta de Archivos")

        # Botón para actualizar la lista de archivos
        layout.operator("object.update_file_list", text="Actualizar Lista")

        # Filtros
        layout.label(text="Filtros:")
        layout.prop(scene, "filter_by_name", text="Filtrar por nombre")
        layout.prop(scene, "filter_selected_only", text="Mostrar seleccionados")

        # Mostrar los archivos filtrados
        layout.label(text="Archivos disponibles:")
        filtered_files = self.get_filtered_files(scene.files_list, scene.filter_by_name, scene.filter_selected_only)
        for file_item in filtered_files:
            layout.prop(file_item, "selected", text=file_item.name)

        # Botón para importar los archivos seleccionados
        layout.operator("object.import_files_operator", text="Importar Archivos")

        # Lista de archivos .blend
        layout.label(text="Escenas .blend disponibles:")
        for blend_item in scene.blend_files:
            layout.prop(blend_item, "selected", text=blend_item.name)

        # Botón para abrir la escena seleccionada
        layout.operator("object.open_blend_file_operator", text="Abrir Escena .blend")

    def get_filtered_files(self, files, filter_name, selected_only):
        filtered_files = files
        if filter_name:  # Filtrar por nombre
            filtered_files = [file for file in filtered_files if filter_name.lower() in file.name.lower()]
        if selected_only:  # Mostrar solo seleccionados
            filtered_files = [file for file in filtered_files if file.selected]
        return filtered_files

# Operador para actualizar la lista de archivos
class UpdateFileListOperator(bpy.types.Operator):
    bl_idname = "object.update_file_list"
    bl_label = "Actualizar Lista de Archivos"

    def execute(self, context):
        scene = context.scene
        folder = scene.fileslist_folder  # Ruta de la carpeta seleccionada

        # Validar que la carpeta exista
        if not os.path.exists(folder):
            self.report({'ERROR'}, f"La carpeta {folder} no existe")
            return {'CANCELLED'}

        # Limpiar la lista actual
        scene.files_list.clear()
        scene.blend_files.clear()

        # Recorrer la carpeta y agregar los archivos soportados
        for root, dirs, files in os.walk(folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(('.fbx', '.obj', '.stl')):  # Archivos soportados
                    file_item = scene.files_list.add()
                    file_item.name = file_name
                    file_item.path = file_path  # Guardar la ruta completa del archivo
                elif file_name.lower().endswith('.blend'):  # Archivos .blend
                    blend_item = scene.blend_files.add()
                    blend_item.name = file_name
                    blend_item.path = file_path  # Guardar la ruta completa del archivo .blend

        self.report({'INFO'}, "Lista de archivos actualizada")
        return {'FINISHED'}

# Operador para abrir la escena .blend seleccionada
class OpenBlendFileOperator(bpy.types.Operator):
    bl_idname = "object.open_blend_file_operator"
    bl_label = "Abrir Escena .blend"

    def execute(self, context):
        scene = context.scene
        # Listar los archivos .blend seleccionados
        selected_blends = [file.path for file in scene.blend_files if file.selected]

        if not selected_blends:
            self.report({'ERROR'}, "No se ha seleccionado ninguna escena .blend para abrir")
            return {'CANCELLED'}

        # Intentar abrir la escena .blend seleccionada
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

# Definir la clase para cada archivo en la lista
class FileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)

# Definir la clase para los archivos .blend
class BlendFileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)

# Registrar las propiedades y clases
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
        name="Filtrar Nombre",
        description="Filtrar archivos por nombre"
    )
    bpy.types.Scene.filter_selected_only = bpy.props.BoolProperty(
        name="Mostrar Seleccionados",
        description="Mostrar solo los archivos seleccionados",
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

if __name__ == "__main__":
    register()
