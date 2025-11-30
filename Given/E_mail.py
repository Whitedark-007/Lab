#!/usr/bin/env python3


import os
import imaplib
import email
from email.header import decode_header
from getpass import getpass
from datetime import datetime

# ---------- Simple ANSI Colors (for terminals that support it) ---------- #
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ----------------- Helper Functions ----------------- #

def decode_header_str(value):
    """Decode MIME-encoded header to readable string."""
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for text, enc in parts:
        if isinstance(text, bytes):
            try:
                decoded.append(text.decode(enc or "utf-8", errors="ignore"))
            except Exception:
                decoded.append(text.decode("utf-8", errors="ignore"))
        else:
            decoded.append(text)
    return "".join(decoded)

def save_attachments(msg, output_dir):
    """Save attachments in the given message to output_dir. Returns list of saved file paths."""
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue

        filename = part.get_filename()
        if filename:
            filename = decode_header_str(filename)
            safe_name = filename.replace("\r", "").replace("\n", "").replace(os.sep, "_")
            file_path = os.path.join(output_dir, safe_name)
            with open(file_path, "wb") as f:
                f.write(part.get_payload(decode=True))
            saved_files.append(file_path)
    return saved_files

def extract_text_body_snippet(msg, max_len=250):
    """Extract a short text body snippet from an email message."""
    body_text = ""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "").lower()
                if ctype == "text/plain" and "attachment" not in disp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_text = payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                        break
        else:
            if msg.get_content_type() == "text/plain":
                payload = msg.get_payload(decode=True)
                if payload:
                    body_text = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
    except Exception:
        body_text = ""

    body_text = body_text.replace("\r", " ").replace("\n", " ")
    if len(body_text) > max_len:
        return body_text[:max_len] + "..."
    return body_text

def highlight_keyword(text, keyword):
    """Highlight keyword in text by uppercasing and surrounding with [] (no color here)."""
    if not keyword:
        return text
    lower = text.lower()
    key = keyword.lower()
    result = ""
    i = 0
    while i < len(text):
        if lower[i:i+len(key)] == key:
            result += "[" + text[i:i+len(key)].upper() + "]"
            i += len(key)
        else:
            result += text[i]
            i += 1
    return result

def print_result_table(data):
    """Print a result/observation style table like lab record."""
    print("\n==================== EMAIL FORENSICS RESULT TABLE ====================")
    headers = ["Field", "Value"]
    rows = [
        ("Case ID", data["case_id"]),
        ("Examiner", data["examiner"]),
        ("Evidence Description", data["evidence_desc"]),
        ("Mode", data["mode"]),
        ("IMAP Server", data["imap_server"] or "N/A"),
        ("Email Address", data["email_user"] or "N/A"),
        ("Mailbox", data["mailbox"] or "N/A"),
        ("Emails Analyzed", data["emails_analyzed"]),
        ("Emails with Attachments", data["emails_with_attachments"]),
        ("Suspicious Keyword", data["suspicious_keyword"] or "None"),
        ("Suspicious Email Count", data["suspicious_emails"]),
        ("Attachments Folder", data["attachments_folder"]),
        ("User Manual Review", data["user_confirm"]),
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
    print("======================================================================\n")

def write_report(report_path, summary, email_details):
    """Write a detailed text report for email forensics."""
    with open(report_path, "w", encoding="utf-8", errors="ignore") as rep:
        rep.write("===== EMAIL FORENSICS REPORT =====\n\n")
        rep.write(f"Date & Time          : {summary['datetime']}\n")
        rep.write(f"Case ID              : {summary['case_id']}\n")
        rep.write(f"Examiner Name        : {summary['examiner']}\n")
        rep.write(f"Evidence Description : {summary['evidence_desc']}\n\n")

        rep.write(f"Mode                 : {summary['mode']}\n")
        rep.write(f"IMAP Server          : {summary['imap_server'] or 'N/A'}\n")
        rep.write(f"Email Address        : {summary['email_user'] or 'N/A'}\n")
        rep.write(f"Mailbox              : {summary['mailbox'] or 'N/A'}\n\n")

        rep.write(f"Total Emails Analyzed     : {summary['emails_analyzed']}\n")
        rep.write(f"Emails with Attachments   : {summary['emails_with_attachments']}\n")
        rep.write(f"Suspicious Keyword        : {summary['suspicious_keyword'] or 'None'}\n")
        rep.write(f"Suspicious Email Count    : {summary['suspicious_emails']}\n")
        rep.write(f"Attachments Folder        : {summary['attachments_folder']}\n")
        rep.write(f"User Manual Review        : {summary['user_confirm']}\n\n")

        rep.write("Conclusion:\n")
        rep.write(f"{summary['conclusion']}\n\n")

        rep.write("----- DETAILED EMAIL ANALYSIS -----\n\n")
        for idx, info in enumerate(email_details, start=1):
            rep.write(f"Email #{idx}\n")
            rep.write(f"  Message ID       : {info['msg_id']}\n")
            rep.write(f"  From             : {info['from']}\n")
            rep.write(f"  To               : {info['to']}\n")
            rep.write(f"  Subject          : {info['subject']}\n")
            rep.write(f"  Date             : {info['date']}\n")
            rep.write(f"  Attachments      : {info['attachments_count']}\n")
            rep.write(f"  Suspicious?      : {'YES' if info['suspicious'] else 'NO'}\n")
            rep.write(f"  Keyword Matches  : {', '.join(info['keyword_hits']) or 'None'}\n")
            rep.write("  Received Headers (for routing/IP analysis):\n")
            for line in info["received_headers"]:
                rep.write(f"    {line}\n")
            rep.write("  Body Snippet:\n")
            rep.write(f"    {info['body_snippet']}\n")
            rep.write("\n")

# ----------------- ONLINE MODE (IMAP) ----------------- #

def run_online_mode(case_id, examiner, evidence_desc):
    print("You selected: ONLINE mode (real IMAP connection)\n")
    print("Notes:")
    print(" - Use IMAP server like: imap.gmail.com, outlook.office365.com, etc.")
    print(" - For Gmail, you usually need an App Password (not your normal password).")
    print(" - Make sure IMAP access is enabled for the account.\n")

    imap_server = input("IMAP server (e.g. imap.gmail.com): ").strip()
    email_user = input("Email address: ").strip()
    email_pass = getpass("Password / App password (input hidden): ")
    mailbox = input("Mailbox name [default: INBOX]: ").strip() or "INBOX"

    if not imap_server or not email_user or not email_pass:
        print("[!] IMAP server, email address, and password are required. Exiting.")
        return None

    default_count = 5
    try:
        count = int(input(f"How many recent emails to analyze? [default: {default_count}]: ") or default_count)
    except ValueError:
        count = default_count

    print("\nSuggested suspicious keywords (for demo):")
    print("  password, login, bank, alert, invoice, otp, lottery, confidential")
    suspicious_keyword = input("Enter a suspicious keyword to flag emails (optional): ").strip()
    print()

    attachments_folder = "email_forensics_attachments_online"

    try:
        print("Connecting to IMAP server and selecting mailbox...\n")

        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        print(f"{GREEN}[+] Login successful.{RESET}")

        status, _ = mail.select(mailbox)
        if status != "OK":
            print(f"[!] Could not open mailbox: {mailbox}")
            return None

        status, data = mail.search(None, "ALL")
        if status != "OK":
            print("[!] Search failed.")
            return None

        all_ids = data[0].split()
        if not all_ids:
            print("[!] No emails found in mailbox.")
            return None

        target_ids = all_ids[-count:]
        print(f"[*] Found {len(all_ids)} emails in '{mailbox}'.")
        print(f"[*] Analyzing last {len(target_ids)} emails.\n")

        print("Analyzing email headers, bodies, and attachments...\n")

        email_details = []
        emails_with_attachments = 0
        suspicious_emails = 0

        for num in target_ids:
            status, msg_data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                print(f"[!] Failed to fetch message ID {num}")
                continue

            msg = email.message_from_bytes(msg_data[0][1])

            msg_id_str = num.decode()
            from_ = decode_header_str(msg.get("From"))
            to_ = decode_header_str(msg.get("To"))
            subj_raw = decode_header_str(msg.get("Subject"))
            date_ = decode_header_str(msg.get("Date"))

            body_snippet_raw = extract_text_body_snippet(msg, max_len=200)

            print("------------------------------------------------")
            print(f"Message ID : {msg_id_str}")
            print(f"From       : {from_}")
            print(f"To         : {to_}")
            print(f"Subject    : {subj_raw}")
            print(f"Date       : {date_}")

            print("\n[Header Analysis - 'Received:' Lines]")
            headers_str = msg.as_string()
            received_lines = []
            for line in headers_str.split("\n"):
                if line.startswith("Received:"):
                    line_clean = line.strip()
                    received_lines.append(line_clean)
                    print(line_clean)

            saved = save_attachments(msg, output_dir=attachments_folder)
            attach_count = len(saved)
            if attach_count > 0:
                emails_with_attachments += 1
                print("\n[Attachments saved:]")
                for fpath in saved:
                    print(" -", fpath)
            else:
                print("\n[No attachments found in this email.]")

            suspicious = False
            keyword_hits = []
            body_snippet = body_snippet_raw

            if suspicious_keyword:
                key_lower = suspicious_keyword.lower()
                if key_lower in (from_ or "").lower():
                    suspicious = True
                    keyword_hits.append("FROM")
                if key_lower in (to_ or "").lower():
                    suspicious = True
                    keyword_hits.append("TO")
                if key_lower in (subj_raw or "").lower():
                    suspicious = True
                    keyword_hits.append("SUBJECT")
                if key_lower in (body_snippet_raw or "").lower():
                    suspicious = True
                    keyword_hits.append("BODY")

                subj_display = highlight_keyword(subj_raw, suspicious_keyword)
                body_display = highlight_keyword(body_snippet_raw, suspicious_keyword)
            else:
                subj_display = subj_raw
                body_display = body_snippet_raw

            print("\n[Body Snippet]")
            print(body_display if body_display else "(No text/plain body found)")

            if suspicious:
                suspicious_emails += 1
                print(f"\n{RED}[!] This email is flagged as SUSPICIOUS.{RESET}")
                print("    Keyword hits in:", ", ".join(keyword_hits))
            else:
                print(f"\n{GREEN}[+] No suspicious keyword match detected in this email.{RESET}")

            email_details.append({
                "msg_id": msg_id_str,
                "from": from_,
                "to": to_,
                "subject": subj_display,
                "date": date_,
                "attachments_count": attach_count,
                "suspicious": suspicious,
                "keyword_hits": keyword_hits,
                "received_headers": received_lines,
                "body_snippet": body_display
            })

            print("------------------------------------------------\n")

        emails_analyzed = len(email_details)
        mail.close()
        mail.logout()

        mode = "ONLINE (IMAP)"
        return {
            "mode": mode,
            "imap_server": imap_server,
            "email_user": email_user,
            "mailbox": mailbox,
            "emails_analyzed": emails_analyzed,
            "emails_with_attachments": emails_with_attachments,
            "suspicious_keyword": suspicious_keyword,
            "suspicious_emails": suspicious_emails,
            "attachments_folder": attachments_folder,
            "email_details": email_details
        }

    except imaplib.IMAP4.error as e:
        print(f"\n[!] IMAP error: {e}\n")
        return None
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}\n")
        return None

# ----------------- OFFLINE DEMO MODE ----------------- #

def run_offline_mode(case_id, examiner, evidence_desc):
    print("You selected: OFFLINE DEMO mode (sample emails, no real account)\n")

    default_count = 8
    try:
        count = int(input(f"How many sample emails to simulate? [default: {default_count}]: ") or default_count)
    except ValueError:
        count = default_count

    print("\nSuggested suspicious keywords (for demo):")
    print("  password, login, bank, alert, invoice, otp, lottery, confidential")
    suspicious_keyword = input("Enter a suspicious keyword to flag emails (optional): ").strip()
    print()

    attachments_folder = "email_forensics_attachments_demo"
    if not os.path.isdir(attachments_folder):
        os.makedirs(attachments_folder, exist_ok=True)

    print("Loading sample email data and simulating analysis...\n")

    base_samples = [
        {
            "from": "alice@example.com",
            "to": "investigator@lab.com",
            "subject": "Meeting notes and attachments",
            "date": "Mon, 24 Nov 2025 10:15:00 +0530",
            "received": [
                "Received: from mail.example.com (192.0.2.10) by mx.lab.com",
                "Received: from alice-laptop (10.0.0.5) by mail.example.com"
            ],
            "attachments": ["notes.pdf"],
            "body": "Hi, please find attached the meeting notes and action items. Nothing urgent or suspicious here."
        },
        {
            "from": "suspicious@phish.com",
            "to": "victim@company.com",
            "subject": "URGENT: Reset your password immediately",
            "date": "Tue, 25 Nov 2025 09:01:00 +0530",
            "received": [
                "Received: from phish-server.com (203.0.113.77) by mx.company.com"
            ],
            "attachments": ["reset_link.html"],
            "body": "Your account is compromised. Click the link in the attachment to reset your password now, or you will lose access."
        },
        {
            "from": "hr@company.com",
            "to": "employee@company.com",
            "subject": "Salary slip for November",
            "date": "Wed, 26 Nov 2025 18:30:00 +0530",
            "received": [
                "Received: from hr-pc (10.0.0.22) by mail.company.com"
            ],
            "attachments": ["salary_slip.pdf"],
            "body": "Please find attached your salary slip for the month. Contact HR if you notice any discrepancy."
        },
        {
            "from": "no-reply@service.com",
            "to": "user@example.com",
            "subject": "Your subscription has been renewed",
            "date": "Thu, 27 Nov 2025 12:00:00 +0530",
            "received": [
                "Received: from service.com (198.51.100.5) by mx.example.com"
            ],
            "attachments": [],
            "body": "Thank you for renewing your subscription. This is an automated message; no suspicious content here."
        },
        {
            "from": "alerts@bank.com",
            "to": "customer@example.com",
            "subject": "Alert: New login from unknown device",
            "date": "Fri, 28 Nov 2025 07:45:00 +0530",
            "received": [
                "Received: from bank.com (203.0.113.99) by mx.example.com"
            ],
            "attachments": ["alert_details.txt"],
            "body": "We detected a login from an unknown device. If this was not you, please contact the bank immediately."
        },
        {
            "from": "lottery@scam.com",
            "to": "randomuser@example.com",
            "subject": "Congratulations! You won the lottery",
            "date": "Sat, 29 Nov 2025 11:20:00 +0530",
            "received": [
                "Received: from scam.com (203.0.113.200) by mx.example.com"
            ],
            "attachments": ["claim_form.docx"],
            "body": "You have WON a huge lottery prize. To claim, send your bank details and ID proof as soon as possible."
        },
        {
            "from": "it-support@company.com",
            "to": "staff@company.com",
            "subject": "Planned maintenance window",
            "date": "Sun, 30 Nov 2025 02:00:00 +0530",
            "received": [
                "Received: from support-pc (10.0.0.50) by mail.company.com"
            ],
            "attachments": [],
            "body": "We will perform scheduled maintenance on the servers this weekend. There is no security incident; just routine work."
        },
        {
            "from": "unknown@malicious.net",
            "to": "target@company.com",
            "subject": "Invoice attached - please review",
            "date": "Mon, 01 Dec 2025 15:10:00 +0530",
            "received": [
                "Received: from malicious.net (198.51.100.77) by mx.company.com"
            ],
            "attachments": ["invoice.exe"],
            "body": "Please open the attached invoice and confirm the payment status. This file may contain malware."
        },
    ]

    samples = []
    while len(samples) < count:
        samples.extend(base_samples)
    samples = samples[:count]

    email_details = []
    emails_with_attachments = 0
    suspicious_emails = 0

    print("Analyzing sample email headers, bodies, and attachments...\n")

    for i, sample in enumerate(samples, start=1):
        msg_id_str = str(i)
        from_ = sample["from"]
        to_ = sample["to"]
        subj_raw = sample["subject"]
        date_ = sample["date"]
        received_lines = sample["received"]
        attach_list = sample["attachments"]
        body_raw = sample["body"]

        print("------------------------------------------------")
        print(f"Message ID : {msg_id_str}")
        print(f"From       : {from_}")
        print(f"To         : {to_}")
        print(f"Subject    : {subj_raw}")
        print(f"Date       : {date_}")

        print("\n[Header Analysis - 'Received:' Lines]")
        for line in received_lines:
            print(line)

        attach_count = len(attach_list)
        if attach_count > 0:
            emails_with_attachments += 1
            print("\n[Attachments simulated & saved:]")
            for name in attach_list:
                safe_name = name.replace("\r", "").replace("\n", "").replace(os.sep, "_")
                file_path = os.path.join(attachments_folder, f"sample_{msg_id_str}_{safe_name}")
                with open(file_path, "w") as f:
                    f.write("This is a simulated attachment for offline demo mode.\n")
                print(" -", file_path)
        else:
            print("\n[No attachments in this sample email.]")

        suspicious = False
        keyword_hits = []

        if suspicious_keyword:
            key_lower = suspicious_keyword.lower()
            if key_lower in from_.lower():
                suspicious = True
                keyword_hits.append("FROM")
            if key_lower in to_.lower():
                suspicious = True
                keyword_hits.append("TO")
            if key_lower in subj_raw.lower():
                suspicious = True
                keyword_hits.append("SUBJECT")
            if key_lower in body_raw.lower():
                suspicious = True
                keyword_hits.append("BODY")

            subj_display = highlight_keyword(subj_raw, suspicious_keyword)
            body_display = highlight_keyword(body_raw, suspicious_keyword)
        else:
            subj_display = subj_raw
            body_display = body_raw

        print("\n[Body Snippet]")
        snippet = body_display
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        print(snippet)

        if suspicious:
            suspicious_emails += 1
            print(f"\n{RED}[!] This sample email is flagged as SUSPICIOUS.{RESET}")
            print("    Keyword hits in:", ", ".join(keyword_hits))
        else:
            print(f"\n{GREEN}[+] No suspicious keyword match detected in this sample email.{RESET}")

        email_details.append({
            "msg_id": msg_id_str,
            "from": from_,
            "to": to_,
            "subject": subj_display,
            "date": date_,
            "attachments_count": attach_count,
            "suspicious": suspicious,
            "keyword_hits": keyword_hits,
            "received_headers": received_lines,
            "body_snippet": snippet
        })

        print("------------------------------------------------\n")

    emails_analyzed = len(email_details)
    mode = "OFFLINE DEMO"

    return {
        "mode": mode,
        "imap_server": None,
        "email_user": None,
        "mailbox": None,
        "emails_analyzed": emails_analyzed,
        "emails_with_attachments": emails_with_attachments,
        "suspicious_keyword": suspicious_keyword,
        "suspicious_emails": suspicious_emails,
        "attachments_folder": attachments_folder,
        "email_details": email_details
    }

# ----------------- Main Logic ----------------- #

def main():
    print("====================================================")
    print("        Email Forensics Tool (IMAP, Python)")
    print("====================================================\n")

    # Case details
    print("Enter Case Details (for your record):")
    case_id = input("  Case ID                : ").strip() or "N/A"
    examiner = input("  Examiner Name          : ").strip() or "N/A"
    evidence_desc = input("  Evidence Description   : ").strip() or "N/A"
    print()

    # Mode selection
    print("Select Mode of Operation:")
    print("  1) ONLINE MODE  - Real IMAP server, real email account")
    print("  2) OFFLINE MODE - Sample emails, no real account required")
    mode_choice = input("Enter choice (1 or 2) [default: 2]: ").strip() or "2"
    print()

    if mode_choice == "1":
        result = run_online_mode(case_id, examiner, evidence_desc)
    else:
        result = run_offline_mode(case_id, examiner, evidence_desc)

    if result is None:
        print("[!] Analysis could not be completed.\n")
        return

    mode = result["mode"]
    imap_server = result["imap_server"]
    email_user = result["email_user"]
    mailbox = result["mailbox"]
    emails_analyzed = result["emails_analyzed"]
    emails_with_attachments = result["emails_with_attachments"]
    suspicious_keyword = result["suspicious_keyword"]
    suspicious_emails = result["suspicious_emails"]
    attachments_folder = result["attachments_folder"]
    email_details = result["email_details"]

    print("====================================================")
    print("               Suspicious Email Summary")
    print("====================================================")
    if suspicious_emails > 0:
        print(f"{YELLOW}[!] Total suspicious emails: {suspicious_emails}{RESET}")
        print("    Listing suspicious Message IDs and Subjects:\n")
        for info in email_details:
            if info["suspicious"]:
                print(f" {YELLOW}- ID {info['msg_id']}: {info['subject']}{RESET}")
        print()
        choice = input("Do you want to re-print details of a specific suspicious email? (enter ID or press Enter to skip): ").strip()
        if choice:
            for info in email_details:
                if info["msg_id"] == choice:
                    print(f"\n{BOLD}===== RE-PRINTING SELECTED EMAIL ====={RESET}")
                    print(f"Message ID : {info['msg_id']}")
                    print(f"From       : {info['from']}")
                    print(f"To         : {info['to']}")
                    print(f"Subject    : {info['subject']}")
                    print(f"Date       : {info['date']}")
                    print("\n[Body Snippet]")
                    print(info["body_snippet"])
                    print(f"{BOLD}======================================{RESET}\n")
                    break
    else:
        print(f"{GREEN}[+] No suspicious emails detected based on the given keyword.{RESET}\n")

    print("====================================================")
    print("           User Manual Review Confirmation")
    print("====================================================")
    print("Please manually review the above headers, suspicious hits, and attachments if needed.")
    user_input = input("Have you manually reviewed the emails and artifacts? (yes/no): ").strip().lower()
    if user_input in ["yes", "y"]:
        user_confirm = "YES"
    else:
        user_confirm = "NO"

    if suspicious_emails > 0:
        conclusion = "Suspicious emails detected based on the provided keyword and header/body review."
    else:
        conclusion = "No suspicious emails detected based on the given criteria. Further detailed manual review may still be required."

    summary = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": case_id,
        "examiner": examiner,
        "evidence_desc": evidence_desc,
        "mode": mode,
        "imap_server": imap_server,
        "email_user": email_user,
        "mailbox": mailbox,
        "emails_analyzed": emails_analyzed,
        "emails_with_attachments": emails_with_attachments,
        "suspicious_keyword": suspicious_keyword,
        "suspicious_emails": suspicious_emails,
        "attachments_folder": attachments_folder,
        "user_confirm": user_confirm,
        "conclusion": conclusion
    }

    report_path = "email_forensics_report.txt"
    write_report(report_path, summary, email_details)

    print("====================================================")
    print("                Result & Report Summary")
    print("====================================================")
    print(f"[+] Text report generated: {report_path}")
    print(f"[+] Conclusion: {conclusion}\n")

    print_result_table(summary)

if __name__ == "__main__":
    main()
