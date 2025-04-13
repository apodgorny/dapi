import json
from datum import Datum


with open('jsonschema.json') as f:
	d = json.load(f)
	d = Datum(d)

print(d.to_empty_datum())
# # Export schema without $defs
# exported = d.to_dict(schema=True)

# # Verify by creating new Datum and exporting again
# d1 = Datum(exported)
# exported1 = d1.to_dict(schema=True)

# print(json.dumps(exported1, indent=4))
