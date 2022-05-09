import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatVectorProperty, StringProperty
from bpy.types import (Panel, Collection)


class Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_idname = "HYDRA_PT_Panel"
    bl_region_type = "UI"
    bl_label = "HydraTools"
    bl_category = "HydraTools"

    @classmethod
    def poll(cls, context):
        return len(bpy.data.collections) > 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        colprop = scene.col_prop

        obj = context.object
        row = layout.row()
        layout.prop(colprop, 'collections')
        row = layout.row()
        layout.prop(colprop, 'armatures')
        row = layout.row()
        row.operator("object.remove_lod")
        
        row = layout.row()
        col = layout.column_flow(columns=2, align=True)
        col.operator("object.add_v_colors")
        col.operator("object.remove_v_colors")
        
        row = layout.row()
        col = layout.column_flow(columns=2, align=False)
        col.operator("object.paint_v_colors")
        col.prop(colprop, 'VertColorPick', text= "")
        
        row = layout.row() 
        col = layout.column_flow(columns=3, align=True)
        col.operator("object.remove_char_code")
        col.operator("object.rename_script")
        col.operator("object.add_char_code")
        
        row = layout.row()
        row.operator("object.applypose")

        row = layout.row()
        label = layout.label(text = 'XFBIN Materials and Material IDs:')
        layout.prop(colprop, 'Old_Material_ID')
        layout.prop(colprop, 'New_Material_ID')
        layout.operator("object.replace_mats")
        layout.operator("object.duplicate_mats")

        label = layout.label(text = 'Posing and Animation ONLY:')
        row = layout.row()
        row.operator("object.ik")
        
        label = layout.label(text = 'EXPERIMENTAL')
        row = layout.row()
        layout.prop(colprop, 'target_armature')
        row = layout.row()
        layout.prop(colprop, 'PathCode')
        row = layout.row()
        layout.prop(colprop, 'CharacterCode')
        row = layout.row()
        layout.prop(colprop, 'ModelID')
        row = layout.row()
        row.operator("object.swap_code")
        '''row = layout.row()
        row.operator("object.opaque")'''
        row = layout.row()
        row.operator("object.fix_names")
        row = layout.row()
        row.operator("object.add_armature_modifier")

        row = layout.row()
        col = layout.split(factor=0.50, align=True)
        col.operator("object.get_textures")
        col.operator("object.apply_texture", icon='FILE_FOLDER')
        col.operator("object.unlink_textures", icon='X')
    
    _context_path = "collection"
    _property_type = Collection
    
class ColProperty(bpy.types.PropertyGroup):

    def collection_list(self, context):
        
        items = []
        
        for collection in bpy.data.collections:
            ColName = (collection.name, collection.name, "")
            items.append(ColName)   
        return items 
    


    def armature_list(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        
        items = []
        
        for a in collections[colprop.collections].all_objects:
            if a.type == 'ARMATURE':
                Name = (a.name, a.name, "")
                items.append(Name)
        return items
    
    def target_list(self, context):

        colprop = bpy.context.scene.col_prop
        items = []
        
        for a in bpy.context.view_layer.objects:
            if a.type == 'ARMATURE' and a.name != colprop.armatures:
                Name = (a.name, a.name, "")
                items.append(Name)
        return items


    collections: EnumProperty(
    items=collection_list,
    name='Collection',
    description="The collection that's going to be used for all operations")
    
    armatures: EnumProperty(
    items=armature_list,
    name='Armature',
    description="The armature that's going to be used for armature related operations")
    
    target_armature: EnumProperty(
    items = target_list,
    name='Armature2',
    description="The armature that's going to be used for armature related operations")

    VertColorPick: FloatVectorProperty(
    name= 'Color',
    description= ("The color that will be used to paint all meshes."),
    default= (0.5, 0.5, 0.5),
    subtype='COLOR_GAMMA',
    min=(0),
    max=(1))

    PathCode: StringProperty(
    name= 'Path Code',
    default= 'code',
    description= "This code will be used in textures, materials, clump and some meshes.\n"
    "Example (c/code/....)"
    )

    CharacterCode: StringProperty(
    name= 'Object Code',
    default= 'code',
    description= "This is the character code, it can either 4 character (2nrt) or 6 characters long(1dio01), FOR CODES THAT END WITH 01 FOR EXAMPLE, THE MODEL ID MUST ONLY BE (t0) and not 00t0"
    )

    ModelID: StringProperty(
    name= 'Model ID',
    default= 'xxtx',
    maxlen= 4,
    description= "00t0 for Naruto models and t0 for Jojo "
    )

    Old_Material_ID: StringProperty(
    name = 'Old Material ID',
    default = '00 00 00 00',
    maxlen= 11,
    description = "You put the material ID you want to replace here. EXAMPLE: (00 00 F0 0A)"
    )

    New_Material_ID: StringProperty(
    name = 'New Material ID',
    default = '00 00 00 00',
    maxlen= 11,
    description = "You put the new material ID here. EXAMPLE: (00 02 00 01)",
    )
    