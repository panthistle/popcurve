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


from random import random, seed, shuffle
from mathutils import Quaternion, Vector

from . import mpath as ModPATH


# ------------------------------------------------------------------------------
#
# ---------------------------- POPEX HELPERS -----------------------------------


def falloff_lists(npts, dct):
    itm = dct["itm"]
    reps = dct["reps"]
    k = dct["idx"]
    repfoff = dct["repfoff"]
    foffstp = dct["repfstp"]
    mir = dct["mir"]
    iinc = dct["gap"] + 1
    ditm = itm
    dstp = 1
    if dct["rev"]:
        iinc = -iinc
        ditm = -itm
        dstp = -1
    i_lst = [i % npts for i in range(k, k + ditm, dstp)]
    if (itm == 1) or (dct["ease"] == "OFF"):
        v_lst = [1] * itm
    else:
        div = itm if dct["cyc"] else itm - 1
        v_lst = ModPATH.it_list(dct["ease"], 1 / div, dct["exp"], mir, itm)
        sref = dct["reflect"]
        if sref == "3":
            v_lst = [i if i >= 0.5 else 1 - i for i in v_lst]
        elif sref == "2":
            v_lst = [i if i <= 0.5 else 1 - i for i in v_lst]
        elif sref == "1":
            v_lst = [1 - i for i in v_lst]
    if (npts == itm) or (reps == 1):
        return i_lst, v_lst
    tlst = v_lst.copy()
    if foffstp > 1:
        fct = 1
        for i in range(reps - 1):
            foff = 1
            fct += 1
            if fct > foffstp:
                fct = 1
                foff = repfoff
            k = i_lst[-1] + iinc
            i_lst += [j % npts for j in range(k, k + ditm, dstp)]
            tlst = [foff * j for j in tlst]
            v_lst += tlst
        return i_lst[:npts], v_lst[:npts]
    for i in range(reps - 1):
        k = i_lst[-1] + iinc
        i_lst += [j % npts for j in range(k, k + ditm, dstp)]
        tlst = [repfoff * j for j in tlst]
        v_lst += tlst
    return i_lst[:npts], v_lst[:npts]


def shuffparams_get(npts, params):
    ids, fvs = falloff_lists(npts, params)
    rndval = params["rndval"]
    shuff = False
    if params["rnduse"]:
        seed(params["rndseed"])
        if rndval:
            fvs = [(1 - random() * rndval) * v for v in fvs]
        shuff = params["rndshuff"]
    return ids, fvs, shuff


def params_get(npts, params):
    ids, fvs = falloff_lists(npts, params)
    rndval = params["rndval"]
    if params["rnduse"] and rndval:
        seed(params["rndseed"])
        fvs = [(1 - random() * rndval) * v for v in fvs]
    return ids, fvs


def attitude_rots(locs, cyclic, dv, up="X"):
    if cyclic:
        l2 = locs[-1]
        locs.append(locs[0])
    else:
        l2 = locs[0] + (locs[0] - locs[1])
        locs.append(locs[-1] + (locs[-1] - locs[-2]))
    a = locs[1] - l2
    if isinstance(dv, str):
        rots = [a.to_track_quat(dv, up)]
        for i in range(1, len(locs) - 1):
            rots.append((locs[i + 1] - locs[i - 1]).to_track_quat(dv, up))
    else:
        rots = [dv.rotation_difference(a)]
        for i in range(1, len(locs) - 1):
            b = locs[i + 1] - locs[i - 1]
            rots.append(a.rotation_difference(b) @ rots[-1])
            a = b
    locs.pop()
    return rots


def dv_from_axis(axis):
    if axis in ("X", "-X"):
        return Vector((1, 0, 0)) if axis == "X" else Vector((-1, 0, 0))
    if axis in ("Y", "-Y"):
        return Vector((0, 1, 0)) if axis == "Y" else Vector((0, -1, 0))
    return Vector((0, 0, 1)) if axis == "Z" else Vector((0, 0, -1))


def sumvals(*args):
    return max(0, sum(args))


# ------------------------------------------------------------------------------
#
# ----------------------------- POPEX CLASS ------------------------------------


class PopEx:
    """path-on-path class"""

    def __init__(self, pool_dct, path_dct, prof_dct):
        self._set_path(path_dct)
        self._set_profile(prof_dct)
        self._set_associations(pool_dct)

    # INITIALIZE

    def _set_path(self, dct):
        self._path = getattr(ModPATH, dct["provider"].capitalize())(dct)
        self._pathclosed = dct["closed"]
        self._pathlocs = self._path.get_locs()
        self._rings = self._path.npts
        self._pathedlocs = []
        self._pathed_lopts = []
        self._pathedrots = []
        self._pathed_rpivs = []
        self._pathed_raxes = []
        self._pathed_ropts = []

    def _set_profile(self, dct):
        if dct:
            self._profile = getattr(ModPATH, dct["provider"].capitalize())(dct)
            self._proflocs = self._profile.get_locs()
            self._rpts = self._profile.npts
            self._profedlocs = []
            self._profed_lopts = []
            self._profedrots = []
            self._profed_rpivs = []
            self._profed_raxes = []
        else:
            self._profile = None
            self._rpts = 1

    def _set_associations(self, dct):
        if self._profile:
            self._direction = dct["direction"]
            self._pathori = dct["pathori"]
            self._path_track = dct["pathtrack"]
            self._path_trackvec = dv_from_axis(dct["pathtrack"])
            self._path_up = dct["pathup"]
            self._path_upfixed = dct["pathupfixed"]
            self._curvedlocs = []
            self._curved_lopts = []
            self._curvedrots = []
            self._curved_rpivs = []
            self._curved_raxes = []
            self._curved_rglob = []
            self._poplocs = []
            self._poprots = []
        else:
            self._direction = "path"
            self._pathori = False
        self._cubevdep = dct["bevdep"]
        self._cubevdeplst = []
        self._cufacbeg = dct["cufacbeg"]
        self._cufacend = dct["cufacend"]
        self._cubevfaclst = []
        self._cufacitmlst = []
        self._cupntrad = dct["pntrad"]
        self._cupntradlst = []
        if self._direction == "prof":
            self._ncus = self._rings
            self._cpts = self._rpts
        else:
            self._ncus = self._rpts
            self._cpts = self._rings

    # MODIFY

    def _pathedloc_get(self, locs, dct):
        nids, nfvs = params_get(self._rings, dct["nprams"])
        axis = Vector(dct["axis"]) * dct["fac"]
        if dct["absboo"]:
            for i, f in zip(nids, nfvs):
                if f:
                    locs[i] = axis * f
        else:
            for i, f in zip(nids, nfvs):
                if f:
                    dv = self._pathlocs[i].normalized()
                    for j in range(3):
                        locs[i][j] = dv[j] * axis[j] * f
        return locs

    def path_edlocations(self, dct):
        if not self._profile:
            self._pathed_lopts.append(dct["bbrot"])
        elif self._profile and self._pathori:
            self._pathed_lopts.append(dct["bbatt"])
        else:
            self._pathed_lopts.append(True)
        locs = [Vector() for _ in range(self._rings)]
        if not dct["fac"]:
            self._pathedlocs.append(locs)
            return
        self._pathedlocs.append(self._pathedloc_get(locs, dct))

    def _pathedrot_get(self, nprams):
        nids, nfvs = params_get(self._rings, nprams)
        lst = [0] * self._rings
        for i, f in zip(nids, nfvs):
            lst[i] = f
        return lst

    def path_edrotations(self, dct):
        axis = dct["axis"]
        self._pathed_raxes.append(axis)
        self._pathed_rpivs.append(Vector(dct["pivot"]))
        bbatt = dct["bbatt"] if self._profile and self._pathori else "before"
        brots = dct["brots"] if self._profile else True
        self._pathed_ropts.append([bbatt, brots])
        fls = self._pathedrot_get(dct["nprams"])
        angle = dct["angle"]
        self._pathedrots.append([Quaternion(axis, angle * f) for f in fls])

    def _profedloc_get(self, locs, dct):
        ids, fvs = params_get(self._rpts, dct["iprams"])
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        axis = Vector(dct["axis"]) * dct["fac"]
        if dct["absboo"]:
            for i, f in zip(nids, nfvs):
                if f:
                    if shuff:
                        shuffle(fvs)
                    for j, p in zip(ids, fvs):
                        if p:
                            locs[i][j] = axis * (f * p)
        else:
            for i, f in zip(nids, nfvs):
                if f:
                    if shuff:
                        shuffle(fvs)
                    for j, p in zip(ids, fvs):
                        if p:
                            dv = self._proflocs[j].normalized()
                            p *= f
                            for k in range(2):
                                locs[i][j][k] = dv[k] * axis[k] * p
        return locs

    def prof_edlocations(self, dct):
        self._profed_lopts.append(dct["bbrot"])
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if not dct["fac"]:
            self._profedlocs.append(locs)
            return
        self._profedlocs.append(self._profedloc_get(locs, dct))

    def _blndedloc_get(self, locs, dct):
        provider = dct["provider"]
        dct[f"res_{provider[:3]}"] = self._rpts
        bln_prof = getattr(ModPATH, provider.capitalize())(dct)
        blocs = bln_prof.get_locs()
        k = dct["idx"] % self._rpts
        blocs = blocs[k:] + blocs[:k]
        if dct["rot_align"]:
            q = Quaternion((0, 0, 1), dct["rot_align"])
            blocs = [q @ loc for loc in blocs]
        ids, fvs = params_get(self._rpts, dct["iprams"])
        nids, nfvs, shuff = shuffparams_get(self._rings, dct["nprams"])
        fac = dct["fac"]
        for i, f in zip(nids, nfvs):
            if f:
                f *= fac
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        locs[i][j] = (blocs[j] - self._proflocs[j]) * (f * p)
        return locs

    def blnd_edlocations(self, dct):
        self._profed_lopts.append(True)
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if not dct["fac"]:
            self._profedlocs.append(locs)
            return
        self._profedlocs.append(self._blndedloc_get(locs, dct))

    def _profedrot_get(self, nprams, iprams):
        nids, nfvs, shuff = shuffparams_get(self._rings, nprams)
        ids, fvs = params_get(self._rpts, iprams)
        lst = [[0] * self._rpts for _ in range(self._rings)]
        for i, f in zip(nids, nfvs):
            if f:
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        lst[i][j] = f * p
        return lst

    def prof_edrotations(self, dct):
        axis = dct["axis"]
        self._profed_raxes.append(axis)
        self._profed_rpivs.append(Vector(dct["pivot"]))
        lst = self._profedrot_get(dct["nprams"], dct["iprams"])
        angle = dct["angle"]
        self._profedrots.append(
            [[Quaternion(axis, angle * f) for f in fls] for fls in lst]
        )

    def _curvedloc_get(self, locs, dct):
        ids, fvs = params_get(self._cpts, dct["iprams"])
        nids, nfvs, shuff = shuffparams_get(self._ncus, dct["nprams"])
        axis = Vector(dct["axis"]) * dct["fac"]
        for i, f in zip(nids, nfvs):
            if f:
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        locs[i][j] = axis * (f * p)
        return locs

    def curv_edlocations(self, dct):
        self._curved_lopts.append(dct["globoo"])
        locs = [[Vector() for _ in range(self._cpts)] for _ in range(self._ncus)]
        if not dct["fac"]:
            self._curvedlocs.append(locs)
            return
        self._curvedlocs.append(self._curvedloc_get(locs, dct))

    def _curvedrot_get(self, nprams, iprams):
        nids, nfvs, shuff = shuffparams_get(self._ncus, nprams)
        ids, fvs = params_get(self._cpts, iprams)
        lst = [[0] * self._cpts for _ in range(self._ncus)]
        for i, f in zip(nids, nfvs):
            if f:
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        lst[i][j] = f * p
        return lst

    def curv_edrotations(self, dct):
        angle = dct["angle"]
        axis = Vector(dct["axis"])
        self._curved_raxes.append(axis)
        self._curved_rpivs.append(Vector(dct["pivot"]))
        lst = self._curvedrot_get(dct["nprams"], dct["iprams"])
        if dct["globoo"] or not self._poprots:
            self._curved_rglob.append(True)
            self._curvedrots.append(
                [[Quaternion(axis, f * angle) for f in fls] for fls in lst]
            )
        else:
            self._curved_rglob.append(False)
            self._curvedrots.append(
                [
                    [Quaternion(q @ axis, f * angle) for q, f in zip(qls, fls)]
                    for qls, fls in zip(self._poprots, lst)
                ]
            )

    def _cudepth_get(self, vlst, val, nprams):
        if self._ncus == 1:
            vlst[0] = val
            return vlst
        nids, nfvs = params_get(self._ncus, nprams)
        for i, f in zip(nids, nfvs):
            if f:
                vlst[i] = f * val
        return vlst

    def curve_depth(self, dct):
        vlst = [0] * self._ncus
        val = dct["fac"] - self._cubevdep
        if not val:
            self._cubevdeplst.append(vlst)
            return
        self._cubevdeplst.append(self._cudepth_get(vlst, val, dct["nprams"]))

    def _cufactor_get(self, vlst, val, nprams):
        if self._ncus == 1:
            vlst[0] = val
            return vlst
        nids, nfvs = params_get(self._ncus, nprams)
        for i, f in zip(nids, nfvs):
            if f:
                vlst[i] = f * val
        return vlst

    def curve_factor(self, dct):
        val = dct["fac"]
        self._cufacitmlst.append(dct["affect"])
        vlst = [0] * self._ncus
        if not val:
            self._cubevfaclst.append(vlst)
            return
        self._cubevfaclst.append(self._cufactor_get(vlst, val, dct["nprams"]))

    def _curadius_get(self, vlst, val, dct):
        if self._ncus == 1:
            nids, nfvs = params_get(self._cpts, dct["nprams"])
            for i, f in zip(nids, nfvs):
                if f:
                    vlst[0][i] = f * val
            return vlst
        nids, nfvs, shuff = shuffparams_get(self._ncus, dct["nprams"])
        ids, fvs = params_get(self._cpts, dct["iprams"])
        for i, f in zip(nids, nfvs):
            if f:
                f *= val
                if shuff:
                    shuffle(fvs)
                for j, p in zip(ids, fvs):
                    if p:
                        vlst[i][j] = f * p
        return vlst

    def curve_radius(self, dct):
        vlst = [[0] * self._cpts for _ in range(self._ncus)]
        val = dct["fac"] - self._cupntrad
        if not val:
            self._cupntradlst.append(vlst)
            return
        self._cupntradlst.append(self._curadius_get(vlst, val, dct))

    # RETURN

    def get_associations(self):
        d = {
            "ncus": self._ncus,
            "cpts": self._cpts,
            "rings": self._rings,
            "rpts": self._rpts,
        }
        return d

    def _path_attitude_update(self, orilocs):
        cyclic = self._pathclosed
        if self._path_upfixed:
            return attitude_rots(orilocs, cyclic, self._path_track, self._path_up)
        return attitude_rots(orilocs, cyclic, self._path_trackvec)

    def _prof_edrots_locs(self):
        rots = []
        locs = [self._proflocs] * self._rings
        after = []
        for boo, vls in zip(self._profed_lopts, self._profedlocs):
            if boo:
                locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(locs, vls)]
            elif after:
                after = [[a + b for a, b in zip(la, lb)] for la, lb in zip(after, vls)]
            else:
                after = vls
        for qls, p in zip(self._profedrots, self._profed_rpivs):
            locs = [
                [q @ (v - p) + p for q, v in zip(ql, vl)] for ql, vl in zip(qls, locs)
            ]
            if rots:
                rots = [[a @ b for a, b in zip(la, lb)] for la, lb in zip(qls, rots)]
            else:
                rots = qls
        if after:
            locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(after, locs)]
        return locs, rots

    def _path_loc_lists(self):
        locs = self._pathlocs
        indy = []
        for boo, vls in zip(self._pathed_lopts, self._pathedlocs):
            if boo:
                locs = [loc + v for loc, v in zip(locs, vls)]
            elif indy:
                indy = [loc + v for loc, v in zip(indy, vls)]
            else:
                indy = vls
        return locs, indy

    def _path_edrots_locs(self):
        locs, edlocs = self._path_loc_lists()
        befo_r, rots, afte_p = [], [], []
        for ols, qls, p in zip(
            self._pathed_ropts, self._pathedrots, self._pathed_rpivs
        ):
            if ols[0] == "before":
                if ols[1]:
                    locs = [q @ (v - p) + p for q, v in zip(qls, locs)]
                    if edlocs:
                        edlocs = [q @ (v - p) + p for q, v in zip(qls, edlocs)]
                elif befo_r:
                    befo_r = [q @ b for q, b in zip(qls, befo_r)]
                else:
                    befo_r = qls
            else:
                if rots:
                    rots = [q @ a for q, a in zip(qls, rots)]
                else:
                    rots = qls
                if ols[1]:
                    afte_p.append([qls, p])
        if rots:
            attrots = self._path_attitude_update(locs)
            rots = [q @ a for q, a in zip(rots, attrots)]
        else:
            rots = self._path_attitude_update(locs)
        if befo_r:
            rots = [q @ b for q, b in zip(rots, befo_r)]
        if edlocs:
            locs = [loc + v for loc, v in zip(locs, edlocs)]
        for qls, p in afte_p:
            locs = [q @ (v - p) + p for q, v in zip(qls, locs)]
        return locs, rots

    def _path_edrots_locs_noatt(self):
        locs = self._pathlocs
        for vls in self._pathedlocs:
            locs = [loc + v for loc, v in zip(locs, vls)]
        rots = []
        for ols, qls, p in zip(
            self._pathed_ropts, self._pathedrots, self._pathed_rpivs
        ):
            if ols[1]:
                locs = [q @ (v - p) + p for q, v in zip(qls, locs)]
            if rots:
                rots = [q @ a for q, a in zip(qls, rots)]
            else:
                rots = qls
        return locs, rots

    def compile_pop_data(self):
        locs, rots = self._prof_edrots_locs()
        if not self._pathori:
            pa_l, pa_r = self._path_edrots_locs_noatt()
        else:
            pa_l, pa_r = self._path_edrots_locs()
        if pa_r:
            locs = [[p + q @ v for v in vls] for p, q, vls in zip(pa_l, pa_r, locs)]
            if rots:
                rots = [[a @ b for b in qls] for a, qls in zip(pa_r, rots)]
            else:
                rots = [[a for _ in range(self._rpts)] for a in pa_r]
        else:
            locs = [[p + v for v in vls] for p, vls in zip(pa_l, locs)]
        if self._direction == "path":
            locs = [[vls[i] for vls in locs] for i in range(self._rpts)]
            if rots:
                rots = [[qls[i] for qls in rots] for i in range(self._rpts)]
        self._poplocs = locs
        self._poprots = rots

    def _curved_loc_lists(self):
        wlocs = []
        olocs = []
        for boo, vls in zip(self._curved_lopts, self._curvedlocs):
            if boo:
                if wlocs:
                    wlocs = [
                        [a + b for a, b in zip(la, lb)] for la, lb in zip(wlocs, vls)
                    ]
                else:
                    wlocs = vls
            elif olocs:
                olocs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(olocs, vls)]
            else:
                olocs = vls
        return wlocs, olocs

    def _curvarray_locs(self):
        locs = self._poplocs
        rots = self._poprots
        for qls, piv, b in zip(
            self._curvedrots, self._curved_rpivs, self._curved_rglob
        ):
            if b:
                locs = [
                    [q @ (v - piv) + piv for q, v in zip(ql, vl)]
                    for ql, vl in zip(qls, locs)
                ]
            else:
                for i, (ql, vl, rl) in enumerate(zip(qls, locs, rots)):
                    cuo = sum(vl, Vector()) / self._cpts
                    pl = [cuo + r @ piv for r in rl]
                    locs[i] = [q @ (v - p) + p for q, v, p in zip(ql, vl, pl)]
        wcs, ocs = self._curved_loc_lists()
        if ocs:
            for qls in self._curvedrots:
                if rots:
                    rots = [
                        [a @ b for a, b in zip(la, lb)] for la, lb in zip(qls, rots)
                    ]
                else:
                    rots = qls
            if rots:
                locs = [
                    [a + q @ b for a, q, b in zip(la, lq, lb)]
                    for la, lq, lb in zip(locs, rots, ocs)
                ]
            else:
                locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(locs, ocs)]
        if wcs:
            locs = [[a + b for a, b in zip(la, lb)] for la, lb in zip(locs, wcs)]
        return locs

    def get_pntlocs(self):
        if not self._profile:
            locs, edlocs = self._path_loc_lists()
            for qls, p in zip(self._pathedrots, self._pathed_rpivs):
                locs = [q @ (loc - p) + p for q, loc in zip(qls, locs)]
            if edlocs:
                locs = [loc + v for loc, v in zip(locs, edlocs)]
            return [locs]
        return self._curvarray_locs()

    def get_bevdeps(self):
        dps = [self._cubevdep] * self._ncus
        if len(self._cubevdeplst) > 1:
            dps = list(map(sumvals, dps, *self._cubevdeplst))
        else:
            for lst in self._cubevdeplst:
                dps = [max(0, a + b) for a, b in zip(dps, lst)]
        return dps

    def get_bevfacs(self):
        begs = [self._cufacbeg] * self._ncus
        ends = [self._cufacend] * self._ncus
        for lst, i in zip(self._cubevfaclst, self._cufacitmlst):
            if i == "start":
                begs = [min(max(0, a + b), 1) for a, b in zip(begs, lst)]
            elif i == "end":
                ends = [min(max(0, a + b), 1) for a, b in zip(ends, lst)]
            else:
                begs = [min(max(0, a + b), 1) for a, b in zip(begs, lst)]
                ends = [min(max(0, a - b), 1) for a, b in zip(ends, lst)]
        return begs, ends

    def get_pntrads(self):
        rds = [[self._cupntrad] * self._cpts for _ in range(self._ncus)]
        if len(self._cupntradlst) > 1:
            rds = [
                list(map(sumvals, la, *lb)) for la, *lb in zip(rds, *self._cupntradlst)
            ]
        else:
            for lst in self._cupntradlst:
                rds = [
                    [max(0, a + b) for a, b in zip(la, lb)] for la, lb in zip(rds, lst)
                ]
        return rds

    # ANIMATION

    def path_anim_update(self, *args):
        self._path.anim_update(*args)
        self._pathlocs = self._path.get_locs()

    def prof_anim_update(self, *args):
        self._profile.anim_update(*args)
        self._proflocs = self._profile.get_locs()

    def pathedloc_anim_data(self, dct, idx):
        locs = [Vector() for _ in range(self._rings)]
        if dct["delta_change"]:
            if dct["fac"]:
                l_p = self._pathedlocs[idx]
                l_d = self._pathedloc_get(locs, dct)
                self._pathedlocs[idx] = [a + b for a, b in zip(l_p, l_d)]
            return
        if not dct["fac"]:
            self._pathedlocs[idx] = locs
            return
        self._pathedlocs[idx] = self._pathedloc_get(locs, dct)

    def pathedrot_anim_data(self, dct, bang, angle, use_facs, idx):
        if bang or use_facs:
            rots = self._pathedrots[idx]
            axis = self._pathed_raxes[idx]
            if not use_facs:
                q = Quaternion(axis, angle)
                self._pathedrots[idx] = [r @ q for r in rots]
                return
            fls = self._pathedrot_get(dct["nprams"])
            if bang:
                self._pathedrots[idx] = [
                    r @ Quaternion(axis, f * angle) for r, f in zip(rots, fls)
                ]
                return
            angle = dct["angle"]
            self._pathedrots[idx] = [Quaternion(axis, f * angle) for f in fls]

    def profedloc_anim_data(self, dct, idx):
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if dct["delta_change"]:
            if dct["fac"]:
                l_p = self._profedlocs[idx]
                l_d = self._profedloc_get(locs, dct)
                self._profedlocs[idx] = [
                    [a + b for a, b in zip(lp, ld)] for lp, ld in zip(l_p, l_d)
                ]
            return
        if not dct["fac"]:
            self._profedlocs[idx] = locs
            return
        self._profedlocs[idx] = self._profedloc_get(locs, dct)

    def blndedloc_anim_data(self, dct, idx):
        locs = [[Vector() for _ in range(self._rpts)] for _ in range(self._rings)]
        if not dct["fac"]:
            self._profedlocs[idx] = locs
            return
        self._profedlocs[idx] = self._blndedloc_get(locs, dct)

    def profedrot_anim_data(self, dct, bang, angle, use_facs, idx):
        if bang or use_facs:
            rots = self._profedrots[idx]
            axis = self._profed_raxes[idx]
            if not use_facs:
                q = Quaternion(axis, angle)
                self._profedrots[idx] = [[r @ q for r in rls] for rls in rots]
                return
            lst = self._profedrot_get(dct["nprams"], dct["iprams"])
            if bang:
                self._profedrots[idx] = [
                    [r @ Quaternion(axis, f * angle) for r, f in zip(rls, fls)]
                    for rls, fls in zip(rots, lst)
                ]
                return
            angle = dct["angle"]
            self._profedrots[idx] = [
                [Quaternion(axis, f * angle) for f in fls] for fls in lst
            ]

    def curvedloc_anim_data(self, dct, idx):
        locs = [[Vector() for _ in range(self._cpts)] for _ in range(self._ncus)]
        if dct["delta_change"]:
            if dct["fac"]:
                l_p = self._curvedlocs[idx]
                l_d = self._curvedloc_get(locs, dct)
                self._curvedlocs[idx] = [
                    [a + b for a, b in zip(lp, ld)] for lp, ld in zip(l_p, l_d)
                ]
            return
        if not dct["fac"]:
            self._curvedlocs[idx] = locs
            return
        self._curvedlocs[idx] = self._curvedloc_get(locs, dct)

    def _curvedrot_global_anim_data(self, dct, bang, angle, use_facs, idx):
        rots = self._curvedrots[idx]
        axis = self._curved_raxes[idx]
        if not use_facs:
            q = Quaternion(axis, angle)
            self._curvedrots[idx] = [[r @ q for r in rls] for rls in rots]
            return
        lst = self._curvedrot_get(dct["nprams"], dct["iprams"])
        if bang:
            self._curvedrots[idx] = [
                [r @ Quaternion(axis, f * angle) for r, f in zip(rls, fls)]
                for rls, fls in zip(rots, lst)
            ]
            return
        angle = dct["angle"]
        self._curvedrots[idx] = [
            [Quaternion(axis, f * angle) for f in fls] for fls in lst
        ]

    def curvedrot_anim_data(self, dct, bang, angle, use_facs, idx):
        if bang or use_facs:
            if dct["globoo"] or not self._poprots:
                self._curvedrot_global_anim_data(dct, bang, angle, use_facs, idx)
                return
            rots = self._curvedrots[idx]
            axis = self._curved_raxes[idx]
            if not use_facs:
                self._curvedrots[idx] = [
                    [r @ Quaternion(q @ axis, angle) for r, q in zip(rls, qls)]
                    for rls, qls in zip(rots, self._poprots)
                ]
                return
            lst = self._curvedrot_get(dct["nprams"], dct["iprams"])
            if bang:
                self._curvedrots[idx] = [
                    [
                        r @ Quaternion(q @ axis, f * angle)
                        for r, q, f in zip(rls, qls, fls)
                    ]
                    for rls, qls, fls in zip(rots, self._poprots, lst)
                ]
                return
            angle = dct["angle"]
            self._curvedrots[idx] = [
                [Quaternion(q @ axis, f * angle) for q, f in zip(qls, fls)]
                for qls, fls in zip(self._poprots, lst)
            ]

    def cudepth_anim_data(self, dct, idx):
        vlst = [0] * self._ncus
        val = dct["fac"]
        if dct["delta_change"]:
            if val:
                l_p = self._cubevdeplst[idx]
                l_d = self._cudepth_get(vlst, val, dct["nprams"])
                self._cubevdeplst[idx] = [a + b for a, b in zip(l_p, l_d)]
            return
        val = dct["fac"] - self._cubevdep
        if not val:
            self._cubevdeplst[idx] = vlst
            return
        self._cubevdeplst[idx] = self._cudepth_get(vlst, val, dct["nprams"])

    def cufactor_anim_data(self, dct, idx):
        vlst = [0] * self._ncus
        val = dct["fac"]
        if dct["delta_change"]:
            if val:
                l_p = self._cubevfaclst[idx]
                l_d = self._cufactor_get(vlst, val, dct["nprams"])
                self._cubevfaclst[idx] = [a + b for a, b in zip(l_p, l_d)]
            return
        if not val:
            self._cubevfaclst[idx] = vlst
            return
        self._cubevfaclst[idx] = self._cufactor_get(vlst, val, dct["nprams"])

    def curadius_anim_data(self, dct, idx):
        vlst = [[0] * self._cpts for _ in range(self._ncus)]
        val = dct["fac"]
        if dct["delta_change"]:
            if val:
                l_p = self._cupntradlst[idx]
                l_d = self._curadius_get(vlst, val, dct)
                self._cupntradlst[idx] = [
                    [a + b for a, b in zip(lp, ld)] for lp, ld in zip(l_p, l_d)
                ]
            return
        val = dct["fac"] - self._cupntrad
        if not val:
            self._cupntradlst[idx] = vlst
            return
        self._cupntradlst[idx] = self._curadius_get(vlst, val, dct)
