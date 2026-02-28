from __future__ import annotations

from faa_emissions_analysis.model import compressible_orifice_mdot, critical_pressure_ratio


def test_critical_pressure_ratio_bounds() -> None:
    ratio = critical_pressure_ratio(1.33)
    assert 0.4 < ratio < 0.7


def test_compressible_orifice_choked_flag() -> None:
    gamma = 1.33
    crit = critical_pressure_ratio(gamma)
    p_up = 200_000.0

    mdot_choked, is_choked = compressible_orifice_mdot(
        p_up_pa=p_up,
        p_down_pa=p_up * (crit * 0.9),
        temperature_k=500.0,
        area_m2=1.0e-6,
        discharge_coeff=0.85,
        gamma=gamma,
        gas_constant_j_kgk=287.0,
    )
    mdot_unchoked, not_choked = compressible_orifice_mdot(
        p_up_pa=p_up,
        p_down_pa=p_up * 0.95,
        temperature_k=500.0,
        area_m2=1.0e-6,
        discharge_coeff=0.85,
        gamma=gamma,
        gas_constant_j_kgk=287.0,
    )

    assert is_choked is True
    assert not_choked is False
    assert mdot_choked > 0.0
    assert mdot_unchoked > 0.0
