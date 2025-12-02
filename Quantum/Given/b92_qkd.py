import random


def simulate_b92(num_bits=200):
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    bob_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    bob_results = []

    for i in range(num_bits):
        bit = alice_bits[i]
        basis = bob_bases[i]
        if bit == 0 and basis == 'Z':
            meas = 0
        elif bit == 1 and basis == 'X':
            meas = 0
        else:
            meas = random.randint(0, 1)
        bob_results.append(meas)

    sifted_bits = [alice_bits[i] for i in range(num_bits) if bob_results[i] == 1]
    efficiency = (len(sifted_bits) / num_bits) * 100.0
    return len(sifted_bits), efficiency, sifted_bits


def main():
    print("=== B92 Quantum Key Distribution (Logical Simulation) ===")
    try:
        n = int(input("Enter number of transmitted bits (e.g., 200): ").strip())
    except ValueError:
        n = 200
        print("Invalid input, using 200.")

    key_len, eff, key = simulate_b92(n)
    print("\n--- Results ---")
    print(f"Sifted key length: {key_len}")
    print(f"Efficiency       : {eff:.2f}%")
    show_key = input("Show first 20 bits of sifted key? [y/n]: ").strip().lower()
    if show_key == 'y':
        print("Sifted key (up to 20 bits):", key[:20])

    obs_lines = []
    obs_lines.append("Observation Table - B92 QKD")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Total transmitted bits : {n}")
    obs_lines.append(f"Sifted key length      : {key_len}")
    obs_lines.append(f"Efficiency (%)         : {eff:.2f}")
    obs_lines.append(f"Sifted key (first 10)  : {key[:10]}")
    obs_text = "\n".join(obs_lines)

    with open("b92_qkd_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show_obs = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show_obs == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to b92_qkd_observation.txt")


if __name__ == "__main__":
    main()
