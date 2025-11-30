import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

CLOUD_EXPORT = os.path.join(SAMPLE_DIR, "cloud_export.json")


def create_sample_cloud_export():
    if os.path.exists(CLOUD_EXPORT):
        return

    export = {
        "service": "Google Drive",
        "account_email": "suspect@example.com",
        "files": [
            {
                "id": "1",
                "name": "ProjectPlan.docx",
                "path": "/Work/ProjectPlan.docx",
                "size_bytes": 20480,
                "owner": "suspect@example.com",
                "shared_with": ["colleague@example.com"],
                "deleted": False,
                "created": "2025-11-01 10:00:00",
                "modified": "2025-11-10 12:00:00"
            },
            {
                "id": "2",
                "name": "Secrets.txt",
                "path": "/Hidden/Secrets.txt",
                "size_bytes": 1024,
                "owner": "suspect@example.com",
                "shared_with": ["external@malicious.com"],
                "deleted": False,
                "created": "2025-11-05 09:00:00",
                "modified": "2025-11-10 15:00:00"
            },
            {
                "id": "3",
                "name": "DeletedEvidence.zip",
                "path": "/Trash/DeletedEvidence.zip",
                "size_bytes": 5096,
                "owner": "suspect@example.com",
                "shared_with": [],
                "deleted": True,
                "created": "2025-10-20 08:00:00",
                "modified": "2025-10-21 09:00:00"
            }
        ],
        "access_logs": [
            {"timestamp": "2025-11-10 15:05:00", "ip": "203.45.67.89",
             "country": "Unknown", "action": "DOWNLOAD", "file_id": "2"},
            {"timestamp": "2025-11-10 15:06:00", "ip": "192.168.1.10",
             "country": "Local", "action": "VIEW", "file_id": "1"},
            {"timestamp": "2025-11-09 11:00:00", "ip": "203.45.67.89",
             "country": "Unknown", "action": "LOGIN", "file_id": None},
        ]
    }
    with open(CLOUD_EXPORT, "w", encoding="utf-8") as f:
        json.dump(export, f, indent=4)


def load_export(path=None):
    if path is None:
        create_sample_cloud_export()
        path = CLOUD_EXPORT
    with open(path, encoding="utf-8") as f:
        return json.load(f), path


def list_files(data, filter_deleted=None, only_shared=None):
    print("\nCloud files:")
    for f in data.get("files", []):
        if filter_deleted is not None and f["deleted"] != filter_deleted:
            continue
        if only_shared and not f["shared_with"]:
            continue
        deleted_mark = "[DELETED] " if f["deleted"] else ""
        print(f"{deleted_mark}{f['id']}: {f['path']} ({f['size_bytes']} bytes)")
        if f["shared_with"]:
            print("   Shared with:", ", ".join(f["shared_with"]))


def search_files(data):
    keyword = input("Enter keyword (name/path) or extension (e.g., .txt): ").strip().lower()
    print("\nSearch results:")
    for f in data.get("files", []):
        if keyword in f["name"].lower() or keyword in f["path"].lower():
            print(f"{f['id']}: {f['path']} - owner={f['owner']}, deleted={f['deleted']}")


def view_access_logs(data):
    print("\nAccess logs:")
    suspicious_ip = input("Mark any IP as suspicious (e.g., 203.45.67.89) or leave blank: ").strip()
    for log in data.get("access_logs", []):
        flag = ""
        if suspicious_ip and log["ip"] == suspicious_ip:
            flag = " [SUSPICIOUS]"
        file_id = log.get("file_id")
        file_name = ""
        if file_id:
            for f in data.get("files", []):
                if f["id"] == file_id:
                    file_name = f"{f['name']} "
                    break
        print(f"[{log['timestamp']}] {log['ip']} ({log['country']}){flag} "
              f"{log['action']} {file_name}".strip())


def generate_cloud_report(data, source_path):
    case_id = input("Enter Case ID: ").strip() or "CASE_CLOUD_DEMO"
    examiner = input("Enter Examiner: ").strip() or "Examiner"
    report_name = f"{case_id}_cloud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)

    suspicious_ip = input("Enter known suspicious IP (leave blank if none): ").strip()

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"CLOUD ANALYSIS REPORT - {case_id}\n")
        f.write(f"Source Export: {source_path}\n")
        f.write(f"Examiner: {examiner}\n")
        f.write(f"Generated: {datetime.now()}\n\n")

        f.write(f"Service: {data.get('service')}\n")
        f.write(f"Account: {data.get('account_email')}\n\n")

        files = data.get("files", [])
        deleted = [fi for fi in files if fi["deleted"]]
        shared = [fi for fi in files if fi["shared_with"]]

        f.write(f"Total files: {len(files)}\n")
        f.write(f"Deleted files: {len(deleted)}\n")
        f.write(f"Shared files: {len(shared)}\n\n")

        f.write("Shared Files:\n")
        for fi in shared:
            f.write(f"- {fi['path']} -> {', '.join(fi['shared_with'])}\n")

        if suspicious_ip:
            f.write(f"\nAccesses from suspicious IP {suspicious_ip}:\n")
            for log in data.get("access_logs", []):
                if log["ip"] == suspicious_ip:
                    f_id = log.get("file_id")
                    fname = ""
                    if f_id:
                        for fi in files:
                            if fi["id"] == f_id:
                                fname = fi["name"]
                                break
                    f.write(f"- [{log['timestamp']}] {log['action']} {fname}\n")

    print("Report saved at:", report_path)


def main():
    print("Cloud export analysis tool.")
    use_custom = input("Use custom cloud export JSON file? (y/N): ").strip().lower()
    path = None
    if use_custom == "y":
        p = input("Enter full path to cloud export JSON: ").strip()
        if os.path.isfile(p):
            path = p
        else:
            print("File not found. Using sample export.")
    data, source_path = load_export(path)

    while True:
        print("\nMain Menu:")
        print("1) List all files")
        print("2) List only deleted files")
        print("3) List only shared files")
        print("4) Search files by name/path/extension")
        print("5) View access logs (and mark suspicious IP)")
        print("6) Generate cloud report")
        print("0) Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            list_files(data, filter_deleted=None)
        elif choice == "2":
            list_files(data, filter_deleted=True)
        elif choice == "3":
            list_files(data, filter_deleted=None, only_shared=True)
        elif choice == "4":
            search_files(data)
        elif choice == "5":
            view_access_logs(data)
        elif choice == "6":
            generate_cloud_report(data, source_path)
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
