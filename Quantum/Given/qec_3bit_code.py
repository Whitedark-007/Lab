import random


def encode_bit(bit):
    return [bit, bit, bit]


def introduce_errors(codeword, error_prob):
    noisy = []
    for b in codeword:
        noisy.append(1 - b if random.random() < error_prob else b)
    return noisy


def decode_majority(bits):
    ones = bits.count(1)
    zeros = len(bits) - ones
    return 1 if ones >= zeros else 0


def theoretical_logical_error(per):
    return 3 * (per ** 2) * (1 - per) + (per ** 3)


def run_simulation(logical_bit, physical_error, trials=1000):
    errors = 0
    for _ in range(trials):
        encoded = encode_bit(logical_bit)
        noisy = introduce_errors(encoded, physical_error)
        decoded = decode_majority(noisy)
        if decoded != logical_bit:
            errors += 1
    return errors / float(trials)


def main():
    print("=== 3-Bit Repetition Code – Error Correction Demo ===")
    try:
        per = float(input("Enter physical bit-flip error probability (e.g., 0.1): ").strip())
    except ValueError:
        per = 0.1
        print("Invalid input, using 0.1.")
    try:
        trials = int(input("Enter number of trials per logical bit (e.g., 1000): ").strip())
    except ValueError:
        trials = 1000
        print("Invalid input, using 1000.")

    logical_err_0 = run_simulation(0, per, trials=trials)
    logical_err_1 = run_simulation(1, per, trials=trials)
    theo = theoretical_logical_error(per)

    print(f"\nLogical input bit 0: empirical logical error rate = {logical_err_0:.4f}")
    print(f"Logical input bit 1: empirical logical error rate = {logical_err_1:.4f}")
    print(f"Theoretical logical error rate (3-bit code): {theo:.4f}")

    obs_lines = []
    obs_lines.append("Observation Table - 3-Bit Repetition QEC")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Physical error prob     : {per}")
    obs_lines.append(f"Trials per logical bit  : {trials}")
    obs_lines.append(f"Logical error (bit 0)   : {logical_err_0:.4f}")
    obs_lines.append(f"Logical error (bit 1)   : {logical_err_1:.4f}")
    obs_lines.append(f"Theoretical logical err  : {theo:.4f}")
    obs_text = "\n".join(obs_lines)

    with open("qec_3bit_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to qec_3bit_observation.txt")


if __name__ == "__main__":
    main()
