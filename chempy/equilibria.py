from __future__ import division, absolute_import

import math
import warnings
from itertools import chain
from collections import defaultdict
from functools import reduce, partial
from operator import mul, add

import numpy as np

from .chemistry import Reaction, ReactionSystem
from .util.arithmeticdict import ArithmeticDict
from .util.plotting import mpl_outside_legend


def reducemap(args, reduce_op, map_op):
    return reduce(reduce_op, map(map_op, *args))


def vec_dot_vec(vec1, vec2):
    # return np.dot(vec1, vec2)
    # return np.add.reduce(np.multiply(vec1, vec2))
    return reducemap((vec1, vec2), add, mul)


def prodpow(bases, exponents):
    if not hasattr(exponents, 'ndim') or exponents.ndim == 1:
        return reducemap((bases, exponents), mul, pow)
    else:
        return np.multiply.reduce(bases**exponents, axis=-1)
    # return reduce(mul, [factor ** exponent for factor, exponent
    #                     in zip(factors, exponents)])


def mat_dot_vec(iter_mat, iter_vec, iter_term=None):  # pure python (slow)
    if iter_term is None:
        return [vec_dot_vec(row, iter_vec) for row in iter_mat]
    else:
        # daxpy
        return [vec_dot_vec(row, iter_vec) + term for row, term
                in zip(iter_mat, iter_term)]


def equilibrium_quotient(concs, stoich):
    if not hasattr(concs, 'ndim') or concs.ndim == 1:
        tot = 1
    else:
        tot = np.ones(concs.shape[0])
        concs = concs.T

    for nr, conc in zip(stoich, concs):
        tot *= conc**nr
    return tot


def equilibrium_residual(rc, c0, stoich, K, activity_product=None):
    """
    Parameters
    ---------
    rc: float
        Reaction coordinate
    c0: array_like of reals
        concentrations
    stoich: tuple
        per specie stoichiometry coefficient
    K: float
        equilibrium constant
    activity_product: callable
        callback for calculating the activity product taking
        concentration as single parameter.
    """
    if not hasattr(stoich, 'ndim') or stoich.ndim == 1:
        c = c0 + stoich*rc
    else:
        c = c0 + np.dot(stoich, rc)
    Q = equilibrium_quotient(c, stoich)
    if activity_product is not None:
        Q *= activity_product(c)
    return K - Q


def get_rc_interval(stoich, c0):
    """ get reaction coordinate interval """
    limits = c0/stoich
    if np.any(limits < 0):
        upper = -np.max(limits[np.argwhere(limits < 0)])
    else:
        upper = 0

    if np.any(limits > 0):
        lower = -np.min(limits[np.argwhere(limits > 0)])
    else:
        lower = 0

    if lower is 0 and upper is 0:
        raise ValueError("0-interval")
    else:
        return lower, upper


def _solve_equilibrium_coord(c0, stoich, K, activity_product=None):
    from scipy.optimize import brentq
    mask, = np.nonzero(stoich)
    stoich_m = stoich[mask]
    c0_m = c0[mask]
    lower, upper = get_rc_interval(stoich_m, c0_m)
    # span = upper - lower
    return brentq(
        equilibrium_residual,
        lower,  # + delta_frac*span,
        upper,  # - delta_frac*span,
        (c0_m, stoich_m, K, activity_product)
    )


def solve_equilibrium(c0, stoich, K, activity_product=None):
    """
    Solve equilibrium concentrations by using scipy.optimize.brentq

    Parameters
    ----------
    c0: array_like
        Initial guess of equilibrium concentrations
    stoich: tuple
        per specie stoichiometry coefficient (law of mass action)
    K: float
        equilibrium constant
    activity_product: callable
        see ``equilibrium_residual``
    delta_frac: float
        to avoid division by zero the span of searched values for
        the reactions coordinate (rc) is shrunk by 2*delta_frac*span(rc)
    """
    stoich = np.array(stoich)
    c0 = np.array(c0)
    rc = _solve_equilibrium_coord(c0, stoich, K, activity_product)
    return c0 + rc*stoich


class Equilibrium(Reaction):
    """
    Represents equilibrium reaction

    See :py:class:`Reaction` for parameters
    """

    str_arrow = '<->'
    latex_arrow = '\\rightleftharpoons'

    def __init__(self, reac, prod, params, *args):
        if not all(arg is None for arg in args):
            raise NotImplementedError("Inactive reac/prod not implemented")
        return super(Equilibrium, self).__init__(reac, prod, params)

    def K(self, state=None):
        """ Return equilibrium quotient (possibly state dependent) """
        if callable(self.params):
            if state is None:
                raise ValueError("No state provided")
            return self.params(state)
        else:
            if state is not None:
                raise ValueError("state provided but params not callable")
            return self.params

    def Q(self, substances, concs):
        stoich = self.non_solid_stoich(substances)
        return equilibrium_quotient(concs, stoich)

    def solid_factor(self, substances, sc_concs):
        factor = 1
        for r, n in self.reac.items():
            if r.solid:
                factor *= sc_concs[substances.index(r)]**-n
        for p, n in self.prod.items():
            if p.solid:
                factor *= sc_concs[substances.index(p)]**n
        return factor

    def dimensionality(self):
        result = 0
        for r, n in self.reac.items():
            if r.solid:
                continue
            result -= n
        for p, n in self.prod.items():
            if p.solid:
                continue
            result += n
        return result

    def __rmul__(lhs, rhs):  # This works on both Py2 and Py3
        if not isinstance(rhs, int) or not isinstance(lhs, Equilibrium):
            return NotImplemented
        return Equilibrium(dict(rhs*ArithmeticDict(int, lhs.reac)),
                           dict(rhs*ArithmeticDict(int, lhs.prod)),
                           lhs.params**rhs)

    def __add__(lhs, rhs):
        keys = set()
        for key in chain(lhs.reac.keys(), lhs.prod.keys(),
                         rhs.reac.keys(), rhs.prod.keys()):
            keys.add(key)
        reac, prod = {}, {}
        for key in keys:
            n = (lhs.prod.get(key, 0) - lhs.reac.get(key, 0) +
                 rhs.prod.get(key, 0) - rhs.reac.get(key, 0))
            if n < 0:
                reac[key] = -n
            elif n > 0:
                prod[key] = n
            else:
                pass  # n == 0
        return Equilibrium(reac, prod, lhs.params * rhs.params)

    def __sub__(lhs, rhs):
        return lhs + -1*rhs


def composition_balance(substances, concs, composition_number):
    if not hasattr(concs, 'ndim') or concs.ndim == 1:
        res = 0
    elif concs.ndim == 2:
        res = np.zeros(concs.shape[0])
        concs = concs.T
    else:
        raise NotImplementedError
    for s, c in zip(substances, concs):
        res += s.composition.get(composition_number, 0)*c
    return res


class EqSystemBase(ReactionSystem):

    def eq_constants(self, non_precip_rxn_idxs=()):
        return np.array([0 if idx in non_precip_rxn_idxs else eq.params for
                         idx, eq in enumerate(self.rxns)])

    def upper_conc_bounds(self, init_concs):
        init_concs_arr = self.as_per_substance_array(init_concs)
        composition_conc = defaultdict(float)
        for conc, subst in zip(init_concs_arr, self.substances):
            for comp_nr, coeff in subst.composition.items():
                if comp_nr == 0:
                    continue
                composition_conc[comp_nr] += coeff*conc
        bounds = []
        for subst in self.substances:
            upper = float('inf')
            for comp_nr, coeff in subst.composition.items():
                if comp_nr == 0:
                    continue
                upper = min(upper, composition_conc[comp_nr]/coeff)
            bounds.append(upper)
        return bounds

    def equilibrium_quotients(self, concs):
        stoichs = self.stoichs()
        return [equilibrium_quotient(concs, stoichs[ri, :])
                for ri in range(self.nr)]

    def stoichs_constants(self, rref=False, Matrix=None, ln=None, exp=None,
                          precipitates=()):
        non_precip_rids = [idx for idx, precip in zip(
            self.solid_rxn_idxs, precipitates) if not precip]
        if rref:
            from pyneqsys.symbolic import linear_rref
            ln = ln or math.log
            rA, rb = linear_rref(self.stoichs(non_precip_rids),
                                 map(ln, self.eq_constants(non_precip_rids)),
                                 Matrix)
            exp = exp or math.exp
            return rA, list(map(exp, rb))
        else:
            return (self.stoichs(non_precip_rids),
                    self.eq_constants(non_precip_rids))

    def composition_balance_vectors(self):
        composition_keys = set()
        for s in self.substances:
            for key in s.composition:
                composition_keys.add(key)
        vs = []
        sorted_composition_keys = sorted(composition_keys)
        for key in sorted_composition_keys:
            vs.append([s.composition.get(key, 0) for s in self.substances])
        return vs, sorted_composition_keys

    def composition_conservation(self, concs, init_concs):
        composition_vecs, comp_keys = self.composition_balance_vectors()
        A = np.array(composition_vecs)
        return (comp_keys,
                np.dot(A, self.as_per_substance_array(concs).T),
                np.dot(A, self.as_per_substance_array(init_concs).T))

    @property
    def solid_substance_idxs(self):
        return [idx for idx, s in enumerate(self.substances) if s.solid]

    @property
    def solid_rxn_idxs(self):
        return [idx for idx, rxn in enumerate(self.rxns) if rxn.has_solids()]

    def fw_switch_factory(self, ri):
        rxn = self.rxns[ri]

        def switch(x, p):
            solid_stoich_coeff = rxn.solid_stoich(self.substances)[1]
            q = rxn.Q(self.substances, x)
            k = rxn.K()
            QoverK = q/k
            if solid_stoich_coeff > 0:
                return QoverK < 1
            elif solid_stoich_coeff < 0:
                return QoverK > 1
            else:
                raise NotImplementedError
        return switch

    def bw_switch_factory(self, ri, small):
        rxn = self.rxns[ri]

        def switch(x, p):
            solid_idx = rxn.solid_stoich(self.substances)[2]
            if x[solid_idx] < small:
                return True
            else:
                return False
        return switch

    def get_neqsys(self, rref_equil=False, rref_preserv=False, **kwargs):
        import sympy as sp
        from pyneqsys import SymbolicSys
        kwargs['pre_processor'] = self.pre_processor
        kwargs['post_processor'] = self.post_processor
        if len(self.solid_rxn_idxs) == 0:
            f = partial(self.f, ln=sp.log, exp=sp.exp,
                        rref_equil=rref_equil,
                        rref_preserv=rref_preserv)
            neqsys = SymbolicSys.from_callback(
                f, self.ns, nparams=self.ns, **kwargs)
        else:
            # we have multiple equation systems corresponding
            # to the permutations of presence of each solid phase
            from pyneqsys import ConditionalNeqSys
            neqsys = ConditionalNeqSys(
                [(self.fw_switch_factory(ri),
                  self.bw_switch_factory(ri, self.small)) for
                 ri in self.solid_rxn_idxs],
                lambda conds: SymbolicSys.from_callback(
                    partial(self.f, ln=sp.log, exp=sp.exp,
                            rref_equil=rref_equil,
                            rref_preserv=rref_preserv,
                            precipitates=conds),
                    self.ns, nparams=self.ns, **kwargs
                )
            )
        return neqsys

    def root(self, init_concs, x0=None, neqsys=None,
             solver='scipy', **kwargs):
        init_concs = self.as_per_substance_array(init_concs)
        if x0 is None:
            # x0 = [0]*self.ns
            x0 = init_concs
        neqsys = neqsys or self.get_neqsys(
            rref_equil=kwargs.pop('rref_equil', False),
            rref_preserv=kwargs.pop('rref_preserv', False)
        )
        x, sol = neqsys.solve(solver, x0, init_concs, **kwargs)
        # Sanity checks:
        sc_upper_bounds = np.array(self.upper_conc_bounds(init_concs))
        neg_conc, too_much = np.any(x < 0), np.any(
            x > sc_upper_bounds*(1 + 1e-12))
        if neg_conc or too_much:
            if neg_conc:
                warnings.warn("Negative concentration")
            if too_much:
                warnings.warn("Too much of at least one component")
            # print("neg_conc, too_much", neg_conc, too_much)  # DEBUG
            # print(x)
            # print(sc_upper_bounds)
            # print(x - sc_upper_bounds*(1 + 1e-12))
            return None, sol
        return x, sol

    def roots(self, init_concs, varied=None, values=None, carry=False,
              x0=None, **kwargs):
        if carry:
            if x0 is not None:
                raise NotImplementedError
        nval = len(values)
        init_concs = self.as_per_substance_array(init_concs)
        if init_concs.ndim == 1:
            init_concs = np.tile(init_concs, (nval, 1))
            init_concs[:, self.as_substance_index(varied)] = values
        elif init_concs.ndim == 2:
            if init_concs.shape[0] != nval:
                raise ValueError("Illegal dimension of init_concs")
            if init_concs.shape[1] != self.ns:
                raise ValueError("Illegal dimension of init_concs")
        else:
            raise ValueError("init_concs has too many dimensions")

        x0 = None
        x = np.empty((nval, self.ns))
        success = np.empty(nval, dtype=bool)
        res = None  # silence pyflakes
        neqsys = self.get_neqsys(
            rref_equil=kwargs.pop('rref_equil', False),
            rref_preserv=kwargs.pop('rref_preserv', False)
        )
        for idx in range(nval):
            root_kw = kwargs.copy()
            if carry and idx > 0 and res.success:
                x0 = res.x
            resx, res = self.root(init_concs[idx, :], x0=x0,
                                  neqsys=neqsys, **root_kw)
            success[idx] = resx is not None
            x[idx, :] = resx
        return x, init_concs, success

    def plot(self, x, init_concs, success, varied, values, ax=None,
             fail_vline=True, plot_kwargs=None, subplot_kwargs=None,
             tex=False, conc_unit_str='M'):
        """ plots results from roots() """
        if ax is None:
            import matplotlib.pyplot as plt
            if subplot_kwargs is None:
                subplot_kwargs = dict(xscale='log', yscale='log')
            ax = plt.subplot(1, 1, 1, **subplot_kwargs)
        if plot_kwargs is None:
            plot_kwargs = {}

        ls, c = '- -- : -.'.split(), 'krgbcmy'
        extra_kw = {}
        for idx_s in range(self.ns):
            if idx_s == self.as_substance_index(varied):
                continue
            if 'ls' not in plot_kwargs and 'linestyle' not in plot_kwargs:
                extra_kw['ls'] = ls[idx_s % len(ls)]
            if 'c' not in plot_kwargs and 'color' not in plot_kwargs:
                extra_kw['c'] = c[idx_s % len(c)]
            try:
                lbl = '$' + self.substances[idx_s].latex_name + '$'
            except TypeError:
                lbl = self.substances[idx_s].name
            extra_kw.update(plot_kwargs)
            ax.plot(values[success], x[success, idx_s],
                    label=lbl, **extra_kw)

        mpl_outside_legend(ax)
        xlbl = '$[' + varied.latex_name + ']$' if tex else str(varied)
        ax.set_xlabel(xlbl + ' / %s' % conc_unit_str)
        ax.set_ylabel('Concentration / %s' % conc_unit_str)
        if fail_vline:
            for i, s in enumerate(success):
                if not s:
                    ax.axvline(values[i], c='k', ls='--')

    def solve_and_plot(self, init_concs, varied, values, roots_kwargs=None,
                       **kwargs):
        x, new_init_concs, success = self.roots(
            init_concs, varied, values, **(roots_kwargs or {}))
        self.plot(x, new_init_concs, success, varied, values, **kwargs)
        return x, new_init_concs, success

    def plot_errors(self, concs, init_concs, varied, axes=None,
                    compositions=True, Q=True, subplot_kwargs=None):
        if axes is None:
            import matplotlib.pyplot as plt
            if subplot_kwargs is None:
                subplot_kwargs = dict(xscale='log')
            fig, axes = plt.subplots(1, 2, figsize=(10, 4),
                                     subplot_kw=subplot_kwargs)

        ls, c = '- -- : -.'.split(), 'krgbcmy'
        if compositions:
            cmp_nrs, m1, m2 = self.composition_conservation(concs, init_concs)
            for cidx, (cmp_nr, a1, a2) in enumerate(zip(cmp_nrs, m1, m2)):
                axes[0].plot(concs[:, self.as_substance_index(varied)],
                             a1-a2, label='Comp ' + str(cmp_nr),
                             ls=ls[cidx % len(ls)], c=c[cidx % len(c)])
                axes[1].plot(concs[:, self.as_substance_index(varied)],
                             (a1-a2)/np.abs(a2), label='Comp ' + str(cmp_nr),
                             ls=ls[cidx % len(ls)], c=c[cidx % len(c)])

        if Q:
            qs = self.equilibrium_quotients(concs)
            ks = [rxn.params*self.solid_factor(self.substances, concs)
                  for rxn in self.rxns]
            for idx, (q, k) in enumerate(zip(qs, ks)):
                axes[0].plot(concs[:, self.as_substance_index(varied)],
                             q-k, label='K R:' + str(idx),
                             ls=ls[(idx+cidx) % len(ls)],
                             c=c[(idx+cidx) % len(c)])
                axes[1].plot(concs[:, self.as_substance_index(varied)],
                             (q-k)/k, label='K R:' + str(idx),
                             ls=ls[(idx+cidx) % len(ls)],
                             c=c[(idx+cidx) % len(c)])

        mpl_outside_legend(axes[0])
        mpl_outside_legend(axes[1])
        axes[0].set_title("Absolute errors")
        axes[1].set_title("Relative errors")


class EqSystemLin(EqSystemBase):

    small = 1e-15  # arbitrary: roughly machine epsilon * 10
    pre_processor = None
    post_processor = None

    def f(self, y, init_concs, rref_equil=False, rref_preserv=False,
          ln=None, exp=None, precipitates=()):
        from pyneqsys.symbolic import linear_exprs
        A, ks = self.stoichs_constants(rref_equil, ln=ln, exp=exp,
                                       precipitates=precipitates)
        # y == C
        f1 = [q/k-1 if k != 0 else q for q, k in zip(prodpow(y, A), ks)]
        B, comp_nrs = self.composition_balance_vectors()
        f2 = linear_exprs(B, y, mat_dot_vec(B, init_concs))
        return f1 + f2


class EqSystemLog(EqSystemBase):

    small = -60  # aribtrary: exp(-60), small but well within domain

    pre_processor = np.log
    post_processor = np.exp

    def f(self, y, init_concs, rref_equil=False, rref_preserv=False,
          ln=None, exp=None, precipitates=()):
        from pyneqsys.symbolic import linear_exprs
        if ln is None:
            ln = math.log
        if exp is None:
            exp = math.exp
        A, ks = self.stoichs_constants(rref_equil, ln=ln, exp=exp,
                                       precipitates=precipitates)
        f1 = mat_dot_vec(A, y, ks)  # y == ln(C)
        B, comp_nrs = self.composition_balance_vectors()
        f2 = linear_exprs(B, map(exp, y), mat_dot_vec(B, init_concs),
                          rref=rref_preserv)
        return f1 + f2
