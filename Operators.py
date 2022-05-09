import bpy, json, os
from bpy.props import EnumProperty, BoolProperty, StringProperty, FloatVectorProperty
from bpy.types import (Operator)
from bpy_extras.io_utils import ImportHelper
from rna_prop_ui import PropertyPanel
from os import listdir
from os.path import isfile, join


class RemoveLOD(bpy.types.Operator):
    bl_idname = "object.remove_lod"
    bl_label = "Remove LOD"
    bl_description = ("This button will remove LOD meshes and adjust the necessary values")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        colprop = bpy.context.scene.col_prop
        collection = bpy.data.collections[colprop.collections]
        armature_obj = bpy.data.objects[colprop.armatures]
        clumpdata = armature_obj.xfbin_clump_data

        bpy.ops.object.select_all(action='DESELECT')
            
        lod = {"_lod1", "_lod2", "lod01", "_LOD1", "_LOD2",
        "_shadow", "_blur0 shadow", "_blur0 shadow01"}

        #delete any mesh that contains any of the strings in the list above
        for obj in collection.all_objects:
            obj.hide_set(False) 
            if any(x in obj.name for x in lod):
                obj.select_set(True)
        bpy.ops.object.delete(use_global=True, confirm=True)
            
        #set LOD levels to 1
        armature_obj.xfbin_clump_data.coord_flag0 = 1
        armature_obj.xfbin_clump_data.coord_flag1 = 1

        #Clear model groups then add 1 model group with the correct settings
        armature_obj.xfbin_clump_data.model_groups.clear()
        g = armature_obj.xfbin_clump_data.model_groups.add()
        g.name = 'Group'
        g.unk = '7F 7F FF FF'
        for child in armature_obj.children:
            gm = g.models.add()
            gm.empty = child

        return {'FINISHED'}


class AddVertColors(Operator):
    bl_idname = "object.add_v_colors"
    bl_label = "Add Vertex Colors"
    bl_description = ('This button will add vertex colors to all the meshes\n'
    'in the active collection')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collections[colprop.collections].all_objects:
            obj.hide_set(False)
            obj.select_set(True)
    
        for i, obj in enumerate(bpy.context.selected_objects):
            if (obj.type == 'MESH'):
                if (len(obj.data.vertex_colors) == 0):
                    obj.data.vertex_colors.new()
                else:
                    self.report({'INFO'}, f'{obj.name} Has at least 1 vertex colors layer')
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class RemoveVertColors(Operator):
    bl_idname = "object.remove_v_colors"
    bl_label = "Clear Vertex Colors"
    bl_description = ('This button will remove all the vertex colors layers in meshes\n'
    "in the active collection")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collections[colprop.collections].all_objects:
            if (obj.type == 'MESH'):
                obj.hide_set(False)
                obj.select_set(True)
    
        for obj in bpy.context.selected_objects:
                while obj.data.vertex_colors:
                    obj.data.vertex_colors.remove(obj.data.vertex_colors[0])
                self.report({'INFO'}, f'Vertex Colors layers in {obj.name} are removed')
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class PaintVertexColors(Operator):
    bl_idname = "object.paint_v_colors"
    bl_label = "Paint Vertex Colors"
    bl_description = ('This button will change the color of the active vertex color layer\n'
    'for meshes in the active collection using the color you choose.\n\n'
    "NOTE: A vertex color layer will be added if there isn't one already")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in collections[colprop.collections].all_objects:
            if (obj.type == 'MESH'):
                obj.hide_set(False)
                obj.select_set(True)
                
        for i, obj in enumerate(bpy.context.selected_objects):
            bpy.context.view_layer.objects.active = obj
            bpy.ops.paint.vertex_paint_toggle()
            bpy.context.scene.col_prop.VertColorPick
            bpy.data.brushes["Draw"].color = bpy.context.scene.col_prop.VertColorPick
            bpy.ops.paint.vertex_color_set()
            bpy.ops.paint.vertex_paint_toggle()
            
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}        



class ApplyRestPose(Operator):
    bl_idname = "object.applypose"
    bl_label = "Apply Rest Pose"
    bl_description = ('This button will Apply the current pose as rest pose')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        selected = bpy.context.selected_objects
        a_object = bpy.data.objects[colprop.armatures]
        
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in collections[colprop.collections].all_objects:
            if (obj.type == 'MESH'):
                obj.hide_set(False)
                obj.select_set(True)
                
        for i, obj in enumerate(bpy.context.selected_objects):
            mod = obj.modifiers.new(type='ARMATURE', name='ArmatureToApply')
            mod.object = bpy.data.objects[colprop.armatures]
            #bpy.ops.object.select_all(action='DESELECT')

        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            for mod in [m for m in obj.modifiers if m.type == 'ARMATURE']:
                bpy.ops.object.modifier_apply( modifier = "ArmatureToApply" )
                bpy.ops.object.select_all(action='DESELECT')
                
        bpy.context.scene.objects[colprop.armatures].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[colprop.armatures]
        bpy.ops.object.posemode_toggle()
        bpy.ops.pose.armature_apply(selected=False)
        bpy.ops.object.posemode_toggle()

        return {'FINISHED'}
        
        
class RemoveCharCode(Operator):
    bl_idname = "object.remove_char_code"
    bl_label = "Remove ID"
    bl_description = ('This button will remove character ID (XXXX0XT0) for all the bones\n'
    "Example: '2nrt00t0 spine' becomes 'Spine' this is useful for mirroring and weight painting")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
    
        
    def execute(self, context):
        colprop = bpy.context.scene.col_prop
        a_object = bpy.data.objects[colprop.armatures]
        armature = bpy.data.armatures[colprop.armatures]
        ab = bpy.data.objects[colprop.armatures].data.bones
        clumpdata = a_object.xfbin_clump_data
        char_id = a_object.data.bones[1].name
        nl = len(armature.bones[1].name)
        nc = len(armature.bones[1].name[:-4])
        filtered_bones = [
        'asianimel01', 'asianimel02', 'asianimel03', 'asianimel04','asianimel',
        'asianimer01', 'asianimer02', 'asianimer03', 'asianimer04','asianimer',
        'udeanmr01', 'udeanmr02', 'udeanmr03', 'udeanmr04', 'udeanmr',
        'udeanml01', 'udeanml02', 'udeanml03', 'udeanml04', 'udeanml']  
        
        for bone in [*a_object.data.bones]:
            if any(x in bone.name for x in filtered_bones):
                i = bone.name.find('_')
                bone.name = bone.name[i:]
            
            elif bone.name[0:nl] == char_id and len(bone.name) > nl and bone.name:
                bone.name = bone.name[nl+1:]
                self.report({'INFO'}, f'ID:{char_id} Removed from {bone.name}')
        
        bpy.ops.object.select_all(action='DESELECT')
        
        #re-sets armatures modifier object to fix a bug in blender 3.0
        for c in bpy.data.objects[colprop.armatures].children:
            for child in c.children:
                if child.type == 'MESH':
                    child.hide_set(False)
                    child.select_set(True)
        for i, obj in enumerate(bpy.context.selected_objects):
            for mod in [m for m in obj.modifiers if m.type == 'ARMATURE']:
                mod.object = bpy.data.objects[colprop.armatures]
                
        bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}
    
class RenameBones(Operator, ImportHelper):
    bl_idname = "object.rename_script"
    bl_label = "Translate Bones"
    bl_description = ("Rename bone names using a bone name dictionary.\n"
    "This is useful when you want to transfer rigs")
    
    filter_glob: StringProperty(
    default='*.json;',
    options={'HIDDEN'}
)


    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        with open(self.filepath,'r') as dictionary: 
            bone_dict = json.load(dictionary)
        colprop = bpy.context.scene.col_prop
        a_object = bpy.data.objects[colprop.armatures]    
        for bone in [*a_object.data.bones]:
            if bone.name in bone_dict.keys():
                bone.name = bone_dict[bone.name]
        return {'FINISHED'}


class AddCharCode(Operator):
    bl_idname = "object.add_char_code"
    bl_label = "Add ID"
    bl_description = ('This button will add the character ID back after removing it')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        colprop = bpy.context.scene.col_prop
        a_object = bpy.data.objects[colprop.armatures]
        armature = bpy.data.armatures[colprop.armatures]
        ab = bpy.data.objects[colprop.armatures].data.bones
        clumpdata = a_object.xfbin_clump_data
        char_id = a_object.data.bones[1].name
        nl = len(armature.bones[1].name)
        nc = len(armature.bones[1].name[:-4])
        filter_char_id = char_id[:4] + '_'
        filtered_bones = [
        'asianimel01', 'asianimel02', 'asianimel03', 'asianimel04','asianimel',
        'asianimer01', 'asianimer02', 'asianimer03', 'asianimer04','asianimer',
        'udeanmr01', 'udeanmr02', 'udeanmr03', 'udeanmr04', 'udeanmr',
        'udeanml01', 'udeanml02', 'udeanml03', 'udeanml04', 'udeanml']  
        #filtered_bones = [filter_char_id + x for x in filtered_bones]
        if ab[0].name[0:nl] == char_id and ab[0].name not in filtered_bones:
            self.report({'WARNING'}, "You need to remove the character ID first!")

        for bone in [*a_object.data.bones]:
            if any(x in bone.name for x in filtered_bones) and bone.name.split('_')[0] == '':
                bone.name = clumpdata.path.split('\\')[-3] + bone.name
            elif any(x in bone.name for x in filtered_bones) and len(bone.name.split('_')[0]) == len(clumpdata.path.split('\\')[-3]):
                bone.name = clumpdata.path.split('\\')[-3] + bone.name[len(clumpdata.path.split('\\')[-3]):]
            elif bone.name[0:nl] != char_id and bone.name:
                self.report({'INFO'}, f"ID:({char_id}) added to ({bone.name})")
                bone.name = char_id + ' ' + bone.name
        
        bpy.ops.object.select_all(action='DESELECT')
        
        #re-sets armatures modifier object to fix a bug in blender 3.0
        for c in bpy.data.objects[colprop.armatures].children:
            for child in c.children:
                if child.type == 'MESH':
                    child.hide_set(False)
                    child.select_set(True)
                    
        for i, obj in enumerate(bpy.context.selected_objects):
            for mod in [m for m in obj.modifiers if m.type == 'ARMATURE']:
                mod.object = bpy.data.objects[colprop.armatures]
        
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class Blend_Mode_Opaque(Operator):
    bl_idname = "object.opaque"
    bl_label = "Set blend mode to opaque"
    bl_description = ('This button will remove all the vertex colors layers in meshes\n'
    "in the active collection")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collections[colprop.collections].all_objects:
            if (obj.type == 'MESH'):
                obj.hide_set(False)
                obj.select_set(True)
    
        for obj in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.context.object.active_material.blend_method = 'OPAQUE'
        return {'FINISHED'}

class StormIK(Operator):
    bl_idname = "object.ik"
    bl_label = "STORM IK"
    bl_description = ('Add IK bones and Constraints.\n'
    'WARNING: THIS WILL CAUSE YOUR MODEL TO LOOK DEFORMED IF EXPORTED AS XFBIN. THIS MUST ONLY BE USED FOR POSING AND ANIMATIONS ONLY.')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        
        colprop = bpy.context.scene.col_prop

        bones = ['r forearm', 'r upperarm', 'r hand', 'r finger01', 'r finger02',
        'r finger11', 'r finger12', 'r finger21', 'r finger22', 'r finger31',
        'r finger32', 'r finger41', 'r finger42', 'l forearm', 'l upperarm',
        'l hand', 'l finger01', 'l finger02', 'l finger11', 'l finger12', 'l finger21',
        'l finger22', 'l finger31', 'l finger32', 'l finger41', 'l finger42',
        'left wearnub','front wearnub', 'back wearnub', 'right wearnub', 'l calf',
        'l foot', 'l toe0', 'r calf', 'r foot', 'r toe0', 'bustnub', 'scarfnub',
        'hair_bl02', 'hair_bc03', 'hair_br02', 'hair_fl02', 'hair_fr02', 'tongue04',
        'tongue03', 'tongue02', 'spine', 'spine1', 'neck']

        ad_name = bpy.data.objects[colprop.armatures].data.name
        a_name = bpy.data.objects[colprop.armatures].name
        collection = bpy.data.collections[colprop.collections]

        if ad_name != a_name:
            for a in collection.all_objects:
                b = []
                if a.type == 'ARMATURE':
                    b.append(a)
                for c in b:
                    c.data.name = c.name
                    self.report({'INFO'}, f"fixed armature name")

        editbone = bpy.data.armatures[colprop.armatures].edit_bones
        model_bones = bpy.data.armatures[colprop.armatures].bones

        bpy.ops.object.remove_char_code()
        bpy.context.view_layer.objects.active = bpy.data.objects[colprop.armatures]
        if bpy.context.mode != 'EDIT_ARMATURE':
            bpy.ops.object.editmode_toggle()

        for b in bones:
            if b in model_bones:
                print(f"Connected ({b}) bone")
                editbone[b].parent.tail = editbone[b].head
                editbone[b].use_connect = True


        #Re-Parent bones
        #------------------------------------------------------------
        editbone['l clavicle'].parent = editbone['spine1']
        editbone['r clavicle'].parent = editbone['spine1']
        editbone['l thigh'].parent = editbone['pelvis']
        editbone['r thigh'].parent = editbone['pelvis']

        #Add IK bones
        #------------------------------------------------------------
        #Head
        head = editbone.new('HeadTrack')
        head.use_deform = False
        head.head.zx = editbone['head'].head.zx
        head.head.y = -0.55
        head.tail.zx = editbone['head'].head.zx
        head.tail.y = -0.65
        #------------------------------------------------------------
        #Feet
        l_foot = editbone.new('L Foot IK')
        l_foot.use_deform = False
        l_foot.head = editbone['l foot'].head
        l_foot.tail.zx = editbone['l foot'].head.zx
        l_foot.tail.y = editbone['l foot'].head.y + 0.1
        editbone['l foot'].use_connect = False
        editbone['l foot'].parent = editbone['L Foot IK']

        r_foot = editbone.new('R Foot IK')
        r_foot.use_deform = False
        r_foot.head = editbone['r foot'].head
        r_foot.tail.zx = editbone['r foot'].head.zx
        r_foot.tail.y = editbone['r foot'].head.y + 0.1
        editbone['r foot'].use_connect = False
        editbone['r foot'].parent = editbone['R Foot IK']
        #------------------------------------------------------------
        #Knees
        l_knee = editbone.new('L Knee IK')
        l_knee.use_deform = False
        l_knee.head.zx = editbone['l calf'].head.zx
        l_knee.head.y = -0.55
        l_knee.tail.zx = editbone['l calf'].head.zx
        l_knee.tail.y = -0.65
        editbone['L Knee IK'].parent = editbone['L Foot IK']
        r_knee = editbone.new('R Knee IK')
        r_knee.use_deform = False
        r_knee.head.zx = editbone['r calf'].head.zx
        r_knee.head.y = -0.55
        r_knee.tail.zx = editbone['r calf'].head.zx
        r_knee.tail.y = -0.65
        editbone['R Knee IK'].parent = editbone['R Foot IK']
        #------------------------------------------------------------
        #Elbows
        l_elbow = editbone.new('L Elbow IK')
        l_elbow.use_deform = False
        l_elbow.head.zx = editbone['l forearm'].head.zx
        l_elbow.head.y = 0.35
        l_elbow.tail.zx = editbone['l forearm'].head.zx
        l_elbow.tail.y = 0.45

        r_elbow = editbone.new('R Elbow IK')
        r_elbow.use_deform = False
        r_elbow.head.zx = editbone['r forearm'].head.zx
        r_elbow.head.y = 0.35
        r_elbow.tail.zx = editbone['r forearm'].head.zx
        r_elbow.tail.y = 0.45
        #-------------------------------------------------------------
        #Hands
        l_hand = editbone.new('L Hand IK')
        l_hand.use_deform = False
        l_hand.head = editbone['l hand'].head
        l_hand.tail.y = editbone['l hand'].head.y
        l_hand.tail.z = editbone['l hand'].head.z + -0.05
        l_hand.tail.x = editbone['l hand'].head.x + 0.05
        editbone['l hand'].tail.x += 0.015
        editbone['l hand'].tail.z += -0.015
        editbone['L Hand IK'].roll = editbone['l hand'].roll

        r_hand = editbone.new('R Hand IK')
        r_hand.use_deform = False
        r_hand.head= editbone['r hand'].head
        r_hand.tail.y = editbone['r hand'].head.y
        r_hand.tail.z = editbone['r hand'].head.z + -0.05
        r_hand.tail.x = editbone['r hand'].head.x + -0.05
        editbone['r hand'].tail.x += -0.015
        editbone['r hand'].tail.z += -0.015
        editbone['R Hand IK'].roll = editbone['r hand'].roll
        #-------------------------------------------------------------
        #Spine

        spine = editbone.new('Spine IK')
        spine.use_deform = False
        spine.head = editbone['spine1'].head
        spine.tail.xz = editbone['spine1'].head.xz
        spine.tail.y = editbone['spine1'].head.y + 0.1

        editbone['spine1'].use_connect = False
        editbone['spine1'].parent = editbone['Spine IK']

        bpy.ops.object.editmode_toggle()
        #-------------------------------------------------------------
        #IK Constraints
        bpy.ops.object.posemode_toggle()
        posebone = bpy.data.objects[colprop.armatures].pose.bones

        l_calf_ik = posebone['l calf'].constraints.new('IK')
        l_calf_ik.target = bpy.data.objects[colprop.armatures]
        l_calf_ik.subtarget = 'L Foot IK'
        l_calf_ik.pole_target = bpy.data.objects[colprop.armatures]
        l_calf_ik.pole_subtarget = 'L Knee IK'
        l_calf_ik.pole_angle = -0.462512
        l_calf_ik.chain_count = 2

        r_calf_ik = posebone['r calf'].constraints.new('IK')
        r_calf_ik.target = bpy.data.objects[colprop.armatures]
        r_calf_ik.subtarget = 'R Foot IK'
        r_calf_ik.pole_target = bpy.data.objects[colprop.armatures]
        r_calf_ik.pole_subtarget = 'R Knee IK'
        r_calf_ik.pole_angle = 0.462512
        r_calf_ik.chain_count = 2
        #-------------------------------------------------------------
        l_forearm_ik = posebone['l forearm'].constraints.new('IK')
        l_forearm_ik.target = bpy.data.objects[colprop.armatures]
        l_forearm_ik.subtarget = 'L Hand IK'
        l_forearm_ik.pole_target = bpy.data.objects[colprop.armatures]
        l_forearm_ik.pole_subtarget = 'L Elbow IK'
        l_forearm_ik.pole_angle = -3.14159
        l_forearm_ik.chain_count = 2

        r_forearm_ik = posebone['r forearm'].constraints.new('IK')
        r_forearm_ik.target = bpy.data.objects[colprop.armatures]
        r_forearm_ik.subtarget = 'R Hand IK'
        r_forearm_ik.pole_target = bpy.data.objects[colprop.armatures]
        r_forearm_ik.pole_subtarget = 'R Elbow IK'
        r_forearm_ik.pole_angle = 3.14159
        r_forearm_ik.chain_count = 2

        #Spine
        #-------------------------------------------------------------
        spine_ik = posebone['spine'].constraints.new('IK')
        spine_ik.target = bpy.data.objects[colprop.armatures]
        spine_ik.subtarget = 'Spine IK'
        spine_ik.chain_count = 1

        #-------------------------------------------------------------
        #DampedTrack

        head_const = posebone['head'].constraints.new('DAMPED_TRACK')
        head_const.target = bpy.data.objects[colprop.armatures]
        head_const.subtarget = 'HeadTrack'

        #-------------------------------------------------------------
        #Copy Location constraints

        l_foot_const = posebone['l foot'].constraints.new('COPY_LOCATION')
        l_foot_const.target = bpy.data.objects[colprop.armatures]
        l_foot_const.subtarget = 'l calf'
        l_foot_const.head_tail = 1

        r_foot_const = posebone['r foot'].constraints.new('COPY_LOCATION')
        r_foot_const.target = bpy.data.objects[colprop.armatures]
        r_foot_const.subtarget = 'r calf'
        r_foot_const.head_tail = 1

        spine1_const = posebone['spine1'].constraints.new('COPY_LOCATION')
        spine1_const.target = bpy.data.objects[colprop.armatures]
        spine1_const.subtarget = 'spine'
        spine1_const.head_tail = 1

        #-------------------------------------------------------------
        #Copy Rotation constraints
        l_forearm_const = posebone['l hand'].constraints.new('COPY_ROTATION')
        l_forearm_const.target = bpy.data.objects[colprop.armatures]
        l_forearm_const.subtarget = 'L Hand IK'

        r_forearm_const = posebone['r hand'].constraints.new('COPY_ROTATION')
        r_forearm_const.target = bpy.data.objects[colprop.armatures]
        r_forearm_const.subtarget = 'R Hand IK'
        #-------------------------------------------------------------
        l_finger02_const = posebone['l finger02'].constraints.new('COPY_ROTATION')
        l_finger02_const.target = bpy.data.objects[colprop.armatures]
        l_finger02_const.subtarget = 'l finger01'
        l_finger02_const.use_x = False
        l_finger02_const.use_y = False
        l_finger02_const.use_z = True
        l_finger02_const.mix_mode = 'ADD'
        l_finger02_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger02_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        l_finger11_const = posebone['l finger11'].constraints.new('COPY_ROTATION')
        l_finger11_const.target = bpy.data.objects[colprop.armatures]
        l_finger11_const.subtarget = 'l finger1'
        l_finger11_const.use_x = True
        l_finger11_const.use_y = False
        l_finger11_const.use_z = False
        l_finger11_const.mix_mode = 'ADD'
        l_finger11_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger11_const.owner_space = 'LOCAL'

        l_finger12_const = posebone['l finger12'].constraints.new('COPY_ROTATION')
        l_finger12_const.target = bpy.data.objects[colprop.armatures]
        l_finger12_const.subtarget = 'l finger11'
        l_finger12_const.use_x = False
        l_finger12_const.use_y = False
        l_finger12_const.use_z = True
        l_finger12_const.mix_mode = 'ADD'
        l_finger12_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger12_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        l_finger21_const = posebone['l finger21'].constraints.new('COPY_ROTATION')
        l_finger21_const.target = bpy.data.objects[colprop.armatures]
        l_finger21_const.subtarget = 'l finger2'
        l_finger21_const.use_x = True
        l_finger21_const.use_y = False
        l_finger21_const.use_z = False
        l_finger21_const.mix_mode = 'ADD'
        l_finger21_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger21_const.owner_space = 'LOCAL'

        l_finger22_const = posebone['l finger22'].constraints.new('COPY_ROTATION')
        l_finger22_const.target = bpy.data.objects[colprop.armatures]
        l_finger22_const.subtarget = 'l finger21'
        l_finger22_const.use_x = False
        l_finger22_const.use_y = False
        l_finger22_const.use_z = True
        l_finger22_const.mix_mode = 'ADD'
        l_finger22_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger22_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        l_finger31_const = posebone['l finger31'].constraints.new('COPY_ROTATION')
        l_finger31_const.target = bpy.data.objects[colprop.armatures]
        l_finger31_const.subtarget = 'l finger3'
        l_finger31_const.use_x = True
        l_finger31_const.use_y = False
        l_finger31_const.use_z = False
        l_finger31_const.mix_mode = 'ADD'
        l_finger31_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger31_const.owner_space = 'LOCAL'

        l_finger32_const = posebone['l finger32'].constraints.new('COPY_ROTATION')
        l_finger32_const.target = bpy.data.objects[colprop.armatures]
        l_finger32_const.subtarget = 'l finger31'
        l_finger32_const.use_x = False
        l_finger32_const.use_y = False
        l_finger32_const.use_z = True
        l_finger32_const.mix_mode = 'ADD'
        l_finger32_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger32_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        l_finger41_const = posebone['l finger41'].constraints.new('COPY_ROTATION')
        l_finger41_const.target = bpy.data.objects[colprop.armatures]
        l_finger41_const.subtarget = 'l finger4'
        l_finger41_const.use_x = True
        l_finger41_const.use_y = False
        l_finger41_const.use_z = False
        l_finger41_const.mix_mode = 'ADD'
        l_finger41_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger41_const.owner_space = 'LOCAL'

        l_finger42_const = posebone['l finger42'].constraints.new('COPY_ROTATION')
        l_finger42_const.target = bpy.data.objects[colprop.armatures]
        l_finger42_const.subtarget = 'l finger41'
        l_finger42_const.use_x = False
        l_finger42_const.use_y = False
        l_finger42_const.use_z = True
        l_finger42_const.mix_mode = 'ADD'
        l_finger42_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_finger42_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        r_finger02_const = posebone['r finger02'].constraints.new('COPY_ROTATION')
        r_finger02_const.target = bpy.data.objects[colprop.armatures]
        r_finger02_const.subtarget = 'r finger01'
        r_finger02_const.use_x = False
        r_finger02_const.use_y = False
        r_finger02_const.use_z = True
        r_finger02_const.mix_mode = 'ADD'
        r_finger02_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger02_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        r_finger11_const = posebone['r finger11'].constraints.new('COPY_ROTATION')
        r_finger11_const.target = bpy.data.objects[colprop.armatures]
        r_finger11_const.subtarget = 'r finger1'
        r_finger11_const.use_x = True
        r_finger11_const.use_y = False
        r_finger11_const.use_z = False
        r_finger11_const.mix_mode = 'ADD'
        r_finger11_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger11_const.owner_space = 'LOCAL'

        r_finger12_const = posebone['r finger12'].constraints.new('COPY_ROTATION')
        r_finger12_const.target = bpy.data.objects[colprop.armatures]
        r_finger12_const.subtarget = 'r finger11'
        r_finger12_const.use_x = False
        r_finger12_const.use_y = False
        r_finger12_const.use_z = True
        r_finger12_const.mix_mode = 'ADD'
        r_finger12_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger12_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        r_finger21_const = posebone['r finger21'].constraints.new('COPY_ROTATION')
        r_finger21_const.target = bpy.data.objects[colprop.armatures]
        r_finger21_const.subtarget = 'r finger2'
        r_finger21_const.use_x = True
        r_finger21_const.use_y = False
        r_finger21_const.use_z = False
        r_finger21_const.mix_mode = 'ADD'
        r_finger21_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger21_const.owner_space = 'LOCAL'

        r_finger22_const = posebone['r finger22'].constraints.new('COPY_ROTATION')
        r_finger22_const.target = bpy.data.objects[colprop.armatures]
        r_finger22_const.subtarget = 'r finger21'
        r_finger22_const.use_x = False
        r_finger22_const.use_y = False
        r_finger22_const.use_z = True
        r_finger22_const.mix_mode = 'ADD'
        r_finger22_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger22_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        r_finger31_const = posebone['r finger31'].constraints.new('COPY_ROTATION')
        r_finger31_const.target = bpy.data.objects[colprop.armatures]
        r_finger31_const.subtarget = 'r finger3'
        r_finger31_const.use_x = True
        r_finger31_const.use_y = False
        r_finger31_const.use_z = False
        r_finger31_const.mix_mode = 'ADD'
        r_finger31_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger31_const.owner_space = 'LOCAL'

        r_finger32_const = posebone['r finger32'].constraints.new('COPY_ROTATION')
        r_finger32_const.target = bpy.data.objects[colprop.armatures]
        r_finger32_const.subtarget = 'r finger31'
        r_finger32_const.use_x = False
        r_finger32_const.use_y = False
        r_finger32_const.use_z = True
        r_finger32_const.mix_mode = 'ADD'
        r_finger32_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger32_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        r_finger41_const = posebone['r finger41'].constraints.new('COPY_ROTATION')
        r_finger41_const.target = bpy.data.objects[colprop.armatures]
        r_finger41_const.subtarget = 'r finger4'
        r_finger41_const.use_x = True
        r_finger41_const.use_y = False
        r_finger41_const.use_z = False
        r_finger41_const.mix_mode = 'ADD'
        r_finger41_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger41_const.owner_space = 'LOCAL'

        r_finger42_const = posebone['r finger42'].constraints.new('COPY_ROTATION')
        r_finger42_const.target = bpy.data.objects[colprop.armatures]
        r_finger42_const.subtarget = 'r finger41'
        r_finger42_const.use_x = False
        r_finger42_const.use_y = False
        r_finger42_const.use_z = True
        r_finger42_const.mix_mode = 'ADD'
        r_finger42_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_finger42_const.owner_space = 'LOCAL'
        #-------------------------------------------------------------
        #Arm Twist Bones
        l_twist06_const = posebone['l arm bone06'].constraints.new('COPY_ROTATION')
        l_twist06_const.target = bpy.data.objects[colprop.armatures]
        l_twist06_const.subtarget = 'l hand'
        l_twist06_const.use_x = True
        l_twist06_const.use_y = False
        l_twist06_const.use_z = False
        l_twist06_const.mix_mode = 'ADD'
        l_twist06_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_twist06_const.owner_space = 'LOCAL'
        l_twist06_const.influence = 0.8
        #-------------------------------------------------------------
        l_twist05_const = posebone['l arm bone05'].constraints.new('COPY_ROTATION')
        l_twist05_const.target = bpy.data.objects[colprop.armatures]
        l_twist05_const.subtarget = 'l arm bone06'
        l_twist05_const.use_x = True
        l_twist05_const.use_y = False
        l_twist05_const.use_z = False
        l_twist05_const.mix_mode = 'ADD'
        l_twist05_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_twist05_const.owner_space = 'LOCAL'
        l_twist06_const.influence = 0.7
        #-------------------------------------------------------------
        l_twist04_const = posebone['l arm bone04'].constraints.new('COPY_ROTATION')
        l_twist04_const.target = bpy.data.objects[colprop.armatures]
        l_twist04_const.subtarget = 'l arm bone05'
        l_twist04_const.use_x = True
        l_twist04_const.use_y = False
        l_twist04_const.use_z = False
        l_twist04_const.mix_mode = 'ADD'
        l_twist04_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_twist04_const.owner_space = 'LOCAL'
        l_twist04_const.influence = 0.65
        #-------------------------------------------------------------
        l_twist03_const = posebone['l arm bone03'].constraints.new('COPY_ROTATION')
        l_twist03_const.target = bpy.data.objects[colprop.armatures]
        l_twist03_const.subtarget = 'l arm bone04'
        l_twist03_const.use_x = True
        l_twist03_const.use_y = False
        l_twist03_const.use_z = False
        l_twist03_const.mix_mode = 'ADD'
        l_twist03_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_twist03_const.owner_space = 'LOCAL'
        l_twist03_const.influence = 0.6
        #-------------------------------------------------------------
        l_twist02_const = posebone['l arm bone02'].constraints.new('COPY_ROTATION')
        l_twist02_const.target = bpy.data.objects[colprop.armatures]
        l_twist02_const.subtarget = 'l arm bone03'
        l_twist02_const.use_x = True
        l_twist02_const.use_y = False
        l_twist02_const.use_z = False
        l_twist02_const.mix_mode = 'ADD'
        l_twist02_const.target_space = 'LOCAL_OWNER_ORIENT'
        l_twist02_const.owner_space = 'LOCAL'
        l_twist02_const.influence = 0.5
        #-------------------------------------------------------------
        r_twist06_const = posebone['r arm bone06'].constraints.new('COPY_ROTATION')
        r_twist06_const.target = bpy.data.objects[colprop.armatures]
        r_twist06_const.subtarget = 'r hand'
        r_twist06_const.use_x = True
        r_twist06_const.use_y = False
        r_twist06_const.use_z = False
        r_twist06_const.mix_mode = 'ADD'
        r_twist06_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_twist06_const.owner_space = 'LOCAL'
        r_twist06_const.influence = 0.8
        #-------------------------------------------------------------
        r_twist05_const = posebone['r arm bone05'].constraints.new('COPY_ROTATION')
        r_twist05_const.target = bpy.data.objects[colprop.armatures]
        r_twist05_const.subtarget = 'r arm bone06'
        r_twist05_const.use_x = True
        r_twist05_const.use_y = False
        r_twist05_const.use_z = False
        r_twist05_const.mix_mode = 'ADD'
        r_twist05_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_twist05_const.owner_space = 'LOCAL'
        r_twist06_const.influence = 0.7
        #-------------------------------------------------------------
        r_twist04_const = posebone['r arm bone04'].constraints.new('COPY_ROTATION')
        r_twist04_const.target = bpy.data.objects[colprop.armatures]
        r_twist04_const.subtarget = 'r arm bone05'
        r_twist04_const.use_x = True
        r_twist04_const.use_y = False
        r_twist04_const.use_z = False
        r_twist04_const.mix_mode = 'ADD'
        r_twist04_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_twist04_const.owner_space = 'LOCAL'
        r_twist04_const.influence = 0.65
        #-------------------------------------------------------------
        r_twist03_const = posebone['r arm bone03'].constraints.new('COPY_ROTATION')
        r_twist03_const.target = bpy.data.objects[colprop.armatures]
        r_twist03_const.subtarget = 'r arm bone04'
        r_twist03_const.use_x = True
        r_twist03_const.use_y = False
        r_twist03_const.use_z = False
        r_twist03_const.mix_mode = 'ADD'
        r_twist03_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_twist03_const.owner_space = 'LOCAL'
        r_twist03_const.influence = 0.6
        #-------------------------------------------------------------
        r_twist02_const = posebone['r arm bone02'].constraints.new('COPY_ROTATION')
        r_twist02_const.target = bpy.data.objects[colprop.armatures]
        r_twist02_const.subtarget = 'r arm bone03'
        r_twist02_const.use_x = True
        r_twist02_const.use_y = False
        r_twist02_const.use_z = False
        r_twist02_const.mix_mode = 'ADD'
        r_twist02_const.target_space = 'LOCAL_OWNER_ORIENT'
        r_twist02_const.owner_space = 'LOCAL'
        r_twist02_const.influence = 0.5
        #-------------------------------------------------------------
        #Spine
        spine_const = posebone['spine'].constraints.new('COPY_ROTATION')
        spine_const.target = bpy.data.objects[colprop.armatures]
        spine_const.subtarget = 'spine1'
        spine_const.use_x = False
        spine_const.use_y = False
        spine_const.use_z = True
        spine_const.mix_mode = 'REPLACE'
        spine_const.influence = 0.5

        return {'FINISHED'}

class FixNames(Operator):
    bl_idname = "object.fix_names"
    bl_label = "Fix names and delete orphans"
    bl_description = ("This will fix names and stuff + delete useless shit")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.collections != "":
            return True
        else:
            return False

    def execute(self, context):
        colprop = bpy.context.scene.col_prop
        collection = bpy.data.collections[colprop.collections]
        armature = bpy.data.armatures

        #fix collection name
        if collection.name[-4:-2] == '.0':
            collection.name = collection.name[0:-4]
        #fix object names and remove all unused names in BlendData
        for o in collection.all_objects:
            if o.name[-4:-2] == '.0':
                o.name = o.name[0:-4]
            elif o.name.startswith('#XFBIN') and o.name[-5:-3] == '.0' :
                o.name = o.name[0:-5] + ']'
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        #fix armature name and remove unused names in BlendData
        for a in collection.all_objects:
            b = []
            if a.type == 'ARMATURE':
                b.append(a)
            for c in b:
                c.data.name = c.name
        for a in armature:
            if a.name[-4:-2] == '.0' and a.users == 0:
                print(a)
                armature.remove(a)
            '''for m in bpy.data.materials:
            if m.name.startswith('[XFBIN]') and m.name[-4:-2] == '.0':
                print(m)'''
        return {'FINISHED'}

class ArmatureModifier(Operator):
    bl_idname = "object.add_armature_modifier"
    bl_label = "Add armature modifier"
    bl_description = ("Add and corrects armature modifiers in meshes of a specific armature")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        colprop = bpy.context.scene.col_prop
        cobj = []

        for obj in bpy.data.objects[colprop.armatures].children:
            for o in obj.children:
                cobj.append(o)
        #print(*cobj, sep = '\n')
        #print(*a_mods, sep = '\n')
        modname = bpy.data.objects[colprop.armatures].name
        for obj in cobj:
            mods = []
            for mod in obj.modifiers:
                if mod.type == 'ARMATURE':
                    mods.append(mod)
            if len(mods) < 1:
                mod = obj.modifiers.new(type= 'ARMATURE', name= modname)
                mod.object = obj.parent.parent
            else:
                for mod in mods:
                    if mod.object != obj.parent.parent:
                        mod.object = obj.parent.parent

        #print(len(cobj))
        return {'FINISHED'}


class Swap_Character_Code(Operator):
    bl_idname = "object.swap_code"
    bl_label = "Swap Character Code"
    bl_description = ("Swaps character code and model ID using the code you input")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
        
    def execute(self, context):
        colprop = bpy.context.scene.col_prop
        collection = bpy.data.collections[colprop.collections]
        armature = bpy.data.armatures[colprop.armatures]
        armature_obj = bpy.data.objects[colprop.armatures]

        #delete .001, .002 etc... to ensure no errors happen
        bpy.ops.object.fix_names()

        #change objects names
        nl = len(armature.bones[1].name) #code00t0 = 8
        nc = len(armature.bones[1].name[:-4]) #code = 4
        nc2 = len(armature.bones[1].name[:-2]) #code00 = 6
        clumpdata = armature_obj.xfbin_clump_data
        for o in collection.all_objects:
            
            #Armature object
            if o.name[:nc2] == armature.bones[1].name[:-2] and o.name.endswith('[C]'):
                o.name = colprop['CharacterCode'] + o.name[nc2:]
            elif o.name[:nc] == armature.bones[1].name[:-4] and o.name.endswith('[C]'):
                o.name = colprop['CharacterCode'] + o.name[nc:]
            
            #asianmel, asianmer etc... these meshes usually match chunk path code
            if len(o.name.split('_')[0]) == len(clumpdata.path.split('\\')[-3]):
                o.name = colprop['PathCode'] + o.name[len(clumpdata.path.split('\\')[-3]):]
            
            #All other objects
            if o.name[:nl] == armature.bones[1].name:
                o.name = colprop['CharacterCode'] + colprop['ModelID'] + o.name[nl:]
            
            
            '''if o.name[:nc2] == armature.bones[1].name[:-2]:
                o.name = colprop['CharacterCode'] + colprop['ModelID'][:2] + o.name[nc2:]
            elif o.name[:nl] == armature.bones[1].name:
                o.name = colprop['CharacterCode'] + colprop['ModelID'] + o.name[nl:]'''
            '''elif o.name[:nc] == armature.bones[1].name[:-4]:
            o.name = colprop['PathCode'] + o.name[nc:]'''

        #make sure that armature name = armature object name
            b = []
            if o.type == 'ARMATURE':
                b.append(o)
            for c in b:
                c.data.name = c.name

        #change texture chunks names
        tex = collection.objects[f'#XFBIN Textures [{collection.name}]'].xfbin_texture_chunks_data.texture_chunks

        for t in tex:
            print(t.texture_name)
            if t.texture_name[:nc2] == armature.bones[1].name[:-2]:
                t.texture_name = colprop['CharacterCode'] + t.texture_name[nc2:]
            elif t.texture_name[:nc] == armature.bones[1].name[:-4]:
                t.texture_name = colprop['CharacterCode'] + t.texture_name[nc:]
            else:
                print(f"{t.texture_name} doesn't start with {armature.bones[1].name[:-4]}")
            
            #Determine Code and object locations in texture path
            code = t.path.split('/')[-3]
            pathob = t.path.split('/')[-1]

            #Change texture path code
            xfclump = armature_obj.xfbin_clump_data
            code = t.path.split('/')[-3]
            newcode = colprop['PathCode']
            t.path = t.path.replace(code, newcode)

            #Change clump path object
            pathob = t.path.split('/')[-1]
            newpathob = t.texture_name + pathob[-4:]
            t.path = t.path.replace(pathob, newpathob)

        #remove and add models and model groups
        armature_obj.xfbin_clump_data.models.clear()
        armature_obj.xfbin_clump_data.model_groups.clear()
        g = armature_obj.xfbin_clump_data.model_groups.add()
        g.name = 'Group'
        g.unk = '7F 7F FF FF'
        for child in armature_obj.children:
            m = armature_obj.xfbin_clump_data.models.add()
            #m.value = child.name
            m.empty = child
            gm = g.models.add()
            #gm.name = child.name
            gm.empty = child
            child.xfbin_nud_data.mesh_bone = child.name

        #Change clump path code
        xfclump = armature_obj.xfbin_clump_data
        code = xfclump.path.split('\\')[-3]
        newcode = colprop['PathCode']
        xfclump.path = xfclump.path.replace(code, newcode)

        #Change clump path object
        pathob = xfclump.path.split('\\')[-1]
        newpathob = colprop['CharacterCode'] + pathob[-8:]
        xfclump.path = xfclump.path.replace(pathob, newpathob)

        #Swap codes in clump materials
        for mat in xfclump.materials:
            for texg in mat.texture_groups:
                for t in texg.textures:
                    if t.texture_name != 'celshade':
                        if t.texture_name[:nc2] == armature.bones[1].name[:-2]:
                            t.texture_name = colprop['CharacterCode'] + t.texture_name[nc2:]
                        elif t.texture_name[:nc] == armature.bones[1].name[:-4]:
                            t.texture_name = colprop['CharacterCode'] + t.texture_name[nc:]
                        else:
                            print(f"{t.texture_name} doesn't start with {armature.bones[1].name[:-4]}")
                        
                        #Determine Code and object locations in texture path
                        code = t.path.split('/')[-3]
                        pathob = t.path.split('/')[-1]

                        #Change clump path code
                        xfclump = armature_obj.xfbin_clump_data
                        code = t.path.split('/')[-3]
                        newcode = colprop['PathCode']
                        t.path = t.path.replace(code, newcode)

                        #Change clump path object
                        pathob = t.path.split('/')[-1]
                        newpathob = t.texture_name + pathob[-4:]
                        t.path = t.path.replace(pathob, newpathob)

            if mat.material_name[:nc2] == armature.bones[1].name[:-2]:
                mat.material_name = colprop['CharacterCode'] + mat.material_name[nc2:]
            elif mat.material_name[:nc] == armature.bones[1].name[:-4]:
                mat.material_name = colprop['CharacterCode'] + mat.material_name[nc:]

        #Reapply materials in meshes after changing the names

        for o in armature_obj.children:
            for c in o.children:
                if c.xfbin_mesh_data.xfbin_material[:nc2] == armature.bones[1].name[:-2]:
                    c.xfbin_mesh_data.xfbin_material = colprop['CharacterCode'] + c.xfbin_mesh_data.xfbin_material[nc2:]
                elif c.xfbin_mesh_data.xfbin_material[:nc] == armature.bones[1].name[:-4]:
                    c.xfbin_mesh_data.xfbin_material = colprop['CharacterCode'] + c.xfbin_mesh_data.xfbin_material[nc:]

        #change collection name and XFBIN Textures
        colname = armature.name[:-4]
        armname = armature.name
        collection.name = colname

        #make sure that the correct armature is selected
        colprop.collections = colname
        colprop.armatures = armname

        #correct XFBIN Textures name
        for o in collection.all_objects:
            if o.name.startswith('#XFBIN Textures') :
                o.name = o.name[0:16] + '[' + collection.name + ']'

        #change bone names
        bpy.ops.object.remove_char_code()
        armature.bones[1].name = colprop['CharacterCode'] + colprop['ModelID']
        bpy.ops.object.add_char_code()

        return {'FINISHED'}


class GetTexturePath(Operator, ImportHelper):
    bl_idname = "object.get_textures"
    bl_label = "  Select Folder"
    bl_description = ('Open texture directory')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
    
    def execute(self, context):
        dir = self.filepath
        colprop = bpy.context.scene.col_prop
        collection = bpy.context.scene.col_prop.collections
        texture_object = '#XFBIN Textures [' + str(collection) +']'
        #object_name = bpy.context.object.name
        bpy.data.objects[texture_object][texture_object] = dir
        bpy.ops.object.select_all(action='DESELECT')
        
        return {'FINISHED'}

class Replace_Mats(Operator):
    bl_idname = "object.replace_mats"
    bl_label = "Replace Materials ID"
    bl_description = (f'Replace material IDs for the selected meshes, if no meshes were selected, the tool will attempt to replace materials for meshes in the selected collection')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT':
            return True
        else:
            return False
    
    def execute(self, context):

        colprop = bpy.context.scene.col_prop

        collection_objects = [o for o in bpy.data.collections[colprop.collections].all_objects if o.type == 'MESH']

        colprop.Old_Material_ID = str(colprop.Old_Material_ID.upper())

        if bpy.context.active_object.type == 'EMPTY':
            for m in [o for o in bpy.context.active_object.children]:
                if colprop.Old_Material_ID in m.xfbin_mesh_data.materials:
                    m.xfbin_mesh_data.materials[colprop.Old_Material_ID].material_id = colprop.New_Material_ID      

        elif len(bpy.context.selected_objects) > 0:
            for m in [o for o in bpy.context.selected_objects]:
                if colprop['Old_Material_ID'] in m.xfbin_mesh_data.materials:
                    m.xfbin_mesh_data.materials[colprop.Old_Material_ID].material_id = colprop.New_Material_ID
                else:
                    self.report({"WARNING"}, f"The material you're attempting to replace does not exist in {m.name}")

        else:
            self.report({"INFO"}, f"No meshes were selected, Attempting to replace materials for meshes in the whole collecton")
            for m in [o for o in collection_objects]:
                if colprop['Old_Material_ID'] in m.xfbin_mesh_data.materials:
                    m.xfbin_mesh_data.materials[colprop.Old_Material_ID].material_id = colprop.New_Material_ID
                else:
                    self.report({"WARNING"}, f"The material you're attempting to replace does not exist in {m.name}")
        
        return {'FINISHED'}

class Duplicate_XFBIN_Mat(Operator):
    bl_idname = "object.duplicate_mats"
    bl_label = "Create New XFBIN Mat"
    bl_description = (f"Creates a separete XFBIN material for the selected mesh and applies it. EXAMPLE: if a mesh has a material called body1, it will make a duplicate copy and applies it")
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT':
            return True
        else:
            return False
    
    def execute(self, context):

        colprop = bpy.context.scene.col_prop

        active = bpy.context.active_object

        mat = active.xfbin_mesh_data.xfbin_material

        matc = active.parent.parent.xfbin_clump_data.materials[mat]

        new = active.parent.parent.xfbin_clump_data.materials.add()

        new.material_name = matc.material_name + "NEW"

        new.field02 = matc.field02

        new.field04 = matc.field04

        new.float_format = matc.float_format

        new.floats = matc.floats

        for i in range(len(matc.texture_groups)):
            tex = new.texture_groups.add()
            for t in range(len(matc.texture_groups[i].textures)):
                    tx = tex.textures.add()
                    

        for i, tg in enumerate(new.texture_groups):
            new.texture_groups[new['texture_groups'][i].name].name = matc['texture_groups'][i]['name']
            new['texture_groups'][i]['flag'] = matc['texture_groups'][i]['flag']
            for a, t in enumerate(new['texture_groups'][i]['textures']):
                new['texture_groups'][i]['textures'][a]['name'] = matc['texture_groups'][i]['textures'][a]['name']
                new['texture_groups'][i]['textures'][a]['path'] = matc['texture_groups'][i]['textures'][a]['path']
                new['texture_groups'][i]['textures'][a]['texture'] = matc['texture_groups'][i]['textures'][a]['texture']
                new['texture_groups'][i]['textures'][a]['texture_name'] = matc['texture_groups'][i]['textures'][a]['texture_name']
        bpy.context.active_object.xfbin_mesh_data.xfbin_material = bpy.context.active_object.xfbin_mesh_data.xfbin_material + 'NEW'


        return {'FINISHED'}

class ApplyTextures(Operator):
    bl_idname = "object.apply_texture"
    bl_label = "Apply Textures"
    bl_description = ('Link textures to material and apply them to view on model')
     
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "" and '#XFBIN Textures [{}]'.format(bpy.context.scene.col_prop.collections) in bpy.data.objects['#XFBIN Textures [{}]'.format(bpy.context.scene.col_prop.collections)]:
            return True
        else:
            return False
        
    def execute(self, context):
        
        #Define collections
        collection = bpy.context.scene.col_prop.collections
        colprop = bpy.context.scene.col_prop
        
        # Get texture paths
        texture_object = '#XFBIN Textures [' + str(collection) +']'
        path = bpy.data.objects[texture_object][texture_object]
        print(path)
        texture_files = [f for f in listdir(path) if isfile(join(path, f))]
        texture_ext = texture_files[0][-4:]
        
        #Set context and select respective armatures
        bpy.data.objects[texture_object].select_set(True)
        bpy.context.scene.objects[colprop.collections].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[colprop.armatures]
        
        #Get materials and number of materials
        xfbin_materials_count = len(bpy.context.object.xfbin_clump_data.materials)
        xfbin_material = {} #Dictionary containing material and it's corresponding textures
        
        
        #Populate dictonary for Blender use 
        for i in range(xfbin_materials_count): #Append '[XFBIN]' to material name for Blender use
            xfbin_material['[XFBIN] '+ bpy.context.object.xfbin_clump_data.materials[i].material_name] = bpy.context.object.xfbin_clump_data.materials[i].texture_groups[0].textures[0].texture_name
        print(xfbin_material)

        
        #Apply Image Texture to material from directory and link corresponding texture
        for i in range(len(xfbin_material)):
            mat = bpy.data.materials[list(xfbin_material)[i]]
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            assert(bsdf)
            surface = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            texImage.image = bpy.data.images.load(path + list(xfbin_material.values())[i] + texture_ext)
            mat.node_tree.links.new(surface.inputs['Base Color'], texImage.outputs['Color'])
        bpy.ops.object.select_all(action='DESELECT')    
        bpy.context.space_data.shading.color_type = 'TEXTURE'
        
        #Delete unused and unlinked textures
        original_type = bpy.context.area.type
        bpy.context.area.type = "OUTLINER"
        bpy.context.space_data.display_mode = 'ORPHAN_DATA'
        bpy.ops.outliner.orphans_purge()
        bpy.context.area.type = original_type

        return {'FINISHED'}

class UnlinkTextures(Operator):
    bl_idname = "object.unlink_textures"
    bl_label = "  Unlink texture(s)"
    bl_description = ('Unlink active textures')
    
    @classmethod
    def poll(cls, context):
        if bpy.context.mode == 'OBJECT' and bpy.context.scene.col_prop.armatures != "":
            return True
        else:
            return False
    
    def execute(self, context):
 
        collections = bpy.data.collections
        colprop = bpy.context.scene.col_prop
        bpy.ops.object.select_all(action='DESELECT')
        
    
        #Get materials and number of materials
        xfbin_materials_count = len(bpy.context.object.xfbin_clump_data.materials)
        xfbin_material = {} #Dictionary containing material and it's corresponding textures 
        
        #Populate dictonary for Blender use 
        for i in range(xfbin_materials_count): #Append '[XFBIN]' to material name for Blender use
            xfbin_material['[XFBIN] '+ bpy.context.object.xfbin_clump_data.materials[i].material_name] = bpy.context.object.xfbin_clump_data.materials[i].texture_groups[0].textures[0].texture_name
        
        
        for obj in collections[colprop.collections].all_objects:
            if (obj.type == 'MESH'):
                obj.hide_set(False)
                obj.select_set(True)
                
                #mat = bpy.context.object.data.materials[0]
                mat = obj.data.materials[0]
                surface = mat.node_tree.nodes["Principled BSDF"]
                mat.use_nodes = False
                #print(mat.node_tree.nodes["Principled BSDF"].inputs[0])
                #mat.node_tree.nodes.delete('ShaderNodeTexImage')
                #mat.node_tree.nodes.remove( node_to_delete )
                
                
        
        #bpy.ops.object.select_all(action='DESELECT')    
        
                
        
        return {'FINISHED'}

