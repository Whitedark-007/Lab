import math
import random


def classical_search(arr, target):
    steps = 0
    for i, v in enumerate(arr):
        steps += 1
        if v == target:
            return i, steps
    return -1, steps


def grover_steps(n_items):
    if n_items <= 0:
        return 0
    return int(round((math.pi / 4) * math.sqrt(n_items)))


def main():
    print("=== Grover-Style Search Complexity Demo ===")
    try:
        N = int(input("Enter database size N (e.g., 16, 64, 256): ").strip())
    except ValueError:
        N = 16
        print("Invalid input, using N=16.")

    data = list(range(N))
    random.shuffle(data)
    target = random.choice(data)

    print(f"\nHidden target (unknown to algorithm) is: {target}")
    idx, steps = classical_search(data, target)
    print("\nClassical linear search:")
    print(f"Found at index      : {idx}")
    print(f"Steps taken         : {steps}")

    g_steps = grover_steps(N)
    print("\nGrover's algorithm (theoretical):")
    print(f"Expected iterations : ~{g_steps}")
    print(f"Speedup factor      : ≈ sqrt(N) compared to classical")

    obs_lines = []
    obs_lines.append("Observation Table - Grover-Style Search")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Database size N      : {N}")
    obs_lines.append(f"Target value         : {target}")
    obs_lines.append(f"Classical steps      : {steps}")
    obs_lines.append(f"Grover steps (approx): {g_steps}")
    obs_text = "\n".join(obs_lines)

    with open("grover_search_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to grover_search_observation.txt")


if __name__ == "__main__":
    main()
