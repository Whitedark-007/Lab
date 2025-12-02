import random
from math import gcd


def shors_sim(N):
    if N % 2 == 0:
        return 2, N // 2

    while True:
        a = random.randint(2, N - 1)
        g = gcd(a, N)
        if g > 1:
            return g, N // g

        r = 1
        while r < 2 * N:
            if pow(a, r, N) == 1:
                break
            r += 1

        if r % 2 != 0:
            continue

        x = pow(a, r // 2, N)
        p1 = gcd(x - 1, N)
        p2 = gcd(x + 1, N)

        if 1 < p1 < N:
            return p1, N // p1
        if 1 < p2 < N:
            return p2, N // p2


def main():
    print("=== Shor's Algorithm – Classical Simulation ===")
    print("Try composite numbers like 15, 21, 35, 77, 91.")

    while True:
        s = input("\nEnter a composite integer (>3) to factor (or 'q' to quit): ").strip()
        if s.lower() == 'q':
            print("Exiting...")
            break
        try:
            N = int(s)
        except ValueError:
            print("Invalid integer, try again.")
            continue

        if N <= 3:
            print("Please enter a number greater than 3.")
            continue

        p, q = shors_sim(N)
        print(f"{N} = {p} × {q}")

        obs_lines = []
        obs_lines.append("Observation Table - Shor Simulation")
        obs_lines.append("--------------------------------------")
        obs_lines.append(f"Number factored : {N}")
        obs_lines.append(f"Factor 1        : {p}")
        obs_lines.append(f"Factor 2        : {q}")
        obs_text = "\n".join(obs_lines)

        fname = f"shor_observation_{N}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(obs_text)

        show = input("Display observation table for this run? [y/n]: ").strip().lower()
        if show == 'y':
            print("\n" + obs_text)
        else:
            print(f"Observation table saved to {fname}")


if __name__ == "__main__":
    main()
