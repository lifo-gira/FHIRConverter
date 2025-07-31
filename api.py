from fastapi import FastAPI, HTTPException
from typing import Dict, Any
from fhir_mapper import convert_to_fhir
import tempfile
import subprocess
import os
import json
from fhir.resources.bundle import Bundle

app = FastAPI()

FHIR_VALIDATOR_PATH = "./fhir/validator_cli.jar"  # Adjust path as needed

@app.get("/")
def root():
    return {"message": "FHIR Converter is running"}


# --- API 1: Convert only ---
@app.post("/convert")
def convert_only(data: Dict[str, Any]):
    try:
        fhir_bundle = convert_to_fhir(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return fhir_bundle  # return only the FHIR bundle (dict), no status wrapper



# --- API 2: Convert and Validate ---
@app.post("/convert-and-validate")
def convert_and_validate(data: Dict[str, Any]):
    try:
        fhir_bundle = convert_to_fhir(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save FHIR to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp_file:
        bundle_obj = Bundle.parse_obj(fhir_bundle)
        tmp_file.write(bundle_obj.json(indent=2))  # This handles dates and FHIR serialization
        tmp_file_path = tmp_file.name

    # Run validation
    try:
        result = subprocess.run(
            ["java", "-jar", FHIR_VALIDATOR_PATH, tmp_file_path, "-version", "4.0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        os.unlink(tmp_file_path)
        raise HTTPException(status_code=500, detail=f"Error running validator: {str(e)}")

    # Clean up temp file
    os.unlink(tmp_file_path)

    return {
        "status": "success",
        "fhir": fhir_bundle,
        "validation": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "valid": result.returncode == 0
        }
    }
