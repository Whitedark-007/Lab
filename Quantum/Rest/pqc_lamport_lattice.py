import os
import time
import random
import hashlib


class LamportOTS:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self):
        zeros = []
        ones = []
        for _ in range(256):
            zeros.append(os.urandom(32))
            ones.append(os.urandom(32))
        self.private_key = {"zeros": zeros, "ones": ones}
        p_zeros = [hashlib.sha256(z).digest() for z in zeros]
        p_ones = [hashlib.sha256(o).digest() for o in ones]
        self.public_key = {"zeros": p_zeros, "ones": p_ones}

    def _message_to_bits(self, message_bytes):
        h = hashlib.sha256(message_bytes).digest()
        value = int.from_bytes(h, "big")
        return bin(value)[2:].zfill(256)

    def sign(self, message_bytes):
        bits = self._message_to_bits(message_bytes)
        signature = []
        for i, b in enumerate(bits):
            signature.append(self.private_key["zeros"][i] if b == '0' else self.private_key["ones"][i])
        return signature

    def verify(self, message_bytes, signature):
        bits = self._message_to_bits(message_bytes)
        for i, b in enumerate(bits):
            expected = self.public_key["zeros"][i] if b == '0' else self.public_key["ones"][i]
            if hashlib.sha256(signature[i]).digest() != expected:
                return False
        return True


class SimpleLatticeEnc:
    def __init__(self, N=11, q=32, noise_bound=2):
        self.N = N
        self.q = q
        self.noise_bound = noise_bound
        self.public_key = None
        self.secret_key = None

    def keygen(self):
        start = time.time()
        self.public_key = [random.randint(0, self.q - 1) for _ in range(self.N)]
        self.secret_key = "dummy_secret"
        return (time.time() - start) * 1000.0

    def encrypt(self, msg_bits):
        if len(msg_bits) != self.N:
            raise ValueError(f"Message must be length {self.N} bits.")
        start = time.time()
        ct = []
        half = self.q // 2
        for b in msg_bits:
            base = 0 if b == 0 else half
            noise = random.randint(-self.noise_bound, self.noise_bound)
            val = (base + noise) % self.q
            ct.append(val)
        return ct, (time.time() - start) * 1000.0

    def decrypt(self, ct):
        half = self.q // 2
        decoded = []
        for val in ct:
            dist0 = min(val, self.q - val)
            d1_raw = (val - half) % self.q
            dist1 = min(d1_raw, self.q - d1_raw)
            decoded.append(1 if dist1 < dist0 else 0)
        return decoded


def lamport_demo():
    print("\n=== Lamport One-Time Signature Demo ===")
    msg_text = input("Enter a message to sign: ")
    msg = msg_text.encode()

    ots = LamportOTS()
    t0 = time.time()
    ots.generate_keys()
    t1 = time.time()
    signature = ots.sign(msg)
    t2 = time.time()
    ok = ots.verify(msg, signature)
    t3 = time.time()

    keygen_ms = (t1 - t0) * 1000.0
    sign_ms = (t2 - t1) * 1000.0
    verify_ms = (t3 - t2) * 1000.0

    print(f"\nKey generation time: {keygen_ms:.2f} ms")
    print(f"Signing time       : {sign_ms:.2f} ms")
    print(f"Verification time  : {verify_ms:.2f} ms")
    print(f"Signature valid?   : {ok}")

    obs_lines = []
    obs_lines.append("Observation Table - Lamport OTS")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Message text         : {msg_text}")
    obs_lines.append(f"Key generation (ms)  : {keygen_ms:.2f}")
    obs_lines.append(f"Signing time (ms)    : {sign_ms:.2f}")
    obs_lines.append(f"Verification time(ms): {verify_ms:.2f}")
    obs_lines.append(f"Signature valid      : {ok}")
    obs_text = "\n".join(obs_lines)
    with open("lamport_ots_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table for Lamport OTS? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to lamport_ots_observation.txt")


def lattice_demo():
    print("\n=== Simple Lattice-Style Encryption Demo ===")
    try:
        N = int(input("Enter dimension N (e.g., 11): ").strip())
    except ValueError:
        N = 11
        print("Invalid input, using N = 11.")
    try:
        q = int(input("Enter modulus q (e.g., 32): ").strip())
    except ValueError:
        q = 32
        print("Invalid input, using q = 32.")
    try:
        noise_bound = int(input("Enter noise bound (e.g., 2): ").strip())
    except ValueError:
        noise_bound = 2
        print("Invalid input, using noise_bound = 2.")

    scheme = SimpleLatticeEnc(N=N, q=q, noise_bound=noise_bound)
    keygen_ms = scheme.keygen()
    print(f"\nKey generation time: {keygen_ms:.2f} ms")

    msg_str = input(f"Enter a {N}-bit message (e.g., 101001...): ").strip()
    if len(msg_str) != N or any(c not in '01' for c in msg_str):
        print("Invalid message; using random bits instead.")
        msg_bits = [random.randint(0, 1) for _ in range(N)]
    else:
        msg_bits = [int(c) for c in msg_str]

    ct, enc_ms = scheme.encrypt(msg_bits)
    dec_bits = scheme.decrypt(ct)
    valid = (dec_bits == msg_bits)

    print("\nCiphertext vector  :", ct)
    print("Decrypted bit list :", dec_bits)
    print(f"Encryption time    : {enc_ms:.2f} ms")
    print(f"Decryption correct?: {valid}")

    obs_lines = []
    obs_lines.append("Observation Table - Lattice Encryption")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"N (dimension)       : {N}")
    obs_lines.append(f"q (modulus)         : {q}")
    obs_lines.append(f"Noise bound         : {noise_bound}")
    obs_lines.append(f"Plaintext bits      : {msg_bits}")
    obs_lines.append(f"Ciphertext vector   : {ct}")
    obs_lines.append(f"Decrypted bits      : {dec_bits}")
    obs_lines.append(f"Encryption time(ms) : {enc_ms:.2f}")
    obs_lines.append(f"Decryption correct  : {valid}")
    obs_text = "\n".join(obs_lines)
    with open("lattice_enc_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table for lattice encryption? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to lattice_enc_observation.txt")


def main():
    while True:
        print("\n=== Post-Quantum Crypto Menu ===")
        print("1. Lamport One-Time Signature")
        print("2. Simple Lattice-Based Encryption")
        print("3. Exit")
        choice = input("Select option (1/2/3): ").strip()

        if choice == '1':
            lamport_demo()
        elif choice == '2':
            lattice_demo()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
