from pydantic import BaseModel, field_validator, model_validator


class ClewsEnergyOutput(BaseModel):
	year: list[int]
	technology: list[str]
	total_discounted_cost_usd: list[float]
	production_by_technology_pj: list[float]
	capital_investment_usd: list[float]
	water_consumption_mm3: list[float]

	@model_validator(mode='after')
	def check_lengths_and_values(self):
		year_len = len(self.year)
		technology_len = len(self.technology)
		total_discounted_cost_usd_len = len(self.total_discounted_cost_usd)
		production_by_technology_pj_len = len(self.production_by_technology_pj)
		capital_investment_usd_len = len(self.capital_investment_usd)
		water_consumption_mm3_len = len(self.water_consumption_mm3)

		if (
			technology_len != year_len
			or total_discounted_cost_usd_len != year_len
			or production_by_technology_pj_len != year_len
			or capital_investment_usd_len != year_len
			or water_consumption_mm3_len != year_len
		):
			raise ValueError(
				"All fields must have the same length. "
				f"Got: year={year_len}, "
				f"technology={technology_len}, "
				f"total_discounted_cost_usd={total_discounted_cost_usd_len}, "
				f"production_by_technology_pj={production_by_technology_pj_len}, "
				f"capital_investment_usd={capital_investment_usd_len}, "
				f"water_consumption_mm3={water_consumption_mm3_len}"
			)

		if any(value < 0 for value in self.total_discounted_cost_usd):
			raise ValueError("total_discounted_cost_usd contains negative values")

		if any(value < 0 for value in self.capital_investment_usd):
			raise ValueError("capital_investment_usd contains negative values")

		return self


class OGCoreInputs(BaseModel):
	initial_debt_ratio: float
	productivity_growth: list[float]
	alpha_G: list[float]
	scenario_label: str

	@field_validator('initial_debt_ratio', mode='after')
	@classmethod
	def validate_initial_debt_ratio(cls, value: float) -> float:
		if value <= 0.0 or value >= 2.0:
			raise ValueError("initial_debt_ratio must be between 0.0 and 2.0 exclusive")
		return value


if __name__ == '__main__':
	sample_clews = ClewsEnergyOutput(
		year=[2025, 2026, 2027],
		technology=['SOLAR', 'SOLAR', 'WIND'],
		total_discounted_cost_usd=[1.2e9, 1.26e9, 1.31e9],
		production_by_technology_pj=[4800.0, 5040.0, 5250.0],
		capital_investment_usd=[3.4e8, 3.57e8, 3.7e8],
		water_consumption_mm3=[185.0, 192.0, 198.0]
	)
	print("ClewsEnergyOutput OK:", sample_clews)

	sample_og = OGCoreInputs(
		initial_debt_ratio=0.45,
		productivity_growth=[0.98, 0.97],
		alpha_G=[0.08, 0.09],
		scenario_label='test_scenario'
	)
	print("OGCoreInputs OK:", sample_og)