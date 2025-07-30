from datetime import datetime, timezone
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.narrative import Narrative
from fhir.resources.practitioner import Practitioner
from semantic_inferencer import guess_field_meaning
from fallback_handler import handle_unknown_field
from pydantic import ValidationError
import uuid


def convert_to_fhir(data):
    # Normalize: strip whitespace from all keys and values
    data = {str(k).strip(): str(v).strip() for k, v in data.items()}

    uhid = str(data.get("uhid", str(uuid.uuid4()))).strip()
    entries = []
    dob_iso = None

    # Parse DOB if exists
    if "dob" in data:
        try:
            try:
                dob_iso = datetime.strptime(data["dob"], "%d-%b-%Y").date().isoformat()
            except ValueError:
                dob_iso = datetime.strptime(data["dob"], "%Y-%m-%d").date().isoformat()
        except Exception:
            dob_iso = None

    # Create Patient resource safely
    try:
        patient_data = {
            "id": uhid,
            "gender": data.get("gender", "").lower() or None,
            "birthDate": dob_iso,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Patient record</div>"
            }
        }

        # Build HumanName only if valid
        human_name = {}
        if data.get("first_name"):
            human_name["given"] = [data["first_name"]]
        if data.get("last_name"):
            human_name["family"] = data["last_name"]

        if human_name:
            patient_data["name"] = [human_name]
            patient_data["text"]["div"] = (
                f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Patient record for "
                f"{data.get('first_name', '')} {data.get('last_name', '')}</div>"
            )

        # Only add Patient if name, gender, or dob exists
        if any(k in patient_data for k in ("name", "gender", "birthDate")):
            patient = Patient.parse_obj(patient_data)
            entries.append(BundleEntry.construct(
                fullUrl=f"urn:uuid:{uhid}",
                resource=patient,
                request={
                    "method": "POST",
                    "url": "Patient"
                }
            ))
    except ValidationError as e:
        print(f"Skipping invalid Patient: {e.json()}")

    # Create Practitioner with valid UUID
    practitioner_id = str(uuid.uuid4())
    practitioner = Practitioner.parse_obj({
        "id": practitioner_id,
        "name": [{"text": "Example Practitioner"}],
        "text": {
            "status": "generated",
            "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Example Practitioner</div>"
        }
    })
    entries.append(BundleEntry.construct(
        fullUrl=f"urn:uuid:{practitioner_id}",
        resource=practitioner,
        request={
            "method": "POST",
            "url": "Practitioner"
        }
    ))

    # Reserved keys not to convert to Observations
    reserved_fields = {"uhid", "first_name", "last_name", "dob", "gender", "password"}

    for field, value in data.items():
        if field in reserved_fields:
            continue

        meaning = guess_field_meaning(field, value)
        obs = handle_unknown_field(field, value, uhid, meaning)

        if obs:
            obs.effectiveDateTime = datetime.now(timezone.utc).isoformat()
            obs.performer = [{"reference": f"urn:uuid:{practitioner_id}"}]
            obs.text = Narrative.construct(
                status="generated",
                div=f"<div xmlns=\"http://www.w3.org/1999/xhtml\">Observation for {meaning}</div>"
            )

            try:
                entry = BundleEntry.parse_obj({
                    "fullUrl": f"urn:uuid:{uuid.uuid4()}",
                    "resource": obs,
                    "request": {
                        "method": "POST",
                        "url": "Observation"
                    }
                })
                entries.append(entry)
            except ValidationError as e:
                print(f"Skipping invalid Observation for field '{field}': {e.json()}")

    if not entries:
        raise ValueError("No valid FHIR resources could be generated from input.")

    # Build the Bundle
    try:
        bundle = Bundle.parse_obj({
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": entries
        })
    except ValidationError as e:
        raise ValueError(f"Invalid Bundle: {e.json()}")

    return bundle.dict()
