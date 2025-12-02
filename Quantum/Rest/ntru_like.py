import random
import time


class NTRULike:
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


def main():
    print("=== Simple NTRU-like Lattice Encryption Demo ===")
    try:
        N = int(input("Enter N (dimension, e.g., 11): ").strip())
    except ValueError:
        N = 11
        print("Invalid input, using N = 11.")
    try:
        q = int(input("Enter q (modulus, e.g., 32): ").strip())
    except ValueError:
        q = 32
        print("Invalid input, using q = 32.")
    try:
        noise_bound = int(input("Enter noise bound (e.g., 2): ").strip())
    except ValueError:
        noise_bound = 2
        print("Invalid input, using noise_bound = 2.")

    scheme = NTRULike(N=N, q=q, noise_bound=noise_bound)
    keygen_ms = scheme.keygen()
    print(f"\nKey generation time: {keygen_ms:.2f} ms")
    print(f"Example public key : {scheme.public_key}")

    msg_str = input(f"\nEnter a {N}-bit message (e.g., 101010...): ").strip()
    if len(msg_str) != N or any(c not in '01' for c in msg_str):
        print("Invalid message; using random bits instead.")
        msg_bits = [random.randint(0, 1) for _ in range(N)]
    else:
        msg_bits = [int(c) for c in msg_str]

    ct, enc_ms = scheme.encrypt(msg_bits)
    dec_bits = scheme.decrypt(ct)
    valid = (dec_bits == msg_bits)

    print("\nPlaintext bits :", msg_bits)
    print("Ciphertext     :", ct)
    print("Decrypted bits :", dec_bits)
    print(f"Encryption time: {enc_ms:.2f} ms")
    print(f"Decryption OK  : {valid}")

    obs_lines = []
    obs_lines.append("Observation Table - NTRU-like Encryption")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"N (dimension)       : {N}")
    obs_lines.append(f"q (modulus)         : {q}")
    obs_lines.append(f"Noise bound         : {noise_bound}")
    obs_lines.append(f"Plaintext bits      : {msg_bits}")
    obs_lines.append(f"Ciphertext vector   : {ct}")
    obs_lines.append(f"Decrypted bits      : {dec_bits}")
    obs_lines.append(f"Encryption time(ms) : {enc_ms:.2f}")
    obs_lines.append(f"Decryption OK       : {valid}")
    obs_text = "\n".join(obs_lines)

    with open("ntru_like_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to ntru_like_observation.txt")


if __name__ == "__main__":
    main()
