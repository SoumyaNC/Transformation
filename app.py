from flask import Flask, request, jsonify
import yaml, datetime

app = Flask(__name__)

# Load config from YAML file
with open("crm_transform.yaml") as f:
    mapping_config = yaml.safe_load(f)

# Transformation helpers
def bucket_age(age):
    age = int(age)
    if age < 18: return "Under 18"
    if age <= 25: return "18-25"
    if age <= 35: return "26-35"
    if age <= 50: return "36-50"
    return "50+"

def calculate_duration(start, end):
    try:
        s = datetime.datetime.fromisoformat(start)
        e = datetime.datetime.fromisoformat(end)
        return int((e - s).total_seconds())
    except:
        return 0

def apply_function(rule, row):
    if rule.startswith("__bucket_age("):
        field = rule.split("(")[1][:-1]
        return bucket_age(row.get(field, 0))
    elif rule.startswith("__duration("):
        f1, f2 = rule.split("(")[1][:-1].split(",")
        return calculate_duration(row.get(f1.strip()), row.get(f2.strip()))
    elif rule.startswith("__now"):
        return datetime.datetime.utcnow().isoformat()
    elif rule.startswith("__const("):
        return rule.split("(")[1][:-1]
    return None

# Main transformer
def transform_record(row, config):
    result = {}
    for dest, rule in config["mappings"].items():
        result[dest] = apply_function(rule, row) if rule.startswith("__") else row.get(rule)
    for key, default in config.get("defaults", {}).items():
        result.setdefault(key, default)
    return result

# API endpoint
@app.route("/api/transform", methods=["POST"])
def transform():
    data = request.json
    crm_data = data.get("crm_data", [])
    call_logs = data.get("call_logs", [])

    crm_index = {c["customer_id"]: c for c in crm_data}
    final = []

    for call in call_logs:
        customer = crm_index.get(call["customer_id"], {})
        combined = {**call, **customer}
        transformed = transform_record(combined, mapping_config)
        final.append(transformed)

    return jsonify(final)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
