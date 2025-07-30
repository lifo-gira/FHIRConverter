def guess_field_meaning(field, value):
    if isinstance(value, str):
        if '@' in value:
            return 'Email'
        if 'Dr' in value or 'doctor' in field.lower():
            return 'Practitioner Reference'
        if value.lower() in ['male', 'female']:
            return 'Gender'
        if value.endswith('AM') or value.endswith('PM'):
            return 'Time'
        if '-' in value and ':' in value:
            return 'DateTime'
        if value.replace(" ", "").isalpha():
            return field.replace("_", " ").title()

    elif isinstance(value, (int, float)):
        if 30 <= value <= 180:
            return "Heart Rate or Blood Pressure"
        elif 10 <= value <= 250:
            return "Weight or Numeric"
        elif 10 < value < 60:
            return "BMI or Age"
        elif value in [0, 1]:
            return "Boolean"

    elif isinstance(value, list):
        return "Score Array"

    elif isinstance(value, dict):
        if "date" in value or "$date" in str(value):
            return "DateTime or Event"

    return field.replace("_", " ").title()
