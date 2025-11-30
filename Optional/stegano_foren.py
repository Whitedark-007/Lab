import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

COVER_FILE = os.path.join(SAMPLE_DIR, "cover.bin")
STEGO_FILE = os.path.join(SAMPLE_DIR, "stego.bin")
TERMINATOR = "####END####"


def create_sample_cover():
    if os.path.exists(COVER_FILE):
        return
    data = bytearray()
    for i in range(5000):
        data.append((i * 73 + 31) % 256)
    with open(COVER_FILE, "wb") as f:
        f.write(data)


def text_to_bits(text):
    return "".join(f"{ord(c):08b}" for c in text)


def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        if len(byte) < 8:
            break
        chars.append(chr(int(byte, 2)))
    return "".join(chars)


def embed_message(cover_path, out_path, message):
    with open(cover_path, "rb") as f:
        data = bytearray(f.read())

    full_message = message + TERMINATOR
    bits = text_to_bits(full_message)

    if len(bits) > len(data):
        raise ValueError("Cover file too small for this message.")

    for i, b in enumerate(bits):
        data[i] = (data[i] & 0b11111110) | int(b)

    with open(out_path, "wb") as f:
        f.write(data)


def detect_stego(path):
    with open(path, "rb") as f:
        data = f.read()

    if not data:
        return 0.0, 0.0

    ones = 0
    zeros = 0
    for b in data:
        if b & 1:
            ones += 1
        else:
            zeros += 1
    total = ones + zeros
    ratio = ones / total if total else 0

    score = 1.0 - abs(0.5 - ratio) * 10
    score = max(0.0, min(score, 1.0))
    return score, ratio


def extract_message(path, max_chars=5000):
    with open(path, "rb") as f:
        data = f.read()

    bits = []
    for b in data:
        bits.append(str(b & 1))
        if len(bits) >= max_chars * 8:
            break

    text = bits_to_text("".join(bits))
    end_idx = text.find(TERMINATOR)
    if end_idx == -1:
        return None
    return text[:end_idx]


def menu_create_stego():
    create_sample_cover()
    print("\nCreate stego file")
    use_custom = input("Use custom cover file? (y/N): ").strip().lower()
    cover_path = COVER_FILE
    if use_custom == "y":
        p = input("Enter path to cover file (any binary file): ").strip()
        if os.path.isfile(p):
            cover_path = p
        else:
            print("Not found, using sample cover instead.")

    msg = input("Enter secret message to embed: ").strip()
    out_path = input(f"Enter output stego file path (default: {STEGO_FILE}): ").strip()
    if not out_path:
        out_path = STEGO_FILE
    try:
        embed_message(cover_path, out_path, msg)
        print("Stego file created at:", out_path)
    except Exception as e:
        print("Error creating stego file:", e)


def menu_detect_stego():
    path = input("Enter path to suspicious file: ").strip()
    if not os.path.isfile(path):
        print("File not found.")
        return
    score, ratio = detect_stego(path)
    print(f"LSB 1s ratio: {ratio:.3f}")
    print(f"Suspicion score (0-1): {score:.3f}")
    if score > 0.7:
        print("High probability of LSB steganography.")
    elif score > 0.4:
        print("Medium probability of steganography.")
    else:
        print("Low probability of steganography.")


def menu_extract_message():
    path = input("Enter path to stego file (for extraction): ").strip()
    if not os.path.isfile(path):
        print("File not found.")
        return
    message = extract_message(path)
    if message is None:
        print("No terminator found; extraction failed or format mismatch.")
    else:
        print("\nExtracted hidden message:")
        print(message)


def main():
    create_sample_cover()
    while True:
        print("\nMain Menu:")
        print("1) Create test stego file (embed message)")
        print("2) Detect if a file may contain LSB stego")
        print("3) Extract message from stego file")
        print("0) Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            menu_create_stego()
        elif choice == "2":
            menu_detect_stego()
        elif choice == "3":
            menu_extract_message()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
