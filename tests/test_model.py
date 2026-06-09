from __future__ import annotations

import pytest

from faa_emissions_analysis.model import compressible_orifice_mdot, critical_pressure_ratio
from faa_emissions_analysis.model.physics_utils import mix_compositions, normalize_composition


# ---------------------------------------------------------------------------
# Pure-Python physics tests (no Cantera required)
# ---------------------------------------------------------------------------

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


def test_normalize_composition_sums_to_one() -> None:
    raw = {"O2": 0.5, "N2": 0.3, "CO2": 0.2}
    result = normalize_composition(raw)
    assert abs(sum(result.values()) - 1.0) < 1e-12
    assert all(v >= 0.0 for v in result.values())


def test_normalize_composition_drops_nonpositive() -> None:
    raw = {"O2": 1.0, "N2": 0.0, "CO2": -0.1}
    result = normalize_composition(raw)
    assert "O2" in result
    assert "N2" not in result
    assert "CO2" not in result
    assert abs(result["O2"] - 1.0) < 1e-12


def test_mix_compositions_sums_to_one() -> None:
    base = {"O2": 0.21, "N2": 0.79}
    added = {"O2": 0.10, "N2": 0.85, "CO2": 0.05}
    for frac in (0.0, 0.1, 0.5, 0.99):
        result = mix_compositions(base, added, frac)
        assert abs(sum(result.values()) - 1.0) < 1e-12, f"mix_fraction={frac} sums to {sum(result.values())}"


def test_mix_compositions_no_added_returns_base() -> None:
    base = {"O2": 0.21, "N2": 0.79}
    result = mix_compositions(base, None, 0.5)
    assert abs(result["O2"] - 0.21) < 1e-12
    assert abs(result["N2"] - 0.79) < 1e-12


# ---------------------------------------------------------------------------
# Cantera-dependent tests
# ---------------------------------------------------------------------------

ct = pytest.importorskip("cantera", reason="Cantera not installed")


def _make_inert_stage_config():
    """Return a minimal ForwardModelConfig + StageConfig for an inert N2 stage."""
    from faa_emissions_analysis.model.types import ForwardModelConfig, StageConfig

    stage = StageConfig(
        name="test_inert",
        distance_m=0.1,
        residence_time_s=0.001,
        pressure_drop_pa=0.0,
        wall_temperature_k=None,
        ua_w_m2_k=0.0,
        area_m2=0.01,
        mix_stream=None,
        mix_fraction=0.0,
        restriction=None,
    )
    config = ForwardModelConfig(
        mechanism="gri30.yaml",
        tracked_species=("O2", "N2"),
        inlet_composition={"O2": 0.21, "N2": 0.79},
        stages=(stage,),
    )
    return config, stage


def test_species_extraction_in_unit_interval() -> None:
    """Every extracted mole fraction must lie in [0, 1]."""
    from faa_emissions_analysis.model.stages import CanteraPathModel

    config, stage = _make_inert_stage_config()
    model = CanteraPathModel(config)

    state = {
        "temperature_k": 800.0,
        "pressure_pa": 200_000.0,
        "mass_flow_kg_s": 0.01,
        "composition": {"O2": 0.21, "N2": 0.79},
    }
    out = model._advance_stage(state, stage)
    for sp, val in out["composition"].items():
        assert 0.0 <= val <= 1.0, f"Species {sp} has out-of-range mole fraction: {val}"


def test_tracked_species_sum_leq_one() -> None:
    """Tracked-species mole fractions must sum to ≤ 1 (they're a subset of all species)."""
    from faa_emissions_analysis.model.stages import CanteraPathModel

    config, stage = _make_inert_stage_config()
    model = CanteraPathModel(config)

    state = {
        "temperature_k": 800.0,
        "pressure_pa": 200_000.0,
        "mass_flow_kg_s": 0.01,
        "composition": {"O2": 0.21, "N2": 0.79},
    }
    out = model._advance_stage(state, stage)
    total = sum(out["composition"].values())
    assert total <= 1.0 + 1e-9, f"Tracked species sum {total} exceeds 1"


def test_mass_conservation_inert_no_restriction() -> None:
    """Mass flow must be unchanged through a no-mixing, no-restriction stage."""
    from faa_emissions_analysis.model.stages import CanteraPathModel

    config, stage = _make_inert_stage_config()
    model = CanteraPathModel(config)

    mdot_in = 0.05
    state = {
        "temperature_k": 800.0,
        "pressure_pa": 200_000.0,
        "mass_flow_kg_s": mdot_in,
        "composition": {"O2": 0.21, "N2": 0.79},
    }
    out = model._advance_stage(state, stage)
    assert out["mass_flow_kg_s"] == mdot_in, (
        f"Mass flow changed from {mdot_in} to {out['mass_flow_kg_s']} in a no-mixing stage"
    )


def test_enthalpy_conservation_adiabatic_inert() -> None:
    """Specific enthalpy must be conserved in an adiabatic, no-reaction stage.

    For an IdealGasConstPressureReactor with energy='on' and no wall heat transfer,
    advancing an inert gas mixture should leave h unchanged (first-law, open system,
    steady flow, no work, no heat, no reaction).
    """
    import cantera as _ct

    from faa_emissions_analysis.model.stages import CanteraPathModel

    config, stage = _make_inert_stage_config()
    model = CanteraPathModel(config)

    T_in = 900.0
    P_in = 150_000.0
    comp = {"O2": 0.21, "N2": 0.79}

    gas_in = _ct.Solution(config.mechanism)
    gas_in.TPX = T_in, P_in, comp
    h_in = gas_in.enthalpy_mass

    state = {
        "temperature_k": T_in,
        "pressure_pa": P_in,
        "mass_flow_kg_s": 0.01,
        "composition": comp,
    }
    out = model._advance_stage(state, stage)

    gas_out = _ct.Solution(config.mechanism)
    gas_out.TPX = out["temperature_k"], out["pressure_pa"], {"O2": out["composition"].get("O2", 0.0), "N2": out["composition"].get("N2", 1.0)}
    h_out = gas_out.enthalpy_mass

    rel_err = abs(h_out - h_in) / max(abs(h_in), 1.0)
    assert rel_err < 1e-4, f"Adiabatic enthalpy not conserved: h_in={h_in:.1f}, h_out={h_out:.1f}, rel_err={rel_err:.2e}"


def test_outlet_pressure_used_for_kinetics() -> None:
    """Reactor must run at prescribed outlet pressure, not inlet pressure."""
    from faa_emissions_analysis.model.stages import CanteraPathModel
    from faa_emissions_analysis.model.types import ForwardModelConfig, StageConfig

    drop = 5_000.0
    stage = StageConfig(
        name="pressure_drop_stage",
        distance_m=0.1,
        residence_time_s=0.001,
        pressure_drop_pa=drop,
        wall_temperature_k=None,
        ua_w_m2_k=0.0,
        area_m2=0.01,
    )
    config = ForwardModelConfig(
        mechanism="gri30.yaml",
        tracked_species=("O2", "N2"),
        inlet_composition={"O2": 0.21, "N2": 0.79},
        stages=(stage,),
    )
    model = CanteraPathModel(config)

    P_in = 200_000.0
    state = {
        "temperature_k": 800.0,
        "pressure_pa": P_in,
        "mass_flow_kg_s": 0.01,
        "composition": {"O2": 0.21, "N2": 0.79},
    }
    out = model._advance_stage(state, stage)
    assert abs(out["pressure_pa"] - (P_in - drop)) < 1.0, (
        f"Outlet pressure {out['pressure_pa']} != prescribed {P_in - drop}"
    )
