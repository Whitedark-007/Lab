#!/usr/bin/env python3

import os
import sys
import hashlib
from datetime import datetime

def human_readable_size(size_bytes):
    """Return human readable size string."""
    if size_bytes is None:
        return "UNKNOWN"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def hash_file(path, chunk_size=1024*1024):
    """Compute MD5 and SHA1 hash of a file."""
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    total_read = 0

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            md5.update(chunk)
            sha1.update(chunk)
            total_read += len(chunk)
            sys.stdout.write(f"\r    [VERIFY] Hashed: {human_readable_size(total_read)}")
            sys.stdout.flush()

    print()  # newline after progress
    return md5.hexdigest(), sha1.hexdigest()

def image_and_hash(source_path, output_path, chunk_size=1024*1024):
    """Copy source to output while computing MD5 and SHA1."""
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    source_size = None
    try:
        source_size = os.path.getsize(source_path)
        print(f"[+] Source size detected: {human_readable_size(source_size)}")
    except Exception:
        print("[!] Could not determine source size (possibly raw device).")

    total_read = 0
    print(f"\n[*] Starting disk imaging process")
    print(f"    From: {source_path}")
    print(f"    To  : {output_path}")
    print("    Copying in 1 MB blocks...\n")

    with open(source_path, "rb", buffering=0) as src, open(output_path, "wb") as dst:
        while True:
            chunk = src.read(chunk_size)
            if not chunk:
                break
            dst.write(chunk)
            md5.update(chunk)
            sha1.update(chunk)
            total_read += len(chunk)

            sys.stdout.write(f"\r    [COPY] Copied: {human_readable_size(total_read)}")
            sys.stdout.flush()

    print("\n\n[*] Imaging completed.")
    try:
        output_size = os.path.getsize(output_path)
        print(f"[+] Output image size: {human_readable_size(output_size)}")
    except Exception:
        output_size = None
        print("[!] Could not determine output image size.")

    if source_size is not None and output_size is not None:
        if source_size == output_size:
            print("[+] SIZE CHECK: Source and image sizes MATCH.")
        else:
            print("[!] SIZE CHECK: Source and image sizes DO NOT MATCH!")

    return md5.hexdigest(), sha1.hexdigest(), source_size, output_size

def write_report(report_path, data):
    """Write a simple text report with all details."""
    with open(report_path, "w") as rep:
        rep.write("===== DISK IMAGING & HASHING REPORT =====\n\n")
        rep.write(f"Date & Time        : {data['datetime']}\n")
        rep.write(f"Case ID            : {data['case_id']}\n")
        rep.write(f"Examiner Name      : {data['examiner']}\n")
        rep.write(f"Evidence Description: {data['evidence_desc']}\n\n")

        rep.write(f"Source Path        : {data['source_path']}\n")
        rep.write(f"Image Path         : {data['output_path']}\n\n")

        rep.write(f"Source Size        : {data['source_size_hr']}\n")
        rep.write(f"Image Size         : {data['output_size_hr']}\n")
        rep.write(f"Size Match         : {data['size_match']}\n\n")

        rep.write("---- Hash Values During Imaging ----\n")
        rep.write(f"MD5 (during copy)  : {data['md5_copy']}\n")
        rep.write(f"SHA1 (during copy) : {data['sha1_copy']}\n\n")

        rep.write("---- Hash Values During Verification ----\n")
        rep.write(f"MD5 (verify file)  : {data['md5_verify']}\n")
        rep.write(f"SHA1 (verify file) : {data['sha1_verify']}\n\n")

        rep.write("---- Verification Result ----\n")
        rep.write(f"MD5 Match          : {data['md5_match']}\n")
        rep.write(f"SHA1 Match         : {data['sha1_match']}\n")
        rep.write(f"User Manual Check  : {data['user_confirm']}\n\n")

        rep.write("Conclusion:\n")
        rep.write(f"{data['conclusion']}\n")

def print_result_table(data):
    """Print a result/observation style table like lab record."""
    print("\n==================== RESULT TABLE ====================")
    headers = ["Field", "Value"]
    rows = [
        ("Case ID", data["case_id"]),
        ("Examiner", data["examiner"]),
        ("Evidence Description", data["evidence_desc"]),
        ("Source Path", data["source_path"]),
        ("Image Path", data["output_path"]),
        ("Source Size", data["source_size_hr"]),
        ("Image Size", data["output_size_hr"]),
        ("Size Match", data["size_match"]),
        ("MD5 (Copy)", data["md5_copy"]),
        ("MD5 (Verify)", data["md5_verify"]),
        ("MD5 Match", data["md5_match"]),
        ("SHA1 (Copy)", data["sha1_copy"]),
        ("SHA1 (Verify)", data["sha1_verify"]),
        ("SHA1 Match", data["sha1_match"]),
        ("User Manual Verification", data["user_confirm"]),
        ("Conclusion", data["conclusion"])
    ]

    col1_width = max(len(h[0]) for h in [headers] + rows) + 2
    col2_width = 60

    print("-" * (col1_width + col2_width + 3))
    print(f"{headers[0]:<{col1_width}}| {headers[1]:<{col2_width}}")
    print("-" * (col1_width + col2_width + 3))
    for field, value in rows:
        if value is None:
            value = ""
        print(f"{field:<{col1_width}}| {str(value)[:col2_width]:<{col2_width}}")
    print("-" * (col1_width + col2_width + 3))
    print("======================================================\n")

def main():
    print("====================================================")
    print("        Disk Imaging & Hashing Tool (Python)")
    print("====================================================\n")

    # Collect case details (for record)
    print("Enter Case Details (for your record):")
    case_id = input("  Case ID                : ").strip() or "N/A"
    examiner = input("  Examiner Name          : ").strip() or "N/A"
    evidence_desc = input("  Evidence Description   : ").strip() or "N/A"
    print()

    print("Notes:")
    print(" - You can use this on a file OR a raw device path.")
    print(" - Windows raw USB example:  \\\\.\\E:")
    print(" - For normal testing, just use a regular file as source.\n")

    source_path = input("Enter source path (file or drive): ").strip()
    if not source_path:
        print("[!] No source path given. Exiting.")
        return

    default_output = "disk_image.dd"
    output_path = input(f"Enter destination image file name [default: {default_output}]: ").strip()
    if not output_path:
        output_path = default_output

    try:
        # Imaging + live hashing
        md5_copy, sha1_copy, source_size, output_size = image_and_hash(source_path, output_path)

        # Verification hashing
        print("\n[*] Verifying integrity of the created image using hashes...")
        md5_verify, sha1_verify = hash_file(output_path)

        md5_match_bool = (md5_copy == md5_verify)
        sha1_match_bool = (sha1_copy == sha1_verify)

        md5_match = "YES" if md5_match_bool else "NO"
        sha1_match = "YES" if sha1_match_bool else "NO"

        print("\n================ HASH VALUES (DURING COPY) ================")
        print("Record these in your observation table (Copy Phase):")
        print(f"MD5  (copy)   : {md5_copy}")
        print(f"SHA1 (copy)   : {sha1_copy}")
        print("===========================================================\n")

        print("================ HASH VALUES (VERIFICATION) ===============")
        print("Record these in your observation table (Verify Phase):")
        print(f"MD5  (verify) : {md5_verify}")
        print(f"SHA1 (verify) : {sha1_verify}")
        print("===========================================================\n")

        print("=============== HASH COMPARISON RESULTS ===================")
        print(f"MD5 Match  : {'YES (Integrity OK)' if md5_match_bool else 'NO (Integrity FAILED!)'}")
        print(f"SHA1 Match : {'YES (Integrity OK)' if sha1_match_bool else 'NO (Integrity FAILED!)'}")
        print("===========================================================\n")

        # Ask user to manually visually confirm hash values
        print("USER INTERACTION:")
        print("Please visually compare the above hash values (Copy vs Verify).")
        user_input = input("Have you manually verified that the hashes match? (yes/no): ").strip().lower()
        if user_input in ["yes", "y"]:
            user_confirm = "YES"
        else:
            user_confirm = "NO"

        if source_size is not None and output_size is not None:
            size_match = "YES" if source_size == output_size else "NO"
        else:
            size_match = "UNKNOWN"

        if md5_match_bool and sha1_match_bool and size_match == "YES":
            conclusion = "Image creation SUCCESSFUL. Integrity verified by size and hash match."
        elif md5_match_bool and sha1_match_bool:
            conclusion = "Image hashes match, but size comparison was not fully available."
        else:
            conclusion = "WARNING: Hash mismatch detected. Image may be corrupted or modified."

        report_data = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "case_id": case_id,
            "examiner": examiner,
            "evidence_desc": evidence_desc,
            "source_path": source_path,
            "output_path": output_path,
            "source_size_hr": human_readable_size(source_size),
            "output_size_hr": human_readable_size(output_size),
            "size_match": size_match,
            "md5_copy": md5_copy,
            "sha1_copy": sha1_copy,
            "md5_verify": md5_verify,
            "sha1_verify": sha1_verify,
            "md5_match": md5_match,
            "sha1_match": sha1_match,
            "user_confirm": user_confirm,
            "conclusion": conclusion
        }

        report_path = "disk_imaging_report.txt"
        write_report(report_path, report_data)

        print(f"[+] Text report generated: {report_path}")
        print(f"[+] Conclusion: {conclusion}\n")

        print_result_table(report_data)

    except PermissionError:
        print("\n[!] Permission denied.")
        print("    - For raw devices, run Python as Administrator/root.\n")
    except FileNotFoundError:
        print(f"\n[!] Source not found: {source_path}\n")
    except Exception as e:
        print(f"\n[!] Error during imaging: {e}\n")

if __name__ == "__main__":
    main()
