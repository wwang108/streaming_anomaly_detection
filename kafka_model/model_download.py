import os
from pathlib import Path
import wandb
from dotenv import load_dotenv
load_dotenv()
if not os.environ.get("WANDB_API_KEY"):
    raise ValueError(
        "You must set the WANDB_API_KEY environment variable " "to download the model."
    )

entity = "wei_academic"
project = "anomaly_detection"
run_name = "frosty-paper-1"

# Initialize the wandb API
api = wandb.Api()

# Get all runs from the project
runs = api.runs(f"{entity}/{project}")

# Find the run ID for the specified run name
for run in runs:
    if run.name == run_name:
        run_id = run.id
        break
else:
    raise ValueError(f"Run with name {run_name} not found in project {project}")

# Now you can use the run ID to get the specific run and download the file
model_name = "isolation_forest_model.joblib"
scaler_name = "scaler.joblib"
try:
    run = api.run(f"{entity}/{project}/{run_id}")
    run.file(model_name).download(replace=True)
    run.file(scaler_name).download(replace=True)
    print(f"Model downloaded")
except:
    print("Cannot download model")