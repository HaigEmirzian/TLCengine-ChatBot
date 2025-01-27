import json
import re

def is_invalid(value):
    if value is None or value == "NULL" or value == "" or isinstance(value, str) and re.match(r'http[s]?://', value): return True
    return False

def simplify_json(json_str):
    python_obj = json.loads(json_str)
    
    def recursive_cleanup(obj):
        if isinstance(obj, dict):
            return {key: recursive_cleanup(value) for key, value in obj.items() if not is_invalid(value)}
        elif isinstance(obj, list):
            return [recursive_cleanup(item) for item in obj if not is_invalid(item)]
        return obj
    
    return json.dumps(recursive_cleanup(python_obj))