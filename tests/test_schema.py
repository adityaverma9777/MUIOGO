import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from bridge.schema import ClewsEnergyOutput, OGCoreInputs


def test_valid_clews_output_instantiates():
	obj = ClewsEnergyOutput(
		year=[2025, 2026, 2027],
		technology=['SOLAR', 'SOLAR', 'WIND'],
		total_discounted_cost_usd=[1.2e9, 1.26e9, 1.31e9],
		production_by_technology_pj=[4800.0, 5040.0, 5250.0],
		capital_investment_usd=[3.4e8, 3.57e8, 3.7e8],
		water_consumption_mm3=[185.0, 192.0, 198.0]
	)
	assert obj.year == [2025, 2026, 2027]


def test_mismatched_lengths_raises():
	with pytest.raises(Exception):
		ClewsEnergyOutput(
			year=[2025, 2026],
			technology=['SOLAR'],
			total_discounted_cost_usd=[1.2e9, 1.26e9],
			production_by_technology_pj=[4800.0, 5040.0],
			capital_investment_usd=[3.4e8, 3.57e8],
			water_consumption_mm3=[185.0, 192.0]
		)


def test_negative_cost_raises():
	with pytest.raises(Exception):
		ClewsEnergyOutput(
			year=[2025, 2026],
			technology=['SOLAR', 'WIND'],
			total_discounted_cost_usd=[-1.2e9, 1.26e9],
			production_by_technology_pj=[4800.0, 5040.0],
			capital_investment_usd=[3.4e8, 3.57e8],
			water_consumption_mm3=[185.0, 192.0]
		)


def test_debt_ratio_out_of_bounds():
	with pytest.raises(Exception):
		OGCoreInputs(
			initial_debt_ratio=2.5,
			productivity_growth=[0.98, 0.97],
			alpha_G=[0.08, 0.09],
			scenario_label='bad'
		)