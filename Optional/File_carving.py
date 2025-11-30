import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "recovered_files")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

DISK_IMAGE = os.path.join(SAMPLE_DIR, "sample_disk_image.bin")


def create_sample_disk_image():
    if os.path.exists(DISK_IMAGE):
        return

    def blob(label, content):
        return label.encode("ascii") + content.encode("utf-8")

    junk = "X" * 200
    img = bytearray(junk.encode("utf-8"))
    img += blob("JPG_START", "This is pretend JPEG binary data...") + b"JPG_END"
    img += junk.encode("utf-8")
    img += blob("PDF_START", "%PDF-FAKE-1.0\nFake PDF content here\n") + b"PDF_END"
    img += junk.encode("utf-8")
    img += blob("TXT_START", "SECRET NOTE: Meet at 9 PM behind the lab.\n") + b"TXT_END"

    with open(DISK_IMAGE, "wb") as f:
        f.write(img)


SIGNATURES = {
    "jpg": (b"JPG_START", b"JPG_END"),
    "pdf": (b"PDF_START", b"PDF_END"),
    "txt": (b"TXT_START", b"TXT_END"),
}


def carve_file(image_bytes, ext, header, footer):
    start = 0
    carved = []
    idx = 1
    while True:
        hpos = image_bytes.find(header, start)
        if hpos == -1:
            break
        fpos = image_bytes.find(footer, hpos + len(header))
        if fpos == -1:
            break

        content_start = hpos + len(header)
        content_end = fpos
        data = image_bytes[content_start:content_end]
        filename = f"carved_{ext}_{idx}.{ext}"
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "wb") as out:
            out.write(data)
        carved.append(out_path)
        idx += 1
        start = fpos + len(footer)
    return carved


def interactive_signature_selection():
    print("\nAvailable file types to carve:")
    keys = list(SIGNATURES.keys())
    for i, k in enumerate(keys, start=1):
        print(f"{i}) {k.upper()}")

    selected = input("Enter comma-separated numbers (e.g., 1,3) or 'all': ").strip().lower()
    if selected == "all" or selected == "":
        return keys

    chosen = []
    for part in selected.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part)
        if 1 <= idx <= len(keys):
            chosen.append(keys[idx - 1])
    return chosen or keys


def run_carving():
    create_sample_disk_image()
    print(f"\nDisk image path: {DISK_IMAGE}")

    use_custom = input("Do you want to use a custom disk image file? (y/N): ").strip().lower()
    image_path = DISK_IMAGE
    if use_custom == "y":
        path = input("Enter full path to your disk image (.bin/.dd/.img): ").strip()
        if os.path.isfile(path):
            image_path = path
        else:
            print("File not found. Using sample image instead.")

    with open(image_path, "rb") as f:
        data = f.read()

    print(f"Loaded {len(data)} bytes from disk image.")
    types_to_carve = interactive_signature_selection()

    carved_paths = []
    for ext in types_to_carve:
        header, footer = SIGNATURES[ext]
        print(f"\nCarving for {ext.upper()} using header={header} footer={footer}")
        results = carve_file(data, ext, header, footer)
        if results:
            print(f"Recovered {len(results)} {ext.upper()} file(s):")
            for r in results:
                print("  -", r)
            carved_paths.extend(results)
        else:
            print(f"No {ext.upper()} segments found.")

    if carved_paths:
        gen_report = input("\nGenerate carving report? (Y/n): ").strip().lower() or "y"
        if gen_report == "y":
            report_name = f"file_carving_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            report_path = os.path.join(OUTPUT_DIR, report_name)
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("FILE CARVING REPORT\n")
                f.write(f"Image: {image_path}\n")
                f.write(f"Generated: {datetime.now()}\n\n")
                for p in carved_paths:
                    f.write(f"Recovered: {p}\n")
            print("Report saved at:", report_path)
    else:
        print("\nNo files recovered; nothing to report.")


def main():
    print("File carving tool ready.")
    run_carving()


if __name__ == "__main__":
    main()
