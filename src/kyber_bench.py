# benchmark_kyber.py
# 3 mesures sur Kyber :
# 1. Temps d'echange de cle
# 2. Temps de chiffrement du message
# 3. Taux de succes de l'attaquant (securite reelle)

import time
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from kyber_core import keygen, encaps, decaps, VARIANTES

# --- CONFIGURATION DES REPERTOIRES ---
for folder in ["results", "figures"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

N_TESTS = 1000
Q = 3329

# ─────────────────────────────────────────
# MESURE 1 : Temps d'echange de cle
# ─────────────────────────────────────────

def mesurer_temps_echange(nom, k, n_tests):
    temps = []
    print(f"  [1] Temps echange {nom}...", end="", flush=True)
    for _ in range(n_tests):
        debut = time.perf_counter()
        pk, sk  = keygen(k)
        cle, ct = encaps(pk, k)
        cle_rec = decaps(sk, ct, k)
        fin = time.perf_counter()
        temps.append((fin - debut) * 1000)
    print(f" OK (moyenne: {np.mean(temps):.3f}ms)")
    return temps

# ─────────────────────────────────────────
# MESURE 2 : Temps de chiffrement
# ─────────────────────────────────────────

def chiffrer_message(cle, message):
    cle_etendue = (cle * (len(message) // len(cle) + 1))[:len(message)]
    return bytes(a ^ b for a, b in zip(message, cle_etendue))

def mesurer_temps_message(nom, k, n_tests):
    temps = []
    message = os.urandom(256)
    print(f"  [2] Temps message  {nom}...", end="", flush=True)
    for _ in range(n_tests):
        pk, sk  = keygen(k)
        cle, ct = encaps(pk, k)
        debut = time.perf_counter()
        chiffrer_message(cle, message)
        fin = time.perf_counter()
        temps.append((fin - debut) * 1000)
    print(f" OK (moyenne: {np.mean(temps):.4f}ms)")
    return temps

# ─────────────────────────────────────────
# MESURE 3 : Taux de succes attaquant
# ─────────────────────────────────────────

def mesurer_attaque(nom, k, n_tests):
    succes = []
    print(f"  [3] Attaque        {nom}...", end="", flush=True)
    for _ in range(n_tests):
        pk, sk_alice = keygen(k)
        cle_bob, ct  = encaps(pk, k)
        sk_attaquant  = np.random.randint(0, Q, size=(k, 256), dtype=np.int64)
        cle_attaquant = decaps(sk_attaquant, ct, k)
        succes.append(1 if cle_attaquant == cle_bob else 0)
    taux = np.mean(succes) * 100
    print(f" OK (taux succes attaquant: {taux:.1f}%)")
    return succes

# ─────────────────────────────────────────
# LANCEMENT DU BENCHMARK
# ─────────────────────────────────────────

print("=" * 45)
print("  BENCHMARK KYBER — 3 mesures")
print("=" * 45 + "\n")

temps_echange   = {}
temps_message   = {}
taux_attaque    = {}

for nom, params in VARIANTES.items():
    k  = params["k"]
    temps_echange[nom]   = mesurer_temps_echange(nom, k, N_TESTS)
    temps_message[nom]   = mesurer_temps_message(nom, k, N_TESTS)
    taux_attaque[nom]    = mesurer_attaque(nom, k, N_TESTS)
    print()

# ─────────────────────────────────────────
# SAUVEGARDE CSV (Dossier results)
# ─────────────────────────────────────────

csv_path = "results/benchmark_kyber.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Variante", "Test", "Temps echange (ms)", "Temps message (ms)", "Attaque reussie"])
    for nom in VARIANTES:
        for i in range(N_TESTS):
            writer.writerow([
                nom, i,
                round(temps_echange[nom][i], 4),
                round(temps_message[nom][i], 6),
                taux_attaque[nom][i],
            ])
print(f"  Données CSV exportées -> {csv_path}\n")

# ─────────────────────────────────────────
# GRAPHIQUES (Dossier figures)
# ─────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Performance Analysis: CRYSTALS-Kyber (KEM)", fontsize=15, fontweight="bold")
couleurs = {"Kyber-512": "royalblue", "Kyber-768": "seagreen", "Kyber-1024": "firebrick"}

# Graphique 1 : Temps echange
for nom, temps in temps_echange.items():
    axes[0].scatter(range(N_TESTS), temps, color=couleurs[nom], alpha=0.3, label=nom, s=5)
axes[0].set_title("1. Key Exchange Latency")
axes[0].set_xlabel("Iterations")
axes[0].set_ylabel("Time (ms)")
axes[0].set_yscale("log") 
axes[0].legend()
axes[0].grid(True, linestyle=":", alpha=0.6)

# Graphique 2 : Temps message
for nom, temps in temps_message.items():
    axes[1].scatter(range(N_TESTS), temps, color=couleurs[nom], alpha=0.3, label=nom, s=5)
axes[1].set_title("2. Message Encryption Latency")
axes[1].set_xlabel("Iterations")
axes[1].set_ylabel("Time (ms)")
axes[1].legend()
axes[1].grid(True, linestyle=":", alpha=0.6)

# Graphique 3 : Taux de succès
noms = list(VARIANTES.keys())
taux_moyens = [np.mean(taux_attaque[n]) * 100 for n in noms]
bars = axes[2].bar(noms, taux_moyens, color=["royalblue","seagreen","firebrick"], alpha=0.8)
axes[2].set_title("3. Attacker Success Rate")
axes[2].set_ylabel("Success Rate (%)")
axes[2].set_ylim(0, 100) # Échelle fixée à 100% pour montrer la robustesse
axes[2].grid(axis="y", linestyle=":", alpha=0.6)

plt.tight_layout()
plot_path = "figures/benchmark_kyber_analysis.png"
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"  Visualisation sauvegardée -> {plot_path}")