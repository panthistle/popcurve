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

from . import mpdop as ModPDOP
from . import mpopc as ModPOPC


# ------------------------------------------------------------------------------
#
# -------------------------------- BMPGS ---------------------------------------


# ---- BMPGS PROPERTIES


class PTDBLNPOPC_vec3(bpy.types.PropertyGroup):
    vert: bpy.props.FloatVectorProperty(
        size=3, default=(0, 0, 0), subtype="TRANSLATION"
    )


class PTDBLNPOPC_anim_index(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="index", description="animate index", default=False, options={"HIDDEN"}
    )
    offrnd: bpy.props.BoolProperty(
        name="random",
        description="random index value in [idx-offset, idx+offset]",
        default=False,
        options={"HIDDEN"},
    )
    offrndseed: bpy.props.IntProperty(
        name="seed", description="random seed", default=0, min=0, options={"HIDDEN"}
    )
    offset: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="start", description="start keyframe", default=1, min=1, options={"HIDDEN"}
    )
    stp: bpy.props.IntProperty(
        name="step", description="keyframe step", default=1, min=1, options={"HIDDEN"}
    )


class PTDBLNPOPC_anim_mirror(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="mirror", description="target mirror", default=False, options={"HIDDEN"}
    )
    cycles: bpy.props.IntProperty(
        name="repeat", description="mirror cycles", default=1, min=1, options={"HIDDEN"}
    )


class PTDBLNPOPC_anim_amount(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="factor", description="animate factor", default=False, options={"HIDDEN"}
    )
    fac: bpy.props.FloatProperty(
        name="target", description="factor", default=0, options={"HIDDEN"}
    )
    mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)


class PTDBLNPOPC_anim_rots(bpy.types.PropertyGroup):
    ani_ang: bpy.props.BoolProperty(
        name="angle",
        description="animate rotation angle",
        default=False,
        options={"HIDDEN"},
    )
    angle: bpy.props.FloatProperty(
        name="angle",
        description="[degrees] to rotate per keyframe",
        default=0,
        min=-3.14,
        max=3.14,
        subtype="ANGLE",
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="start", description="from keyframe", default=1, min=1, options={"HIDDEN"}
    )
    end: bpy.props.IntProperty(
        name="end", description="to keyframe", default=1, min=1, options={"HIDDEN"}
    )
    lerp: bpy.props.BoolProperty(
        name="lerp",
        description="use interpolation factoring",
        default=False,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_tmp_states(bpy.types.PropertyGroup):
    on: bpy.props.BoolProperty(default=False)
    off: bpy.props.BoolProperty(default=False)


class PTDBLNPOPC_batchcoll_toggle(bpy.types.PropertyGroup):
    path: bpy.props.BoolProperty(
        name="path", description="toggle path edits", default=False, options={"HIDDEN"}
    )
    prof: bpy.props.BoolProperty(
        name="profile",
        description="toggle profile edits",
        default=False,
        options={"HIDDEN"},
    )
    curve: bpy.props.BoolProperty(
        name="curve",
        description="toggle curve edits",
        default=False,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_batchcoll_update(bpy.types.PropertyGroup):
    edits: bpy.props.PointerProperty(type=PTDBLNPOPC_batchcoll_toggle)
    nodes: bpy.props.IntProperty(
        name="nodes",
        description="previous nodes",
        default=12,
        min=3,
        options={"HIDDEN"},
    )
    points: bpy.props.IntProperty(
        name="points",
        description="previous points",
        default=12,
        min=3,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_params(bpy.types.PropertyGroup):
    def params_npts_update(self, context):
        self.idx = self.get("idx", 0)
        self.itm = self.get("itm", 1)

    def params_idx_get(self):
        return self.get("idx", 0)

    def params_idx_set(self, value):
        den = self.get("npts", 1)
        self["idx"] = value % den

    def params_itm_get(self):
        return self.get("itm", 1)

    def params_itm_set(self, value):
        self["itm"] = min(max(1, value), self.get("npts", 1))

    def params_itm_update(self, context):
        self.gap = self.get("gap", 0)

    def params_gap_get(self):
        return self.get("gap", 0)

    def params_gap_set(self, value):
        hi = max(0, self.get("npts", 1) - self.get("itm", 1))
        self["gap"] = min(max(0, value), hi)

    def params_gap_update(self, context):
        self.reps = self.get("reps", 1)

    def params_reps_get(self):
        return self.get("reps", 1)

    def params_reps_set(self, value):
        num = self.get("npts", 1)
        itm = self.get("itm", 1)
        den = itm + self.get("gap", 0)
        hi = num // den
        hi += 0 if num % den < itm else 1
        self["reps"] = min(max(1, value), hi)

    def params_reps_update(self, context):
        self.repfstp = self.get("repfstp", 1)

    def params_repfstp_get(self):
        return self.get("repfstp", 1)

    def params_repfstp_set(self, value):
        self["repfstp"] = min(max(1, value), self.get("reps", 1))

    npts: bpy.props.IntProperty(default=12, update=params_npts_update)
    ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=(
            ("OFF", "off", "no interpolation"),
            ("LINEAR", "linear", "linear"),
            ("IN", "in", "ease in"),
            ("OUT", "out", "ease out"),
            ("IN-OUT", "in-out", "ease in and out"),
        ),
        default="OFF",
    )
    exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    cyc: bpy.props.BoolProperty(
        name="lag", description="interpolation excludes last increment", default=False
    )
    mir: bpy.props.BoolProperty(
        name="mirror", description="interpolation mirror", default=False
    )
    rev: bpy.props.BoolProperty(
        name="reverse", description="reverse direction", default=False
    )
    reflect: bpy.props.EnumProperty(
        name="reflect",
        description="inverted interpolation values",
        items=(
            ("0", "none", "do not use"),
            ("1", "all", "reflect all"),
            ("2", "highs", "filter lows"),
            ("3", "lows", "filter highs"),
        ),
        default="0",
    )
    idx: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        get=params_idx_get,
        set=params_idx_set,
    )
    itm: bpy.props.IntProperty(
        name="items",
        description="group items",
        default=1,
        get=params_itm_get,
        set=params_itm_set,
        update=params_itm_update,
    )
    gap: bpy.props.IntProperty(
        name="gap",
        description="number of items between groups",
        default=0,
        get=params_gap_get,
        set=params_gap_set,
        update=params_gap_update,
    )
    reps: bpy.props.IntProperty(
        name="groups",
        description="number of groups",
        default=1,
        get=params_reps_get,
        set=params_reps_set,
        update=params_reps_update,
    )
    repfstp: bpy.props.IntProperty(
        name="step",
        description="falloff step",
        default=1,
        get=params_repfstp_get,
        set=params_repfstp_set,
    )
    repfoff: bpy.props.FloatProperty(
        name="step factor", description="enhance-fade (falloff step factor)", default=1
    )
    rnduse: bpy.props.BoolProperty(
        name="random", description="randomize values", default=False
    )
    rndval: bpy.props.FloatProperty(
        name="amount", description="influence", default=1, min=0, max=1
    )
    rndseed: bpy.props.IntProperty(
        name="seed", description="random seed", default=0, min=0
    )
    rndshuff: bpy.props.BoolProperty(
        name="shuffle",
        description="shuffle incoming list (randomized or interpolated lists)",
        default=False,
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPC_noiz(bpy.types.PropertyGroup):
    def noiz_active_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.pop_simple_update()

    active: bpy.props.BoolProperty(
        name="toggle",
        description="enable/disable noise",
        default=False,
        update=noiz_active_update,
        options={"HIDDEN"},
    )
    ampli: bpy.props.FloatProperty(default=0)
    vfac: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    nseed: bpy.props.IntProperty(default=0)
    ani_noiz: bpy.props.BoolProperty(
        name="noise",
        description="animate noise",
        default=False,
        options={"HIDDEN"},
    )
    ani_seed: bpy.props.BoolProperty(
        name="clock seed",
        description="animated seed",
        default=False,
        options={"HIDDEN"},
    )
    ani_blin: bpy.props.IntProperty(
        name="blend-in",
        description="number of keyframes to full effect",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    ani_blout: bpy.props.IntProperty(
        name="blend-out",
        description="number of keyframes to no effect",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    ani_stp: bpy.props.IntProperty(
        name="step", description="keyframe step", default=1, min=1, options={"HIDDEN"}
    )

    def anim_state(self):
        return self.ani_noiz


def path_prof_lerp_items():
    items = (
        ("LINEAR", "linear", "linear"),
        ("IN", "in", "ease in"),
        ("OUT", "out", "ease out"),
        ("IN-OUT", "in-out", "ease in and out"),
    )
    return items


class PTDBLNPOPC_pathed(bpy.types.PropertyGroup):
    def pathed_npts_update(self, context):
        self.pol_sid = self.get("pol_sid", 3)

    def pathed_polsid_get(self):
        return self.get("pol_sid", 3)

    def pathed_polsid_set(self, value):
        hi = min(max(3, self.get("npts", 1) // 2), 20)
        self["pol_sid"] = min(max(3, value), hi)

    def pathed_polcoff_get(self):
        return self.get("pol_coff", 0)

    def pathed_polcoff_set(self, value):
        self["pol_coff"] = 0 if value < 0.001 else value

    def pathed_polsidcoff_update(self, context):
        self.pol_cres = self.get("pol_cres", 0)

    def pathed_polcres_get(self):
        return self.get("pol_cres", 0)

    def pathed_polcres_set(self, value):
        if not self.pol_coff:
            self["pol_cres"] = 0
        else:
            npts = self.get("npts", 3)
            sides = min(npts // 2, self.pol_sid)
            xtra = npts - 2 * sides
            seg = (2 * sides + xtra - xtra % sides) // sides - 1
            self["pol_cres"] = min(max(0, value), seg)

    npts: bpy.props.IntProperty(default=12, update=pathed_npts_update)
    user_dim: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    user_piv: bpy.props.FloatVectorProperty(
        name="pivot",
        description="custom shape origin",
        size=3,
        default=(0, 0, 0),
    )
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPC_vec3)
    cust_dim: bpy.props.FloatVectorProperty(
        name="size", description="path dimensions", size=3, default=(8, 8, 8)
    )
    lin_dim: bpy.props.FloatProperty(name="length", description="length", default=8)
    lin_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    lin_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    wav_dim: bpy.props.FloatProperty(name="length", description="length", default=8)
    wav_amp: bpy.props.FloatProperty(
        name="amplitude", description="amplitude", default=0.5
    )
    wav_frq: bpy.props.FloatProperty(
        name="frequency", description="wave cycles", default=1
    )
    wav_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    arc_dim: bpy.props.FloatProperty(
        name="chord",
        description="chord length",
        default=8,
    )
    arc_fac: bpy.props.FloatProperty(
        name="factor",
        description="variant factor of radius vs. sagitta",
        default=4,
    )
    arc_off: bpy.props.FloatProperty(
        name="offset",
        description="circle center offset",
        default=0,
    )
    ell_dim: bpy.props.FloatVectorProperty(
        name="size", description="ellipse dimensions", size=2, default=(8, 8)
    )
    pol_dim: bpy.props.FloatVectorProperty(
        name="size", description="polygon dimensions", size=2, default=(8, 8)
    )
    pol_sid: bpy.props.IntProperty(
        name="sides",
        description="polygon sides",
        default=3,
        get=pathed_polsid_get,
        set=pathed_polsid_set,
        update=pathed_polsidcoff_update,
    )
    pol_coff: bpy.props.FloatProperty(
        name="offset",
        description="bevel offset",
        default=0.1,
        get=pathed_polcoff_get,
        set=pathed_polcoff_set,
        update=pathed_polsidcoff_update,
    )
    pol_cres: bpy.props.IntProperty(
        name="segments",
        description="bevel segments",
        default=0,
        get=pathed_polcres_get,
        set=pathed_polcres_set,
    )
    pol_ang: bpy.props.FloatProperty(
        name="slope",
        description="polygon start angle",
        default=0,
        subtype="ANGLE",
    )
    pol_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    pol_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    hel_dim: bpy.props.FloatVectorProperty(
        name="size", description="width", size=2, default=(8, 8)
    )
    hel_len: bpy.props.FloatProperty(name="size", description="length", default=8)
    hel_stp: bpy.props.FloatProperty(
        name="frequency", description="revolutions", default=2
    )
    hel_fac: bpy.props.FloatProperty(
        name="width factor", description="grow / shrink", default=1
    )
    hel_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    hel_invert: bpy.props.BoolProperty(
        name="invert", description="inverted width factor", default=False
    )
    hel_hlrp: bpy.props.BoolProperty(
        name="length", description="interpolate length", default=False
    )
    hel_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    hel_mir: bpy.props.BoolProperty(
        name="mirror", description="width interpolation mirror", default=False
    )
    hel_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    spi_dim: bpy.props.FloatProperty(
        name="diameter",
        description="spherical spiral diameter",
        default=8,
    )
    spi_revs: bpy.props.FloatProperty(
        name="frequency", description="revolutions", default=1
    )
    tor_dim: bpy.props.FloatVectorProperty(
        name="size", description="size", size=2, default=(8, 2)
    )
    tor_stp: bpy.props.FloatProperty(
        name="frequency", description="helical curves", default=4
    )
    tor_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)

    def pathed_common_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.pop_simple_update()

    closed: bpy.props.BoolProperty(
        name="closed",
        description="closed or open path",
        default=False,
        update=pathed_common_update,
        options={"HIDDEN"},
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            if key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


class PTDBLNPOPC_path(bpy.types.PropertyGroup):
    def path_provider_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_provider(caller="path")

    def path_res_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.update_replace(caller="path")

    def path_user_ob_check(self, object):
        return object.type == "MESH"

    def path_user_ob_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_provider(caller="path")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="path",
        description="path selection",
        items=(
            ("line", "line", "line"),
            ("wave", "wave", "wave"),
            ("arc", "arc", "arc"),
            ("ellipse", "ellipse", "ellipse"),
            ("polygon", "polygon", "polygon"),
            ("helix", "helix", "helix"),
            ("spiral", "spiral", "spherical spiral"),
            ("torus", "torus", "torus"),
            ("custom", "custom", "user path"),
        ),
        default="line",
        update=path_provider_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_wav: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_arc: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_pol: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=6,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_hel: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=24,
        min=4,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_spi: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=24,
        min=4,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_tor: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=36,
        min=4,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom path provider",
        type=bpy.types.Object,
        poll=path_user_ob_check,
        update=path_user_ob_update,
    )
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPC_pathed)
    ani_dim: bpy.props.BoolProperty(
        name="size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_dim_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_lin_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=8,
        options={"HIDDEN"},
    )
    ani_wav_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=8,
        options={"HIDDEN"},
    )
    ani_arc_dim: bpy.props.FloatProperty(
        name="target",
        description="chord",
        default=8,
        options={"HIDDEN"},
    )
    ani_spi_dim: bpy.props.FloatProperty(
        name="target",
        description="diameter",
        default=8,
        options={"HIDDEN"},
    )
    ani_dim_2d: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=2,
        default=(8, 8),
        options={"HIDDEN"},
    )
    ani_dim_3d: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=3,
        default=(8, 8, 8),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_fac2: bpy.props.BoolProperty(
        name="factor2", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac2_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_fac3: bpy.props.BoolProperty(
        name="factor3", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac3_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_fac4: bpy.props.BoolProperty(
        name="factor4", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac4_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_lin_exp: bpy.props.FloatProperty(
        name="target",
        description="exponent",
        default=2,
        min=0.2,
        max=5,
        options={"HIDDEN"},
    )
    ani_wav_amp: bpy.props.FloatProperty(
        name="target", description="amplitude", default=0.5, options={"HIDDEN"}
    )
    ani_wav_frq: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )
    ani_wav_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_arc_fac: bpy.props.FloatProperty(
        name="target", description="factor", default=4, options={"HIDDEN"}
    )
    ani_hel_len: bpy.props.FloatProperty(
        name="target", description="size", default=8, options={"HIDDEN"}
    )
    ani_hel_fac: bpy.props.FloatProperty(
        name="target", description="width factor", default=1, options={"HIDDEN"}
    )
    ani_hel_stp: bpy.props.FloatProperty(
        name="target", description="frequency", default=2, options={"HIDDEN"}
    )
    ani_hel_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_spi_revs: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )
    ani_tor_stp: bpy.props.FloatProperty(
        name="target", description="frequency", default=2, options={"HIDDEN"}
    )
    ani_tor_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )

    def anim_state(self):
        if self.ani_dim:
            return True
        provider = self.provider
        if provider == "helix" and (self.ani_fac2 or self.ani_fac3 or self.ani_fac4):
            return True
        if provider == "wave" and (self.ani_fac2 or self.ani_fac3):
            return True
        if provider == "torus" and self.ani_fac2:
            return True
        fac_paths = {"wave", "arc", "helix", "spiral", "line", "torus"}
        return self.ani_fac and (provider in fac_paths)

    def to_dct(self):
        d = dict.fromkeys(
            (
                "provider",
                "res_lin",
                "res_wav",
                "res_arc",
                "res_ell",
                "res_pol",
                "res_hel",
                "res_spi",
                "res_tor",
            )
        )
        for key in d.keys():
            d[key] = getattr(self, key)
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.pathed.to_dct(exclude=xvs))
        return d


class PTDBLNPOPC_profed(bpy.types.PropertyGroup):
    def profed_npts_update(self, context):
        self.idx = self.get("idx", 0)
        self.pol_sid = self.get("pol_sid", 3)

    def profed_idx_get(self):
        return self.get("idx", 0)

    def profed_idx_set(self, value):
        den = self.get("npts", 1)
        self["idx"] = value % den

    def profed_polsid_get(self):
        return self.get("pol_sid", 3)

    def profed_polsid_set(self, value):
        hi = min(max(3, self.get("npts", 1) // 2), 20)
        self["pol_sid"] = min(max(3, value), hi)

    def profed_polcoff_get(self):
        return self.get("pol_coff", 0)

    def profed_polcoff_set(self, value):
        self["pol_coff"] = 0 if value < 0.001 else value

    def profed_polsidcoff_update(self, context):
        self.pol_cres = self.get("pol_cres", 0)

    def profed_polcres_get(self):
        return self.get("pol_cres", 0)

    def profed_polcres_set(self, value):
        if not self.pol_coff:
            self["pol_cres"] = 0
        else:
            npts = self.get("npts", 3)
            sides = min(npts // 2, self.get("pol_sid", 3))
            xtra = npts - 2 * sides
            seg = (2 * sides + xtra - xtra % sides) // sides - 1
            self["pol_cres"] = min(max(0, value), seg)

    npts: bpy.props.IntProperty(default=12, update=profed_npts_update)
    user_dim: bpy.props.FloatVectorProperty(size=2, default=(0, 0))
    user_piv: bpy.props.FloatVectorProperty(
        name="pivot",
        description="custom shape origin",
        size=3,
        default=(0, 0, 0),
    )
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPC_vec3)
    cust_dim: bpy.props.FloatVectorProperty(
        name="size", description="profile dimensions", size=2, default=(2, 2)
    )
    lin_dim: bpy.props.FloatProperty(name="length", description="length", default=2)
    lin_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    lin_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    wav_dim: bpy.props.FloatProperty(name="length", description="length", default=2)
    wav_amp: bpy.props.FloatProperty(
        name="amplitude", description="amplitude", default=0.5
    )
    wav_frq: bpy.props.FloatProperty(
        name="frequency", description="wave cycles", default=1
    )
    wav_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    arc_dim: bpy.props.FloatProperty(
        name="chord",
        description="chord length",
        default=2,
    )
    arc_fac: bpy.props.FloatProperty(
        name="factor",
        description="variant factor of radius vs. sagitta",
        default=1,
    )
    arc_off: bpy.props.FloatProperty(
        name="offset",
        description="circle center offset",
        default=0,
    )
    ell_dim: bpy.props.FloatVectorProperty(
        name="size", description="ellipse dimensions", size=2, default=(2, 2)
    )
    pol_dim: bpy.props.FloatVectorProperty(
        name="size", description="polygon dimensions", size=2, default=(2, 2)
    )
    pol_sid: bpy.props.IntProperty(
        name="sides",
        description="polygon sides",
        default=3,
        get=profed_polsid_get,
        set=profed_polsid_set,
        update=profed_polsidcoff_update,
    )
    pol_coff: bpy.props.FloatProperty(
        name="offset",
        description="bevel offset",
        default=0.1,
        get=profed_polcoff_get,
        set=profed_polcoff_set,
        update=profed_polsidcoff_update,
    )
    pol_cres: bpy.props.IntProperty(
        name="segments",
        description="bevel segments",
        default=0,
        get=profed_polcres_get,
        set=profed_polcres_set,
    )
    pol_ang: bpy.props.FloatProperty(
        name="slope",
        description="polygon start angle",
        default=0,
        subtype="ANGLE",
    )
    pol_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    pol_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    idx: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        get=profed_idx_get,
        set=profed_idx_set,
    )
    rot_align: bpy.props.FloatProperty(
        name="angle",
        description="rotation",
        default=0,
        subtype="ANGLE",
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            if key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


def prof_blnd_provider_items():
    items = (
        ("line", "line", "line"),
        ("wave", "wave", "wave"),
        ("arc", "arc", "arc"),
        ("ellipse", "ellipse", "ellipse"),
        ("polygon", "polygon", "polygon"),
        ("custom", "custom", "user profile"),
    )
    return items


class PTDBLNPOPC_prof(bpy.types.PropertyGroup):
    def prof_provider_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_provider(caller="prof")

    def prof_res_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.update_replace(caller="prof")

    def prof_user_ob_check(self, object):
        return object.type == "MESH"

    def prof_user_ob_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_provider(caller="prof")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="profile",
        description="profile selection",
        items=prof_blnd_provider_items(),
        default="line",
        update=prof_provider_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_wav: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_arc: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_pol: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=6,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom profile provider",
        type=bpy.types.Object,
        poll=prof_user_ob_check,
        update=prof_user_ob_update,
    )
    profed: bpy.props.PointerProperty(type=PTDBLNPOPC_profed)
    ani_dim: bpy.props.BoolProperty(
        name="size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_dim_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_lin_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=2,
        options={"HIDDEN"},
    )
    ani_wav_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=2,
        options={"HIDDEN"},
    )
    ani_arc_dim: bpy.props.FloatProperty(
        name="target",
        description="chord",
        default=2,
        options={"HIDDEN"},
    )
    ani_epc_dim: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=2,
        default=(2, 2),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_fac2: bpy.props.BoolProperty(
        name="factor 2", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac2_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_fac3: bpy.props.BoolProperty(
        name="factor 3", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac3_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)
    ani_lin_exp: bpy.props.FloatProperty(
        name="target",
        description="exponent",
        default=2,
        min=0.2,
        max=5,
        options={"HIDDEN"},
    )
    ani_wav_amp: bpy.props.FloatProperty(
        name="target", description="amplitude", default=0.5, options={"HIDDEN"}
    )
    ani_wav_frq: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )
    ani_wav_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_arc_fac: bpy.props.FloatProperty(
        name="target", description="factor", default=1, options={"HIDDEN"}
    )

    def anim_state(self):
        if self.ani_dim:
            return True
        if self.provider == "wave" and (self.ani_fac2 or self.ani_fac3):
            return True
        fac_profs = {"wave", "arc", "line"}
        return self.ani_fac and (self.provider in fac_profs)

    def to_dct(self):
        d = dict.fromkeys(
            (
                "provider",
                "res_lin",
                "res_wav",
                "res_arc",
                "res_ell",
                "res_pol",
            )
        )
        for key in d.keys():
            d[key] = getattr(self, key)
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.profed.to_dct(exclude=xvs))
        return d


class PTDBLNPOPC_blnd(bpy.types.PropertyGroup):
    def blnd_provider_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_blnd_provider()

    def blnd_user_ob_check(self, object):
        return object.type == "MESH"

    def blnd_user_ob_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.setup_blnd_provider()

    name: bpy.props.StringProperty(default="Blend")
    provider: bpy.props.EnumProperty(
        name="blend profile",
        description="blend profile selection",
        items=prof_blnd_provider_items(),
        default="line",
        update=blnd_provider_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom blend profile provider",
        type=bpy.types.Object,
        poll=blnd_user_ob_check,
        update=blnd_user_ob_update,
    )
    active: bpy.props.BoolProperty(default=False)
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPC_profed)
    fac: bpy.props.FloatProperty(default=0)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_val: bpy.props.FloatProperty(
        name="target",
        default=0,
        description="blend factor",
        min=-1,
        max=1,
        options={"HIDDEN"},
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_mirror)

    def anim_state(self):
        return self.ani_nidx.active or self.ani_fac or self.ani_idx.active

    def to_dct(self):
        d = dict.fromkeys(("provider", "fac"))
        for key in d.keys():
            d[key] = getattr(self, key)
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.blnded.to_dct(exclude=xvs))
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_pathloc(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Location")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 1))
    absboo: bpy.props.BoolProperty(default=True)
    bbatt: bpy.props.BoolProperty(default=True)
    bbrot: bpy.props.BoolProperty(default=True)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_amount)

    def anim_state(self, dummy=False):
        return self.ani_nidx.active or self.ani_fac.active

    def to_dct(self):
        d = {
            "fac": self.fac,
            "axis": self.axis,
            "absboo": self.absboo,
            "bbatt": self.bbatt,
            "bbrot": self.bbrot,
        }
        d["nprams"] = self.nprams.to_dct()
        return d


class PTDBLNPOPC_pathrot(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Rotation")
    active: bpy.props.BoolProperty(default=False)
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    angle: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    bbatt: bpy.props.StringProperty(default="after")
    brots: bpy.props.BoolProperty(default=False)
    pivot: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_rots)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)

    def anim_state(self):
        return self.ani_rot.ani_ang or self.ani_nidx.active

    def to_dct(self):
        d = {
            "axis": self.axis,
            "angle": self.angle,
            "bbatt": self.bbatt,
            "brots": self.brots,
            "pivot": self.pivot,
        }
        d["nprams"] = self.nprams.to_dct()
        return d


class PTDBLNPOPC_profloc(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Location")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 1))
    absboo: bpy.props.BoolProperty(default=True)
    bbrot: bpy.props.BoolProperty(default=True)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_amount)

    def anim_state(self, dummy=False):
        return self.ani_nidx.active or self.ani_idx.active or self.ani_fac.active

    def to_dct(self):
        d = {
            "fac": self.fac,
            "axis": self.axis,
            "absboo": self.absboo,
            "bbrot": self.bbrot,
        }
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_profrot(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Rotation")
    active: bpy.props.BoolProperty(default=False)
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 1, 0))
    angle: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    pivot: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_rots)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)

    def anim_state(self):
        return self.ani_rot.ani_ang or self.ani_nidx.active or self.ani_idx.active

    def to_dct(self):
        d = {"axis": self.axis, "angle": self.angle, "pivot": self.pivot}
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_culoc(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Location")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 1))
    globoo: bpy.props.BoolProperty(default=True)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_amount)

    def anim_state(self, dummy=False):
        return self.ani_nidx.active or self.ani_idx.active or self.ani_fac.active

    def to_dct(self):
        d = {"fac": self.fac, "axis": self.axis, "globoo": self.globoo}
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_curot(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Rotation")
    active: bpy.props.BoolProperty(default=False)
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    angle: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    pivot: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    globoo: bpy.props.BoolProperty(default=True)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_rots)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)

    def anim_state(self):
        return self.ani_rot.ani_ang or self.ani_nidx.active or self.ani_idx.active

    def to_dct(self):
        d = {
            "axis": self.axis,
            "angle": self.angle,
            "pivot": self.pivot,
            "globoo": self.globoo,
        }
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_cudep(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Depth")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0.25)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_amount)

    def anim_state(self, dummy=False):
        return self.ani_nidx.active or self.ani_fac.active

    def to_dct(self):
        d = {"fac": self.fac}
        d["nprams"] = self.nprams.to_dct()
        return d


class PTDBLNPOPC_pnrad(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Radius")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=1.0)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    tmp_state: bpy.props.PointerProperty(type=PTDBLNPOPC_tmp_states)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPC_anim_amount)

    def anim_state(self, prof_on):
        if self.ani_nidx.active or self.ani_fac.active:
            return True
        return prof_on and self.ani_idx.active

    def to_dct(self):
        d = {"fac": self.fac}
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPC_track_actions(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="name")


class PTDBLNPOPC_track(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Track")
    idns: bpy.props.CollectionProperty(type=PTDBLNPOPC_track_actions)
    active: bpy.props.BoolProperty(default=True)
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=2)
    s_sca: bpy.props.FloatProperty(default=1)
    s_rep: bpy.props.FloatProperty(default=1)
    sa_beg: bpy.props.IntProperty(default=1)
    sa_end: bpy.props.IntProperty(default=2)
    s_beg: bpy.props.IntProperty(default=1)
    s_end: bpy.props.IntProperty(default=2)
    s_blend: bpy.props.StringProperty(default="REPLACE")
    s_blauto: bpy.props.BoolProperty(default=False)
    s_blin: bpy.props.IntProperty(default=0)
    s_blout: bpy.props.IntProperty(default=0)
    s_xpl: bpy.props.StringProperty(default="HOLD")
    s_bak: bpy.props.BoolProperty(default=False)
    st_warp: bpy.props.BoolProperty(default=False)
    st_curve: bpy.props.StringProperty(default="12")
    st_ease: bpy.props.StringProperty(default="0")
    st_ctrl: bpy.props.BoolProperty(default=False)
    st_fra: bpy.props.IntProperty(default=1)

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key == "idns" or key in exclude:
                continue
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPC_rngs(bpy.types.PropertyGroup):
    def rngs_common_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.update_replace()

    active: bpy.props.BoolProperty(default=False)
    invert: bpy.props.BoolProperty(
        name="invert",
        description="invert selections",
        default=False,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rndsel: bpy.props.BoolProperty(
        name="randomize",
        description="random selections",
        default=False,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rbeg: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    ritm: bpy.props.IntProperty(
        name="items",
        description="group items",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rgap: bpy.props.IntProperty(
        name="gap",
        description="number of items between groups",
        default=0,
        min=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rstp: bpy.props.IntProperty(
        name="groups",
        description="number of groups",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    nseed: bpy.props.IntProperty(
        name="seed",
        description="random seed",
        default=0,
        min=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    _sindz = {"data": set()}

    def sindz_get(self):
        return self._sindz["data"]

    def sindz_set(self, value):
        self._sindz["data"] = value


class PTDBLNPOPC_attitude(bpy.types.PropertyGroup):
    def attitude_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.pop_simple_update()

    def attitude_track_update(self, context):
        axes = ("X", "Y", "Z")
        self.up = axes[self.get("up", 0)]

    def attitude_up_get(self):
        return self.get("up", 0)

    def attitude_up_set(self, value):
        t = self.get("track", 2)
        if t in (value, value + 3):
            value = value + 1 if value < 2 else 0
        self["up"] = value

    active: bpy.props.BoolProperty(
        name="attitude",
        description="rotation from tangent vectors and direction",
        default=True,
        update=attitude_update,
        options={"HIDDEN"},
    )
    track: bpy.props.EnumProperty(
        name="track axis",
        description="track-axis selection",
        items=(
            ("X", "X", "X"),
            ("Y", "Y", "Y"),
            ("Z", "Z", "Z"),
            ("-X", "-X", "-X"),
            ("-Y", "-Y", "-Y"),
            ("-Z", "-Z", "-Z"),
        ),
        default="Z",
        update=attitude_track_update,
        options={"HIDDEN"},
    )
    upfixed: bpy.props.BoolProperty(
        name="fixed up",
        description="fixed up-axis",
        default=False,
        update=attitude_update,
        options={"HIDDEN"},
    )
    up: bpy.props.EnumProperty(
        name="up axis",
        description="up-axis selection",
        items=(("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z")),
        default="X",
        get=attitude_up_get,
        set=attitude_up_set,
        update=attitude_update,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_curve(bpy.types.PropertyGroup):
    def curve_replace_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.update_replace()

    spline: bpy.props.EnumProperty(
        name="spline",
        description="spline type",
        items=(
            ("POLY", "polyline", "polyline"),
            ("NURBS", "nurbs", "nurbs"),
        ),
        default="NURBS",
        update=curve_replace_update,
        options={"HIDDEN"},
    )
    direction: bpy.props.EnumProperty(
        name="curve direction",
        description="curve direction, effective when curve array is enabled",
        items=(("path", "path", "path"), ("prof", "profile", "profile")),
        default="prof",
        update=curve_replace_update,
        options={"HIDDEN"},
    )

    def curve_bevres_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="bevres")

    def curve_ures_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="ures")

    bevres: bpy.props.IntProperty(
        name="bevel resolution",
        description="bevel resolution",
        default=4,
        min=1,
        max=32,
        update=curve_bevres_update,
        options={"HIDDEN"},
    )
    ures: bpy.props.IntProperty(
        name="resolution u",
        description="segment subdivisions",
        default=12,
        min=1,
        max=64,
        update=curve_ures_update,
        options={"HIDDEN"},
    )

    def curve_smooth_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="smooth")

    def curve_cyclic_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="cyclic")

    def curve_fillcaps_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="fillcaps")

    def curve_endpoints_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="endpoints")

    smooth: bpy.props.FloatProperty(
        name="twist smooth",
        description="smoothing iteration for tangents",
        default=0,
        min=0,
        max=4,
        update=curve_smooth_update,
        options={"HIDDEN"},
    )
    cyclic: bpy.props.BoolProperty(
        name="cyclic",
        description="closed loop curve",
        default=False,
        update=curve_cyclic_update,
        options={"HIDDEN"},
    )
    fillcaps: bpy.props.BoolProperty(
        name="fill caps",
        description="use fill caps for non-cyclic curve",
        default=True,
        update=curve_fillcaps_update,
        options={"HIDDEN"},
    )
    endpoints: bpy.props.BoolProperty(
        name="endpoints",
        description="use endpoints for non-cyclic, nurbs-spline curve",
        default=True,
        update=curve_endpoints_update,
        options={"HIDDEN"},
    )

    def curve_bevdep_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="bevdep")

    def curve_pntrad_update(self, context):
        pool = context.scene.ptdblnpopc_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopc.curve_setts(caller="pntrad")

    bevdep: bpy.props.FloatProperty(
        name="bevel depth",
        description="bevel depth start value",
        default=0.25,
        min=0,
        update=curve_bevdep_update,
        options={"HIDDEN"},
    )
    pntrad: bpy.props.FloatProperty(
        name="point radius",
        description="spline point radius start value",
        default=1.0,
        min=0,
        update=curve_pntrad_update,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_anicalc(bpy.types.PropertyGroup):
    info: bpy.props.StringProperty(name="results", description="results", default="")

    def anicalc_type_update(self, context):
        bpy.ops.ptdblnpopc.anicalc(current=False)

    calc_type: bpy.props.EnumProperty(
        name="calculation",
        description="calculation",
        items=(
            ("offsets", "offsets", "index offsets from items"),
            ("loop", "loop", "loop from [items, offset, start, step]"),
            ("cycles", "cycles", "mirror cycles from loop"),
            ("strip", "time scale", "strip time scale from control frame and function"),
        ),
        default="offsets",
        update=anicalc_type_update,
        options={"HIDDEN"},
    )
    loop: bpy.props.IntProperty(
        name="loop",
        description="total keyframes",
        default=5,
        min=2,
        options={"HIDDEN"},
    )
    items: bpy.props.IntProperty(
        name="items",
        description="items (nodes or points)",
        default=12,
        min=3,
        options={"HIDDEN"},
    )

    def anicalc_offset_get(self):
        return self.get("offset", 1)

    def anicalc_offset_set(self, value):
        den = self.get("items", 3) - 1
        self["offset"] = max(1, value % den)

    offset: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=1,
        get=anicalc_offset_get,
        set=anicalc_offset_set,
        options={"HIDDEN"},
    )
    start: bpy.props.IntProperty(
        name="start",
        description="start keyframe",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    step: bpy.props.IntProperty(
        name="step",
        description="keyframe step",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    exp: bpy.props.EnumProperty(
        name="timewarp curve",
        description="warp function",
        items=(
            ("2", "quad", "quadratic"),
            ("3", "cube", "cubic"),
            ("4", "quart", "quartic"),
            ("5", "quint", "quintic"),
        ),
        default="2",
        options={"HIDDEN"},
    )
    fra: bpy.props.IntProperty(
        name="frame",
        description="control frame",
        default=2,
        min=2,
        options={"HIDDEN"},
    )
    first: bpy.props.IntProperty(
        name="first",
        description="first frame",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    last: bpy.props.IntProperty(
        name="last",
        description="last frame",
        default=2,
        min=2,
        options={"HIDDEN"},
    )


class PTDBLNPOPC_pool(bpy.types.PropertyGroup):
    curve: bpy.props.PointerProperty(type=PTDBLNPOPC_curve)
    path: bpy.props.PointerProperty(type=PTDBLNPOPC_path)
    path_att: bpy.props.PointerProperty(type=PTDBLNPOPC_attitude)
    prof: bpy.props.PointerProperty(type=PTDBLNPOPC_prof)
    noiz: bpy.props.PointerProperty(type=PTDBLNPOPC_noiz)
    rngs: bpy.props.PointerProperty(type=PTDBLNPOPC_rngs)
    blnd: bpy.props.CollectionProperty(type=PTDBLNPOPC_blnd)
    blnd_idx: bpy.props.IntProperty(name="Blend", default=-1, options={"HIDDEN"})
    pathloc: bpy.props.CollectionProperty(type=PTDBLNPOPC_pathloc)
    pathloc_idx: bpy.props.IntProperty(name="Location", default=-1, options={"HIDDEN"})
    pathrot: bpy.props.CollectionProperty(type=PTDBLNPOPC_pathrot)
    pathrot_idx: bpy.props.IntProperty(name="Rotation", default=-1, options={"HIDDEN"})
    profloc: bpy.props.CollectionProperty(type=PTDBLNPOPC_profloc)
    profloc_idx: bpy.props.IntProperty(name="Location", default=-1, options={"HIDDEN"})
    profrot: bpy.props.CollectionProperty(type=PTDBLNPOPC_profrot)
    profrot_idx: bpy.props.IntProperty(name="Rotation", default=-1, options={"HIDDEN"})
    culoc: bpy.props.CollectionProperty(type=PTDBLNPOPC_culoc)
    culoc_idx: bpy.props.IntProperty(name="Location", default=-1, options={"HIDDEN"})
    curot: bpy.props.CollectionProperty(type=PTDBLNPOPC_curot)
    curot_idx: bpy.props.IntProperty(name="Rotation", default=-1, options={"HIDDEN"})
    cudep: bpy.props.CollectionProperty(type=PTDBLNPOPC_cudep)
    cudep_idx: bpy.props.IntProperty(name="Depth", default=-1, options={"HIDDEN"})
    pnrad: bpy.props.CollectionProperty(type=PTDBLNPOPC_pnrad)
    pnrad_idx: bpy.props.IntProperty(name="Radius", default=-1, options={"HIDDEN"})
    trax: bpy.props.CollectionProperty(type=PTDBLNPOPC_track)
    trax_idx: bpy.props.IntProperty(name="Track", default=-1, options={"HIDDEN"})
    SPLINE_TYPES = {"POLY", "NURBS"}
    batchtoggle_ops: bpy.props.PointerProperty(type=PTDBLNPOPC_batchcoll_toggle)
    batchupdate_ops: bpy.props.PointerProperty(type=PTDBLNPOPC_batchcoll_update)
    update_ok: bpy.props.BoolProperty(default=True)
    use_profile: bpy.props.BoolProperty(default=False)
    show_warn: bpy.props.BoolProperty(
        name="show warnings",
        description="show confirmation pop-ups",
        default=True,
        options={"HIDDEN"},
    )
    setcoll: bpy.props.PointerProperty(type=bpy.types.Collection)
    setcoll_name: bpy.props.StringProperty(default="cpop_set")
    replace_set: bpy.props.BoolProperty(
        name="replace set",
        default=False,
        description=(
            "if enabled, running any of the 'Load ...' commands "
            "will replace the current set"
        ),
        options={"HIDDEN"},
    )
    ncus: bpy.props.IntProperty(default=12)
    cpts: bpy.props.IntProperty(default=12)
    anicalc: bpy.props.PointerProperty(type=PTDBLNPOPC_anicalc)
    animorph: bpy.props.BoolProperty(default=False)
    ani_kf_type: bpy.props.EnumProperty(
        name="key_type",
        description="keyframe interpolation",
        items=(
            ("0", "Constant", "constant interpolation"),
            ("1", "Linear", "linear interpolation"),
            ("2", "Bezier", "bezier interpolation"),
        ),
        default="1",
        options={"HIDDEN"},
    )
    ani_kf_start: bpy.props.IntProperty(
        name="start",
        default=1,
        min=1,
        description="first keyframe number",
        options={"HIDDEN"},
    )
    ani_kf_step: bpy.props.IntProperty(
        name="step",
        description="frame-distance between two successive keyframes",
        default=10,
        min=1,
        options={"HIDDEN"},
    )
    ani_kf_loop: bpy.props.IntProperty(
        name="loop",
        description="number of keyframes to complete animation",
        default=5,
        min=2,
        options={"HIDDEN"},
    )

    def pool_act_name_get(self):
        return self.get("act_name", "Action")

    def pool_act_name_set(self, value):
        v = value.strip()
        self["act_name"] = v if v else "Action"

    act_name: bpy.props.StringProperty(
        name="name",
        description="action name",
        default="Action",
        get=pool_act_name_get,
        set=pool_act_name_set,
    )

    def data_anim_state_eval(self):
        if self.noiz.active and self.noiz.anim_state():
            return True
        if self.path.anim_state():
            return True
        for item in self.pathloc:
            if item.active and item.anim_state():
                return True
        for item in self.pathrot:
            if item.active and item.anim_state():
                return True
        if self.use_profile:
            if self.prof.anim_state():
                return True
            for item in self.blnd:
                if item.active and item.anim_state():
                    return True
            for item in self.profloc:
                if item.active and item.anim_state():
                    return True
            for item in self.profrot:
                if item.active and item.anim_state():
                    return True
            for item in self.culoc:
                if item.active and item.anim_state():
                    return True
            for item in self.curot:
                if item.active and item.anim_state():
                    return True
        return False

    def deps_anim_state_eval(self):
        if self.use_profile:
            for item in self.cudep:
                if item.active and item.anim_state():
                    return True
        return False

    def rads_anim_state_eval(self):
        prof_on = self.use_profile
        for item in self.pnrad:
            if item.active and item.anim_state(prof_on):
                return True
        return False

    def to_dct(self):
        return {
            "use_profile": self.use_profile,
            "pathori": self.path_att.active,
            "pathtrack": self.path_att.track,
            "pathup": self.path_att.up,
            "pathupfixed": self.path_att.upfixed,
            "direction": self.curve.direction,
            "pntrad": self.curve.pntrad,
            "bevdep": self.curve.bevdep,
        }

    def props_unset(self):
        exclude = {
            "setcoll",
            "replace_set",
            "update_ok",
            "show_warn",
            "anicalc",
        }
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            self.property_unset(key)


# ---- BMPGS OPERATORS


# ---- PATH EDITOR


class PTDBLNPOPC_OT_path_edit(bpy.types.Operator):
    bl_label = "Path Settings"
    bl_idname = "ptdblnpopc.path_edit"
    bl_description = "path settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPC_pathed)

    def invoke(self, context, event):
        path = context.scene.ptdblnpopc_pool.path
        self.provider = path.provider
        xcl = {"upv", "closed"}
        d = path.pathed.to_dct(exclude=xcl)
        for key in d.keys():
            setattr(self.pathed, key, d[key])
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        path = pool.path
        xcl = {"npts", "upv", "closed"}
        d = self.pathed.to_dct(exclude=xcl)
        for key in d.keys():
            setattr(path.pathed, key, d[key])
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"path_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        cns = s.column(align=True)
        cvs = s.column(align=True)
        getattr(ModPDOP, self.provider)(cns, cvs, self.pathed)


# ---- PROFILE EDITOR


class PTDBLNPOPC_OT_prof_edit(bpy.types.Operator):
    bl_label = "Profile Settings"
    bl_idname = "ptdblnpopc.prof_edit"
    bl_description = "profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    profed: bpy.props.PointerProperty(type=PTDBLNPOPC_profed)

    def invoke(self, context, event):
        prof = context.scene.ptdblnpopc_pool.prof
        self.provider = prof.provider
        d = prof.profed.to_dct(exclude={"upv"})
        for key in d.keys():
            setattr(self.profed, key, d[key])
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        prof = pool.prof
        d = self.profed.to_dct(exclude={"npts", "upv"})
        for key in d.keys():
            setattr(prof.profed, key, d[key])
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"prof_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        cns = s.column(align=True)
        cvs = s.column(align=True)
        getattr(ModPDOP, self.provider)(cns, cvs, self.profed, isprof=True)


# ---- BLENDS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_blnd_edit(bpy.types.Operator):
    bl_label = "Blend Settings"
    bl_idname = "ptdblnpopc.blnd_edit"
    bl_description = "blend profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    fac: bpy.props.FloatProperty(
        name="factor", description="blend factor", default=0, min=-1, max=1
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("blend", "blend", "blend"),
            ("points", "points", "points"),
            ("nodes", "nodes", "nodes"),
            ("all", "all", "all"),
        ),
        default="all",
    )
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPC_profed)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        d = item.blnded.to_dct(exclude={"upv"})
        for key in d.keys():
            setattr(self.blnded, key, d[key])
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        d = self.blnded.to_dct(exclude={"npts", "upv"})
        for key in d.keys():
            setattr(item.blnded, key, d[key])
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.blnd[pool.blnd_idx]
        self.provider = item.provider
        self.fac = item.fac
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.blnd[pool.blnd_idx]
        item.fac = self.fac
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"nodes", "all"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), True)
        if self.selview in {"points", "all"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"), False)
        if self.selview in {"blend", "all"}:
            box = layout.box()
            row = box.row(align=True)
            s = row.split(factor=0.25)
            cns = s.column(align=True)
            cvs = s.column(align=True)
            getattr(ModPDOP, self.provider)(cns, cvs, self.blnded, isprof=True)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text="Align")
        row = sc.row(align=True)
        row.label(text="Factor")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self.blnded, "idx", text="")
        row.prop(self.blnded, "rot_align", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


# ---- PATH LOCATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_pathloc_edit(bpy.types.Operator):
    bl_label = "Path Locations"
    bl_idname = "ptdblnpopc.pathloc_edit"
    bl_description = "path locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    use_profile: bpy.props.BoolProperty(default=False)
    pathatt_active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    axis: bpy.props.FloatVectorProperty(
        name="influence",
        description="axis factor",
        size=3,
        default=(1, 1, 1),
        min=-1,
        max=1,
    )
    absboo: bpy.props.BoolProperty(
        name="move",
        description="absolute or relative translation (path space)",
        default=True,
    )
    bbatt: bpy.props.BoolProperty(
        name="update attitude",
        description="effective when path attitude is enabled",
        default=True,
    )
    bbrot: bpy.props.BoolProperty(
        name="before rotations",
        description="add location edits before or after path rotations",
        default=True,
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        d = item.nprams.to_dct()
        for key in d.keys():
            setattr(self.nprams, key, d[key])

    def copy_to_pg(self, item):
        d = self.nprams.to_dct(exclude={"npts"})
        for key in d.keys():
            setattr(item.nprams, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.pathloc[pool.pathloc_idx]
        self.use_profile = pool.use_profile
        self.pathatt_active = pool.path_att.active
        self.fac = item.fac
        self.axis = item.axis
        self.absboo = item.absboo
        self.bbatt = item.bbatt
        self.bbrot = item.bbrot
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.pathloc[pool.pathloc_idx]
        item.fac = self.fac
        item.axis = self.axis
        item.absboo = self.absboo
        item.bbatt = self.bbatt
        item.bbrot = self.bbrot
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pathloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), False)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        carray = self.use_profile
        if carray:
            names = ("Translation", "Axis", "Factor", "Attitude")
        else:
            names = ("Translation", "Axis", "Factor", "Order")
        for n in names:
            row = sc.row(align=True)
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        cap = "absolute" if self.absboo else "relative"
        row.prop(self, "absboo", text=cap, toggle=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")
        row = sc.row(align=True)
        if carray:
            row.enabled = self.pathatt_active
            row.prop(self, "bbatt", toggle=True)
        else:
            cap = "before rotations" if self.bbrot else "after rotations"
            row.prop(self, "bbrot", text=cap, toggle=True)


# ---- PATH ROTATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_pathrot_edit(bpy.types.Operator):
    bl_label = "Path Rotations"
    bl_idname = "ptdblnpopc.pathrot_edit"
    bl_description = "path rotations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    use_profile: bpy.props.BoolProperty(default=False)
    pathatt_active: bpy.props.BoolProperty(default=False)
    axis: bpy.props.FloatVectorProperty(
        name="axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    angle: bpy.props.FloatProperty(
        name="angle", description="rotation angle", default=0, subtype="ANGLE"
    )
    bbatt: bpy.props.EnumProperty(
        name="order",
        description="rotation sequence",
        items=(
            ("after", "after attitude", "effective when path attitude is enabled"),
            ("before", "before attitude", "effective when path attitude is enabled"),
        ),
        default="after",
    )
    brots: bpy.props.BoolProperty(
        name="rotate path", description="rotate path locations", default=False
    )
    pivot: bpy.props.FloatVectorProperty(
        name="pivot", size=3, default=(0, 0, 0), description="rotation pivot"
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        d = item.nprams.to_dct()
        for key in d.keys():
            setattr(self.nprams, key, d[key])

    def copy_to_pg(self, item):
        d = self.nprams.to_dct(exclude={"npts"})
        for key in d.keys():
            setattr(item.nprams, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.pathrot[pool.pathrot_idx]
        self.use_profile = pool.use_profile
        self.pathatt_active = pool.path_att.active
        self.axis = item.axis
        self.angle = item.angle
        self.bbatt = item.bbatt
        self.brots = item.brots
        self.pivot = item.pivot
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.pathrot[pool.pathrot_idx]
        item.axis = self.axis
        item.angle = self.angle
        item.bbatt = self.bbatt
        item.brots = self.brots
        item.pivot = self.pivot
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pathrot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), False)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        carr = self.use_profile
        if carr:
            names = ("Axis", "Angle", "Order", "Effect", "Pivot")
        else:
            names = ("Axis", "Angle", "Pivot")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "angle", text="")
        if carr:
            row = sc.row(align=True)
            row.enabled = self.pathatt_active
            row.prop(self, "bbatt", text="")
            row = sc.row(align=True)
            row.prop(self, "brots", toggle=True)
        row = sc.row(align=True)
        row.enabled = self.brots if carr else True
        row.prop(self, "pivot", text="")


# ---- PROFILE LOCATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_profloc_edit(bpy.types.Operator):
    bl_label = "Profile Locations"
    bl_idname = "ptdblnpopc.profloc_edit"
    bl_description = "profile locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    axis: bpy.props.FloatVectorProperty(
        name="influence",
        description="axis factor",
        size=3,
        default=(1, 1, 1),
        min=-1,
        max=1,
    )
    absboo: bpy.props.BoolProperty(
        name="move",
        description="absolute or relative translation (profile space)",
        default=True,
    )
    bbrot: bpy.props.BoolProperty(
        name="before rotations",
        description="add location edits before or after profile rotations",
        default=True,
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("nodes", "nodes", "nodes"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.profloc[pool.profloc_idx]
        self.fac = item.fac
        self.axis = item.axis
        self.absboo = item.absboo
        self.bbrot = item.bbrot
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.profloc[pool.profloc_idx]
        item.fac = self.fac
        item.axis = self.axis
        item.absboo = self.absboo
        item.bbrot = self.bbrot
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"profloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"nodes", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), True)
        if self.selview in {"points", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"), False)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Translation", "Axis", "Factor", "Order")
        for n in names:
            row = sc.row(align=True)
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        cap = "absolute" if self.absboo else "relative"
        row.prop(self, "absboo", text=cap, toggle=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")
        row = sc.row(align=True)
        cap = "before rotations" if self.bbrot else "after rotations"
        row.prop(self, "bbrot", text=cap, toggle=True)


# ---- PROFILE ROTATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_profrot_edit(bpy.types.Operator):
    bl_label = "Profile Rotations"
    bl_idname = "ptdblnpopc.profrot_edit"
    bl_description = "profile rotations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    axis: bpy.props.FloatVectorProperty(
        name="axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    angle: bpy.props.FloatProperty(
        name="angle", description="rotation angle", default=0, subtype="ANGLE"
    )
    pivot: bpy.props.FloatVectorProperty(
        name="pivot", size=3, default=(0, 0, 0), description="rotation pivot"
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("nodes", "nodes", "nodes"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.profrot[pool.profrot_idx]
        self.axis = item.axis
        self.angle = item.angle
        self.pivot = item.pivot
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.profrot[pool.profrot_idx]
        item.axis = self.axis
        item.angle = self.angle
        item.pivot = self.pivot
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"profrot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"nodes", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), True)
        if self.selview in {"points", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"), False)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Axis", "Angle", "Pivot")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "angle", text="")
        row = sc.row(align=True)
        row.prop(self, "pivot", text="")


# ---- CURVE LOCATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_culoc_edit(bpy.types.Operator):
    bl_label = "Curve Locations"
    bl_idname = "ptdblnpopc.culoc_edit"
    bl_description = "curve locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    axis: bpy.props.FloatVectorProperty(
        name="influence",
        description="axis factor",
        size=3,
        default=(1, 1, 1),
        min=-1,
        max=1,
    )
    globoo: bpy.props.BoolProperty(
        name="move", description="global (world) or local (object) axis", default=True
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("curves", "curves", "curves"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.culoc[pool.culoc_idx]
        self.fac = item.fac
        self.axis = item.axis
        self.globoo = item.globoo
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.culoc[pool.culoc_idx]
        item.fac = self.fac
        item.axis = self.axis
        item.globoo = self.globoo
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"culoc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"curves", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Curves", "Groups"), True)
        if self.selview in {"points", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"), False)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Translation", "Axis", "Factor")
        for n in names:
            row = sc.row(align=True)
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        cap = "global axis" if self.globoo else "local axis"
        row.prop(self, "globoo", text=cap, toggle=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


# ---- CURVE ROTATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_curot_edit(bpy.types.Operator):
    bl_label = "Curve Rotations"
    bl_idname = "ptdblnpopc.curot_edit"
    bl_description = "curve rotations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    axis: bpy.props.FloatVectorProperty(
        name="axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    angle: bpy.props.FloatProperty(
        name="angle", description="rotation angle", default=0, subtype="ANGLE"
    )
    pivot: bpy.props.FloatVectorProperty(
        name="pivot", size=3, default=(0, 0, 0), description="rotation pivot"
    )
    globoo: bpy.props.BoolProperty(
        name="spin",
        description="global (world) or local (object) space (axis and pivot)",
        default=True,
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("curves", "curves", "curves"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.curot[pool.curot_idx]
        self.axis = item.axis
        self.angle = item.angle
        self.pivot = item.pivot
        self.globoo = item.globoo
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.curot[pool.curot_idx]
        item.axis = self.axis
        item.angle = self.angle
        item.pivot = self.pivot
        item.globoo = self.globoo
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"curot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"curves", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Curves", "Groups"), True)
        if self.selview in {"points", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"), False)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Rotation", "Axis", "Angle", "Pivot")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        cap = "global space" if self.globoo else "local space"
        row.prop(self, "globoo", text=cap, toggle=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "angle", text="")
        row = sc.row(align=True)
        row.prop(self, "pivot", text="")


# ---- CURVE BEVEL DEPTH COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_cudep_edit(bpy.types.Operator):
    bl_label = "Curve Bevel Depth"
    bl_idname = "ptdblnpopc.cudep_edit"
    bl_description = "curve bevel depth"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(name="factor", description="bevel depth", default=0.25)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        d = item.nprams.to_dct()
        for key in d.keys():
            setattr(self.nprams, key, d[key])

    def copy_to_pg(self, item):
        d = self.nprams.to_dct()
        for key in d.keys():
            setattr(item.nprams, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.cudep[pool.cudep_idx]
        self.fac = item.fac
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.cudep[pool.cudep_idx]
        item.fac = self.fac
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"cudep_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        ModPDOP.params_layout_draw(box, self.nprams, ("Curves", "Groups"), False)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text="Factor")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


# ---- CURVE POINT RADIUS COLLECTION ITEM EDITOR


class PTDBLNPOPC_OT_pnrad_edit(bpy.types.Operator):
    bl_label = "Curve Point Radius"
    bl_idname = "ptdblnpopc.pnrad_edit"
    bl_description = "curve point radius"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    use_profile: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(name="factor", description="point radius", default=1.0)
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("curves", "curves", "curves"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPC_params)

    def copy_from_pg(self, item):
        d = item.nprams.to_dct()
        for key in d.keys():
            setattr(self.nprams, key, d[key])
        if self.use_profile:
            d = item.iprams.to_dct()
            for key in d.keys():
                setattr(self.iprams, key, d[key])

    def copy_to_pg(self, item):
        d = self.nprams.to_dct(exclude={"npts"})
        for key in d.keys():
            setattr(item.nprams, key, d[key])
        if self.use_profile:
            d = self.iprams.to_dct(exclude={"npts"})
            for key in d.keys():
                setattr(item.iprams, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopc_pool
        item = pool.pnrad[pool.pnrad_idx]
        self.use_profile = pool.use_profile
        self.fac = item.fac
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopc_pool
        pool.update_ok = False
        item = pool.pnrad[pool.pnrad_idx]
        item.fac = self.fac
        self.copy_to_pg(item)
        try:
            ModPOPC.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pnrad_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.use_profile:
            if self.selview in {"curves", "both"}:
                box = layout.box()
                ModPDOP.params_layout_draw(box, self.nprams, ("Curves", "Groups"), True)
            if self.selview in {"points", "both"}:
                box = layout.box()
                ModPDOP.params_layout_draw(
                    box, self.iprams, ("Points", "Groups"), False
                )
        else:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"), False)
        if self.use_profile:
            row = layout.row(align=True)
            row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text="Factor")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPC_vec3,
    PTDBLNPOPC_anim_index,
    PTDBLNPOPC_anim_mirror,
    PTDBLNPOPC_anim_amount,
    PTDBLNPOPC_anim_rots,
    PTDBLNPOPC_tmp_states,
    PTDBLNPOPC_batchcoll_toggle,
    PTDBLNPOPC_params,
    PTDBLNPOPC_pathed,
    PTDBLNPOPC_profed,
    PTDBLNPOPC_batchcoll_update,
    PTDBLNPOPC_curve,
    PTDBLNPOPC_path,
    PTDBLNPOPC_prof,
    PTDBLNPOPC_blnd,
    PTDBLNPOPC_pathloc,
    PTDBLNPOPC_pathrot,
    PTDBLNPOPC_profloc,
    PTDBLNPOPC_profrot,
    PTDBLNPOPC_culoc,
    PTDBLNPOPC_curot,
    PTDBLNPOPC_cudep,
    PTDBLNPOPC_pnrad,
    PTDBLNPOPC_noiz,
    PTDBLNPOPC_rngs,
    PTDBLNPOPC_attitude,
    PTDBLNPOPC_track_actions,
    PTDBLNPOPC_track,
    PTDBLNPOPC_anicalc,
    PTDBLNPOPC_pool,
    PTDBLNPOPC_OT_path_edit,
    PTDBLNPOPC_OT_pathloc_edit,
    PTDBLNPOPC_OT_pathrot_edit,
    PTDBLNPOPC_OT_prof_edit,
    PTDBLNPOPC_OT_blnd_edit,
    PTDBLNPOPC_OT_profloc_edit,
    PTDBLNPOPC_OT_profrot_edit,
    PTDBLNPOPC_OT_culoc_edit,
    PTDBLNPOPC_OT_curot_edit,
    PTDBLNPOPC_OT_cudep_edit,
    PTDBLNPOPC_OT_pnrad_edit,
)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.ptdblnpopc_params = bpy.props.PointerProperty(
        type=PTDBLNPOPC_params
    )
    bpy.types.Scene.ptdblnpopc_pathed = bpy.props.PointerProperty(
        type=PTDBLNPOPC_pathed
    )
    bpy.types.Scene.ptdblnpopc_profed = bpy.props.PointerProperty(
        type=PTDBLNPOPC_profed
    )
    bpy.types.Scene.ptdblnpopc_pool = bpy.props.PointerProperty(type=PTDBLNPOPC_pool)


def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ptdblnpopc_pool
    del bpy.types.Scene.ptdblnpopc_profed
    del bpy.types.Scene.ptdblnpopc_pathed
    del bpy.types.Scene.ptdblnpopc_params
