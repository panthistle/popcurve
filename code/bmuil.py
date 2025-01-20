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


# ------------------------------------------------------------------------------
#
# ------------------------------- BMUIL ----------------------------------------


# ---- USER LISTS


class PTDBLNPOPC_UL_pathloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_pathrot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_blnd(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_profloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_profrot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_culoc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_curot(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_cudep(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_pnrad(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPC_UL_trax(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


# ---- PANELS


def curveset_ok(pool):
    coll = pool.setcoll
    if not coll:
        return False
    nobs = sum(
        1
        for ob in coll.objects
        if (ob.type == "CURVE" and ob.data.splines[0].type in pool.SPLINE_TYPES)
    )
    if pool.use_profile:
        items = len(pool.rngs.sindz_get()) if pool.rngs.active else pool.ncus
    else:
        items = 1
    return nobs == items


def ed_panels_ok(pool):
    prof_eval = pool.prof.clean if pool.use_profile else True
    return pool.path.clean and prof_eval


def coll_ops_tmpl(bcol, pool, cname, iname, coll_ob, coll_idx, ops_on):
    col = bcol.column(align=True)
    row = col.row(align=True)
    rc = row.column(align=True)
    c_op = rc.operator("ptdblnpopc.citem_add")
    c_op.cname = cname
    c_op.iname = iname
    boo = coll_ob[coll_idx].active if ops_on else False
    rc = row.column(align=True)
    rc.enabled = boo
    c_op = rc.operator("ptdblnpopc.citem_copy")
    c_op.cname = cname
    c_op.iname = iname
    c = col.column(align=True)
    c.enabled = ops_on
    row = c.row(align=True)
    user_list = f"PTDBLNPOPC_UL_{cname}"
    row.template_list(user_list, "", pool, cname, pool, iname, rows=2, maxrows=2)
    row = c.row(align=True)
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopc.citem_enable", text="Disable" if boo else "Enable")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopc.citem_remove", text="Remove")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    col.enabled = coll_idx > 0
    c_op = col.operator("ptdblnpopc.citem_move", icon="TRIA_UP", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = False
    row = c.row(align=True)
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    boo = False
    for i in coll_ob:
        if i.active:
            boo = True
            break
    c_op = col.operator(
        "ptdblnpopc.citem_enable",
        text="Disable All" if boo else "Enable All",
    )
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    c_op.flagall = not boo
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    c_op = col.operator("ptdblnpopc.citem_remove", text="Remove All")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    col = row.column(align=True)
    col.enabled = coll_idx < (len(coll_ob) - 1)
    c_op = col.operator("ptdblnpopc.citem_move", icon="TRIA_DOWN", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = True


def anim_rot_tmpl(c, ob):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "ani_ang", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.ani_ang
    col.prop(ob, "angle", text="")
    row = c.row(align=True)
    row.enabled = ob.ani_ang
    row.prop(ob, "beg", text="")
    row.prop(ob, "end", text="")


def anim_ind_tmpl(c, ob, cap):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True, text=cap)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "offset", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob, "offrnd", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.offrnd
    col.prop(ob, "offrndseed", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    row.prop(ob, "beg", text="")
    row.prop(ob, "stp", text="")


def anim_fac_tmpl(c, ob):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "fac", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob.mirror, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.mirror.active
    col.prop(ob.mirror, "cycles", text="")


def anim_fac_mirror_tmpl(c, flag, afm_ob):
    row = c.row(align=True)
    row.enabled = flag
    col = row.column(align=True)
    col.prop(afm_ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = afm_ob.active
    col.prop(afm_ob, "cycles", text="")


class PTDBLNPOPC_PT_ui:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Cpop"


class PTDBLNPOPC_PT_ui_setup(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Setup"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        setcoll_ok = bool(pool.setcoll)
        edpans_ok = ed_panels_ok(pool)
        layout = self.layout
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = edpans_ok
        rc.operator("ptdblnpopc.pop_reset", text="Load Current").newdef = False
        rc = row.column(align=True)
        rc.operator("ptdblnpopc.pop_reset", text="Load Default").newdef = True
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator("ptdblnpopc.read_setts", text="Load File")
        rc = row.column(align=True)
        rc.enabled = setcoll_ok and edpans_ok and not pool.animorph
        rc.operator("ptdblnpopc.write_setts", text="Save File")
        row = col.row(align=True)
        row.enabled = setcoll_ok
        cap = pool.setcoll.name if setcoll_ok else "none"
        row.prop(pool, "replace_set", text=f'replace  "{cap}"', toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = setcoll_ok and edpans_ok and not pool.animorph
        carr = pool.use_profile
        cap = "Curve Array" if carr else "Single Curve"
        row.operator("ptdblnpopc.popcurve_setup", text=cap).single = carr
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(pool, "show_warn", toggle=True)


class PTDBLNPOPC_PT_ui_curve(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Curve"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        curve = pool.curve
        layout = self.layout
        layout.enabled = curveset_ok(pool) and not pool.animorph
        edpans_ok = ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        col.enabled = edpans_ok
        row = col.row(align=True)
        c = row.column(align=True)
        c.prop(curve, "spline", text="")
        c = row.column(align=True)
        c.enabled = pool.use_profile
        c.prop(curve, "direction", text="")
        col = bcol.column(align=True)
        row = col.row(align=True)
        c = row.column(align=True)
        c.enabled = curve.spline != "POLY"
        c.prop(curve, "ures", text="")
        c = row.column(align=True)
        c.prop(curve, "bevres", text="")
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(curve, "smooth", text="")
        row.prop(curve, "cyclic", toggle=True, text="cyclic")
        row = col.row(align=True)
        row.enabled = not curve.cyclic
        c = row.column(align=True)
        c.enabled = curve.spline == "NURBS"
        c.prop(curve, "endpoints", toggle=True)
        c = row.column(align=True)
        c.prop(curve, "fillcaps", toggle=True)
        col = bcol.column(align=True)
        col.enabled = edpans_ok
        row = col.row(align=True)
        row.prop(curve, "bevdep", text="")
        row.prop(curve, "pntrad", text="")


class PTDBLNPOPC_PT_ui_path(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        set_ok = curveset_ok(pool)
        path = pool.path
        layout = self.layout
        path_rule = pool.prof.clean if pool.use_profile else True
        path_setup = set_ok and path_rule and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_setup
        col = row.column(align=True)
        col.prop(path, "provider", text="")
        col = row.column(align=True)
        provider = path.provider
        if provider == "custom":
            col.prop(path, "user_ob", text="")
        else:
            col.enabled = path.clean
            col.prop(path, f"res_{provider[:3]}", text="")
        path_edit = set_ok and ed_panels_ok(pool)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_edit
        row.operator("ptdblnpopc.path_edit", text="Edit")
        pathed = path.pathed
        if pool.use_profile:
            col = bcol.column(align=True)
            col.enabled = path_edit and not pool.animorph
            row = col.row(align=True)
            row.prop(pathed, "closed", toggle=True)
            path_att = pool.path_att
            col = bcol.column(align=True)
            col.enabled = path_edit
            row = col.row(align=True)
            rc = row.column(align=True)
            rc.prop(path_att, "active", toggle=True)
            rc = row.column(align=True)
            rc.enabled = path_att.active
            rc.prop(path_att, "upfixed", toggle=True)
            row = col.row(align=True)
            row.enabled = path_att.active
            rc = row.column(align=True)
            rc.prop(path_att, "track", text="")
            rc = row.column(align=True)
            rc.enabled = path_att.upfixed
            rc.prop(path_att, "up", text="")
        row = col.row(align=True)
        row.enabled = False
        cap = f"nodes: {pathed.npts}" if path.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPC_PT_ui_path_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        path = pool.path
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        provider = path.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        elif provider == "helix":
            dname = "width"
            dprop = "ani_dim_2d"
            fname = "length"
            fprop = "ani_hel_len"
            fname2 = "factor"
            fprop2 = "ani_hel_fac"
            fname3 = "frequency"
            fprop3 = "ani_hel_stp"
            fname4 = "phase"
            fprop4 = "ani_hel_pha"
        elif provider == "spiral":
            dname = "diameter"
            dprop = "ani_spi_dim"
            fname = "frequency"
            fprop = "ani_spi_revs"
        elif provider == "torus":
            dname = "size"
            dprop = "ani_dim_2d"
            fname = "frequency"
            fprop = "ani_tor_stp"
            fname2 = "phase"
            fprop2 = "ani_tor_pha"
        else:
            dname = "size"
            dprop = "ani_dim_3d" if provider == "custom" else "ani_dim_2d"
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(path, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = path.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(3):
                if path.pathed.user_dim[i]:
                    row.prop(path, dprop, index=i, text="")
        else:
            row.prop(path, dprop, text="")
        anim_fac_mirror_tmpl(c, path.ani_dim, path.ani_dim_mirror)
        if provider in {"line", "wave", "arc", "helix", "spiral", "torus"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(path, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = path.ani_fac
            col.prop(path, fprop, text="")
            anim_fac_mirror_tmpl(c, path.ani_fac, path.ani_fac_mirror)
            if provider in {"wave", "helix", "torus"}:
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(path, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = path.ani_fac2
                col.prop(path, fprop2, text="")
                anim_fac_mirror_tmpl(c, path.ani_fac2, path.ani_fac2_mirror)
                if provider in {"wave", "helix"}:
                    row = c.row(align=True)
                    col = row.column(align=True)
                    col.prop(path, "ani_fac3", toggle=True, text=fname3)
                    col = row.column(align=True)
                    col.enabled = path.ani_fac3
                    col.prop(path, fprop3, text="")
                    anim_fac_mirror_tmpl(c, path.ani_fac3, path.ani_fac3_mirror)
                    if provider == "helix":
                        row = c.row(align=True)
                        col = row.column(align=True)
                        col.prop(path, "ani_fac4", toggle=True, text=fname4)
                        col = row.column(align=True)
                        col.enabled = path.ani_fac4
                        col.prop(path, fprop4, text="")
                        anim_fac_mirror_tmpl(c, path.ani_fac4, path.ani_fac4_mirror)


class PTDBLNPOPC_PT_ui_pathloc(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Path Locations"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.pathloc
        collid = pool.pathloc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "pathloc", "pathloc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.pathloc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_pathloc_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_pathloc"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.pathloc:
            item = pool.pathloc[pool.pathloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_pathrot(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Path Rotations"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.pathrot
        collid = pool.pathrot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "pathrot", "pathrot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            row = col.row(align=True)
            row.enabled = item.active
            row.operator("ptdblnpopc.pathrot_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_pathrot_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_pathrot"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.pathrot:
            item = pool.pathrot[pool.pathrot_idx]
            c.enabled = item.active
            anim_rot_tmpl(c, item.ani_rot)
            row = c.row(align=True)
            row.prop(item.ani_rot, "lerp", text="factors", toggle=True)
            col = c.column(align=True)
            col.enabled = item.active and item.ani_rot.lerp
            anim_ind_tmpl(col, item.ani_nidx, "node id")
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_prof(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Profile"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        set_ok = curveset_ok(pool)
        prof = pool.prof
        layout = self.layout
        prof_setup = set_ok and pool.path.clean and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_setup
        col = row.column(align=True)
        col.prop(prof, "provider", text="")
        col = row.column(align=True)
        provider = prof.provider
        if provider == "custom":
            col.prop(prof, "user_ob", text="")
        else:
            col.enabled = prof.clean
            col.prop(prof, f"res_{provider[:3]}", text="")
        prof_edit = set_ok and ed_panels_ok(pool)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_edit
        row.operator("ptdblnpopc.prof_edit", text="Edit")
        profed = prof.profed
        row = col.row(align=True)
        row.enabled = False
        cap = f"points: {profed.npts}" if prof.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPC_PT_ui_prof_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_prof"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        prof = pool.prof
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        provider = prof.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        else:
            dname = "size"
            dprop = "ani_epc_dim"
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(prof, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = prof.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(2):
                if prof.profed.user_dim[i]:
                    row.prop(prof, dprop, index=i, text="")
        else:
            row.prop(prof, dprop, text="")
        anim_fac_mirror_tmpl(c, prof.ani_dim, prof.ani_dim_mirror)
        if provider in {"line", "wave", "arc"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(prof, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = prof.ani_fac
            col.prop(prof, fprop, text="")
            anim_fac_mirror_tmpl(c, prof.ani_fac, prof.ani_fac_mirror)
            if provider == "wave":
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = prof.ani_fac2
                col.prop(prof, fprop2, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac2, prof.ani_fac2_mirror)
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac3", toggle=True, text=fname3)
                col = row.column(align=True)
                col.enabled = prof.ani_fac3
                col.prop(prof, fprop3, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac3, prof.ani_fac3_mirror)


class PTDBLNPOPC_PT_ui_blnd(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Profile Blends"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopc.blnd_add").clone = False
        row.operator("ptdblnpopc.blnd_add", text="Clone").clone = True
        pblnd = pool.blnd
        pblndid = pool.blnd_idx
        ops_on = bool(pblnd)
        c = col.column(align=True)
        c.enabled = ops_on
        row = c.row(align=True)
        row.template_list(
            "PTDBLNPOPC_UL_blnd",
            "",
            pool,
            "blnd",
            pool,
            "blnd_idx",
            rows=2,
            maxrows=4,
        )
        row = c.row(align=True)
        boo = pblnd[pblndid].active if ops_on else False
        rc = row.column(align=True)
        rc.operator(
            "ptdblnpopc.blnd_enable", text="Disable" if boo else "Enable"
        ).doall = False
        rc = row.column(align=True)
        rc.operator("ptdblnpopc.blnd_remove", text="Remove").doall = False
        rc = row.column(align=True)
        rc.enabled = pblndid > 0
        rc.operator("ptdblnpopc.blnd_move", icon="TRIA_UP", text="").move_down = False
        row = c.row(align=True)
        rc = row.column(align=True)
        rc.enabled = len(pblnd) > 1
        boo = False
        for i in pblnd:
            if i.active:
                boo = True
                break
        blen_op = rc.operator(
            "ptdblnpopc.blnd_enable",
            text="Disable All" if boo else "Enable All",
        )
        blen_op.doall = True
        blen_op.flagall = not boo
        rc = row.column(align=True)
        rc.enabled = len(pblnd) > 1
        rc.operator("ptdblnpopc.blnd_remove", text="Remove All").doall = True
        rc = row.column(align=True)
        rc.enabled = pblndid < len(pblnd) - 1
        rc.operator("ptdblnpopc.blnd_move", icon="TRIA_DOWN", text="").move_down = True
        if ops_on:
            col = bcol.column()
            item = pblnd[pblndid]
            row = col.row(align=True)
            c = row.column(align=True)
            c.prop(item, "provider", text="")
            c = row.column(align=True)
            c.enabled = item.provider == "custom"
            c.prop(item, "user_ob", text="")
            col = bcol.column(align=True)
            row = col.row(align=True)
            row.enabled = item.active
            row.operator("ptdblnpopc.blnd_edit", text="Edit")


class PTDBLNPOPC_PT_ui_blnd_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_blnd"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.blnd:
            item = pool.blnd[pool.blnd_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(item, "ani_fac", toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac
            col.prop(item, "ani_fac_val", text="")
            anim_fac_mirror_tmpl(c, item.ani_fac, item.ani_fac_mirror)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_profloc(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Profile Locations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.profloc
        collid = pool.profloc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "profloc", "profloc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.profloc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_profloc_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_profloc"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.profloc:
            item = pool.profloc[pool.profloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_profrot(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Profile Rotations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.profrot
        collid = pool.profrot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "profrot", "profrot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.profrot_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_profrot_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_profrot"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.profrot:
            item = pool.profrot[pool.profrot_idx]
            c.enabled = item.active
            anim_rot_tmpl(c, item.ani_rot)
            row = c.row(align=True)
            row.prop(item.ani_rot, "lerp", text="factors", toggle=True)
            col = c.column(align=True)
            col.enabled = item.active and item.ani_rot.lerp
            anim_ind_tmpl(col, item.ani_nidx, "node id")
            anim_ind_tmpl(col, item.ani_idx, "point id")
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_culoc(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Curve Locations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.culoc
        collid = pool.culoc_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "culoc", "culoc_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.culoc_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_culoc_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_culoc"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.culoc:
            item = pool.culoc[pool.culoc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "curve id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_curot(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Curve Rotations"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        collob = pool.curot
        collid = pool.curot_idx
        ops_on = bool(collob)
        coll_ops_tmpl(bcol, pool, "curot", "curot_idx", collob, collid, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = collob[collid]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.curot_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_curot_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_curot"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.curot:
            item = pool.curot[pool.curot_idx]
            c.enabled = item.active
            anim_rot_tmpl(c, item.ani_rot)
            row = c.row(align=True)
            row.prop(item.ani_rot, "lerp", text="factors", toggle=True)
            col = c.column(align=True)
            col.enabled = item.active and item.ani_rot.lerp
            anim_ind_tmpl(col, item.ani_nidx, "curve id")
            anim_ind_tmpl(col, item.ani_idx, "point id")
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_cudep(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Curve Bevel Depth"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        cudep = pool.cudep
        cudepidx = pool.cudep_idx
        ops_on = bool(cudep)
        coll_ops_tmpl(bcol, pool, "cudep", "cudep_idx", cudep, cudepidx, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = cudep[cudepidx]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.cudep_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_cudep_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_cudep"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.cudep:
            item = pool.cudep[pool.cudep_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "curve id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_pnrad(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Curve Point Radius"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        pnrad = pool.pnrad
        pnradidx = pool.pnrad_idx
        ops_on = bool(pnrad)
        coll_ops_tmpl(bcol, pool, "pnrad", "pnrad_idx", pnrad, pnradidx, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = pnrad[pnradidx]
            col.enabled = item.active
            row = col.row(align=True)
            row.operator("ptdblnpopc.pnrad_edit", text="Edit")
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPC_PT_ui_pnrad_anim(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPC_PT_ui_pnrad"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.pnrad:
            item = pool.pnrad[pool.pnrad_idx]
            c.enabled = item.active
            if pool.use_profile:
                anim_ind_tmpl(c, item.ani_nidx, "curve id")
                anim_ind_tmpl(c, item.ani_idx, "point id")
            else:
                anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="none")


class PTDBLNPOPC_PT_ui_noiz(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Noise Locations"

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        noiz = pool.noiz
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopc.pop_noiz", text="Edit")
        row.prop(
            noiz,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if noiz.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = noiz.active
        c.label(text="animation options")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, "ani_noiz", toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_noiz
        col.prop(noiz, "ani_seed", toggle=True)
        row = c.row(align=True)
        row.enabled = noiz.ani_noiz
        row.prop(noiz, "ani_blin", text="")
        row.prop(noiz, "ani_blout", text="")
        row.prop(noiz, "ani_stp", text="")


class PTDBLNPOPC_PT_ui_ranges(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Range Selection"

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopc_pool.use_profile

    def draw(self, context):
        pool = context.scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool) and not pool.animorph
        rngs = pool.rngs
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        col = row.column(align=True)
        range_on = rngs.active
        cap = "Disable" if range_on else "Enable"
        row.operator("ptdblnpopc.curange_react", text=cap).active = range_on
        col = row.column(align=True)
        col.enabled = range_on
        col.prop(rngs, "invert", toggle=True)
        row = bcol.row(align=True)
        row.enabled = range_on
        col = row.column(align=True)
        row = col.row(align=True)
        row.prop(rngs, "rbeg", text="")
        row = col.row(align=True)
        row.prop(rngs, "ritm", text="")
        row = col.row(align=True)
        row.prop(rngs, "rgap", text="")
        row = col.row(align=True)
        row.prop(rngs, "rstp", text="")
        row = bcol.row(align=True)
        row.enabled = range_on
        col = row.column(align=True)
        col.prop(rngs, "rndsel", toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.rndsel
        col.prop(rngs, "nseed", text="")


class PTDBLNPOPC_PT_ui_utilities(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Utilities"

    def draw(self, context):
        pass


class PTDBLNPOPC_PT_ui_batchcoll_toggle(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Batch Toggle Edits"
    bl_parent_id = "PTDBLNPOPC_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        b_ops = pool.batchtoggle_ops
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_ops, "path", toggle=True)
        prof_on = pool.use_profile
        if prof_on:
            row.prop(b_ops, "prof", toggle=True)
        row.prop(b_ops, "curve", toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = b_ops.path or b_ops.curve or (prof_on and b_ops.prof)
        row.operator("ptdblnpopc.batchcoll_toggle", text="Disable").action = "disable"
        row.operator("ptdblnpopc.batchcoll_toggle", text="Enable").action = "enable"


class PTDBLNPOPC_PT_ui_batchcoll_update(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Batch Update Edits"
    bl_parent_id = "PTDBLNPOPC_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        b_ops = pool.batchupdate_ops
        b_eds = b_ops.edits
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool) and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_ops, "nodes", text="")
        prof_on = pool.use_profile
        if prof_on:
            row.prop(b_ops, "points", text="")
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.prop(b_eds, "path", toggle=True)
        if prof_on:
            row.prop(b_eds, "prof", toggle=True)
        row.prop(b_eds, "curve", toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = b_eds.path or b_eds.curve or (prof_on and b_eds.prof)
        row.operator("ptdblnpopc.batchcoll_update")


class PTDBLNPOPC_PT_ui_anicalc(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Anicalc"
    bl_parent_id = "PTDBLNPOPC_PT_ui_utilities"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        clc = pool.anicalc
        layout = self.layout
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        c = row.column(align=True)
        c.operator("ptdblnpopc.anicalc", text="Calculate").current = False
        caller = clc.calc_type
        c = row.column(align=True)
        c.enabled = caller != "offsets"
        c.operator("ptdblnpopc.anicalc", text="Current").current = True
        row = bcol.row(align=True)
        row.prop(clc, "calc_type", text="")
        row = bcol.row(align=True)
        col = row.column(align=True)
        row = col.row(align=True)
        if caller == "loop":
            row.prop(clc, "items", text="")
            row.prop(clc, "offset", text="")
            row = col.row(align=True)
            row.prop(clc, "start", text="")
            row.prop(clc, "step", text="")
        elif caller == "offsets":
            row.prop(clc, "items", text="")
        elif caller == "cycles":
            row.prop(clc, "loop", text="")
        else:
            row.prop(clc, "fra", text="")
            row.prop(clc, "exp", text="")
            row = col.row(align=True)
            row.prop(clc, "first", text="")
            row.prop(clc, "last", text="")
        row = col.row(align=True)
        row.prop(clc, "info", text="")


class PTDBLNPOPC_PT_ui_animode(PTDBLNPOPC_PT_ui, bpy.types.Panel):
    bl_label = "Animation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        layout = self.layout
        layout.enabled = curveset_ok(pool) and ed_panels_ok(pool)
        animode_on = pool.animorph
        cap = "Leave Animode" if animode_on else "Enter Animode"
        box = layout.box()
        bcol = box.column()
        row = bcol.row()
        row.operator("ptdblnpopc.animorph_setup", text=cap).exiting = animode_on
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        row.prop(pool, "act_name", text="")
        row.prop(pool, "ani_kf_type", text="")
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        row.prop(pool, "ani_kf_start", text="")
        row.prop(pool, "ani_kf_step", text="")
        row.prop(pool, "ani_kf_loop", text="")
        row = col.row(align=True)
        row.operator("ptdblnpopc.anicycmirend")
        trax = pool.trax
        traxidx = pool.trax_idx
        nla_on = animode_on and bool(trax)
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = animode_on
        rc.operator("ptdblnpopc.anim_action", text="Add")
        rc = row.column(align=True)
        rc.enabled = nla_on
        rc.operator("ptdblnpopc.track_copy", text="Copy")
        col = col.column(align=True)
        col.enabled = nla_on
        row = col.row(align=True)
        row.template_list(
            "PTDBLNPOPC_UL_trax", "", pool, "trax", pool, "trax_idx", rows=2, maxrows=4
        )
        row = col.row(align=True)
        boo = trax[traxidx].active if nla_on else True
        c = row.column(align=True)
        c.operator(
            "ptdblnpopc.track_enable", text="Disable" if boo else "Enable"
        ).doall = False
        c = row.column(align=True)
        c.operator("ptdblnpopc.track_remove", text="Remove").doall = False
        row = col.row(align=True)
        c = row.column(align=True)
        c.enabled = len(trax) > 1
        boo = False
        for i in trax:
            if i.active:
                boo = True
                break
        t_op = c.operator(
            "ptdblnpopc.track_enable", text="Disable All" if boo else "Enable All"
        )
        t_op.doall = True
        t_op.flagall = not boo
        c = row.column(align=True)
        c.enabled = len(trax) > 1
        c.operator("ptdblnpopc.track_remove", text="Remove All").doall = True
        c = col.column(align=True)
        if nla_on:
            item = trax[traxidx]
            row = c.row(align=True)
            row.enabled = item.active
            row.operator("ptdblnpopc.track_edit", text="Edit")
            box = c.box()
            box.enabled = False
            row = box.row(align=True)
            s = row.split(factor=0.6)
            sc = s.column(align=True)
            names = ("Action Range:", "Strip Frames:", "Scale:", "Repeat:")
            for n in names:
                row = sc.row(align=True)
                row.label(text=n)
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text=f"{item.sa_beg} - {item.sa_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_beg} - {item.s_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_sca:.4f}")
            row = sc.row(align=True)
            reps = 1.0 if item.st_warp else item.s_rep
            row.label(text=f"{reps:.4f}")
        else:
            c.enabled = False
            c.label(text="no tracks")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPC_UL_pathloc,
    PTDBLNPOPC_UL_pathrot,
    PTDBLNPOPC_UL_blnd,
    PTDBLNPOPC_UL_profloc,
    PTDBLNPOPC_UL_profrot,
    PTDBLNPOPC_UL_culoc,
    PTDBLNPOPC_UL_curot,
    PTDBLNPOPC_UL_cudep,
    PTDBLNPOPC_UL_pnrad,
    PTDBLNPOPC_UL_trax,
    PTDBLNPOPC_PT_ui_setup,
    PTDBLNPOPC_PT_ui_path,
    PTDBLNPOPC_PT_ui_path_anim,
    PTDBLNPOPC_PT_ui_pathloc,
    PTDBLNPOPC_PT_ui_pathloc_anim,
    PTDBLNPOPC_PT_ui_pathrot,
    PTDBLNPOPC_PT_ui_pathrot_anim,
    PTDBLNPOPC_PT_ui_prof,
    PTDBLNPOPC_PT_ui_prof_anim,
    PTDBLNPOPC_PT_ui_blnd,
    PTDBLNPOPC_PT_ui_blnd_anim,
    PTDBLNPOPC_PT_ui_profloc,
    PTDBLNPOPC_PT_ui_profloc_anim,
    PTDBLNPOPC_PT_ui_profrot,
    PTDBLNPOPC_PT_ui_profrot_anim,
    PTDBLNPOPC_PT_ui_curve,
    PTDBLNPOPC_PT_ui_culoc,
    PTDBLNPOPC_PT_ui_culoc_anim,
    PTDBLNPOPC_PT_ui_curot,
    PTDBLNPOPC_PT_ui_curot_anim,
    PTDBLNPOPC_PT_ui_cudep,
    PTDBLNPOPC_PT_ui_cudep_anim,
    PTDBLNPOPC_PT_ui_pnrad,
    PTDBLNPOPC_PT_ui_pnrad_anim,
    PTDBLNPOPC_PT_ui_noiz,
    PTDBLNPOPC_PT_ui_ranges,
    PTDBLNPOPC_PT_ui_utilities,
    PTDBLNPOPC_PT_ui_batchcoll_toggle,
    PTDBLNPOPC_PT_ui_batchcoll_update,
    PTDBLNPOPC_PT_ui_anicalc,
    PTDBLNPOPC_PT_ui_animode,
)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
