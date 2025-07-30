from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity

def handle_unknown_field(field, value, uhid, meaning):
    if isinstance(value, (int, float)):
        return Observation.construct(
            status="final",
            code=CodeableConcept.construct(text=meaning),
            valueQuantity=Quantity.construct(value=value),
            subject={"reference": f"Patient/{uhid}"}
        )
    else:
        return Observation.construct(
            status="final",
            code=CodeableConcept.construct(text=meaning),
            valueString=str(value),
            subject={"reference": f"Patient/{uhid}"}
        )
