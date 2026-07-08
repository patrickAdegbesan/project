"""
seed_data.py
Pre-loads the database with realistic simulation runs so the web app
looks fully populated for demonstration and screenshots.

Run:  python seed_data.py
"""

import json
import sys
from datetime import datetime, timedelta

# Must import app context before anything else
from app import app, db, SimulationRun
from config import SimConfig
from experiments import run_experiments, summarise_experiments

RUNS = [
    {
        "run_name":    "Lagos Island Peak-Hour Scenario",
        "num_nodes":   3,
        "service_rate": 1.0,
        "buffer_size": 50,
        "duration":    500,
        "num_reps":    5,
        "seed":        42,
        "load_levels": [0.5, 0.8, 1.0, 1.2],
        "offset_mins": 120,   # how many minutes ago this run was created
    },
    {
        "run_name":    "Victoria Island High-Density Test",
        "num_nodes":   5,
        "service_rate": 1.0,
        "buffer_size": 100,
        "duration":    500,
        "num_reps":    5,
        "seed":        99,
        "load_levels": [0.5, 0.8, 1.0, 1.2],
        "offset_mins": 90,
    },
    {
        "run_name":    "M/M/1 Validation Run",
        "num_nodes":   1,
        "service_rate": 1.0,
        "buffer_size": 200,
        "duration":    1000,
        "num_reps":    1,
        "seed":        42,
        "load_levels": [0.8],
        "offset_mins": 60,
    },
    {
        "run_name":    "Surulere Base Station Cluster",
        "num_nodes":   4,
        "service_rate": 1.0,
        "buffer_size": 75,
        "duration":    500,
        "num_reps":    5,
        "seed":        77,
        "load_levels": [0.5, 0.8, 1.0, 1.2],
        "offset_mins": 30,
    },
    {
        "run_name":    "Ikeja Commercial Zone Analysis",
        "num_nodes":   3,
        "service_rate": 1.0,
        "buffer_size": 30,   # small buffer → more drops at high load
        "duration":    500,
        "num_reps":    5,
        "seed":        123,
        "load_levels": [0.5, 0.8, 1.0, 1.2],
        "offset_mins": 10,
    },
]


def seed():
    with app.app_context():
        db.create_all()

        # Clear existing data for a clean demo load
        SimulationRun.query.delete()
        db.session.commit()

        for i, spec in enumerate(RUNS):
            print(f"[{i+1}/{len(RUNS)}] Running: {spec['run_name']} …", flush=True)

            cfg = SimConfig(
                service_rate     = spec["service_rate"],
                num_nodes        = spec["num_nodes"],
                buffer_size      = spec["buffer_size"],
                duration         = spec["duration"],
                num_replications = spec["num_reps"],
                load_levels      = tuple(spec["load_levels"]),
            )

            raw_df  = run_experiments(cfg, base_seed=spec["seed"])
            summary = summarise_experiments(raw_df)
            results = summary.to_dict(orient="records")

            created_at   = datetime.utcnow() - timedelta(minutes=spec["offset_mins"])
            completed_at = created_at + timedelta(seconds=4)

            run = SimulationRun(
                run_name     = spec["run_name"],
                num_nodes    = spec["num_nodes"],
                service_rate = spec["service_rate"],
                buffer_size  = spec["buffer_size"],
                duration     = spec["duration"],
                num_reps     = spec["num_reps"],
                seed         = spec["seed"],
                load_levels  = json.dumps(spec["load_levels"]),
                results_json = json.dumps(results),
                status       = "done",
                created_at   = created_at,
                completed_at = completed_at,
            )
            db.session.add(run)
            db.session.commit()
            print(f"   Saved run id={run.id}  ({len(results)} load levels)")

        total = SimulationRun.query.count()
        print(f"\nDone. {total} simulation runs in database.")
        print("Start the app with:  python app.py")


if __name__ == "__main__":
    seed()
