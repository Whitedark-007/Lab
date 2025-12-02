import random

def simulate_bb84(num_bits=50, eve=False):
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    bob_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    bob_results = []

    for i in range(num_bits):
        bit = alice_bits[i]
        a_basis = alice_bases[i]
        b_basis = bob_bases[i]

        # Eve intercept-resend (simple model)
        if eve:
            eve_basis = random.choice(['Z', 'X'])
            if eve_basis != a_basis and random.random() < 0.5:
                bit = 1 - bit

        # Bob's measurement
        if b_basis == a_basis:
            received_bit = bit
        else:
            received_bit = random.randint(0, 1)

        bob_results.append(received_bit)

    # Sifting
    sifted_alice = []
    sifted_bob = []
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])

    if len(sifted_alice) == 0:
        error_rate = 0.0
    else:
        errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
        error_rate = (errors / len(sifted_alice)) * 100.0

    return {
        "total_bits": num_bits,
        "sifted_length": len(sifted_alice),
        "error_rate": error_rate,
        "sifted_alice": sifted_alice,
        "sifted_bob": sifted_bob,
        "eve": eve,
    }


def main():
    print("=== BB84 Quantum Key Distribution (Logical Simulation) ===")
    try:
        n = int(input("Enter number of transmitted bits (e.g., 50 or 100): ").strip())
    except ValueError:
        n = 50
        print("Invalid input, using 50 bits.")

    eve_input = input("Simulate eavesdropper (Eve)? [y/n]: ").strip().lower()
    eve_present = (eve_input == 'y')

    result = simulate_bb84(num_bits=n, eve=eve_present)

    print("\n--- Summary ---")
    print(f"Total transmitted bits : {result['total_bits']}")
    print(f"Sifted key length      : {result['sifted_length']}")
    print(f"Error rate on sifted   : {result['error_rate']:.2f}%")

    show_keys = input("Show first 20 bits of Alice & Bob sifted keys? [y/n]: ").strip().lower()
    if show_keys == 'y' and result['sifted_length'] > 0:
        print("Alice sifted key:", result['sifted_alice'][:20])
        print("Bob   sifted key:", result['sifted_bob'][:20])

    if eve_present:
        interpretation = "High error rate (~25%) suggests eavesdropping."
    else:
        interpretation = "Low error rate (~0–5%) means secure channel (ideal model)."
    print("\n" + interpretation)

    # Build observation table text
    obs_lines = []
    obs_lines.append("Observation Table - BB84 QKD")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Total transmitted bits : {result['total_bits']}")
    obs_lines.append(f"Sifted key length      : {result['sifted_length']}")
    obs_lines.append(f"Error rate on sifted   : {result['error_rate']:.2f}%")
    obs_lines.append(f"Eavesdropper simulated : {result['eve']}")
    if result['sifted_length'] > 0:
        obs_lines.append(f"Alice sifted (first 10): {result['sifted_alice'][:10]}")
        obs_lines.append(f"Bob sifted (first 10)  : {result['sifted_bob'][:10]}")
    obs_lines.append(f"Interpretation         : {interpretation}")

    obs_text = "\n".join(obs_lines)

    # Save to txt file
    with open("bb84_qkd_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    # Ask whether to display
    show_obs = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show_obs == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to bb84_qkd_observation.txt")


if __name__ == "__main__":
    main()
