import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_query(prompt: str, expect_permission: bool = False):
    print(f"\n==========================================")
    print(f"QUERY: '{prompt}'")
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/chat", json={"message": prompt}, timeout=120)
        elapsed = round(time.time() - start, 2)
        print(f"Elapsed: {elapsed}s | Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Agent Status: {data.get('status')}")
            steps = data.get("steps", [])
            print(f"Steps taken ({len(steps)}):")
            for s in steps:
                act = s.get("action_type")
                tool = s.get("tool_name", "")
                msg = s.get("status_message", "")
                print(f"  - [{act}] {tool}: {msg}")
            
            if data.get("permission_request"):
                perm = data.get("permission_request")
                print(f"PERM REQUEST DETECTED: ID={perm.get('id')}, Tool={perm.get('tool_name')}")
                if expect_permission:
                    print("SUCCESS: Expected sensitive permission was correctly intercepted!")
                    # Test approving it!
                    print("Testing approval...")
                    apr = requests.post(f"{BASE_URL}/permissions/{perm.get('id')}/approve", timeout=60)
                    print(f"Approval response status: {apr.status_code}")
                    if apr.status_code == 200:
                        apr_data = apr.json()
                        print(f"Post-approval status: {apr_data.get('status')}")
                        print(f"Final response: {apr_data.get('final_response', '')[:200]}...")
            else:
                resp = data.get("final_response", "")
                print(f"Response:\n{resp}")
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Assignment inquiry (LMS tools)
    test_query("Do I have any assignments due this week?")

    # Test 2: Windows process launch (System tool)
    test_query("Open Calculator.")

    # Test 3: Sensitive action interception & approval
    test_query("Send an email to prof.martinez@university.edu with subject 'Extension Request' and body 'Dear Professor, could I please request a 2-day extension on Assignment 3?'", expect_permission=True)
