import random


def teleport(symbol):
    m1 = random.randint(0, 1)
    m2 = random.randint(0, 1)
    final_state = symbol
    return m1, m2, final_state


def main():
    print("=== Quantum Teleportation (Symbolic Simulation) ===")
    print("Choose a state |ψ> to teleport:")
    print("1. |0>")
    print("2. |1>")
    print("3. |+>  = (|0>+|1>)/√2")
    print("4. |->  = (|0>-|1>)/√2")

    choice = input("Enter your choice (1-4): ").strip()
    mapping = {'1': '0', '2': '1', '3': '+', '4': '-'}
    symbol = mapping.get(choice, '0')

    print(f"\nPreparing state |{symbol}> on the sender's side...")
    print("Creating entangled pair shared between sender and receiver...")
    print("Performing Bell measurement and sending 2 classical bits...")

    m1, m2, final_state = teleport(symbol)

    print("\n--- Results ---")
    print(f"Measurement bits sent over classical channel: ({m1}, {m2})")
    print(f"State at receiver after applying corrections: |{final_state}>")

    obs_lines = []
    obs_lines.append("Observation Table - Teleportation (Symbolic)")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Input state symbol       : {symbol}")
    obs_lines.append(f"Measurement bits (m1,m2) : ({m1}, {m2})")
    obs_lines.append(f"Final state at receiver  : {final_state}")
    obs_text = "\n".join(obs_lines)

    with open("teleportation_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to teleportation_observation.txt")


if __name__ == "__main__":
    main()
