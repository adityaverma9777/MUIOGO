import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bridge.runner import run_coupled, run_converging

FIXTURE_CSV = str(Path('tests/fixtures/sample_clews_output.csv'))

def main():
    print("=" * 55)
    print("  OG-CLEWS Bridge Demo — GSoC 2026")
    print("=" * 55)

    print("\n[1/2] Running COUPLED workflow (CLEWS → OG-Core)...\n")
    coupled_result = run_coupled(
        clews_csv_path=FIXTURE_CSV,
        direction="clews_to_og",
        scenario_label="demo_coupled",
        output_dir="demo_outputs/coupled"
    )
    print("\nCoupled result:")
    print(json.dumps(coupled_result, indent=2))

    print("\n[2/2] Running CONVERGING workflow (iterative)...\n")
    converging_result = run_converging(
        clews_csv_path=FIXTURE_CSV,
        scenario_label="demo_converging",
        output_dir="demo_outputs/converging",
        max_iterations=5,
        tolerance=1e-4
    )
    print("\nConverging result:")
    print(json.dumps(converging_result, indent=2))

    print("\n" + "=" * 55)
    print("  Demo complete. Check demo_outputs/ for JSON results.")
    print("=" * 55)

if __name__ == '__main__':
    main()
