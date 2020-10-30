# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import pytest

from ..parsing import (
    formula_to_composition, formula_to_html, formula_to_latex, formula_to_unicode,
    parsing_library, to_reaction
)
from ..testing import requires


@requires(parsing_library)
def test_formula_to_composition():
    # General covalent compounds, with states, groups, nested groups.
    assert formula_to_composition('H2O') == {1: 2, 8: 1}
    assert formula_to_composition('H2O(cr)') == {1: 2, 8: 1}
    assert formula_to_composition('H2O(g)') == {1: 2, 8: 1}
    assert formula_to_composition('H2O(l)') == {1: 2, 8: 1}
    assert formula_to_composition('H2O(s)') == {1: 2, 8: 1}
    assert formula_to_composition('NH3') == {1: 3, 7: 1}
    assert formula_to_composition('NH3(aq)') == {1: 3, 7: 1}
    assert formula_to_composition('NH3(cr)') == {1: 3, 7: 1}
    assert formula_to_composition('NH3(g)') == {1: 3, 7: 1}
    assert formula_to_composition('NH3(l)') == {1: 3, 7: 1}
    assert formula_to_composition('NH3(s)') == {1: 3, 7: 1}
    assert formula_to_composition('((H2O)2OH)12') == {1: 60, 8: 36}
    assert formula_to_composition('((H2O)2OH)12(aq)') == {1: 60, 8: 36}
    assert formula_to_composition('((H2O)2OH)12(cr)') == {1: 60, 8: 36}
    assert formula_to_composition('((H2O)2OH)12(g)') == {1: 60, 8: 36}
    assert formula_to_composition('((H2O)2OH)12(l)') == {1: 60, 8: 36}
    assert formula_to_composition('((H2O)2OH)12(s)') == {1: 60, 8: 36}

    # Organic compounds, with states, structural formulas, molecular
    # formulas, groups, nested groups.
    assert formula_to_composition('CH4') == {1: 4, 6: 1}
    assert formula_to_composition('CH4(aq)') == {1: 4, 6: 1}
    assert formula_to_composition('CH4(cr)') == {1: 4, 6: 1}
    assert formula_to_composition('CH4(g)') == {1: 4, 6: 1}
    assert formula_to_composition('CH4(l)') == {1: 4, 6: 1}
    assert formula_to_composition('CH4(s)') == {1: 4, 6: 1}

    # Ionic compounds, with hydrates and states.
    assert formula_to_composition('NaCl') == {11: 1, 17: 1}
    assert formula_to_composition('NaCl(s)') == {11: 1, 17: 1}
    assert formula_to_composition('BaCl2') == {17: 2, 56: 1}
    assert formula_to_composition('BaCl2(aq)') == {17: 2, 56: 1}
    assert formula_to_composition('BaCl2(s)') == {17: 2, 56: 1}
    assert formula_to_composition('BaCl2.2H2O(s)') == {1: 4, 8: 2, 17: 2, 56: 1}
    assert formula_to_composition('Al2(SO4)3') == {13: 2, 16: 3, 8: 12}
    assert formula_to_composition('Al2(SO4)3(aq)') == {13: 2, 16: 3, 8: 12}
    assert formula_to_composition('Al2(SO4)3(s)') == {13: 2, 16: 3, 8: 12}
    assert formula_to_composition('Na2CO3') == {11: 2, 6: 1, 8: 3}
    assert formula_to_composition('Na2CO3(s)') == {11: 2, 6: 1, 8: 3}
    assert formula_to_composition('Na2CO3(aq)') == {11: 2, 6: 1, 8: 3}
    assert formula_to_composition('Na2CO3.7H2O') == {11: 2, 6: 1, 8: 10, 1: 14}
    assert formula_to_composition('Na2CO3.7H2O(s)') == {11: 2, 6: 1, 8: 10, 1: 14}

    # Ions, with states and charge variations.
    # Special case:  electrons and charge
    #     electron/negative charge:  {0, -1}
    #     positive charge:  {0, 1}
    assert formula_to_composition('e-') == {0: -1}
    assert formula_to_composition('e-(aq)') == {0: -1}
    assert formula_to_composition('e/-') == {0: -1}
    assert formula_to_composition('e/-(aq)') == {0: -1}
    assert formula_to_composition('e-1') == {0: -1}
    assert formula_to_composition('e-1(aq)') == {0: -1}
    assert formula_to_composition('e/-1') == {0: -1}
    assert formula_to_composition('e/-1(aq)') == {0: -1}
    assert formula_to_composition('e/1-') == {0: -1}
    assert formula_to_composition('e/1-(aq)') == {0: -1}

    assert formula_to_composition('Cl-') == {0: -1, 17: 1}
    assert formula_to_composition('Cl-1') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/-') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/-1') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/1-') == {0: -1, 17: 1}
    assert formula_to_composition('Cl-(aq)') == {0: -1, 17: 1}
    assert formula_to_composition('Cl-1(aq)') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/-(aq)') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/-1(aq)') == {0: -1, 17: 1}
    assert formula_to_composition('Cl/1-(aq)') == {0: -1, 17: 1}

    assert formula_to_composition('O-2') == {0: -2, 8: 1}
    assert formula_to_composition('O-2(aq)') == {0: -2, 8: 1}
    assert formula_to_composition('O/-2') == {0: -2, 8: 1}
    assert formula_to_composition('O/-2(aq)') == {0: -2, 8: 1}
    assert formula_to_composition('O/2-') == {0: -2, 8: 1}
    assert formula_to_composition('O/2-(aq)') == {0: -2, 8: 1}

    assert formula_to_composition('P-3') == {0: -3, 15: 1}
    assert formula_to_composition('P-3(aq)') == {0: -3, 15: 1}
    assert formula_to_composition('P/-3') == {0: -3, 15: 1}
    assert formula_to_composition('P/-3(aq)') == {0: -3, 15: 1}
    assert formula_to_composition('P/3-') == {0: -3, 15: 1}
    assert formula_to_composition('P/3-(aq)') == {0: -3, 15: 1}

    assert formula_to_composition('Na+') == {0: 1, 11: 1}
    assert formula_to_composition('Na+1') == {0: 1, 11: 1}
    assert formula_to_composition('Na/+') == {0: 1, 11: 1}
    assert formula_to_composition('Na/+1') == {0: 1, 11: 1}
    assert formula_to_composition('Na/1+') == {0: 1, 11: 1}
    assert formula_to_composition('Na+(aq)') == {0: 1, 11: 1}
    assert formula_to_composition('Na+1(aq)') == {0: 1, 11: 1}
    assert formula_to_composition('Na/+(aq)') == {0: 1, 11: 1}
    assert formula_to_composition('Na/+1(aq)') == {0: 1, 11: 1}
    assert formula_to_composition('Na/1+(aq)') == {0: 1, 11: 1}

    assert formula_to_composition('Ca+2') == {0: 2, 20: 1}
    assert formula_to_composition('Ca+2(aq)') == {0: 2, 20: 1}
    assert formula_to_composition('Ca/+2') == {0: 2, 20: 1}
    assert formula_to_composition('Ca/+2(aq)') == {0: 2, 20: 1}
    assert formula_to_composition('Ca/2+') == {0: 2, 20: 1}
    assert formula_to_composition('Ca/2+(aq)') == {0: 2, 20: 1}

    assert formula_to_composition('Fe/3+') == {0: 3, 26: 1}
    assert formula_to_composition('Fe/+3') == {0: 3, 26: 1}
    assert formula_to_composition('Fe+3') == {0: 3, 26: 1}
    assert formula_to_composition('Fe/3+(aq)') == {0: 3, 26: 1}
    assert formula_to_composition('Fe/+3(aq)') == {0: 3, 26: 1}
    assert formula_to_composition('Fe+3(aq)') == {0: 3, 26: 1}

    # Polyatomic ions.
    assert formula_to_composition('OH-') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH-(aq)') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH-1') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH-1(aq)') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/-') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/-(aq)') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/-1') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/-1(aq)') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/1-') == {0: -1, 8: 1, 1: 1}
    assert formula_to_composition('OH/1-(aq)') == {0: -1, 8: 1, 1: 1}

    assert formula_to_composition('SO4-2') == {0: -2, 16: 1, 8: 4}
    assert formula_to_composition('SO4-2(aq)') == {0: -2, 16: 1, 8: 4}
    assert formula_to_composition('SO4/-2') == {0: -2, 16: 1, 8: 4}
    assert formula_to_composition('SO4/-2(aq)') == {0: -2, 16: 1, 8: 4}
    assert formula_to_composition('SO4/2-') == {0: -2, 16: 1, 8: 4}
    assert formula_to_composition('SO4/2-(aq)') == {0: -2, 16: 1, 8: 4}

    assert formula_to_composition('PO4-3') == {0: -3, 15: 1, 8: 4}
    assert formula_to_composition('PO4-3(aq)') == {0: -3, 15: 1, 8: 4}
    assert formula_to_composition('PO4/-3') == {0: -3, 15: 1, 8: 4}
    assert formula_to_composition('PO4/-3(aq)') == {0: -3, 15: 1, 8: 4}
    assert formula_to_composition('PO4/3-') == {0: -3, 15: 1, 8: 4}
    assert formula_to_composition('PO4/3-(aq)') == {0: -3, 15: 1, 8: 4}

    assert formula_to_composition('NH4+') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4+(aq)') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4+1') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4+1(aq)') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/+') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/+(aq)') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/+1') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/+1(aq)') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/1+') == {0: 1, 7: 1, 1: 4}
    assert formula_to_composition('NH4/1+(aq)') == {0: 1, 7: 1, 1: 4}

    assert formula_to_composition('Fe(SCN)2+') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2+(aq)') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2+1(aq)') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/+') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/+(aq)') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/+1') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/+1(aq)') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/1+') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}
    assert formula_to_composition('Fe(SCN)2/1+(aq)') == {
        0: 1, 6: 2, 7: 2, 16: 2, 26: 1}

    # Complexes, many cases.
    # ion/complex, complex/ion, complex/complex
    # hydrates, states
    # ionic complexes
    # subgrouped complexes ([Fe(CN)6]-3) and not ([FeCl6]-3)
    assert formula_to_composition('K4[Fe(CN)6]') == {19: 4, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('K4[Fe(CN)6](aq)') == {19: 4, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('K4[Fe(CN)6](s)') == {19: 4, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('K3[Fe(CN)6]') == {19: 3, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('K3[Fe(CN)6](aq)') == {19: 3, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('K3[Fe(CN)6](s)') == {19: 3, 26: 6, 6: 6, 7: 6}
    assert formula_to_composition('[Fe(H2O)6][Fe(CN)6].19H2O') == {26: 2, 1: 50, 8: 25, 6: 6, 7: 7}
    assert formula_to_composition('[Fe(H2O)6][Fe(CN)6].19H2O(s)') == {26: 2, 1: 50, 8: 25, 6: 6, 7: 7}

    # Non-integer subscripts, with states.
    # See also phases, below.
    assert formula_to_composition('Ca2.832Fe0.6285Mg5.395(CO3)6') == {20: 2.832, 26: 0.6285, 12: 5.395, 6: 6, 8: 18}
    assert formula_to_composition('Ca2.832Fe0.6285Mg5.395(CO3)6(s)') == {20: 2.832, 26: 0.6285, 12: 5.395, 6: 6, 8: 18}

    # Radicals, with charges and states.
    assert formula_to_composition('.NO2') == {7: 1, 8: 2}
    assert formula_to_composition('.NO2(g)') == {7: 1, 8: 2}
    assert formula_to_composition('.NH2') == {1: 2, 7: 1}
    assert formula_to_composition('.NH2(g)') == {1: 2, 7: 1}
    assert formula_to_composition('ONOOH') == {1: 1, 7: 1, 8: 3}
    assert formula_to_composition('ONOOH(g)') == {1: 1, 7: 1, 8: 3}
    assert formula_to_composition('.ONOO') == {7: 1, 8: 3}
    assert formula_to_composition('.ONOO(g)') == {7: 1, 8: 3}
    assert formula_to_composition('.NO3-2') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3-2(g)') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3/-2') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3/-2(g)') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3/2-') == {0: -2, 7: 1, 8: 3}
    assert formula_to_composition('.NO3/2-(g)') == {0: -2, 7: 1, 8: 3}

    # Structures should (?) fail.
    with pytest.raises(ValueError):
        formula_to_composition('F-F')

    # Phases, with states and non-integer subscripts.
    assert formula_to_composition('alpha-FeOOH(s)') == {1: 1, 8: 2, 26: 1}
    assert formula_to_composition('epsilon-Zn(OH)2(s)') == {1: 2, 8: 2, 30: 1}


@requires(parsing_library)
def test_to_reaction():
    from chempy.chemistry import Reaction, Equilibrium
    rxn = to_reaction(
        "H+ + OH- -> H2O; 1.4e11; ref={'doi': '10.1039/FT9908601539'}",
        'H+ OH- H2O'.split(), '->', Reaction)
    assert rxn.__class__ == Reaction

    assert rxn.reac['H+'] == 1
    assert rxn.reac['OH-'] == 1
    assert rxn.prod['H2O'] == 1
    assert rxn.param == 1.4e11
    assert rxn.ref['doi'].startswith('10.')

    eq = to_reaction("H+ + OH- = H2O; 1e-14; ref='rt, [H2O] == 1 M'",
                     'H+ OH- H2O'.split(), '=', Equilibrium)
    assert eq.__class__ == Equilibrium

    assert eq.reac['H+'] == 1
    assert eq.reac['OH-'] == 1
    assert eq.prod['H2O'] == 1
    assert eq.ref.startswith('rt')

    for s in ['2 e-(aq) + (2 H2O) -> H2 + 2 OH- ; 1e6 ; ',
              '2 * e-(aq) + (2 H2O) -> 1 * H2 + 2 * OH- ; 1e6 ; ']:
        rxn2 = to_reaction(s, 'e-(aq) H2 OH- H2O'.split(), '->', Reaction)
        assert rxn2.__class__ == Reaction
        assert rxn2.reac['e-(aq)'] == 2
        assert rxn2.inact_reac['H2O'] == 2
        assert rxn2.prod['H2'] == 1
        assert rxn2.prod['OH-'] == 2
        assert rxn2.param == 1e6

    r1 = to_reaction("-> H2O", None, '->', Reaction)
    assert r1.reac == {}
    assert r1.prod == {'H2O': 1}
    assert r1.param is None

    r2 = to_reaction("H2O ->", None, '->', Reaction)
    assert r2.reac == {'H2O': 1}
    assert r2.prod == {}
    assert r2.param is None

    from chempy.kinetics.rates import MassAction
    ma = MassAction([3.14])
    r3 = to_reaction("H+ + OH- -> H2O", None, '->', Reaction, param=ma)
    assert r3.param.args == [3.14]

    rxn3 = to_reaction("H2O + H2O -> H3O+ + OH-", 'H3O+ OH- H2O'.split(), '->', Reaction)
    assert rxn3.reac == {'H2O': 2} and rxn3.prod == {'H3O+': 1, 'OH-': 1}

    rxn4 = to_reaction("2 e-(aq) + (2 H2O) + (2 H+) -> H2 + 2 H2O", 'e-(aq) H2 H2O H+'.split(), '->', Reaction)
    assert rxn4.reac == {'e-(aq)': 2} and rxn4.inact_reac == {'H2O': 2, 'H+': 2} and rxn4.prod == {'H2': 1, 'H2O': 2}


@requires(parsing_library)
def test_formula_to_latex():
    assert formula_to_latex('H2O') == 'H_{2}O'
    assert formula_to_latex('C6H6/+') == 'C_{6}H_{6}^{+}'
    assert formula_to_latex('Fe(CN)6/3-') == 'Fe(CN)_{6}^{3-}'
    assert formula_to_latex('Fe(CN)6-3') == 'Fe(CN)_{6}^{3-}'
    assert formula_to_latex('C18H38/2+') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('C18H38/+2') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('C18H38+2') == 'C_{18}H_{38}^{2+}'
    assert formula_to_latex('((H2O)2OH)12') == '((H_{2}O)_{2}OH)_{12}'
    assert formula_to_latex('NaCl') == 'NaCl'
    assert formula_to_latex('NaCl(s)') == 'NaCl(s)'
    assert formula_to_latex('e-(aq)') == 'e^{-}(aq)'
    assert formula_to_latex('Ca+2(aq)') == 'Ca^{2+}(aq)'
    assert formula_to_latex('.NO2(g)') == r'^\bullet NO_{2}(g)'
    assert formula_to_latex('.NH2') == r'^\bullet NH_{2}'
    assert formula_to_latex('ONOOH') == 'ONOOH'
    assert formula_to_latex('.ONOO') == r'^\bullet ONOO'
    assert formula_to_latex('.NO3/2-') == r'^\bullet NO_{3}^{2-}'
    assert formula_to_latex('.NO3-2') == r'^\bullet NO_{3}^{2-}'
    assert formula_to_latex('alpha-FeOOH(s)') == r'\alpha-FeOOH(s)'
    assert formula_to_latex('epsilon-Zn(OH)2(s)') == (
        r'\varepsilon-Zn(OH)_{2}(s)')
    assert formula_to_latex('Na2CO3.7H2O(s)') == r'Na_{2}CO_{3}\cdot 7H_{2}O(s)'
    assert formula_to_latex('Na2CO3.1H2O(s)') == r'Na_{2}CO_{3}\cdot H_{2}O(s)'


@requires(parsing_library)
def test_formula_to_unicoce():
    assert formula_to_unicode('NH4+') == u'NH₄⁺'
    assert formula_to_unicode('H2O') == u'H₂O'
    assert formula_to_unicode('C6H6/+') == u'C₆H₆⁺'
    assert formula_to_unicode('Fe(CN)6/3-') == u'Fe(CN)₆³⁻'
    assert formula_to_unicode('Fe(CN)6-3') == u'Fe(CN)₆³⁻'
    assert formula_to_unicode('C18H38/2+') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('C18H38/+2') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('C18H38+2') == u'C₁₈H₃₈²⁺'
    assert formula_to_unicode('((H2O)2OH)12') == u'((H₂O)₂OH)₁₂'
    assert formula_to_unicode('NaCl') == u'NaCl'
    assert formula_to_unicode('NaCl(s)') == u'NaCl(s)'
    assert formula_to_unicode('e-(aq)') == u'e⁻(aq)'
    assert formula_to_unicode('Ca+2(aq)') == u'Ca²⁺(aq)'
    assert formula_to_unicode('.NO2(g)') == u'⋅NO₂(g)'
    assert formula_to_unicode('.NH2') == u'⋅NH₂'
    assert formula_to_unicode('ONOOH') == u'ONOOH'
    assert formula_to_unicode('.ONOO') == u'⋅ONOO'
    assert formula_to_unicode('.NO3/2-') == u'⋅NO₃²⁻'
    assert formula_to_unicode('.NO3-2') == u'⋅NO₃²⁻'
    assert formula_to_unicode('alpha-FeOOH(s)') == u'α-FeOOH(s)'
    assert formula_to_unicode('epsilon-Zn(OH)2(s)') == u'ε-Zn(OH)₂(s)'
    assert formula_to_unicode('Na2CO3.7H2O(s)') == u'Na₂CO₃·7H₂O(s)'
    assert formula_to_unicode('Na2CO3.1H2O(s)') == u'Na₂CO₃·H₂O(s)'


@requires(parsing_library)
def test_formula_to_html():
    assert formula_to_html('H2O') == 'H<sub>2</sub>O'
    assert formula_to_html('C6H6/+') == 'C<sub>6</sub>H<sub>6</sub><sup>+</sup>'
    assert formula_to_html('Fe(CN)6/3-') == 'Fe(CN)<sub>6</sub><sup>3-</sup>'
    assert formula_to_html('Fe(CN)6-3') == 'Fe(CN)<sub>6</sub><sup>3-</sup>'
    assert formula_to_html('C18H38/2+') == 'C<sub>18</sub>H<sub>38</sub><sup>2+</sup>'
    assert formula_to_html('C18H38/+2') == 'C<sub>18</sub>H<sub>38</sub><sup>2+</sup>'
    assert formula_to_html('C18H38+2') == 'C<sub>18</sub>H<sub>38</sub><sup>2+</sup>'
    assert formula_to_html('((H2O)2OH)12') == '((H<sub>2</sub>O)<sub>2</sub>OH)<sub>12</sub>'
    assert formula_to_html('NaCl') == 'NaCl'
    assert formula_to_html('NaCl(s)') == 'NaCl(s)'
    assert formula_to_html('e-(aq)') == 'e<sup>-</sup>(aq)'
    assert formula_to_html('Ca+2(aq)') == 'Ca<sup>2+</sup>(aq)'
    assert formula_to_html('.NO2(g)') == r'&sdot;NO<sub>2</sub>(g)'
    assert formula_to_html('.NH2') == r'&sdot;NH<sub>2</sub>'
    assert formula_to_html('ONOOH') == 'ONOOH'
    assert formula_to_html('.ONOO') == r'&sdot;ONOO'
    assert formula_to_html('.NO3/2-') == r'&sdot;NO<sub>3</sub><sup>2-</sup>'
    assert formula_to_html('.NO3-2') == r'&sdot;NO<sub>3</sub><sup>2-</sup>'
    assert formula_to_html('alpha-FeOOH(s)') == r'&alpha;-FeOOH(s)'
    assert formula_to_html('epsilon-Zn(OH)2(s)') == (
        r'&epsilon;-Zn(OH)<sub>2</sub>(s)')
    assert formula_to_html('Na2CO3.7H2O(s)') == 'Na<sub>2</sub>CO<sub>3</sub>&sdot;7H<sub>2</sub>O(s)'
    assert formula_to_html('Na2CO3.1H2O(s)') == 'Na<sub>2</sub>CO<sub>3</sub>&sdot;H<sub>2</sub>O(s)'
