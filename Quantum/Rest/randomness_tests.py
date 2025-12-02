import random
import math


def generate_bits(count):
    return [random.randint(0, 1) for _ in range(count)]


def frequency_test(bits):
    n = len(bits)
    zeros = bits.count(0)
    ones = n - zeros
    if n == 0:
        return zeros, ones, 0.0
    chi2 = float((zeros - ones) ** 2) / float(n)
    return zeros, ones, chi2


def runs_test(bits):
    if not bits:
        return 0
    runs = 1
    for i in range(1, len(bits)):
        if bits[i] != bits[i - 1]:
            runs += 1
    return runs


def entropy(bits):
    n = len(bits)
    if n == 0:
        return 0.0
    p0 = bits.count(0) / float(n)
    p1 = 1.0 - p0
    h = 0.0
    for p in (p0, p1):
        if p > 0:
            h -= p * math.log(p, 2)
    return h


def analyze_stream(bits, label):
    zeros, ones, chi2 = frequency_test(bits)
    r = runs_test(bits)
    h = entropy(bits)
    return {
        "label": label,
        "total": len(bits),
        "zeros": zeros,
        "ones": ones,
        "chi2": chi2,
        "runs": r,
        "entropy": h,
    }


def main():
    print("=== Randomness Analysis (Frequency, Runs, Entropy) ===")
    try:
        n = int(input("Enter number of bits to generate (e.g., 1000): ").strip())
    except ValueError:
        n = 1000
        print("Invalid input, using 1000 bits.")

    random.seed()
    bits_quantum = generate_bits(n)
    random.seed(12345)
    bits_classical = generate_bits(n)

    res_q = analyze_stream(bits_quantum, "Simulated Quantum RNG")
    res_c = analyze_stream(bits_classical, "Classical RNG (fixed seed)")

    for res in (res_q, res_c):
        print(f"\n--- {res['label']} ---")
        print(f"Total bits     : {res['total']}")
        print(f"0s             : {res['zeros']}")
        print(f"1s             : {res['ones']}")
        print(f"Chi-squared    : {res['chi2']:.4f}")
        print(f"Runs           : {res['runs']}")
        print(f"Shannon entropy: {res['entropy']:.4f} (ideal ≈ 1.0)")

    print("\nInterpretation: Good randomness → 0s and 1s counts close, chi² small, entropy ≈ 1.")

    obs_lines = []
    obs_lines.append("Observation Table - Randomness Tests")
    obs_lines.append("--------------------------------------")
    for res in (res_q, res_c):
        obs_lines.append(f"\nSource              : {res['label']}")
        obs_lines.append(f"Total bits          : {res['total']}")
        obs_lines.append(f"0s                  : {res['zeros']}")
        obs_lines.append(f"1s                  : {res['ones']}")
        obs_lines.append(f"Chi-squared         : {res['chi2']:.4f}")
        obs_lines.append(f"Runs                : {res['runs']}")
        obs_lines.append(f"Shannon entropy     : {res['entropy']:.4f}")
    obs_text = "\n".join(obs_lines)

    with open("randomness_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to randomness_observation.txt")


if __name__ == "__main__":
    main()
