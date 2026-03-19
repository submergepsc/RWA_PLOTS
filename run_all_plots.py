#!/usr/bin/env python3
"""Utility to run the plot_1 ~ plot_5 scripts in sequence."""

import subprocess
import sys
from pathlib import Path

def main() -> None:
    repo_root = Path(__file__).resolve().parent
    scripts = [
        "plot_1_stacked_bars.py",
        "plot_2_queue.py",
        "plot_3_throught.py",
        "plot_4_certifycate.py",
        "plot_5_scalability.py",
    ]

    for script_name in scripts:
        script_path = repo_root / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"Required plot script not found: {script_path}")

        print(f"\n=== Running {script_name} ===")
        result = subprocess.run([sys.executable, str(script_path)], cwd=repo_root)
        if result.returncode != 0:
            raise RuntimeError(f"Plot script {script_name} failed with exit code {result.returncode}")

    print("\nAll plot scripts completed successfully.")



if __name__ == "__main__":
    main()
