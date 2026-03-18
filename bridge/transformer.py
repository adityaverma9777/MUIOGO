import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from bridge.schema import ClewsEnergyOutput, OGCoreInputs


def clews_to_ogcore(clews: ClewsEnergyOutput, scenario_label: str = "default") -> OGCoreInputs:
		"""
		Maps CLEWS energy system outputs to OG-Core macroeconomic parameters.

		Mapping assumptions (explicitly labelled):
		- Productivity growth: A 1% rise in energy system cost reduces TFP by 0.12%
			(12% energy-cost-to-productivity pass-through). This is a modelling assumption
			that would be calibrated to country-specific data in a full implementation.
		- alpha_G: Energy capital investment as a share of total system cost, scaled by 0.35
			to reflect a typical public-private split in developing country energy sectors.
			Clipped to [0.01, 0.40] - the valid range accepted by OG-Core.
		- initial_debt_ratio: Derived from water stress relative to total system cost.
			Higher water stress implies greater fiscal pressure on government budgets.
		"""
		costs = np.array(clews.total_discounted_cost_usd)
		cost_growth = np.diff(costs) / costs[:-1]
		productivity_growth = (1.0 - cost_growth * 0.12).tolist()

		investments = np.array(clews.capital_investment_usd)
		alpha_G_raw = investments / costs * 0.35
		alpha_G_clipped = np.clip(alpha_G_raw, 0.01, 0.40)
		# Trim to same length as productivity_growth (which is len(costs)-1)
		alpha_G = alpha_G_clipped[:len(productivity_growth)].tolist()

		water = np.array(clews.water_consumption_mm3)
		water_stress = float(np.mean(water) / (np.mean(costs) + 1e-9))
		initial_debt_ratio = float(min(0.3 + water_stress * 0.5, 1.8))
		# Floor at 0.01 to satisfy OGCoreInputs validator
		initial_debt_ratio = max(initial_debt_ratio, 0.01)

		return OGCoreInputs(
				initial_debt_ratio=initial_debt_ratio,
				productivity_growth=productivity_growth,
				alpha_G=alpha_G,
				scenario_label=scenario_label
		)


if __name__ == '__main__':
		from pathlib import Path

		from bridge.extractor import load_clews_output

		clews_data = load_clews_output(
				Path(__file__).parent.parent / 'tests' / 'fixtures' / 'sample_clews_output.csv'
		)
		result = clews_to_ogcore(clews_data, scenario_label='demo')
		print("OGCoreInputs from CLEWS:")
		print(f"  initial_debt_ratio: {result.initial_debt_ratio:.4f}")
		print(f"  productivity_growth: {[round(x,4) for x in result.productivity_growth]}")
		print(f"  alpha_G: {[round(x,4) for x in result.alpha_G]}")
		print(f"  scenario_label: {result.scenario_label}")