##############################################################################
#                                                                            #
#   PopCurve for Blender  --  Copyright (C) 2024  Pan Thistle                #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU General Public License as published by     #
#   the Free Software Foundation, either version 3 of the License, or        #
#   (at your option) any later version.                                      #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU General Public License for more details.                             #
#                                                                            #
#   You should have received a copy of the GNU General Public License        #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
#                                                                            #
##############################################################################


# ------------------------------------------------------------------------------
#
# ----------------------------- IMPORTS ----------------------------------------


import bpy
import os
import json

from bpy_extras.io_utils import ImportHelper, ExportHelper

from . import mpopc as ModPOPC
from . import mfnop as ModFNOP


# ------------------------------------------------------------------------------
#
# ------------------------------- BMOPS ----------------------------------------


# ---- POP OPERATORS


class PTDBLNPOPC_OT_pop_simple_update(bpy.types.Operator):
    bl_label = "Simple Update"
    bl_idname = "ptdblnpopc.pop_simple_update"
    bl_description = "pop simple update"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_simple_update: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_pop_reset(bpy.types.Operator):
    bl_label = "Update Settings"
    bl_idname = "ptdblnpopc.pop_reset"
    bl_description = "update set - load default settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    newdef: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        nd = getattr(properties, "newdef")
        if nd:
            return "update set - load default settings"
        return "update set - load current settings"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        if bool(pool.setcoll) and pool.replace_set and pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            replace_set = pool.replace_set
            rename_coll = False
            if self.newdef:
                pool.props_unset()
                rename_coll = True
            ModPOPC.scene_update_newset(scene, replace_set, rename_coll)
            context.view_layer.update()
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_reset: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_popcurve_setup(bpy.types.Operator):
    bl_label = "Pop Curve Setup"
    bl_idname = "ptdblnpopc.popcurve_setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    single: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if getattr(properties, "single"):
            return f"active interface: Curve Array"
        return f"active interface: Single Curve"

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            pool.use_profile = not self.single
            ModPOPC.scene_update_newset(scene, True, False)
            context.view_layer.update()
        except Exception as my_err:
            pool.update_ok = True
            print(f"popcurve_setup: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_curange_react(bpy.types.Operator):
    bl_label = "Range Active Toggle"
    bl_idname = "ptdblnpopc.curange_react"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    active: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if getattr(properties, "active"):
            return "disable active range objects"
        return "enable active range objects"

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            pool.rngs.active = not self.active
            ModPOPC.scene_update_newset(scene, True, False)
            context.view_layer.update()
        except Exception as my_err:
            pool.update_ok = True
            print(f"curange_react: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_batchcoll_toggle(bpy.types.Operator):
    bl_label = "Batch Collection Toggle States"
    bl_idname = "ptdblnpopc.batchcoll_toggle"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    action: bpy.props.StringProperty(default="disable", options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        act = getattr(properties, "action")
        if act == "disable":
            return "disable edits"
        return "enable edits"

    def disable_items(self, coll):
        for item in coll:
            item.active = False

    def enable_items(self, coll):
        for item in coll:
            item.active = True

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        b_ops = pool.batchtoggle_ops
        act = self.action
        try:
            if act == "disable":
                if b_ops.path:
                    self.disable_items(pool.pathloc)
                    self.disable_items(pool.pathrot)
                if pool.use_profile:
                    if b_ops.prof:
                        self.disable_items(pool.profloc)
                        self.disable_items(pool.profrot)
                        self.disable_items(pool.blnd)
                    if b_ops.curve:
                        self.disable_items(pool.culoc)
                        self.disable_items(pool.curot)
                        self.disable_items(pool.cudep)
                        self.disable_items(pool.pnrad)
                elif b_ops.curve:
                    self.disable_items(pool.pnrad)
            else:
                if b_ops.path:
                    self.enable_items(pool.pathloc)
                    self.enable_items(pool.pathrot)
                if pool.use_profile:
                    if b_ops.prof:
                        self.enable_items(pool.profloc)
                        self.enable_items(pool.profrot)
                        self.enable_items(pool.blnd)
                    if b_ops.curve:
                        self.enable_items(pool.culoc)
                        self.enable_items(pool.curot)
                        self.enable_items(pool.cudep)
                        self.enable_items(pool.pnrad)
                elif b_ops.curve:
                    self.enable_items(pool.pnrad)
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"batchcoll_toggle: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_batchcoll_update(bpy.types.Operator):
    bl_label = "Update Collection Items"
    bl_idname = "ptdblnpopc.batchcoll_update"
    bl_description = "basic update (only edits with all items in one group)"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def update_nodes(self, coll, oldnodes, newnodes):
        for item in coll:
            if item.nprams.itm == oldnodes:
                item.nprams.itm = newnodes

    def update_edits(self, coll, oldnodes, newnodes, oldpoints, newpoints):
        for item in coll:
            if item.nprams.itm == oldnodes:
                item.nprams.itm = newnodes
            if item.iprams.itm == oldpoints:
                item.iprams.itm = newpoints

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        b_ops = pool.batchupdate_ops
        b_eds = b_ops.edits
        try:
            ndn = pool.path.pathed.npts
            ndo = b_ops.nodes
            if b_eds.path:
                self.update_nodes(pool.pathloc, ndo, ndn)
                self.update_nodes(pool.pathrot, ndo, ndn)
            if pool.use_profile:
                ptn = pool.prof.profed.npts
                pto = b_ops.points
                if b_eds.prof:
                    self.update_edits(pool.profloc, ndo, ndn, pto, ptn)
                    self.update_edits(pool.profrot, ndo, ndn, pto, ptn)
                    self.update_edits(pool.blnd, ndo, ndn, pto, ptn)
                if b_eds.curve:
                    cuprof = pool.curve.direction == "profile"
                    nco = ndo if cuprof else pto
                    npo = pto if cuprof else ndo
                    self.update_edits(pool.culoc, nco, pool.ncus, npo, pool.cpts)
                    self.update_edits(pool.curot, nco, pool.ncus, npo, pool.cpts)
                    self.update_nodes(pool.cudep, nco, pool.ncus)
                    self.update_edits(pool.pnrad, nco, pool.ncus, npo, pool.cpts)
            elif b_eds.curve:
                self.update_nodes(pool.pnrad, ndo, pool.cpts)
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"batchcoll_update: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_update_replace(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "ptdblnpopc.update_replace"
    bl_description = "pop setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="none", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        if self.caller == "prof":
            for item in pool.blnd:
                item.active = False
        try:
            ModPOPC.scene_update_newset(scene, True, False)
            context.view_layer.update()
        except Exception as my_err:
            pool.update_ok = True
            print(f"update_replace: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_setup_provider(bpy.types.Operator):
    bl_label = "Provider Update"
    bl_idname = "ptdblnpopc.setup_provider"
    bl_description = "pop provider setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="path", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        caller = self.caller
        if caller == "prof":
            ndims = 2
            pg = pool.prof
            for item in pool.blnd:
                item.active = False
            pg_edit = pg.profed
        else:
            ndims = 3
            pg = pool.path
            pg_edit = pg.pathed
        provider = pg.provider
        pg_edit.upv.clear()
        try:
            if provider != "custom":
                ModPOPC.scene_update_newset(scene, True, False)
                pool.update_ok = True
                return {"FINISHED"}
            ModFNOP.validate_scene_object(scene, pg.user_ob)
            ob = pg.user_ob
            if not ob:
                raise Exception("invalid object!")
            verts = ModFNOP.user_mesh_verts(ob.data)
            for v in verts:
                i = pg_edit.upv.add()
                i.vert = v
            for i in range(ndims):
                v = round(ob.dimensions[i], 5)
                pg_edit.user_dim[i] = v
                pg_edit.cust_dim[i] = v
            pg.user_ob = None
            ModPOPC.scene_update_newset(scene, True, False)
        except Exception as my_err:
            pg.clean = False
            pg.user_ob = None
            pool.update_ok = True
            print(f"{caller} setup_provider: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_setup_blnd_provider(bpy.types.Operator):
    bl_label = "Provider Update"
    bl_idname = "ptdblnpopc.setup_blnd_provider"
    bl_description = "blend provider setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        npts = pool.prof.profed.npts
        item = pool.blnd[pool.blnd_idx]
        i_ed = item.blnded
        i_ed.upv.clear()
        provider = item.provider
        try:
            if provider != "custom":
                if (provider == "polygon") and (npts < 6):
                    raise Exception("vertex count mismatch!")
                i_ed.npts = npts
                if item.active:
                    ModPOPC.scene_update(scene)
                pool.update_ok = True
                return {"FINISHED"}
            ModFNOP.validate_scene_object(scene, item.user_ob)
            ob = item.user_ob
            if not ob:
                raise Exception("invalid object!")
            verts = ModFNOP.user_mesh_verts(ob.data)
            if len(verts) != npts:
                raise Exception("vertex count mismatch!")
            for v in verts:
                i = i_ed.upv.add()
                i.vert = v
            for i in range(2):
                v = round(ob.dimensions[i], 5)
                i_ed.user_dim[i] = v
                i_ed.cust_dim[i] = v
            i_ed.npts = npts
            item.user_ob = None
            if item.active:
                ModPOPC.scene_update(scene)
        except Exception as my_err:
            item.user_ob = None
            item.active = False
            pool.update_ok = True
            print(f"blend provider setup: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_pop_noiz(bpy.types.Operator):
    bl_label = "Noise Locations"
    bl_idname = "ptdblnpopc.pop_noiz"
    bl_description = "noise locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    ampli: bpy.props.FloatProperty(
        name="amplitude", description="noise amount", default=0, min=0
    )
    nseed: bpy.props.IntProperty(
        name="seed", description="random seed", default=0, min=0
    )
    vfac: bpy.props.FloatVectorProperty(
        name="axis", description="axis factor", size=3, default=(0, 0, 0), min=0, max=1
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.noiz.active

    def invoke(self, context, event):
        noiz = context.scene.ptdblnpopc_pool.noiz
        self.ampli = noiz.ampli
        self.nseed = noiz.nseed
        self.vfac = noiz.vfac
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        noiz = pool.noiz
        noiz.ampli = self.ampli
        noiz.nseed = self.nseed
        noiz.vfac = self.vfac
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_noiz: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Amplitude", "Seed", "Influence")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "ampli", text="")
        row = sc.row(align=True)
        row.prop(self, "nseed", text="")
        row = sc.row(align=True)
        row.prop(self, "vfac", text="")


# ---- BLEND COLLECTION OPERATORS


class PTDBLNPOPC_OT_blnd_add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "ptdblnpopc.blnd_add"
    bl_description = "new edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    clone: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        clone = getattr(properties, "clone")
        if clone:
            return "new edit - profile clone"
        return "new edit"

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            item = pool.blnd.add()
            item.active = False
            if self.clone:
                prof = pool.prof
                d = prof.profed.to_dct(exclude={"upv"})
                for key in d.keys():
                    setattr(item.blnded, key, d[key])
                item.provider = prof.provider
                if item.provider == "custom":
                    for v in prof.profed.upv:
                        i = item.blnded.upv.add()
                        i.vert = v.vert
            else:
                item.blnded.npts = pool.prof.profed.npts
            item.nprams.npts = pool.path.pathed.npts
            item.iprams.npts = pool.prof.profed.npts
            pool.blnd_idx = len(pool.blnd) - 1
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_blnd_enable(bpy.types.Operator):
    bl_label = "Enable"
    bl_idname = "ptdblnpopc.blnd_enable"
    bl_description = "enable/disable edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        npts = pool.prof.profed.npts
        try:
            if self.doall:
                if self.flagall:
                    for item in pool.blnd:
                        if item.provider in {"line", "wave", "arc", "ellipse"}:
                            item.active = True
                        elif item.provider == "polygon":
                            item.active = npts > 5
                        else:
                            item.active = len(item.blnded.upv) == npts
                else:
                    for item in pool.blnd:
                        item.active = False
            else:
                item = pool.blnd[pool.blnd_idx]
                if item.active:
                    item.active = False
                else:
                    if item.provider in {"line", "wave", "arc", "ellipse"}:
                        item.active = True
                    elif item.provider == "polygon":
                        item.active = npts > 5
                        if not item.active:
                            raise Exception("vertex count mismatch!")
                    else:
                        item.active = len(item.blnded.upv) == npts
                        if not item.active:
                            raise Exception("vertex count mismatch!")
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_blnd_remove(bpy.types.Operator):
    bl_label = "Remove"
    bl_idname = "ptdblnpopc.blnd_remove"
    bl_description = "remove edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            if self.doall:
                pool.blnd.clear()
                pool.blnd_idx = -1
            else:
                idx = pool.blnd_idx
                pool.blnd.remove(idx)
                pool.blnd_idx = min(max(0, idx - 1), len(pool.blnd) - 1)
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_blnd_move(bpy.types.Operator):
    bl_label = "Stack"
    bl_idname = "ptdblnpopc.blnd_move"
    bl_description = "change stack order"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        idx = pool.blnd_idx
        try:
            if self.move_down:
                if idx < len(pool.blnd) - 1:
                    pool.blnd.move(idx, idx + 1)
                    pool.blnd_idx += 1
            elif idx > 0:
                pool.blnd.move(idx, idx - 1)
                pool.blnd_idx -= 1
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- CURVE SETTINGS OPERATOR


class PTDBLNPOPC_OT_curve_setts(bpy.types.Operator):
    bl_label = "Curve Settings"
    bl_idname = "ptdblnpopc.curve_setts"
    bl_description = "curve settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="cyclic", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        cu = pool.curve
        caller = self.caller
        try:
            oblst = pool.setcoll.objects[:]
            cyclic = cu.cyclic
            fillcaps = False if cyclic else cu.fillcaps
            endpoints = False if cyclic else cu.endpoints
            if caller == "cyclic":
                if cu.spline == "NURBS":
                    for ob in oblst:
                        ob.data.use_fill_caps = fillcaps
                        cl = ob.data.splines[0]
                        cl.use_cyclic_u = cyclic
                        cl.use_endpoint_u = endpoints
                else:
                    for ob in oblst:
                        ob.data.use_fill_caps = fillcaps
                        cl = ob.data.splines[0]
                        cl.use_cyclic_u = cyclic
            elif caller == "endpoints" and cu.spline == "NURBS":
                for ob in oblst:
                    cl = ob.data.splines[0]
                    cl.use_endpoint_u = endpoints
            elif caller == "fillcaps":
                for ob in oblst:
                    ob.data.use_fill_caps = fillcaps
            elif caller == "ures":
                ures = cu.ures
                for ob in oblst:
                    ob.data.resolution_u = ures
            elif caller == "bevres":
                bevres = cu.bevres
                for ob in oblst:
                    ob.data.bevel_resolution = bevres
            elif caller == "smooth":
                smooth = cu.smooth
                for ob in oblst:
                    ob.data.twist_smooth = smooth
            else:
                ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"curve_setts: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- PATHLOC/PATHROT/PROFLOC/PROFROT/CULOC/CUROT/CUDEP/PNRAD COLLECTIONS OPERATORS


class PTDBLNPOPC_OT_citem_add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "ptdblnpopc.citem_add"
    bl_description = "new edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            item = coll.add()
            item.active = False
            if cname in {"pathloc", "pathrot"}:
                item.nprams.npts = pool.path.pathed.npts
            elif pool.use_profile:
                if cname in {"profloc", "profrot"}:
                    item.nprams.npts = pool.path.pathed.npts
                    item.iprams.npts = pool.prof.profed.npts
                else:
                    item.nprams.npts = pool.ncus
                    if cname in {"culoc", "curot", "pnrad"}:
                        item.iprams.npts = pool.cpts
            elif cname == "pnrad":
                item.nprams.npts = pool.cpts
            idx = len(coll) - 1
            setattr(pool, iname, idx)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_citem_copy(bpy.types.Operator):
    bl_label = "Copy"
    bl_idname = "ptdblnpopc.citem_copy"
    bl_description = "new edit - copy from active"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def dct_to_pg(self, d, item):
        if "nprams" in d.keys():
            npar = d.pop("nprams")
            for key in npar.keys():
                setattr(item.nprams, key, npar[key])
        if "iprams" in d.keys():
            ipar = d.pop("iprams")
            for key in ipar.keys():
                setattr(item.iprams, key, ipar[key])
        for key in d.keys():
            setattr(item, key, d[key])

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            idx = getattr(pool, iname)
            target = coll[idx]
            d = target.to_dct()
            item = coll.add()
            self.dct_to_pg(d, item)
            idx = len(coll) - 1
            setattr(pool, iname, idx)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_citem_enable(bpy.types.Operator):
    bl_label = "Enable"
    bl_idname = "ptdblnpopc.citem_enable"
    bl_description = "enable/disable edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            if self.doall:
                for item in coll:
                    item.active = self.flagall
            else:
                idx = getattr(pool, iname)
                item = coll[idx]
                item.active = not item.active
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_citem_remove(bpy.types.Operator):
    bl_label = "Remove"
    bl_idname = "ptdblnpopc.citem_remove"
    bl_description = "remove edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            if self.doall:
                coll.clear()
                setattr(pool, iname, -1)
            else:
                idx = getattr(pool, iname)
                coll.remove(idx)
                idx = min(max(0, idx - 1), len(coll) - 1)
                setattr(pool, iname, idx)
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_citem_move(bpy.types.Operator):
    bl_label = "Stack"
    bl_idname = "ptdblnpopc.citem_move"
    bl_description = "change stack order"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            idx = getattr(pool, iname)
            if self.move_down:
                if idx < len(coll) - 1:
                    newid = idx + 1
                    coll.move(idx, newid)
                    setattr(pool, iname, newid)
            elif idx > 0:
                newid = idx - 1
                coll.move(idx, newid)
                setattr(pool, iname, newid)
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- FILE I/O OPERATORS


class PTDBLNPOPC_OT_write_setts(bpy.types.Operator, ExportHelper):
    bl_label = "Save Settings"
    bl_idname = "ptdblnpopc.write_setts"
    bl_description = "save current settings to .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filename_ext = ".json"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        self.filepath = pool.setcoll.name
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            fpath = self.filepath
            path = os.path.dirname(fpath)
            os.makedirs(path, exist_ok=True)
            pool.setcoll_name = pool.setcoll.name
            data = ModFNOP.setts_to_json(pool)
            with open(fpath, mode="w") as f:
                json.dump(data, f, indent=2)
        except Exception as my_err:
            pool.update_ok = True
            print(f"write_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_read_setts(bpy.types.Operator, ImportHelper):
    bl_label = "Load Settings"
    bl_idname = "ptdblnpopc.read_setts"
    bl_description = "update set - load settings from .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filter_glob: bpy.props.StringProperty(default="*.json;*.txt", options={"HIDDEN"})

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            fpath = self.filepath
            if not os.path.isfile(fpath):
                raise Exception("invalid file path")
            with open(fpath, mode="r") as f:
                data = json.load(f)
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            replace_set = pool.replace_set
            pool.props_unset()
            ModFNOP.json_to_setts(data, pool)
            ModPOPC.scene_update_newset(scene, replace_set, True)
            context.view_layer.update()
        except Exception as my_err:
            pool.update_ok = True
            print(f"read_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        layout = self.layout
        if bool(pool.setcoll) and pool.replace_set and pool.show_warn:
            row = layout.row(align=True)
            row.label(text="WARNING! This will discard all changes")


# ---- ANIMATION OPERATORS


class PTDBLNPOPC_OT_animorph_setup(bpy.types.Operator):
    bl_label = "Exit Animation Mode?"
    bl_idname = "ptdblnpopc.animorph_setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    exiting: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        aniout = getattr(properties, "exiting")
        if aniout:
            return "remove existing animations"
        return "enter animation mode"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        if self.exiting and pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            oblst = pool.setcoll.objects[:]
            for ob in oblst:
                if ob.data.animation_data:
                    ob.data.animation_data_clear()
            if pool.trax:
                print("---- popcurve animode: delete trash")
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            pool.trax.clear()
            pool.trax_idx = -1
            if self.exiting:
                pool.animorph = False
            else:
                for ob in oblst:
                    ob.data.animation_data_create()
                pool.animorph = True
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"animorph_setup: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_anicycmirend(bpy.types.Operator):
    bl_label = "Set Loop Range"
    bl_idname = "ptdblnpopc.anicycmirend"
    bl_description = "set frame range in the Timeline"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            start = pool.ani_kf_start
            step = pool.ani_kf_step
            loop = pool.ani_kf_loop
            scene.frame_start = start
            scene.frame_end = (start - 1) + (loop - 1) * step
        except Exception as my_err:
            pool.update_ok = True
            print(f"anicycmirend: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_anicalc(bpy.types.Operator):
    bl_label = "Anicalc"
    bl_idname = "ptdblnpopc.anicalc"
    bl_description = "animation calculations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    current: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        update = getattr(properties, "current")
        if update:
            return "get values from animode"
        return "animation calculations"

    def invoke(self, context, event):
        if self.current:
            pool = context.scene.ptdblnpopc_pool
            beg = pool.ani_kf_start
            stp = pool.ani_kf_step
            loop = pool.ani_kf_loop
            pool.anicalc.loop = loop
            pool.anicalc.first = beg
            pool.anicalc.last = beg + stp * (loop - 1)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        clc = scene.ptdblnpopc_pool.anicalc
        caller = clc.calc_type
        try:
            if caller == "loop":
                val = clc.items // clc.offset + 1
                clc.info = str(val)
            elif caller == "offsets":
                offsets = sorted(ModFNOP.anicalc_factors(clc.items))[:-1]
                clc.info = ", ".join(str(i) for i in offsets)
            elif caller == "cycles":
                loop = clc.loop
                if not loop % 2:
                    self.report({"INFO"}, "loop should be odd, positive integer!")
                hlp = loop // 2
                cycles = sorted(ModFNOP.anicalc_factors(hlp))
                clc.info = ", ".join(str(i) for i in cycles)
            else:
                exp = int(clc.exp)
                clc.last = max(clc.last, clc.first + 2)
                clc.fra = min(max(clc.first + 1, clc.fra), clc.last - 1)
                ratio = ModFNOP.anicalc_delay(clc.fra, clc.first, clc.last, exp)
                clc.info = str(ratio)
        except Exception as my_err:
            clc.info = ""
            print(f"anicalc: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


# ---- NLA-TRACK COLLECTION OPERATORS


class PTDBLNPOPC_OT_track_edit(bpy.types.Operator):
    bl_label = "Track Settings"
    bl_idname = "ptdblnpopc.track_edit"
    bl_description = "track settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def track_update(self, context):
        if self.update_pause:
            return None
        reps = 1 if self.st_warp else self.s_rep
        fval = (self.sa_end - self.sa_beg) * self.s_sca * reps
        self.s_end = self.s_beg + int(fval)
        if self.st_ctrl:
            self.st_fra = self.st_fra
        if not self.s_blauto:
            self.s_blin = self.s_blin

    def track_sa_beg_get(self):
        return self.get("sa_beg", 1)

    def track_sa_beg_set(self, value):
        val = min(max(self.ac_beg, value), self.ac_end - 1)
        if not self.update_pause and (val >= self.sa_end):
            val = self.sa_end - 1
        self["sa_beg"] = val

    def track_sa_end_get(self):
        return self.get("sa_end", 2)

    def track_sa_end_set(self, value):
        val = min(max(self.ac_beg + 1, value), self.ac_end)
        if not self.update_pause and (val <= self.sa_beg):
            val = self.sa_beg + 1
        self["sa_end"] = val

    def track_s_blin_get(self):
        return self.get("s_blin", 0)

    def track_s_blin_set(self, value):
        frms = self.s_end - self.s_beg
        self["s_blin"] = min(max(0, value), frms)

    def track_s_blin_update(self, context):
        self.s_blout = self.get("s_blout", 0)

    def track_s_blout_get(self):
        return self.get("s_blout", 0)

    def track_s_blout_set(self, value):
        frms = (self.s_end - self.s_beg) - self.s_blin
        self["s_blout"] = min(max(0, value), frms)

    def track_st_ctrl_update(self, context):
        if self.st_ctrl:
            self.st_fra = self.get("st_fra", 1)

    def track_st_fra_get(self):
        return self.get("st_fra", 1)

    def track_st_fra_set(self, value):
        self["st_fra"] = min(max(self.sa_beg + 1, value), self.sa_end - 1)

    update_pause: bpy.props.BoolProperty(default=True)
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    s_sca: bpy.props.FloatProperty(
        name="scale",
        description="time scaling factor",
        default=1,
        min=0.001,
        max=100,
        update=track_update,
    )
    s_rep: bpy.props.FloatProperty(
        name="repeat",
        description=(
            "number of times to repeat selected range, "
            "effective when timewarp is disabled"
        ),
        default=1,
        min=1,
        max=100,
        update=track_update,
    )
    sa_beg: bpy.props.IntProperty(
        name="first",
        description="first frame from action to use",
        default=1,
        get=track_sa_beg_get,
        set=track_sa_beg_set,
        update=track_update,
    )
    sa_end: bpy.props.IntProperty(
        name="last",
        description="last frame from action to use",
        default=2,
        get=track_sa_end_get,
        set=track_sa_end_set,
        update=track_update,
    )
    s_beg: bpy.props.IntProperty(
        name="start",
        description="strip start frame",
        default=1,
        min=1,
        update=track_update,
    )
    s_end: bpy.props.IntProperty(default=2)
    s_blend: bpy.props.EnumProperty(
        name="blend type",
        description="method of combining strip with accumulated result",
        items=(
            ("REPLACE", "replace", "replace"),
            ("COMBINE", "combine", "combine"),
            ("ADD", "add", "add"),
            ("SUBTRACT", "subtract", "subtract"),
            ("MULTIPLY", "multiply", "multiply"),
        ),
        default="REPLACE",
    )
    s_blin: bpy.props.IntProperty(
        name="blend in",
        description="blend-in frames",
        default=0,
        get=track_s_blin_get,
        set=track_s_blin_set,
        update=track_s_blin_update,
    )
    s_blout: bpy.props.IntProperty(
        name="blend out",
        description="blend-out frames",
        default=0,
        get=track_s_blout_get,
        set=track_s_blout_set,
    )
    s_blauto: bpy.props.BoolProperty(
        name="auto blend",
        description="use auto-blend",
        default=False,
    )
    s_xpl: bpy.props.EnumProperty(
        name="extrapolation",
        description="action to take for gaps past the strip extents",
        items=(
            ("NOTHING", "nothing", "nothing"),
            ("HOLD", "hold", "hold"),
            ("HOLD_FORWARD", "hold forward", "hold forward"),
        ),
        default="HOLD",
    )
    s_bak: bpy.props.BoolProperty(
        name="reverse",
        description="play in reverse, effective when timewarp is disabled",
        default=False,
    )
    st_warp: bpy.props.BoolProperty(
        name="timewarp",
        description="use time function curves",
        default=False,
        update=track_update,
    )
    st_curve: bpy.props.EnumProperty(
        name="timewarp curve",
        description="timewarp function",
        items=(
            ("12", "sine", "sine"),
            ("9", "quad", "quadratic"),
            ("6", "cube", "cubic"),
            ("10", "quart", "quartic"),
            ("11", "quint", "quintic"),
            ("8", "expo", "dramatic"),
        ),
        default="12",
    )
    st_ease: bpy.props.EnumProperty(
        name="timewarp easing",
        description="timewarp interpolation easing",
        items=(
            ("0", "auto", "automatic"),
            ("1", "in", "ease in"),
            ("2", "out", "ease out"),
            ("3", "in-out", "ease in and out"),
        ),
        default="0",
    )
    st_ctrl: bpy.props.BoolProperty(
        name="control",
        description="use timewarp control frame for deceleration",
        default=False,
        update=track_st_ctrl_update,
    )
    st_fra: bpy.props.IntProperty(
        name="timewarp control frame",
        description="timewarp control frame",
        default=1,
        get=track_st_fra_get,
        set=track_st_fra_set,
    )

    def copy_from_pg(self, item):
        d = self.as_keywords(ignore=("update_pause",))
        for key in d.keys():
            d[key] = getattr(item, key)
            setattr(self, key, d[key])

    def copy_to_pg(self, item):
        d = self.as_keywords(ignore=("update_pause", "ac_beg", "ac_end"))
        for key in d.keys():
            d[key] = getattr(self, key)
            setattr(item, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.trax[pool.trax_idx]
        self.update_pause = True
        self.copy_from_pg(item)
        self.update_pause = False
        self.track_update(context)
        return self.execute(context)

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.trax[pool.trax_idx]
        self.copy_to_pg(item)
        try:
            oblst = pool.setcoll.objects[:]
            blauto = self.s_blauto
            blin = 0 if blauto else self.s_blin
            blout = 0 if blauto else self.s_blout
            time_warp = self.st_warp
            if time_warp:
                reps = 1
                sbak = False
                w_kicu = int(self.st_curve)
                w_keas = int(self.st_ease)
                ctr_con = w_kicu in {6, 9, 10, 11} and w_keas == 2
                if self.st_ctrl and ctr_con:
                    fpts = 3
                    fvls = (
                        self.s_beg,
                        self.sa_beg,
                        self.s_beg + self.st_fra - self.sa_beg,
                        self.st_fra,
                        self.s_end,
                        self.sa_end,
                    )
                    klerps = (1, w_kicu, 1)
                    keases = (0, w_keas, 0)
                else:
                    fpts = 2
                    fvls = (self.s_beg, self.sa_beg, self.s_end, self.sa_end)
                    klerps = (w_kicu, 1)
                    keases = (w_keas, 0)
            else:
                reps = self.s_rep
                sbak = self.s_bak
            for ob, idn in zip(oblst, item.idns):
                tsn = idn.name
                strip = ob.data.animation_data.nla_tracks[tsn].strips[tsn]
                strip.scale = self.s_sca
                strip.repeat = reps
                strip.action_frame_start = self.sa_beg
                strip.action_frame_end = self.sa_end
                strip.frame_start = self.s_beg
                strip.frame_end = self.s_end
                strip.blend_type = self.s_blend
                strip.use_auto_blend = blauto
                strip.blend_in = blin
                strip.blend_out = blout
                strip.extrapolation = self.s_xpl
                strip.use_reverse = sbak
                strip.use_animated_time = time_warp
                if time_warp:
                    ModFNOP.strip_time_fcurve_reset(strip, fpts, fvls, klerps, keases)
                else:
                    try:
                        stfc = strip.fcurves[0]
                        stfc.keyframe_points.clear()
                    except:
                        pass
                    strip.strip_time = 0.0
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        row = col.row()
        row.label(text="Action Range")
        row = col.row()
        row.label(text="Start Frame")
        col = s.column(align=True)
        row = col.row(align=True)
        row.prop(self, "sa_beg", text="")
        row.prop(self, "sa_end", text="")
        row = col.row(align=True)
        row.prop(self, "s_beg", text="")
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        names = ("Blend Type", "Blend Time", "Extrapolation")
        for n in names:
            row = col.row()
            row.label(text=n)
        col = s.column(align=True)
        row = col.row(align=True)
        row.prop(self, "s_blend", text="")
        row.prop(self, "s_blauto", toggle=True)
        row = col.row(align=True)
        row.enabled = not self.s_blauto
        row.prop(self, "s_blin", text="")
        row.prop(self, "s_blout", text="")
        row = col.row(align=True)
        row.prop(self, "s_xpl", text="")
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        names = ("Time Scale", "Playback", "Strip Time", "Curve", "Ctrl Frame")
        for n in names:
            row = col.row()
            row.label(text=n)
        accel = self.st_warp
        col = s.column(align=True)
        row = col.row(align=True)
        row.prop(self, "s_sca", text="")
        row = col.row(align=True)
        row.enabled = not accel
        row.prop(self, "s_rep", text="")
        row.prop(self, "s_bak", toggle=True)
        row = col.row(align=True)
        row.prop(self, "st_warp", toggle=True)
        row = col.row(align=True)
        row.enabled = accel
        row.prop(self, "st_curve", text="")
        row.prop(self, "st_ease", text="")
        row = col.row(align=True)
        ctr_con = self.st_curve in {"6", "9", "10", "11"} and self.st_ease == "2"
        row.enabled = accel and ctr_con
        c = row.column(align=True)
        c.prop(self, "st_ctrl", toggle=True)
        c = row.column(align=True)
        c.enabled = self.st_ctrl
        c.prop(self, "st_fra", text="")


class PTDBLNPOPC_OT_track_enable(bpy.types.Operator):
    bl_label = "Enable"
    bl_idname = "ptdblnpopc.track_enable"
    bl_description = "mute/unmute tracks"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            oblst = pool.setcoll.objects[:]
            if self.doall:
                boo_mute = not self.flagall
                for ob in oblst:
                    for track in ob.data.animation_data.nla_tracks:
                        track.mute = boo_mute
                for item in pool.trax:
                    item.active = not boo_mute
            else:
                item = pool.trax[pool.trax_idx]
                boo_mute = item.active
                for ob, idn in zip(oblst, item.idns):
                    ob.data.animation_data.nla_tracks[idn.name].mute = boo_mute
                item.active = not boo_mute
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_track_remove(bpy.types.Operator):
    bl_label = "Remove"
    bl_idname = "ptdblnpopc.track_remove"
    bl_description = "remove tracks"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            oblst = pool.setcoll.objects[:]
            if self.doall:
                for ob in oblst:
                    nt = [t for t in ob.data.animation_data.nla_tracks]
                    for t in nt:
                        ob.data.animation_data.nla_tracks.remove(t)
                pool.trax.clear()
                pool.trax_idx = -1
            else:
                idx = pool.trax_idx
                item = pool.trax[idx]
                for ob, idn in zip(oblst, item.idns):
                    t = ob.data.animation_data.nla_tracks.get(idn.name)
                    if t:
                        ob.data.animation_data.nla_tracks.remove(t)
                pool.trax.remove(idx)
                pool.trax_idx = min(max(0, idx - 1), len(pool.trax) - 1)
            print("---- popcurve track_remove: delete trash")
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPC_OT_track_copy(bpy.types.Operator):
    bl_label = "Copy"
    bl_idname = "ptdblnpopc.track_copy"
    bl_description = "new track - copy selected"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            oblst = pool.setcoll.objects[:]
            target = pool.trax[pool.trax_idx]
            idnlst = [i.name for i in target.idns]
            d = target.to_dct()
            source = pool.trax.add()
            for key in d.keys():
                setattr(source, key, d[key])
            source.name = f"{source.name}_copy"
            blauto = source.s_blauto
            blin = 0 if blauto else source.s_blin
            blout = 0 if blauto else source.s_blout
            time_warp = source.st_warp
            if time_warp:
                reps = 1
                sbak = False
                w_kicu = int(source.st_curve)
                w_keas = int(source.st_ease)
                ctr_con = w_kicu in {6, 9, 10, 11} and w_keas == 2
                if source.st_ctrl and ctr_con:
                    fpts = 3
                    fvls = (
                        source.s_beg,
                        source.sa_beg,
                        source.s_beg + source.st_fra - source.sa_beg,
                        source.st_fra,
                        source.s_end,
                        source.sa_end,
                    )
                    klerps = (1, w_kicu, 1)
                    keases = (0, w_keas, 0)
                else:
                    fpts = 2
                    fvls = (source.s_beg, source.sa_beg, source.s_end, source.sa_end)
                    klerps = (w_kicu, 1)
                    keases = (w_keas, 0)
            else:
                reps = source.s_rep
                sbak = source.s_bak
            for ob, actname in zip(oblst, idnlst):
                act = bpy.data.actions.get(actname)
                if not act:
                    print(f"{ob.name} - null action reference!")
                    continue
                action = act.copy()
                name = action.name
                item = source.idns.add()
                item.name = name
                track = ob.data.animation_data.nla_tracks.new()
                track.name = name
                track.mute = not source.active
                start = int(action.frame_range[0])
                strip = track.strips.new(name, start, action)
                strip.scale = source.s_sca
                strip.repeat = reps
                strip.action_frame_start = source.sa_beg
                strip.action_frame_end = source.sa_end
                strip.frame_start = source.s_beg
                strip.frame_end = source.s_end
                strip.blend_type = source.s_blend
                strip.use_auto_blend = blauto
                strip.blend_in = blin
                strip.blend_out = blout
                strip.extrapolation = source.s_xpl
                strip.use_reverse = sbak
                strip.use_animated_time = time_warp
                if time_warp:
                    ModFNOP.strip_time_fcurve_reset(strip, fpts, fvls, klerps, keases)
            idx = len(pool.trax) - 1
            pool.trax.move(idx, 0)
            pool.trax_idx = 0
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- ANIMATION ACTION OPERATOR


class PTDBLNPOPC_OT_anim_action(bpy.types.Operator):
    bl_label = "Animation"
    bl_idname = "ptdblnpopc.anim_action"
    bl_description = "new track - compile animation action"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        try:
            oblst = pool.setcoll.objects[:]
        except Exception as my_err:
            pool.update_ok = True
            print(f"ani_action (oblst): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ------------------ Action evaluation -------------------#

        try:
            act_loc = pool.data_anim_state_eval()
            act_dep = pool.deps_anim_state_eval()
            act_rad = pool.rads_anim_state_eval()
            if not (act_loc or act_dep or act_rad):
                raise Exception("no animation values!")
        except Exception as my_err:
            pool.update_ok = True
            print(f"ani_action (acteval): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ----------------- Interpolation Lists ------------------#

        use_profile = pool.use_profile
        loop = pool.ani_kf_loop
        try:
            if act_dep:
                cudep_d = ModFNOP.aniact_edvals_dict_onedim(pool.cudep, loop, False)
            if act_rad:
                if use_profile:
                    pnrad_d = ModFNOP.aniact_edvals_dict_twodim(pool.pnrad, loop)
                else:
                    pnrad_d = ModFNOP.aniact_edvals_dict_onedim(pool.pnrad, loop, True)
            if act_loc:
                path = pool.path
                path_flag = path.anim_state()
                if path_flag:
                    path_d = ModFNOP.aniact_path_edit_dict(path, loop)
                pathloc_d = ModFNOP.aniact_edvals_dict_onedim(pool.pathloc, loop, False)
                pathrot_d = ModFNOP.aniact_edrots_dict_onedim(pool.pathrot, loop)
                noiz = pool.noiz
                if noiz.active:
                    nsd = None if (noiz.anim_state() and noiz.ani_seed) else noiz.nseed
                    noiz_d = {
                        "seed": nsd,
                        "ampli": ModFNOP.aniact_noiz_list(noiz, loop),
                    }
                if use_profile:
                    prof = pool.prof
                    prof_flag = prof.anim_state()
                    if prof_flag:
                        prof_d = ModFNOP.aniact_prof_edit_dict(prof, loop)
                    blnd_d = ModFNOP.aniact_blendvals_dict(pool.blnd, loop)
                    profloc_d = ModFNOP.aniact_edvals_dict_twodim(pool.profloc, loop)
                    profrot_d = ModFNOP.aniact_edrots_dict_twodim(pool.profrot, loop)
                    culoc_d = ModFNOP.aniact_edvals_dict_twodim(pool.culoc, loop)
                    curot_d = ModFNOP.aniact_edrots_dict_twodim(pool.curot, loop)
        except Exception as my_err:
            pool.update_ok = True
            print(f"ani_action (lrplst): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ------------------- Animation Loop ---------------------#

        ncus = pool.ncus
        cpts = pool.cpts
        sindz = pool.rngs.sindz_get()
        sindz_on = use_profile and pool.rngs.active
        live_curves = len(sindz) if sindz_on else ncus
        kloc = [[] for _ in range(live_curves)]
        kdep = []
        krad = []
        try:
            pop = ModPOPC.new_pop_instance(pool)
            ModPOPC.pop_update(pop, pool)
            for i in range(loop):
                if act_loc:
                    if path_flag:
                        pop.path_anim_update(*(v[i] for v in path_d.values()))
                    for dct, nids, ams, lid in zip(
                        pathloc_d["dcts"],
                        pathloc_d["nids"],
                        pathloc_d["ams"],
                        pathloc_d["lids"],
                    ):
                        dct["nprams"]["idx"] = nids[i]
                        dct["fac"] = ams[i]
                        pop.pathedloc_anim_data(dct, lid)
                    for dct, bang, angs, ufac, nids, lid in zip(
                        pathrot_d["dcts"],
                        pathrot_d["b_angs"],
                        pathrot_d["angs"],
                        pathrot_d["use_facs"],
                        pathrot_d["nids"],
                        pathrot_d["lids"],
                    ):
                        dct["nprams"]["idx"] = nids[i]
                        pop.pathedrot_anim_data(dct, bang, angs[i], ufac, lid)
                    if use_profile:
                        if prof_flag:
                            pop.prof_anim_update(*(v[i] for v in prof_d.values()))
                        for dct, ids, nids, ams, lid in zip(
                            blnd_d["dcts"],
                            blnd_d["ids"],
                            blnd_d["nids"],
                            blnd_d["ams"],
                            blnd_d["lids"],
                        ):
                            dct["iprams"]["idx"] = ids[i]
                            dct["nprams"]["idx"] = nids[i]
                            dct["fac"] = ams[i]
                            pop.blndedloc_anim_data(dct, lid)
                        for dct, ids, nids, ams, lid in zip(
                            profloc_d["dcts"],
                            profloc_d["ids"],
                            profloc_d["nids"],
                            profloc_d["ams"],
                            profloc_d["lids"],
                        ):
                            dct["iprams"]["idx"] = ids[i]
                            dct["nprams"]["idx"] = nids[i]
                            dct["fac"] = ams[i]
                            pop.profedloc_anim_data(dct, lid)
                        for dct, bang, angs, ufac, ids, nids, lid in zip(
                            profrot_d["dcts"],
                            profrot_d["b_angs"],
                            profrot_d["angs"],
                            profrot_d["use_facs"],
                            profrot_d["ids"],
                            profrot_d["nids"],
                            profrot_d["lids"],
                        ):
                            dct["iprams"]["idx"] = ids[i]
                            dct["nprams"]["idx"] = nids[i]
                            pop.profedrot_anim_data(dct, bang, angs[i], ufac, lid)
                        pop.compile_pop_data()
                        for dct, ids, nids, ams, lid in zip(
                            culoc_d["dcts"],
                            culoc_d["ids"],
                            culoc_d["nids"],
                            culoc_d["ams"],
                            culoc_d["lids"],
                        ):
                            dct["nprams"]["idx"] = nids[i]
                            dct["iprams"]["idx"] = ids[i]
                            dct["fac"] = ams[i]
                            pop.curvedloc_anim_data(dct, lid)
                        for dct, bang, angs, ufac, ids, nids, lid in zip(
                            curot_d["dcts"],
                            curot_d["b_angs"],
                            curot_d["angs"],
                            curot_d["use_facs"],
                            curot_d["ids"],
                            curot_d["nids"],
                            curot_d["lids"],
                        ):
                            dct["iprams"]["idx"] = ids[i]
                            dct["nprams"]["idx"] = nids[i]
                            pop.curvedrot_anim_data(dct, bang, angs[i], ufac, lid)
                    locs = pop.get_pntlocs()
                    if noiz.active:
                        locs = ModPOPC.noiz_locs(
                            locs, noiz.vfac, noiz_d["ampli"][i], noiz_d["seed"]
                        )
                    if sindz_on:
                        locs = [locs[j] for j in range(ncus) if j in sindz]
                    for icu, vlst in enumerate(locs):
                        kloc[icu].append(vlst)
                if act_dep:
                    for dct, nids, ams, lid in zip(
                        cudep_d["dcts"],
                        cudep_d["nids"],
                        cudep_d["ams"],
                        cudep_d["lids"],
                    ):
                        dct["nprams"]["idx"] = nids[i]
                        dct["fac"] = ams[i]
                        pop.cudepth_anim_data(dct, lid)
                    deps = pop.get_bevdeps()
                    if sindz_on:
                        deps = [deps[j] for j in range(ncus) if j in sindz]
                    kdep.append(deps)
                if act_rad:
                    for dct, ids, ams, nids, lid in zip(
                        pnrad_d["dcts"],
                        pnrad_d["ids"],
                        pnrad_d["ams"],
                        pnrad_d["nids"],
                        pnrad_d["lids"],
                    ):
                        dct["iprams"]["idx"] = ids[i]
                        dct["fac"] = ams[i]
                        dct["nprams"]["idx"] = nids[i]
                        pop.curadius_anim_data(dct, lid)
                    rads = pop.get_pntrads()
                    if sindz_on:
                        rads = [rads[j] for j in range(ncus) if j in sindz]
                    krad.append(rads)
        except Exception as my_err:
            pool.update_ok = True
            print(f"ani_action (animloop): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ----------------- Action to NLA Track ------------------#

        a_name = pool.act_name
        k_beg = pool.ani_kf_start
        k_stp = pool.ani_kf_step
        ki_type = int(pool.ani_kf_type)
        kls = [ki_type] * loop
        fls = [k_beg + i * k_stp for i in range(loop)]
        try:
            trk = pool.trax.add()
            pts_pre = "splines[0].points"
            funcname = "aniact_fc_create_bez" if ki_type == 2 else "aniact_fc_create"
            fc_create = getattr(ModFNOP, funcname)
            for i, ob in enumerate(oblst):
                name = f"{ob.data.name}_{a_name}"
                action = bpy.data.actions.new(name)
                if act_loc:
                    vals = kloc[i]
                    for j in range(cpts):
                        dp = f"{pts_pre}[{j}].co"
                        jvals = [v[j] for v in vals]
                        for di in range(3):
                            vls = [v[di] for v in jvals]
                            fc_create(action, dp, di, fls, vls, kls, loop)
                if act_dep:
                    dp = "bevel_depth"
                    vls = [deps[i] for deps in kdep]
                    di = 0
                    fc_create(action, dp, di, fls, vls, kls, loop)
                if act_rad:
                    vals = [rads[i] for rads in krad]
                    for j in range(cpts):
                        dp = f"{pts_pre}[{j}].radius"
                        di = 0
                        vls = [v[j] for v in vals]
                        fc_create(action, dp, di, fls, vls, kls, loop)
                tn = trk.idns.add()
                tn.name = action.name
                ModFNOP.aniact_nla_track_add(ob.data, action)
            k_end = fls[-1]
            trk.ac_beg = k_beg
            trk.ac_end = k_end
            trk.sa_beg = k_beg
            trk.sa_end = k_end
            trk.s_beg = k_beg
            trk.s_end = k_end
            idx = len(pool.trax) - 1
            pool.trax.move(idx, 0)
            pool.trax_idx = 0
        except Exception as my_err:
            pool.update_ok = True
            print(f"ani_action (actnla): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPC_OT_pop_simple_update,
    PTDBLNPOPC_OT_pop_reset,
    PTDBLNPOPC_OT_popcurve_setup,
    PTDBLNPOPC_OT_curange_react,
    PTDBLNPOPC_OT_batchcoll_toggle,
    PTDBLNPOPC_OT_batchcoll_update,
    PTDBLNPOPC_OT_update_replace,
    PTDBLNPOPC_OT_setup_provider,
    PTDBLNPOPC_OT_setup_blnd_provider,
    PTDBLNPOPC_OT_curve_setts,
    PTDBLNPOPC_OT_pop_noiz,
    PTDBLNPOPC_OT_blnd_add,
    PTDBLNPOPC_OT_blnd_enable,
    PTDBLNPOPC_OT_blnd_remove,
    PTDBLNPOPC_OT_blnd_move,
    PTDBLNPOPC_OT_citem_add,
    PTDBLNPOPC_OT_citem_copy,
    PTDBLNPOPC_OT_citem_enable,
    PTDBLNPOPC_OT_citem_remove,
    PTDBLNPOPC_OT_citem_move,
    PTDBLNPOPC_OT_write_setts,
    PTDBLNPOPC_OT_read_setts,
    PTDBLNPOPC_OT_animorph_setup,
    PTDBLNPOPC_OT_anicycmirend,
    PTDBLNPOPC_OT_anicalc,
    PTDBLNPOPC_OT_track_edit,
    PTDBLNPOPC_OT_track_enable,
    PTDBLNPOPC_OT_track_remove,
    PTDBLNPOPC_OT_track_copy,
    PTDBLNPOPC_OT_anim_action,
)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
