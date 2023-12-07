import os
from pathlib import Path
import wandb
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if the WANDB_API_KEY environment variable is set
if not os.environ.get("WANDB_API_KEY"):
    raise ValueError(
        "You must set the WANDB_API_KEY environment variable to download the model."
    )

# Define the Weights & Biases (wandb) entity, project, and specific run name
entity = "wei_academic"
project = "anomaly_detection"
run_name = "frosty-paper-1"

# Initialize the wandb API
api = wandb.Api()

# Retrieve all runs from the specified project
runs = api.runs(f"{entity}/{project}")

# Find and retrieve the specific run ID for the given run name
for run in runs:
    if run.name == run_name:
        run_id = run.id
        break
else:
    raise ValueError(f"Run with name {run_name} not found in project {project}")

# Download the model and scaler files using the run ID
model_name = "isolation_forest_model.joblib"
scaler_name = "scaler.joblib"
try:
    run = api.run(f"{entity}/{project}/{run_id}")
    run.file(model_name).download(replace=True)  # Download the model file
    run.file(scaler_name).download(replace=True)  # Download the scaler file
    print(f"Model downloaded")
except:
    print("Cannot download model")
