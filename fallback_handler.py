from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity


def handle_unknown_field(field, value, uhid, meaning):
    subject = {"reference": f"Patient/{uhid}"}
    code = CodeableConcept.construct(text=meaning)

    try:
        # Attempt to convert to float if it's a numeric-looking string
        numeric_value = float(value)
        return Observation(
            status="final",
            code=code,
            valueQuantity=Quantity.construct(value=numeric_value),
            subject=subject
        )
    except (ValueError, TypeError):
        # Fall back to string if it's not convertible
        return Observation(
            status="final",
            code=code,
            valueString=str(value),
            subject=subject
        )
