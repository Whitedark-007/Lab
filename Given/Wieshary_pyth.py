#!/usr/bin/env python3
import os
from datetime import datetime

def human_readable_size(size_bytes):
    if size_bytes is None:
        return "UNKNOWN"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_file_metadata(root_dir):
    """Return list of dicts with path, size, and MAC times."""
    records = []
    for base, dirs, files in os.walk(root_dir):
        for name in files:
            full_path = os.path.join(base, name)
            try:
                stats = os.stat(full_path)
                size = stats.st_size
                mtime = datetime.fromtimestamp(stats.st_mtime)
                atime = datetime.fromtimestamp(stats.st_atime)
                ctime = datetime.fromtimestamp(stats.st_ctime)
                records.append({
                    "path": full_path,
                    "size": size,
                    "mtime": mtime,
                    "atime": atime,
                    "ctime": ctime,
                })
            except Exception:
                continue
    return records

def filter_records(records, ext_filter=None, min_size_bytes=0):
    filtered = []
    for r in records:
        if ext_filter:
            if not r["path"].lower().endswith(ext_filter.lower()):
                continue
        if r["size"] < min_size_bytes:
            continue
        filtered.append(r)
    return filtered

def write_report(report_path, summary, records, interesting_paths):
    with open(report_path, "w", encoding="utf-8", errors="ignore") as rep:
        rep.write("===== FILE METADATA & TIMELINE REPORT =====\n\n")
        rep.write(f"Date & Time          : {summary['datetime']}\n")
        rep.write(f"Case ID              : {summary['case_id']}\n")
        rep.write(f"Examiner Name        : {summary['examiner']}\n")
        rep.write(f"Evidence Description : {summary['evidence_desc']}\n\n")

        rep.write(f"Root Directory Scanned   : {summary['root_dir']}\n")
        rep.write(f"Total Files Found        : {summary['total_files']}\n")
        rep.write(f"Files After Filtering    : {summary['filtered_files']}\n")
        rep.write(f"Extension Filter         : {summary['ext_filter'] or 'None'}\n")
        rep.write(f"Minimum Size Filter      : {summary['min_size_kb']} KB\n\n")

        rep.write("Conclusion:\n")
        rep.write(f"{summary['conclusion']}\n\n")

        rep.write("----- FILTERED FILE METADATA -----\n\n")
        for idx, r in enumerate(records, start=1):
            rep.write(f"File #{idx}\n")
            rep.write(f"  Path       : {r['path']}\n")
            rep.write(f"  Size       : {human_readable_size(r['size'])}\n")
            rep.write(f"  Modified   : {r['mtime']}\n")
            rep.write(f"  Accessed   : {r['atime']}\n")
            rep.write(f"  Created    : {r['ctime']}\n")
            rep.write("\n")

        rep.write("----- MANUALLY MARKED INTERESTING FILES -----\n\n")
        if interesting_paths:
            for p in interesting_paths:
                rep.write(f" * {p}\n")
        else:
            rep.write("No files were manually marked as interesting.\n")

def print_result_table(summary):
    print("\n==================== FILE ANALYSIS RESULT TABLE ====================")
    headers = ["Field", "Value"]
    rows = [
        ("Case ID", summary["case_id"]),
        ("Examiner", summary["examiner"]),
        ("Evidence Description", summary["evidence_desc"]),
        ("Root Directory", summary["root_dir"]),
        ("Total Files Found", summary["total_files"]),
        ("Files After Filter", summary["filtered_files"]),
        ("Extension Filter", summary["ext_filter"] or "None"),
        ("Min Size (KB)", summary["min_size_kb"]),
        ("User Manual Review", summary["user_confirm"]),
        ("Conclusion", summary["conclusion"]),
    ]

    col1_width = max(len(r[0]) for r in rows) + 2
    col2_width = 60

    print("-" * (col1_width + col2_width + 3))
    print(f"{'Field':<{col1_width}}| {'Value':<{col2_width}}")
    print("-" * (col1_width + col2_width + 3))
    for field, value in rows:
        print(f"{field:<{col1_width}}| {str(value)[:col2_width]:<{col2_width}}")
    print("-" * (col1_width + col2_width + 3))
    print("====================================================================\n")

def main():
    print("====================================================")
    print("        File Metadata & Timeline Analyzer")
    print("====================================================\n")

    # Case details
    print("Enter Case Details (for your record):")
    case_id = input("  Case ID                : ").strip() or "N/A"
    examiner = input("  Examiner Name          : ").strip() or "N/A"
    evidence_desc = input("  Evidence Description   : ").strip() or "N/A"
    print()

    root_dir = input("Enter root directory to scan (e.g. C:\\Evidence or /mnt/usb): ").strip()
    if not root_dir:
        print("[!] No directory given. Exiting.")
        return

    if not os.path.isdir(root_dir):
        print(f"[!] Directory does not exist: {root_dir}")
        return

    print("\nYou can optionally apply filters:")
    ext_filter = input("  Enter extension to filter by (e.g. .log, .txt) [leave blank for all]: ").strip()
    min_size_kb_str = input("  Enter minimum file size in KB [default: 0]: ").strip()
    try:
        min_size_kb = int(min_size_kb_str) if min_size_kb_str else 0
    except ValueError:
        min_size_kb = 0

    min_size_bytes = min_size_kb * 1024

    print("\n[*] Scanning directory and collecting file metadata...")
    records = get_file_metadata(root_dir)
    total_files = len(records)
    print(f"[+] Total files found: {total_files}")

    filtered = filter_records(records, ext_filter or None, min_size_bytes)
    print(f"[+] Files after applying filters: {len(filtered)}")

    if not filtered:
        print("[!] No files matched the given filters. You may adjust filters and run again.\n")

    # Show a preview
    print("\nPreview of filtered files (up to 10):")
    for r in filtered[:10]:
        print(f" - {r['path']} ({human_readable_size(r['size'])})")

    print("\nYou can mark some files as 'interesting' for further analysis.")
    interesting_paths = []
    while True:
        choice = input("Enter full path of an interesting file (or press Enter to stop): ").strip()
        if not choice:
            break
        interesting_paths.append(choice)

    print("\nPlease confirm that you have manually reviewed the listed files and timestamps.")
    user_input = input("Have you manually reviewed the file list and marked interesting ones? (yes/no): ").strip().lower()
    user_confirm = "YES" if user_input in ["yes", "y"] else "NO"

    if filtered:
        conclusion = "File metadata and timelines collected successfully. Potential evidence files identified based on filters and manual review."
    else:
        conclusion = "No files matched the given filters. Manual re-check or changed criteria may be required."

    summary = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": case_id,
        "examiner": examiner,
        "evidence_desc": evidence_desc,
        "root_dir": root_dir,
        "total_files": total_files,
        "filtered_files": len(filtered),
        "ext_filter": ext_filter,
        "min_size_kb": min_size_kb,
        "user_confirm": user_confirm,
        "conclusion": conclusion,
    }

    report_path = "file_timeline_report.txt"
    write_report(report_path, summary, filtered, interesting_paths)

    print(f"\n[+] Text report generated: {report_path}")
    print(f"[+] Conclusion: {conclusion}\n")

    print_result_table(summary)

if __name__ == "__main__":
    main()
