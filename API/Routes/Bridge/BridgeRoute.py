import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
PROJECT_ROOT = Path(__file__).resolve().parents[3]

from flask import Blueprint, jsonify, request

from bridge.runner import run_coupled, run_converging

bridge_api = Blueprint('bridge_api', __name__, url_prefix='/bridge')


@bridge_api.route('/coupled', methods=['POST'])
def coupled():
    try:
        body = request.json or {}
        result = run_coupled(
            clews_csv_path=body.get('clews_csv_path', str(PROJECT_ROOT / 'tests' / 'fixtures' / 'sample_clews_output.csv')),
            direction=body.get('direction', 'clews_to_og'),
            scenario_label=body.get('scenario_label', 'coupled_run'),
            output_dir=body.get('output_dir', str(PROJECT_ROOT / 'WebAPP' / 'DataStorage' / 'CoupledRuns'))
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e), "type": "ValueError"}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e), "type": "FileNotFoundError"}), 404
    except Exception as e:
        return jsonify({"error": str(e), "type": "InternalError"}), 500


@bridge_api.route('/converging', methods=['POST'])
def converging():
    try:
        body = request.json or {}
        result = run_converging(
            clews_csv_path=body.get('clews_csv_path', str(PROJECT_ROOT / 'tests' / 'fixtures' / 'sample_clews_output.csv')),
            scenario_label=body.get('scenario_label', 'converging_run'),
            output_dir=body.get('output_dir', str(PROJECT_ROOT / 'WebAPP' / 'DataStorage' / 'ConvergingRuns')),
            max_iterations=int(body.get('max_iterations', 10)),
            tolerance=float(body.get('tolerance', 1e-4))
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e), "type": "ValueError"}), 400
    except FileNotFoundError as e:
        return jsonify({"error": str(e), "type": "FileNotFoundError"}), 404
    except Exception as e:
        return jsonify({"error": str(e), "type": "InternalError"}), 500
