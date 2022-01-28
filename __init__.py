# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Hydra Tools",
    "author" : "HydraBladeZ, Dei",
    "description" : "",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy
from . Panel import (Panel, ColProperty)
from . Operators import (RemoveLOD, AddVertColors, RemoveVertColors,
    PaintVertexColors, ApplyRestPose, RemoveCharCode, RenameBones, AddCharCode)

classes = (Panel, RemoveLOD, ColProperty, AddVertColors, RemoveVertColors,
    PaintVertexColors, ApplyRestPose, RemoveCharCode, RenameBones, AddCharCode)
    
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.col_prop = bpy.props.PointerProperty(type = ColProperty)
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.col_prop
