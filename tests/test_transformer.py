import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from bridge.schema import ClewsEnergyOutput, OGCoreInputs
from bridge.transformer import clews_to_ogcore


def make_clews(n=4):
	base_cost = 1.2e9
	return ClewsEnergyOutput(
		year=list(range(2025, 2025 + n)),
		technology=['SOLAR'] * n,
		total_discounted_cost_usd=[base_cost * (1.05 ** i) for i in range(n)],
		production_by_technology_pj=[4800.0 + i * 200 for i in range(n)],
		capital_investment_usd=[3.4e8 * (1.03 ** i) for i in range(n)],
		water_consumption_mm3=[185.0 + i * 5 for i in range(n)]
	)


def test_transformer_returns_ogcore_inputs():
	result = clews_to_ogcore(make_clews(4), scenario_label='test')
	assert isinstance(result, OGCoreInputs)
	assert 0.0 < result.initial_debt_ratio < 2.0


def test_productivity_growth_length():
	result = clews_to_ogcore(make_clews(5))
	assert len(result.productivity_growth) == 4


def test_alpha_g_within_bounds():
	result = clews_to_ogcore(make_clews(4))
	for v in result.alpha_G:
		assert 0.01 <= v <= 0.40