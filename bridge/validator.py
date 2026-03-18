from bridge.schema import OGCoreInputs


def validate_for_ogcore(inputs: OGCoreInputs) -> list[str]:
	warnings: list[str] = []

	if inputs.initial_debt_ratio > 1.0:
		warnings.append(
			f"High initial_debt_ratio ({inputs.initial_debt_ratio:.3f}). OG-Core may have convergence issues above 1.0."
		)

	if any(v < 0 for v in inputs.productivity_growth):
		warnings.append(
			"Negative productivity_growth detected. Verify CLEWS cost trajectory — energy costs may be decreasing too sharply."
		)

	if any(v > 1 for v in inputs.productivity_growth):
		warnings.append(
			"productivity_growth above 1.0 (>100%). Check that TotalDiscountedCost values are in consistent units."
		)

	if len(inputs.productivity_growth) < 3:
		warnings.append(
			f"Only {len(inputs.productivity_growth)} projection periods. At least 3 are recommended for meaningful OG-Core results."
		)

	if any(v < 0.01 or v > 0.40 for v in inputs.alpha_G):
		warnings.append(
			"alpha_G values outside valid OG-Core range [0.01, 0.40]. Values were clipped during transformation."
		)

	return warnings


def assert_valid(inputs: OGCoreInputs) -> None:
	warnings = validate_for_ogcore(inputs)
	if warnings:
		print(
			f"BRIDGE VALIDATION: {len(warnings)} warning(s) for scenario '{inputs.scenario_label}':"
		)
		for w in warnings:
			print(f"  WARNING: {w}")
		print("  Proceeding with caution.")
	else:
		print(
			f"BRIDGE VALIDATION: All checks passed for scenario '{inputs.scenario_label}'."
		)