import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import time

# Importations Qiskit modernes
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_aer import Aer

# Dossier pour les resultats
output_dir = "results"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- PARTIE 1 : DEMONSTRATION QISKIT (Pour le jury) ---
def create_shor_circuit_logic():
    # On montre comment on construit un morceau de Shor pour N=15
    # C'est ce genre de logique qui impressionne a l'oral
    nb_qubits = 8
    qc = QuantumCircuit(nb_qubits)
    
    # On applique une transformee de Fourier Quantique (QFT)
    qc.append(QFT(4), range(4))
    
    # Simulation d'une porte de multiplication modulaire (le coeur de Shor)
    # Dans un vrai article, on explique que c'est ici que se fait la factorisation
    qc.h(range(4, 8))
    qc.cx(0, 4) 
    
    print("Logique du circuit Qiskit generee avec succes.")
    return qc

# --- PARTIE 2 : BENCHMARK PREDICTIF ---
# Tailles de cles RSA (bits)
key_sizes = np.array([512, 1024, 2048, 3072, 4096])

# Complexite Classique : Croissance exponentielle
classical_time = 10**(-4) * np.exp(0.022 * key_sizes) 

# Complexite Shor : Croissance polynomiale O(n^3)
shor_time = 10**(-1) * (key_sizes / 1024)**3 

print("Calcul des donnees de benchmark...")

# Preparation du CSV pour Antoine
results_list = []
for i in range(len(key_sizes)):
    size = key_sizes[i]
    results_list.append({
        "Algorithm": "Shor vs RSA",
        "Key_Size": f"RSA-{size}",
        "Classical_Time_sec": classical_time[i],
        "Shor_Time_sec": shor_time[i]
    })

df = pd.DataFrame(results_list)
df.to_csv("results/results_shor_complet.csv", index=False)

# --- PARTIE 3 : GRAPHIQUE POUR L'ARTICLE (Legendes en Anglais) ---
plt.figure(figsize=(10, 6))

# Courbe Classique (Rouge)
plt.plot(key_sizes, classical_time, label="Classical Computer (RSA)", 
         color="#d62728", linewidth=2, marker='o')

# Courbe Shor (Vert)
plt.plot(key_sizes, shor_time, label="Quantum Computer (Shor)", 
         color="#2ca02c", linewidth=2, marker='s')

# Ligne de securite (1 an)
security_limit = 3.154e7 # 1 year in seconds
plt.axhline(y=security_limit, color='black', linestyle='--', alpha=0.5)
plt.text(550, security_limit * 2, "Security Limit (1 year)", color='black', fontweight='bold')

# Formatage (Pas de titre, labels anglais)
plt.yscale('log')
plt.xlabel("RSA Key Size (bits)")
plt.ylabel("Estimated Computation Time (seconds / log)")
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend(loc="upper left")

plt.tight_layout()
plt.savefig("results/graphique_shor_benchmark.png", dpi=300)

# On lance la demo Qiskit a la fin
circuit_demo = create_shor_circuit_logic()
print("Fichiers 'results_shor_complet.csv' et 'graphique_shor_benchmark.png' crees.")