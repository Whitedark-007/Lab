import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

BACKUP_PATH = os.path.join(SAMPLE_DIR, "mobile_backup.json")


def create_sample_mobile_backup():
    if os.path.exists(BACKUP_PATH):
        return

    sample_data = {
        "device_info": {
            "model": "Android DemoPhone X",
            "imei": "123456789012345",
            "owner": "User A"
        },
        "contacts": [
            {"name": "Alice", "number": "+919876543210"},
            {"name": "Bob", "number": "+911234567890"},
            {"name": "Unknown", "number": "+918888888888"},
        ],
        "call_logs": [
            {"number": "+919876543210", "type": "OUTGOING", "duration_sec": 300,
             "timestamp": "2025-11-12 20:30:00"},
            {"number": "+911234567890", "type": "INCOMING", "duration_sec": 120,
             "timestamp": "2025-11-12 21:00:00"},
            {"number": "+918888888888", "type": "MISSED", "duration_sec": 0,
             "timestamp": "2025-11-12 22:00:00"},
        ],
        "sms": [
            {"number": "+919876543210", "direction": "SENT",
             "body": "Meet at 9 PM behind the lab.", "timestamp": "2025-11-12 18:00:00"},
            {"number": "+918888888888", "direction": "RECEIVED",
             "body": "Bring the documents and pen drive.", "timestamp": "2025-11-12 18:30:00"},
        ],
        "app_chats": [
            {"app": "WhatsApp", "peer": "Alice", "direction": "SENT",
             "body": "Did you delete the emails?", "timestamp": "2025-11-12 19:00:00"},
            {"app": "WhatsApp", "peer": "Alice", "direction": "RECEIVED",
             "body": "Yes, all traces removed.", "timestamp": "2025-11-12 19:05:00"},
        ],
        "locations": [
            {"timestamp": "2025-11-12 21:00:00",
             "lat": 12.9716, "lon": 77.5946, "place": "Bangalore Central"},
            {"timestamp": "2025-11-12 22:00:00",
             "lat": 12.2958, "lon": 76.6394, "place": "Mysore"},
        ]
    }
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=4)


def load_backup(path=None):
    if path is None:
        create_sample_mobile_backup()
        path = BACKUP_PATH
    with open(path, encoding="utf-8") as f:
        return json.load(f), path


def print_contacts(data):
    print("\nContacts:")
    for c in data.get("contacts", []):
        print(f"{c['name']} -> {c['number']}")


def filter_by_number_prompt():
    n = input("Enter (part of) phone number to search (or leave empty for all): ").strip()
    return n or None


def print_call_logs(data):
    print("\nCall logs:")
    target = filter_by_number_prompt()
    for c in data.get("call_logs", []):
        if target and target not in c["number"]:
            continue
        print(f"[{c['timestamp']}] {c['type']} {c['number']} ({c['duration_sec']} sec)")


def print_sms(data):
    print("\nSMS messages:")
    target = filter_by_number_prompt()
    keyword = input("Enter keyword to search in SMS body (optional): ").strip().lower()
    for s in data.get("sms", []):
        if target and target not in s["number"]:
            continue
        if keyword and keyword not in s["body"].lower():
            continue
        direction = "->" if s["direction"] == "SENT" else "<-"
        print(f"[{s['timestamp']}] {direction} {s['number']}: {s['body']}")


def print_app_chats(data):
    print("\nApp chats:")
    app_filter = input("Filter by app name (e.g., WhatsApp) or leave blank: ").strip()
    peer_filter = input("Filter by peer name (e.g., Alice) or leave blank: ").strip()

    for m in data.get("app_chats", []):
        if app_filter and app_filter.lower() not in m["app"].lower():
            continue
        if peer_filter and peer_filter.lower() not in m["peer"].lower():
            continue
        arrow = "->" if m["direction"] == "SENT" else "<-"
        print(f"[{m['timestamp']}] {m['app']} {arrow} {m['peer']}: {m['body']}")


def print_locations(data):
    print("\nLocation history:")
    for loc in data.get("locations", []):
        print(f"[{loc['timestamp']}] {loc['lat']},{loc['lon']} - {loc['place']}")


def generate_report(data, source_path):
    case_id = input("Enter Case ID: ").strip() or "CASE_MOBILE_DEMO"
    examiner = input("Enter Examiner Name: ").strip() or "Examiner"
    report_name = f"{case_id}_mobile_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"MOBILE ANALYSIS REPORT - {case_id}\n")
        f.write(f"Source Backup: {source_path}\n")
        f.write(f"Examiner: {examiner}\n")
        f.write(f"Generated: {datetime.now()}\n\n")

        f.write("Device Info:\n")
        di = data.get("device_info", {})
        for k, v in di.items():
            f.write(f"  {k}: {v}\n")

        f.write("\nTotal Contacts: " + str(len(data.get("contacts", []))) + "\n")
        f.write("Total Call Logs: " + str(len(data.get("call_logs", []))) + "\n")
        f.write("Total SMS: " + str(len(data.get("sms", []))) + "\n")
        f.write("Total App Chats: " + str(len(data.get("app_chats", []))) + "\n")
        f.write("Total Locations: " + str(len(data.get("locations", []))) + "\n\n")

        f.write("Suspicious SMS (containing 'meet' or 'documents'):\n")
        for s in data.get("sms", []):
            if "meet" in s["body"].lower() or "document" in s["body"].lower():
                f.write(f"- [{s['timestamp']}] {s['number']}: {s['body']}\n")

    print("Report saved at:", report_path)


def main():
    print("Mobile backup analysis tool.")
    use_custom = input("Use custom mobile backup JSON file? (y/N): ").strip().lower()
    path = None
    if use_custom == "y":
        p = input("Enter full path to JSON backup: ").strip()
        if os.path.isfile(p):
            path = p
        else:
            print("File not found. Using sample backup instead.")
    data, source_path = load_backup(path)

    while True:
        print("\nMain Menu:")
        print("1) View contacts")
        print("2) View call logs")
        print("3) View SMS")
        print("4) View app chats")
        print("5) View location history")
        print("6) Generate summary report")
        print("0) Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            print_contacts(data)
        elif choice == "2":
            print_call_logs(data)
        elif choice == "3":
            print_sms(data)
        elif choice == "4":
            print_app_chats(data)
        elif choice == "5":
            print_locations(data)
        elif choice == "6":
            generate_report(data, source_path)
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
