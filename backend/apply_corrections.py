import json
import requests
import os

def apply_corrections():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'corrections.json')
    with open(json_path, 'r') as f:
        corrections = json.load(f)

    url = 'http://127.0.0.1:8000/api/marks/corrections/'
    
    success_count = 0
    fail_count = 0
    
    for correction in corrections:
        response = requests.post(url, json=correction)
        if response.status_code == 200:
            print(f"SUCCESS: {correction['admission_no']} - {correction['subject']}")
            success_count += 1
        else:
            print(f"FAILED: {correction['admission_no']} - {correction['subject']} | Error: {response.json()}")
            fail_count += 1

    print(f"\nApplied corrections: {success_count} succeeded, {fail_count} failed.")

if __name__ == '__main__':
    apply_corrections()
