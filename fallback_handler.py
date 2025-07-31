from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity
from fhir.resources.fhirtypes import ReferenceType

def handle_unknown_field(field, value, uhid, meaning):
    subject = {"reference": f"Patient/{uhid}"}
    code = CodeableConcept.construct(text=meaning)

    if isinstance(value, (int, float)):
        return Observation(
            status="final",
            code=code,
            valueQuantity=Quantity(value=value),
            subject=subject
        )
    else:
        return Observation(
            status="final",
            code=code,
            valueString=str(value),
            subject=subject
        )
