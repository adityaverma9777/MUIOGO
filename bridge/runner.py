import json
import logging
from pathlib import Path

from bridge.extractor import load_clews_output
from bridge.transformer import clews_to_ogcore
from bridge.validator import assert_valid


logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s [BRIDGE] %(levelname)s: %(message)s',
	datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def run_coupled(
	clews_csv_path: str | Path,
	direction: str = "clews_to_og",
	scenario_label: str = "coupled_run",
	output_dir: str | Path = "WebAPP/DataStorage/CoupledRuns"
) -> dict:
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	logger.info(f"Starting coupled run | direction={direction} | scenario={scenario_label}")

	if direction == "clews_to_og":
		clews_data = load_clews_output(clews_csv_path)
		logger.info(f"Loaded CLEWS output: {len(clews_data.year)} time periods")

		og_inputs = clews_to_ogcore(clews_data, scenario_label=scenario_label)
		logger.info(f"Transformed to OG-Core inputs | debt_ratio={og_inputs.initial_debt_ratio:.3f}")

		assert_valid(og_inputs)

		out_path = output_dir / f"{scenario_label}_ogcore_inputs.json"
		with open(out_path, 'w') as f:
			json.dump(og_inputs.model_dump(), f, indent=2)
		logger.info(f"Saved OG-Core inputs to {out_path}")

		return {
			"status": "success",
			"direction": direction,
			"scenario": scenario_label,
			"periods": len(clews_data.year),
			"ogcore_inputs_path": str(out_path),
			"initial_debt_ratio": round(og_inputs.initial_debt_ratio, 4),
			"productivity_growth": [round(x, 4) for x in og_inputs.productivity_growth],
			"alpha_G": [round(x, 4) for x in og_inputs.alpha_G]
		}

	elif direction == "og_to_clews":
		logger.info("og_to_clews direction: stub only, not yet implemented")
		return {"status": "stub", "message": "og_to_clews direction is not yet implemented"}

	else:
		raise ValueError(f"Unknown direction '{direction}'. Use 'clews_to_og' or 'og_to_clews'.")


def run_converging(
	clews_csv_path: str | Path,
	scenario_label: str = "converging_run",
	output_dir: str | Path = "WebAPP/DataStorage/ConvergingRuns",
	max_iterations: int = 10,
	tolerance: float = 1e-4
) -> dict:
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	logger.info(f"Starting converging run | max_iter={max_iterations} | tol={tolerance} | scenario={scenario_label}")

	clews_data = load_clews_output(clews_csv_path)
	og_inputs = clews_to_ogcore(clews_data, scenario_label=scenario_label)
	assert_valid(og_inputs)

	prev_debt_ratio = og_inputs.initial_debt_ratio
	prev_productivity = list(og_inputs.productivity_growth)
	final_delta = None
	converged_at = None

	for i in range(1, max_iterations + 1):
		logger.info(f"Stub: applying 0.1% OG-Core feedback to productivity growth (iteration {i})")
		updated_productivity = [v * 1.001 for v in prev_productivity]

		import numpy as np
		import numpy as np_
		new_debt_ratio = float(min(prev_debt_ratio * (1 + 0.001 * i), 1.8))

		from bridge.schema import OGCoreInputs
		iter_inputs = OGCoreInputs(
			initial_debt_ratio=new_debt_ratio,
			productivity_growth=updated_productivity,
			alpha_G=og_inputs.alpha_G,
			scenario_label=f"{scenario_label}_iter{i}"
		)

		iter_path = output_dir / f"{scenario_label}_iter{i}.json"
		with open(iter_path, 'w') as f:
			json.dump(iter_inputs.model_dump(), f, indent=2)

		delta = abs(new_debt_ratio - prev_debt_ratio)
		logger.info(f"Iteration {i} complete | delta={delta:.6f} | saved to {iter_path}")

		if delta < tolerance:
			converged_at = i
			final_delta = delta
			logger.info(f"Converged at iteration {i} (delta={delta:.6f} < tol={tolerance})")
			break

		prev_debt_ratio = new_debt_ratio
		prev_productivity = updated_productivity
		final_delta = delta

	status = "converged" if converged_at else "max_iterations_reached"
	return {
		"status": status,
		"scenario": scenario_label,
		"iterations_run": converged_at or max_iterations,
		"final_delta": round(final_delta, 8) if final_delta else None,
		"tolerance": tolerance,
		"output_dir": str(output_dir)
	}