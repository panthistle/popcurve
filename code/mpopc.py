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

from random import seed, randint, uniform
from mathutils import Vector

from . import mdata as ModDATA


# ------------------------------------------------------------------------------
#
# ------------------------------ CURVE -----------------------------------------


def create_nurbs(ncus, pts, cyclic, endpts, fcaps, smooth, ures, bres, coll):
    name = f"{coll.name}_item"
    for i in range(ncus):
        cd = bpy.data.curves.new(name, "CURVE")
        cl = cd.splines.new(type="NURBS")
        cl.points.add(pts - 1)
        vflat = [0, 0, 0, 1] * pts
        cl.points.foreach_set("co", vflat)
        cl.use_cyclic_u = cyclic
        cl.use_endpoint_u = endpts
        cd.dimensions = "3D"
        cd.fill_mode = "FULL"
        cd.twist_smooth = smooth
        cd.resolution_u = ures
        cd.bevel_resolution = bres
        cd.use_fill_caps = fcaps
        ob = bpy.data.objects.new(name, cd)
        coll.objects.link(ob)
    return coll.objects[:]


def curves_create(ncus, pts, cu, coll):
    spl_type = cu.spline
    cyclic = cu.cyclic
    smooth = cu.smooth
    ures = cu.ures
    bres = cu.bevres
    endpts = False if cyclic else cu.endpoints
    fcaps = False if cyclic else cu.fillcaps
    if spl_type == "NURBS":
        return create_nurbs(ncus, pts, cyclic, endpts, fcaps, smooth, ures, bres, coll)
    name = f"{coll.name}_item"
    for i in range(ncus):
        cd = bpy.data.curves.new(name, "CURVE")
        cl = cd.splines.new(type="POLY")
        cl.points.add(pts - 1)
        vflat = [0, 0, 0, 1] * pts
        cl.points.foreach_set("co", vflat)
        cl.use_cyclic_u = cyclic
        cd.dimensions = "3D"
        cd.fill_mode = "FULL"
        cd.twist_smooth = smooth
        cd.bevel_resolution = bres
        cd.use_fill_caps = fcaps
        ob = bpy.data.objects.new(name, cd)
        coll.objects.link(ob)
    return coll.objects[:]


# ------------------------------------------------------------------------------
#
# ------------------------- SCENE UPDATES --------------------------------------


def noiz_locs(locs, axis, amp, ns):
    val = sum(1 if i else 0 for i in axis) * amp
    if not val:
        return locs
    seed(ns)
    return [
        [loc + Vector((i * uniform(-amp, amp) for i in axis)) for loc in vls]
        for vls in locs
    ]


def new_pop_instance(pool):
    path = pool.path
    path.clean = (path.provider != "custom") or (len(path.pathed.upv) > 2)
    if not path.clean:
        raise Exception("user path, not enough verts")
    if pool.use_profile:
        prof = pool.prof
        prof.clean = (prof.provider != "custom") or (len(prof.profed.upv) > 2)
        if not prof.clean:
            raise Exception("user profile, not enough verts")
        prof_dct = prof.to_dct()
    else:
        prof_dct = None
    pop = ModDATA.PopEx(pool.to_dct(), path.to_dct(), prof_dct)
    return pop


def update_associations(pool, dct):
    ncus = dct["ncus"]
    pool.ncus = ncus
    cpts = dct["cpts"]
    pool.cpts = cpts
    rings = dct["rings"]
    rpts = dct["rpts"]
    pool.path.pathed.npts = rings
    for item in pool.pathloc:
        item.nprams.npts = rings
    for item in pool.pathrot:
        item.nprams.npts = rings
    if pool.use_profile:
        pool.prof.profed.npts = rpts
        for item in pool.blnd:
            item.blnded.npts = rpts
            item.nprams.npts = rings
            item.iprams.npts = rpts
        for item in pool.profloc:
            item.nprams.npts = rings
            item.iprams.npts = rpts
        for item in pool.profrot:
            item.nprams.npts = rings
            item.iprams.npts = rpts
        for item in pool.culoc:
            item.nprams.npts = ncus
            item.iprams.npts = cpts
        for item in pool.curot:
            item.nprams.npts = ncus
            item.iprams.npts = cpts
        for item in pool.cudep:
            item.nprams.npts = ncus
        for item in pool.pnrad:
            item.nprams.npts = ncus
            item.iprams.npts = cpts
    else:
        for item in pool.pnrad:
            item.nprams.npts = cpts


def pop_update(pop, pool):
    for item in pool.pathloc:
        if item.active:
            pop.path_edlocations(item.to_dct())
    for item in pool.pathrot:
        if item.active:
            pop.path_edrotations(item.to_dct())
    for item in pool.pnrad:
        if item.active:
            pop.curve_radius(item.to_dct())
    if pool.use_profile:
        for item in pool.blnd:
            if item.active:
                pop.blnd_edlocations(item.to_dct())
        for item in pool.profloc:
            if item.active:
                pop.prof_edlocations(item.to_dct())
        for item in pool.profrot:
            if item.active:
                pop.prof_edrotations(item.to_dct())
        pop.compile_pop_data()
        for item in pool.culoc:
            if item.active:
                pop.curv_edlocations(item.to_dct())
        for item in pool.curot:
            if item.active:
                pop.curv_edrotations(item.to_dct())
        for item in pool.cudep:
            if item.active:
                pop.curve_depth(item.to_dct())


def curves_update(pool, pop, oblst, sindz_on):
    pop_update(pop, pool)
    locs = pop.get_pntlocs()
    noiz = pool.noiz
    if noiz.active:
        locs = noiz_locs(locs, noiz.vfac, noiz.ampli, noiz.nseed)
    rads = pop.get_pntrads()
    deps = pop.get_bevdeps()
    if sindz_on:
        ncus = pool.ncus
        sindz = pool.rngs.sindz_get()
        locs = [locs[i] for i in range(ncus) if i in sindz]
        rads = [rads[i] for i in range(ncus) if i in sindz]
        deps = [deps[i] for i in range(ncus) if i in sindz]
    for ob, vls, rls, dv in zip(oblst, locs, rads, deps):
        cu = ob.data
        cu.bevel_depth = dv
        cl = cu.splines[0]
        for p, loc, rad in zip(cl.points, vls, rls):
            p.co = loc[:] + (1.0,)
            p.radius = rad


def rngids_calc(npts, k, itm, gap, reps):
    ids = [i % npts for i in range(k, k + itm)]
    if (npts == itm) or (reps < 2):
        return ids
    iinc = gap + 1
    for i in range(reps - 1):
        k = ids[-1] + iinc
        ids += [j % npts for j in range(k, k + itm)]
    return ids[:npts]


def range_indices_update(rngs, items):
    rngs.rbeg = rngs.rbeg % items
    rngs.ritm = min(rngs.ritm, items)
    rngs.rgap = min(rngs.rgap, items - rngs.ritm)
    grp = rngs.ritm + rngs.rgap
    hi = items // grp
    hi += 0 if items % grp < rngs.ritm else 1
    rngs.rstp = min(rngs.rstp, hi)
    inds = rngids_calc(items, rngs.rbeg, rngs.ritm, rngs.rgap, rngs.rstp)
    if rngs.invert:
        inds_set = set(inds)
        inds = [i for i in range(items) if i not in inds_set]
    if rngs.rndsel:
        seed(rngs.nseed)
        inds_len = len(inds)
        inds = [inds[randint(0, inds_len - 1)] for _ in range(inds_len)]
    inds_set = set(i for i in inds if i < items)
    rngs.sindz_set(inds_set)
    return len(inds_set)


def scene_update_newset(scene, replace_set, rename_coll):
    pool = scene.ptdblnpopc_pool
    pop = new_pop_instance(pool)
    dct = pop.get_associations()
    update_associations(pool, dct)
    live_curves = pool.ncus
    sindz_on = pool.use_profile and pool.rngs.active
    if sindz_on:
        live_curves = range_indices_update(pool.rngs, live_curves)
    if pool.setcoll and replace_set:
        name = pool.setcoll_name if rename_coll else pool.setcoll.name
        bpy.data.collections.remove(pool.setcoll)
        print("---- popcurve replace: delete trash")
        bpy.ops.outliner.orphans_purge(do_recursive=True)
    else:
        name = pool.setcoll_name
    pool.setcoll = bpy.data.collections.new(name)
    scene.collection.children.link(pool.setcoll)
    oblst = curves_create(live_curves, pool.cpts, pool.curve, pool.setcoll)
    curves_update(pool, pop, oblst, sindz_on)


def scene_update(scene):
    pool = scene.ptdblnpopc_pool
    pop = new_pop_instance(pool)
    dct = pop.get_associations()
    sindz_on = pool.use_profile and pool.rngs.active
    if sindz_on:
        dummy = range_indices_update(pool.rngs, dct["ncus"])
    oblst = pool.setcoll.objects[:]
    curves_update(pool, pop, oblst, sindz_on)
