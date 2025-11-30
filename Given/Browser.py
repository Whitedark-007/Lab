#!/usr/bin/env python3
import csv
from datetime import datetime

def load_history(csv_path):
    entries = []
    try:
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            # normalize fieldnames
            field_map = {name.lower(): name for name in reader.fieldnames}
            url_key = field_map.get("url")
            title_key = field_map.get("title")
            time_key = field_map.get("visit_time") or field_map.get("time") or field_map.get("last_visit_time")

            if not url_key or not title_key or not time_key:
                print("[!] CSV must contain 'url', 'title', and 'visit_time' (or 'time') columns.")
                return []

            for row in reader:
                entries.append({
                    "url": row.get(url_key, ""),
                    "title": row.get(title_key, ""),
                    "visit_time": row.get(time_key, ""),
                })
    except FileNotFoundError:
        print(f"[!] CSV file not found: {csv_path}")
    except Exception as e:
        print(f"[!] Error reading CSV: {e}")
    return entries

def filter_history(entries, domain_filter=None, keyword_filter=None):
    results = []
    for e in entries:
        if domain_filter:
            if domain_filter.lower() not in e["url"].lower():
                continue
        if keyword_filter:
            if (keyword_filter.lower() not in e["url"].lower()
                    and keyword_filter.lower() not in e["title"].lower()):
                continue
        results.append(e)
    return results

def write_report(report_path, summary, filtered_entries, important_entries):
    with open(report_path, "w", encoding="utf-8", errors="ignore") as rep:
        rep.write("===== BROWSER HISTORY ANALYSIS REPORT =====\n\n")
        rep.write(f"Date & Time          : {summary['datetime']}\n")
        rep.write(f"Case ID              : {summary['case_id']}\n")
        rep.write(f"Examiner Name        : {summary['examiner']}\n")
        rep.write(f"Evidence Description : {summary['evidence_desc']}\n\n")

        rep.write(f"CSV Source File          : {summary['csv_path']}\n")
        rep.write(f"Total Entries Loaded     : {summary['total_entries']}\n")
        rep.write(f"Entries After Filtering  : {summary['filtered_entries']}\n")
        rep.write(f"Domain Filter            : {summary['domain_filter'] or 'None'}\n")
        rep.write(f"Keyword Filter           : {summary['keyword_filter'] or 'None'}\n\n")

        rep.write("Conclusion:\n")
        rep.write(f"{summary['conclusion']}\n\n")

        rep.write("----- FILTERED HISTORY ENTRIES -----\n\n")
        for idx, e in enumerate(filtered_entries, start=1):
            rep.write(f"Visit #{idx}\n")
            rep.write(f"  Time   : {e['visit_time']}\n")
            rep.write(f"  URL    : {e['url']}\n")
            rep.write(f"  Title  : {e['title']}\n")
            rep.write("\n")

        rep.write("----- MANUALLY FLAGGED IMPORTANT VISITS -----\n\n")
        if important_entries:
            for e in important_entries:
                rep.write(f" * {e}\n")
        else:
            rep.write("No visits were manually flagged.\n")

def print_result_table(summary):
    print("\n==================== BROWSER HISTORY RESULT TABLE ====================")
    rows = [
        ("Case ID", summary["case_id"]),
        ("Examiner", summary["examiner"]),
        ("Evidence Description", summary["evidence_desc"]),
        ("CSV Source File", summary["csv_path"]),
        ("Total Entries Loaded", summary["total_entries"]),
        ("Entries After Filter", summary["filtered_entries"]),
        ("Domain Filter", summary["domain_filter"] or "None"),
        ("Keyword Filter", summary["keyword_filter"] or "None"),
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
    print("======================================================================\n")

def main():
    print("====================================================")
    print("           Browser History Analyzer (CSV)")
    print("====================================================\n")

    # Case details
    print("Enter Case Details (for your record):")
    case_id = input("  Case ID                : ").strip() or "N/A"
    examiner = input("  Examiner Name          : ").strip() or "N/A"
    evidence_desc = input("  Evidence Description   : ").strip() or "N/A"
    print()

    csv_path = input("Enter path to browser history CSV file: ").strip()
    if not csv_path:
        print("[!] No CSV path given. Exiting.")
        return

    entries = load_history(csv_path)
    total_entries = len(entries)
    if not entries:
        print("[!] No entries loaded from CSV.")
        return
    print(f"[+] Loaded {total_entries} entries from history CSV.\n")

    print("You can filter by domain and/or keyword in URL/title.")
    domain_filter = input("  Domain filter (e.g. facebook.com, bank.com) [blank for none]: ").strip()
    keyword_filter = input("  Keyword filter (e.g. login, password, torrent) [blank for none]: ").strip()

    filtered = filter_history(entries, domain_filter or None, keyword_filter or None)
    print(f"\n[+] Entries after filtering: {len(filtered)}")

    print("\nPreview of filtered entries (up to 10):")
    for e in filtered[:10]:
        print(f"- [{e['visit_time']}] {e['url']}  ({e['title']})")

    print("\nYou can manually write down any particularly important visits (copy/paste from above).")
    important_entries = []
    while True:
        val = input("Enter an important visit (or press Enter to stop): ").strip()
        if not val:
            break
        important_entries.append(val)

    print("\nPlease confirm that you have manually reviewed the filtered visit list.")
    user_input = input("Have you manually reviewed the history entries? (yes/no): ").strip().lower()
    user_confirm = "YES" if user_input in ["yes", "y"] else "NO"

    if filtered:
        conclusion = "Browser history entries of interest were identified based on domain/keyword filters and manual review."
    else:
        conclusion = "No history entries matched the given filters. Different filters or manual inspection may be required."

    summary = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": case_id,
        "examiner": examiner,
        "evidence_desc": evidence_desc,
        "csv_path": csv_path,
        "total_entries": total_entries,
        "filtered_entries": len(filtered),
        "domain_filter": domain_filter,
        "keyword_filter": keyword_filter,
        "user_confirm": user_confirm,
        "conclusion": conclusion,
    }

    report_path = "browser_history_report.txt"
    write_report(report_path, summary, filtered, important_entries)

    print(f"\n[+] Text report generated: {report_path}")
    print(f"[+] Conclusion: {conclusion}\n")

    print_result_table(summary)

if __name__ == "__main__":
    main()
