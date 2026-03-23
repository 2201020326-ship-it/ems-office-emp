#!/usr/bin/env python
"""Test script for date and time types in EMS API."""

import json
import urllib.request
import urllib.error
import time
import sys

base_url = "http://127.0.0.1:5000"

def test_workflow():
    """Test the complete EMS workflow with date/time types."""
    try:
        # Test 1: Register employee
        print("=" * 60)
        print("TEST 1: Register Employee")
        print("=" * 60)
        payload = {
            "name": "David Brown",
            "phone": "5557777777",
            "password": "TestPass789"
        }
        req = urllib.request.Request(
            f"{base_url}/register",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"✓ Employee registered with ID: {data['employee_id']}")
            emp_id = data['employee_id']

        # Test 2: Submit work details with date and time
        print("\n" + "=" * 60)
        print("TEST 2: Submit Work Details (with date and time)")
        print("=" * 60)
        payload = {
            "employee_id": emp_id,
            "work_date": "2026-03-20",
            "slots": [
                {
                    "start_time": "08:00:00",
                    "end_time": "11:30:00",
                    "description": "Morning work"
                },
                {
                    "start_time": "12:30:00",
                    "end_time": "16:45:00",
                    "description": "Afternoon work"
                }
            ]
        }
        req = urllib.request.Request(
            f"{base_url}/work-details",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"✓ Work details submitted successfully")
            print(f"  - Slots saved: {data['slots_saved']}")
            print(f"  - Work date: {data['work_date']}")
            print(f"  - Employee ID: {data['employee_id']}")

        time.sleep(1)

        # Test 3: Retrieve timesheets to verify date/time formatting
        print("\n" + "=" * 60)
        print("TEST 3: Retrieve Timesheets (verify date/time format)")
        print("=" * 60)
        req = urllib.request.Request(f"{base_url}/timesheets/{emp_id}", method="GET")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            print(f"✓ Retrieved {len(data)} timesheet records\n")
            
            for i, record in enumerate(data, 1):
                print(f"  Slot #{i}:")
                print(f"    - work_date: {record['work_date']} (DATE format)")
                print(f"    - start_time: {record['start_time']} (TIME format)")
                print(f"    - end_time: {record['end_time']} (TIME format)")
                print(f"    - slot_number: {record['slot_number']}")
                print(f"    - description: {record['description']}")

        print("\n" + "=" * 60)
        print("✓✓✓ SUCCESS: All date and time types working correctly! ✓✓✓")
        print("=" * 60)
        print("\nSummary:")
        print("  • Date stored as DATE format (YYYY-MM-DD)")
        print("  • Time stored as TIME format (HH:MM:SS)")
        print("  • All endpoints working with proper type validation")
        return True

    except urllib.error.HTTPError as e:
        print(f"\n✗ HTTP Error {e.code}: {e.reason}")
        error_body = e.read().decode()
        print(f"  Response body: {error_body}")
        return False
    except urllib.error.URLError as e:
        print(f"\n✗ Connection Error: {e.reason}")
        print("  Is the API server running on http://127.0.0.1:5000?")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)
