import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import time
from numpy.random import randint

# --- CONFIGURATION DES RÉPERTOIRES ---
for folder in ['figures', 'results']:
    if not os.path.exists(folder):
        os.makedirs(folder)

def simulate_bb84(n, interception=False):
    """Simule le protocole BB84 et retourne le taux d'erreur."""
    alice_bits = randint(2, size=n)
    alice_bases = randint(2, size=n)
    bob_bases = randint(2, size=n)
    errors = 0
    common_bases = 0
    
    for i in range(n):
        if alice_bases[i] == bob_bases[i]:
            common_bases += 1
            if interception:
                # Eve génère 25% d'erreurs sur les bases concordantes
                if randint(0, 100) < 25: 
                    errors += 1
    return (errors / common_bases * 100) if common_bases > 0 else 0

# --- BENCHMARK 1 : TAUX D'ERREUR ET VARIANCE ---
print("Lancement du Benchmark Statistiques BB84...")
n_tests = [10, 20, 40, 50, 100]
final_results = []

plt.figure(figsize=(12, 7))

for n in n_tests:
    # 1000 itérations pour une robustesse statistique
    safe_data = [simulate_bb84(n, False) for _ in range(1000)]
    eve_data = [simulate_bb84(n, True) for _ in range(1000)]
    
    # Calcul des métriques (Moyenne et Variance)
    final_results.append(["BB84", f"{n} Qubits", "Mean (Safe)", np.mean(safe_data), "%"])
    final_results.append(["BB84", f"{n} Qubits", "Variance (Safe)", np.var(safe_data), "raw"])
    final_results.append(["BB84", f"{n} Qubits", "Mean (Interception)", np.mean(eve_data), "%"])
    final_results.append(["BB84", f"{n} Qubits", "Variance (Interception)", np.var(eve_data), "raw"])

    # Scatter plot pour la visualisation de la distribution
    plt.scatter([n]*1000, eve_data, color='crimson', alpha=0.1, label='Interception' if n==n_tests[0] else "")
    plt.scatter([n]*1000, safe_data, color='seagreen', alpha=0.1, label='Safe Channel' if n==n_tests[0] else "")

# Graphique 1 : Error Rate
plt.axhline(y=11, color='darkorange', linestyle='--', linewidth=2, label='Security Threshold (11%)')
plt.title("BB84 Error Rate Distribution vs. Qubit Count", fontsize=14)
plt.xlabel("Number of Qubits", fontsize=12)
plt.ylabel("Error Rate (%)", fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, linestyle=':', alpha=0.6)
plt.savefig("figures/bb84_error_rate_analysis.png", dpi=300)

# --- BENCHMARK 2 : TEMPS D'EXÉCUTION (SCALABILITÉ) ---
print("Lancement du Benchmark Performance (Time vs. Size)...")
time_results = []
sizes = [100, 500, 1000, 5000, 10000]

for s in sizes:
    start_time = time.perf_counter()
    _ = [simulate_bb84(s, True) for _ in range(100)]
    end_time = time.perf_counter()
    avg_time = (end_time - start_time) / 100
    time_results.append(avg_time)
    
    final_results.append(["BB84", f"{s} Qubits", "Execution Time", avg_time, "seconds"])

# Graphique 2 : Temps d'exécution
plt.figure(figsize=(10, 6))
plt.plot(sizes, time_results, marker='o', linestyle='-', color='royalblue', linewidth=2)
plt.title("BB84 Simulation Scalability (Execution Time)", fontsize=14)
plt.xlabel("Number of Qubits (Data Size)", fontsize=12)
plt.ylabel("Average Time per Simulation (s)", fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.savefig("figures/bb84_execution_time.png", dpi=300)

# --- EXPORT DES DONNÉES ---
df = pd.DataFrame(final_results, columns=["Algorithm", "Configuration", "Metric", "Value", "Unit"])
df.to_csv("results/bb84_final_benchmarks.csv", index=False)

print("\nTraitement terminé avec succès.")
print("Fichiers générés :")
print("- figures/bb84_error_rate_analysis.png")
print("- figures/bb84_execution_time.png")
print("- results/bb84_final_benchmarks.csv")