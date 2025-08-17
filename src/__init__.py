from . import biometric
from . import evaluate
from . import summary
import os
import yaml

def run_all():
    """
    Runs the entire evaluation pipeline in sequence:
    1. Biometric measurement (biometric.py)
    2. Model evaluation (evaluate.py)
    3. Results summary (summary.py)
    """
    print("--- Starting biometric measurement ---")
    biometric.main()
    print("--- Biometric measurement finished ---\n")

    print("--- Starting model evaluation ---")
    evaluate.main()
    print("--- Model evaluation finished ---\n")

    print("--- Starting results summary ---")
    summary.main()
    print("--- Results summary finished ---\n")
    
    print("All processes completed successfully.")

if __name__ == '__main__':
    # To ensure the script can find config.yaml when run from the project root,
    # we need to make sure the current working directory is correct.
    # When __init__.py is run, its path is src/__init__.py
    # We need to change the working directory to the parent directory.
    # Get the absolute path of config.yaml
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    work_dir = cfg["work_dir"]
    os.chdir(work_dir)
    
    run_all()
