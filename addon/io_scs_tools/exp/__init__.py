# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2013-2014: SCS Software

from io_scs_tools.exp import pia
from io_scs_tools.exp import pic
from io_scs_tools.exp import pip
from io_scs_tools.exp import pis
from io_scs_tools.exp import pix

from io_scs_tools.utils import object as _object
from io_scs_tools.utils import path as _path
from io_scs_tools.utils import get_scs_globals as _get_scs_globals
from io_scs_tools.utils.printout import lprint


def batch_export(operator_instance, init_obj_list, exclude_switched_off=True, menu_filepath=None):
    """This function calls other sorting functions and depending on the resulting output
    dictionary it exports all available 'SCS Game Objects' into specified locations.

    :param operator_instance: operator from within this function is called (used for report)
    :type operator_instance: bpy.types.Operator
    :param init_obj_list: initial object list which should be exported
    :type init_obj_list: tuple of Blender objects
    :param exclude_switched_off: exlude game object wich root is excplicity exluded by property
    :type exclude_switched_off: bool
    :param menu_filepath: filepath used from menu export
    :type menu_filepath: str
    """

    lprint("", report_errors=-1, report_warnings=-1)  # Clear the 'error_messages' and 'warning_messages'
    game_objects_dict = _object.sort_out_game_objects_for_export(init_obj_list)
    if exclude_switched_off:
        game_objects_dict = _object.exclude_switched_off(game_objects_dict)

    if game_objects_dict:
        scs_game_objects_exported = 0

        # GET GLOBAL FILE PATH
        global_export_filepath = _get_scs_globals().global_export_filepath
        global_filepath = _path.get_blenderfilewise_abs_filepath(global_export_filepath)

        for root_object in game_objects_dict:
            game_object_list = game_objects_dict[root_object]

            # GET CUSTOM FILE PATH
            scs_root_object_export_filepath = root_object.scs_props.scs_root_object_export_filepath
            # print(' scs_root_object_export_filepath:\n%r' % str(scs_root_object_export_filepath))
            custom_filepath = _path.get_blenderfilewise_abs_filepath(scs_root_object_export_filepath, data_type="'SCS Game Object' custom export")
            # print(' custom_filepath (%r):\n%r' % (root_object.name, str(custom_filepath)))

            # MAKE FINAL FILEPATH
            filepath = None
            if menu_filepath:
                filepath = menu_filepath
            elif scs_root_object_export_filepath and custom_filepath and root_object.scs_props.scs_root_object_allow_custom_path:
                filepath = custom_filepath
            elif global_filepath:
                filepath = global_filepath

            # print(' filepath (%r):\n%r' % (root_object.name, str(filepath)))
            scs_project_path = _get_scs_globals().scs_project_path
            if filepath and filepath.startswith(scs_project_path) and scs_project_path != "":
                pix.export(filepath, root_object, game_object_list)
                scs_game_objects_exported += 1
                # if result != {'FINISHED'}: return {'CANCELLED'}
            else:
                if filepath:
                    message = (
                        "No valid export inside SCS Project Base Path found!\n\t   "
                        "Make sure that SCS Project Base Path is properly set and\n\t   " +
                        "that you are exporting somewhere inside that path!\n\t   " +
                        "SCS Project Base Path:\n\t   \"" + scs_project_path + "\"\n\t   " +
                        "SCS Game Object export path:\n\t   \"" + filepath + "\""
                    )
                else:
                message = "No valid export path found! Please check the export path."
                lprint('E ' + message)
                operator_instance.report({'ERROR'}, message.replace("\t", "").replace("   ", ""))
                return {'CANCELLED'}

        if scs_game_objects_exported > 0:
            if scs_game_objects_exported == 1:
                message = "Single 'SCS Game Object' exported."
            else:
                message = "%i 'SCS Game Objects' exported." % scs_game_objects_exported
            lprint('I ' + message)
        else:
            message = "Nothing to export! Please set at least one 'SCS Root Object'."
            lprint('E ' + message)
            operator_instance.report({'ERROR'}, message)
            return {'CANCELLED'}
    else:
        message = "Please create at least one 'SCS Root Object' and parent your objects to it in order to export a 'SCS Game Object'!\n" \
                  "(For more information, please refer to 'SCS Blender Tools' documentation.)"
        lprint('E ' + message)
        operator_instance.report({'ERROR'}, message)
        return {'CANCELLED'}

    return {'FINISHED'}