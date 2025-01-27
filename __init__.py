import bpy
import os

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

# Nueva clase para almacenar los archivos .blend
class BlendFileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)

# Operador para abrir un archivo .blend
class OpenBlendFileOperator(bpy.types.Operator):
    bl_idname = "object.open_blend_file"
    bl_label = "Abrir archivo .blend"

    def execute(self, context):
        # Obtener el archivo .blend seleccionado
        selected_blend_file = None
        for blend_item in context.scene.blend_files_list:
            if blend_item.selected:
                selected_blend_file = blend_item.path
                break

        if selected_blend_file and os.path.exists(selected_blend_file):
            bpy.ops.wm.open_mainfile(filepath=selected_blend_file)  # Abrir el archivo .blend
            self.report({'INFO'}, f"Se ha abierto el archivo: {selected_blend_file}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No se seleccionó un archivo .blend válido.")
            return {'CANCELLED'}

# Operador para actualizar la lista de archivos .blend
class UpdateBlendFileListOperator(bpy.types.Operator):
    bl_idname = "object.update_blend_file_list"
    bl_label = "Actualizar Lista de Archivos .blend"

    def execute(self, context):
        scene = context.scene
        folder = scene.fileslist_folder  # Ruta de la carpeta seleccionada

        # Limpiar la lista actual
        scene.blend_files_list.clear()

        # Recorrer la carpeta y agregar los archivos .blend
        for root, dirs, files in os.walk(folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.lower().endswith('.blend'):  # Solo archivos .blend
                    file_item = scene.blend_files_list.add()
                    file_item.name = file_name
                    file_item.path = file_path

        self.report({'INFO'}, "Lista de archivos .blend actualizada")
        return {'FINISHED'}

# Operador para actualizar la lista de archivos soportados (.fbx, .obj, .stl)
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

        # Recorrer la carpeta y agregar los archivos soportados
        for root, dirs, files in os.walk(folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(('.fbx', '.obj', '.stl')):  # Archivos soportados
                    file_item = scene.files_list.add()
                    file_item.name = file_name
                    file_item.path = file_path  # Guardar la ruta completa del archivo

        self.report({'INFO'}, "Lista de archivos actualizada")
        return {'FINISHED'}

# Clase para cada archivo en la lista de importación
class FileItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty()
    selected: bpy.props.BoolProperty(default=False)  # Permite seleccionar o deseleccionar el archivo

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

        # Campo para seleccionar la carpeta
        layout.prop(scene, "fileslist_folder", text="Carpeta de Archivos")

        # Botón para actualizar la lista de archivos
        layout.operator("object.update_file_list", text="Actualizar Lista de Archivos")

        # Mostrar los archivos disponibles para importar
        layout.label(text="Archivos disponibles:")
        for file_item in scene.files_list:
            layout.prop(file_item, "selected", text=file_item.name)

        # Botón para importar los archivos seleccionados
        layout.operator("object.import_files_operator", text="Importar Archivos")

        # Sección para seleccionar los archivos .blend
        layout.label(text="Archivos .blend disponibles:")
        layout.operator("object.update_blend_file_list", text="Actualizar Lista de Archivos .blend")

        # Mostrar los archivos .blend disponibles en una lista
        for blend_item in scene.blend_files_list:
            layout.prop(blend_item, "selected", text=blend_item.name)

        # Botón para abrir el archivo .blend seleccionado
        layout.operator("object.open_blend_file", text="Abrir archivo .blend")

# Registrar las propiedades y clases
def register():
    bpy.utils.register_class(ImportFilesOperator)
    bpy.utils.register_class(FileItem)
    bpy.utils.register_class(BlendFileItem)
    bpy.utils.register_class(UpdateFileListOperator)
    bpy.utils.register_class(UpdateBlendFileListOperator)
    bpy.utils.register_class(OpenBlendFileOperator)
    bpy.utils.register_class(FilesListPanel)

    bpy.types.Scene.fileslist_folder = bpy.props.StringProperty(
        name="Carpeta",
        description="Selecciona una carpeta con archivos soportados (.fbx, .obj, .stl)",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.files_list = bpy.props.CollectionProperty(type=FileItem)  # Lista de archivos soportados
    bpy.types.Scene.blend_files_list = bpy.props.CollectionProperty(type=BlendFileItem)  # Lista de archivos .blend
    bpy.types.Scene.selected_blend_file = bpy.props.StringProperty(
        name="Archivo .blend",
        description="Selecciona un archivo .blend",
        subtype='FILE_PATH',
    )

def unregister():
    bpy.utils.unregister_class(ImportFilesOperator)
    bpy.utils.unregister_class(FileItem)
    bpy.utils.unregister_class(BlendFileItem)
    bpy.utils.unregister_class(UpdateFileListOperator)
    bpy.utils.unregister_class(UpdateBlendFileListOperator)
    bpy.utils.unregister_class(OpenBlendFileOperator)
    bpy.utils.unregister_class(FilesListPanel)

    del bpy.types.Scene.selected_blend_file
    del bpy.types.Scene.fileslist_folder
    del bpy.types.Scene.files_list
    del bpy.types.Scene.blend_files_list

if __name__ == "__main__":
    register()
