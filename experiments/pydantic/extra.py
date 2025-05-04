from pydantic import BaseModel
from o import O  # Импорт твоего O с обновлённым Field

class X(O):
	value: str = O.Field('', description='Test description')

print(X.model_fields['value'].description)
print(X.model_fields['value'].json_schema_extra)