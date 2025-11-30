import os
import textwrap
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
MEMORY_DUMP_PATH = os.path.join(SAMPLE_DIR, "memory_dump.txt")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def create_sample_memory_dump():
    if os.path.exists(MEMORY_DUMP_PATH):
        return
    content = textwrap.dedent("""\
    # SIMPLE RAM DUMP SIMULATION
    [METADATA]
    capture_time=2025-11-12 10:20:30
    os=Windows 10 x64
    profile=Win10x64

    [PROCESSES]
    PID,PPID,NAME,USER,PATH
    4,0,System,SYSTEM,C:\\Windows\\System32\\ntoskrnl.exe
    312,4,smss.exe,SYSTEM,C:\\Windows\\System32\\smss.exe
    528,528,csrss.exe,SYSTEM,C:\\Windows\\System32\\csrss.exe
    612,528,wininit.exe,SYSTEM,C:\\Windows\\System32\\wininit.exe
    720,612,services.exe,SYSTEM,C:\\Windows\\System32\\services.exe
    800,612,lsass.exe,SYSTEM,C:\\Windows\\System32\\lsass.exe
    1400,720,svchost.exe,LOCAL SERVICE,C:\\Windows\\System32\\svchost.exe
    1500,720,svchost.exe,NETWORK SERVICE,C:\\Windows\\System32\\svchost.exe
    2000,720,chrome.exe,User,C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
    2100,720,chrome.exe,User,C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
    2500,720,unknown_malware.exe,User,C:\\Users\\User\\AppData\\Roaming\\evil\\unknown_malware.exe

    [NETWORK]
    LADDR,LPORT,RADDR,RPORT,PROTO,PID,STATE
    192.168.1.10,49200,142.250.71.238,443,TCP,2000,ESTABLISHED
    192.168.1.10,49201,142.250.71.238,443,TCP,2100,ESTABLISHED
    192.168.1.10,50000,185.203.113.55,4444,TCP,2500,ESTABLISHED
    192.168.1.10,53,8.8.8.8,53,UDP,720,OPEN
    192.168.1.10,137,0.0.0.0,0,UDP,720,LISTEN

    [STRINGS]
    "C2_SERVER=185.203.113.55"
    "Mimikatz was here"
    "Password=SuperSecret123"
    "malware payload injected"
    """)
    with open(MEMORY_DUMP_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def load_section(section_name):
    if not os.path.exists(MEMORY_DUMP_PATH):
        create_sample_memory_dump()

    data = []
    current_section = None
    with open(MEMORY_DUMP_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("[") and line.endswith("]"):
                current_section = line.strip("[]")
                continue
            if current_section == section_name and line and not line.startswith("#"):
                data.append(line)
    return data


def parse_processes():
    lines = load_section("PROCESSES")
    if not lines:
        return []

    header = lines[0].split(",")
    processes = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != len(header):
            continue
        proc = dict(zip(header, parts))
        processes.append(proc)
    return processes


def parse_connections():
    lines = load_section("NETWORK")
    if not lines:
        return []

    header = lines[0].split(",")
    conns = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != len(header):
            continue
        conns.append(dict(zip(header, parts)))
    return conns


def parse_strings():
    lines = load_section("STRINGS")
    return [l.strip().strip('"') for l in lines if l.strip()]


def pretty_print_table(rows, columns):
    if not rows:
        print("No data found.")
        return

    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))

    line = " | ".join(col.ljust(widths[col]) for col in columns)
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))


def menu_list_processes():
    processes = parse_processes()
    if not processes:
        print("No processes parsed.")
        return

    while True:
        print("\nProcess Menu:")
        print("1) Show all processes")
        print("2) Filter by process name")
        print("3) Filter by PID")
        print("4) Show suspicious (contains 'malware' or 'mimikatz')")
        print("0) Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            pretty_print_table(processes, ["PID", "PPID", "NAME", "USER", "PATH"])
        elif choice == "2":
            name = input("Enter (part of) process name to search: ").strip().lower()
            filtered = [p for p in processes if name in p["NAME"].lower()]
            pretty_print_table(filtered, ["PID", "PPID", "NAME", "USER", "PATH"])
        elif choice == "3":
            pid = input("Enter PID to search: ").strip()
            filtered = [p for p in processes if p["PID"] == pid]
            pretty_print_table(filtered, ["PID", "PPID", "NAME", "USER", "PATH"])
        elif choice == "4":
            keywords = ["malware", "mimikatz"]
            filtered = [p for p in processes if any(k in p["NAME"].lower() for k in keywords)]
            pretty_print_table(filtered, ["PID", "PPID", "NAME", "USER", "PATH"])
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def menu_list_connections():
    conns = parse_connections()
    if not conns:
        print("No connections parsed.")
        return

    while True:
        print("\nNetwork Menu:")
        print("1) Show all connections")
        print("2) Filter by remote IP")
        print("3) Filter by port")
        print("4) Show suspicious ports (>1024 and not 80/443)")
        print("0) Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            pretty_print_table(conns, ["LADDR", "LPORT", "RADDR", "RPORT", "PROTO", "PID", "STATE"])
        elif choice == "2":
            ip = input("Enter (part of) remote IP: ").strip()
            filtered = [c for c in conns if ip in c["RADDR"]]
            pretty_print_table(filtered, ["LADDR", "LPORT", "RADDR", "RPORT", "PROTO", "PID", "STATE"])
        elif choice == "3":
            port = input("Enter port to search (local or remote): ").strip()
            filtered = [c for c in conns if c["LPORT"] == port or c["RPORT"] == port]
            pretty_print_table(filtered, ["LADDR", "LPORT", "RADDR", "RPORT", "PROTO", "PID", "STATE"])
        elif choice == "4":
            filtered = []
            for c in conns:
                try:
                    rp = int(c["RPORT"])
                except ValueError:
                    continue
                if rp > 1024 and rp not in (80, 443):
                    filtered.append(c)
            pretty_print_table(filtered, ["LADDR", "LPORT", "RADDR", "RPORT", "PROTO", "PID", "STATE"])
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")


def menu_search_strings():
    strings = parse_strings()
    if not strings:
        print("No strings parsed.")
        return

    while True:
        print("\nString / IOC Search:")
        print("1) Show all strings")
        print("2) Search for a keyword")
        print("3) Search using common malware keywords")
        print("0) Back")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            for s in strings:
                print(s)
        elif choice == "2":
            kw = input("Enter keyword: ").strip().lower()
            for s in strings:
                if kw in s.lower():
                    print(s)
        elif choice == "3":
            default_iocs = ["mimikatz", "payload", "C2_SERVER", "Password"]
            print("Using default IOCs:", ", ".join(default_iocs))
            for s in strings:
                if any(k.lower() in s.lower() for k in default_iocs):
                    print("[HIT]", s)
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def generate_report():
    case_id = input("Enter Case ID for the report: ").strip() or "CASE_RAM_DEMO"
    examiner = input("Enter Examiner Name: ").strip() or "Examiner"
    report_name = f"{case_id}_ram_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = os.path.join(REPORTS_DIR, report_name)

    processes = parse_processes()
    conns = parse_connections()
    strings = parse_strings()

    suspicious_procs = [p for p in processes if "malware" in p["NAME"].lower()]
    suspicious_conns = []
    for c in conns:
        try:
            rp = int(c["RPORT"])
        except ValueError:
            continue
        if rp > 1024 and rp not in (80, 443):
            suspicious_conns.append(c)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"RAM ANALYSIS REPORT - {case_id}\n")
        f.write(f"Examiner: {examiner}\n")
        f.write(f"Generated: {datetime.now()}\n\n")

        f.write("Suspicious Processes:\n")
        for p in suspicious_procs:
            f.write(f"- PID {p['PID']} NAME {p['NAME']} PATH {p['PATH']}\n")
        if not suspicious_procs:
            f.write("- None detected by simple rules\n")
        f.write("\nSuspicious Connections:\n")
        for c in suspicious_conns:
            f.write(f"- {c['LADDR']}:{c['LPORT']} -> {c['RADDR']}:{c['RPORT']} PID {c['PID']}\n")
        if not suspicious_conns:
            f.write("- None detected by simple rules\n")

        f.write("\nInteresting Strings (containing 'password' or 'C2'):\n")
        for s in strings:
            if "password" in s.lower() or "c2" in s.lower():
                f.write(f"- {s}\n")

    print(f"\nReport generated: {report_path}")


def main():
    create_sample_memory_dump()
    while True:
        print("\nMain Menu:")
        print("1) View / analyze process list")
        print("2) View / analyze network connections")
        print("3) Search for strings / IOCs")
        print("4) Generate simple forensic report")
        print("5) Show path of sample memory dump")
        print("0) Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            menu_list_processes()
        elif choice == "2":
            menu_list_connections()
        elif choice == "3":
            menu_search_strings()
        elif choice == "4":
            generate_report()
        elif choice == "5":
            print(f"Sample memory dump located at: {MEMORY_DUMP_PATH}")
        elif choice == "0":
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()
