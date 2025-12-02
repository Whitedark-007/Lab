import random
import math


def simulate_chsh(trials=1000):
    settings = {
        '00': (0.0,  math.pi / 4),
        '01': (0.0, -math.pi / 4),
        '10': (math.pi / 2,  math.pi / 4),
        '11': (math.pi / 2, -math.pi / 4),
    }
    sums = {'00': 0.0, '01': 0.0, '10': 0.0, '11': 0.0}
    counts = {'00': 0, '01': 0, '10': 0, '11': 0}

    for _ in range(trials):
        a = random.randint(0, 1)
        b = random.randint(0, 1)
        key = f"{a}{b}"
        theta_a, theta_b = settings[key]
        e = -math.cos(theta_a - theta_b)
        outcome = 1 if random.random() < (1 + e) / 2 else -1
        sums[key] += outcome
        counts[key] += 1

    exp_values = {}
    for key in sums:
        exp_values[key] = 0.0 if counts[key] == 0 else sums[key] / counts[key]
    S = abs(exp_values['00'] + exp_values['01'] + exp_values['10'] - exp_values['11'])
    return S, exp_values


def main():
    print("=== Device-Independent QKD – CHSH Bell Test ===")
    try:
        n = int(input("Enter number of trials (e.g., 5000): ").strip())
    except ValueError:
        n = 5000
        print("Invalid input, using 5000.")

    S, exps = simulate_chsh(n)
    print("\n--- CHSH Results ---")
    for key in ['00', '01', '10', '11']:
        print(f"E({key}) ≈ {exps[key]:.4f}")
    print(f"\nCHSH S parameter ≈ {S:.4f}")
    violated = S > 2
    print(f"Bell inequality violated (S > 2)? {'YES' if violated else 'NO'}")

    obs_lines = []
    obs_lines.append("Observation Table - DI-QKD CHSH Test")
    obs_lines.append("--------------------------------------")
    obs_lines.append(f"Trials              : {n}")
    for key in ['00', '01', '10', '11']:
        obs_lines.append(f"E({key})            : {exps[key]:.4f}")
    obs_lines.append(f"S parameter         : {S:.4f}")
    obs_lines.append(f"Bell violation      : {violated}")
    obs_text = "\n".join(obs_lines)

    with open("di_qkd_chsh_observation.txt", "w", encoding="utf-8") as f:
        f.write(obs_text)

    show = input("\nDisplay observation table? [y/n]: ").strip().lower()
    if show == 'y':
        print("\n" + obs_text)
    else:
        print("\nObservation table saved to di_qkd_chsh_observation.txt")


if __name__ == "__main__":
    main()
