import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from bridge.schema import ClewsEnergyOutput


def load_clews_output(csv_path: str | Path) -> ClewsEnergyOutput:
	csv_path = Path(csv_path)
	if not csv_path.exists():
		raise FileNotFoundError(f"CLEWS output CSV not found: {csv_path}")

	df = pd.read_csv(csv_path)

	required = [
		'YEAR',
		'TECHNOLOGY',
		'FUEL',
		'TotalDiscountedCost',
		'ProductionByTechnology',
		'CapitalInvestment',
		'WaterConsumption',
	]
	missing_cols = [col for col in required if col not in df.columns]
	if missing_cols:
		raise ValueError(f"Missing required columns: {missing_cols}")

	numeric_cols = [
		'TotalDiscountedCost',
		'ProductionByTechnology',
		'CapitalInvestment',
		'WaterConsumption',
	]
	grouped = df.groupby('YEAR')[numeric_cols].sum().reset_index()
	grouped = grouped.sort_values('YEAR', ascending=True)

	return ClewsEnergyOutput(
		year=grouped['YEAR'].tolist(),
		technology=['aggregated'] * len(grouped),
		total_discounted_cost_usd=grouped['TotalDiscountedCost'].tolist(),
		production_by_technology_pj=grouped['ProductionByTechnology'].tolist(),
		capital_investment_usd=grouped['CapitalInvestment'].tolist(),
		water_consumption_mm3=grouped['WaterConsumption'].tolist(),
	)


if __name__ == '__main__':
	from pathlib import Path

	result = load_clews_output(
		Path(__file__).parent.parent / 'tests' / 'fixtures' / 'sample_clews_output.csv'
	)
	print("Loaded CLEWS output:")
	print(f"  Years: {result.year}")
	print(f"  Total costs (USD): {result.total_discounted_cost_usd}")
	print(f"  Capital investment: {result.capital_investment_usd}")
	print(f"  Water consumption: {result.water_consumption_mm3}")