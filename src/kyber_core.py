import numpy as np
import hashlib

VARIANTES = {
    "Kyber-512":  {"k": 2, "securite": 128},
    "Kyber-768":  {"k": 3, "securite": 192},
    "Kyber-1024": {"k": 4, "securite": 256},
}

N = 256
Q = 3329

def keygen(k):
    A = np.random.randint(0, Q, size=(k,k,N), dtype=np.int64)
    s = np.random.randint(0, Q, size=(k,N), dtype=np.int64)
    t = np.einsum('ijk,jk->ik', A, s) % Q
    return (A, t), s

def encaps(pk, k):
    A, t = pk
    r = np.random.randint(0, Q, size=(k,N), dtype=np.int64)
    m = np.random.randint(0, 2, size=N, dtype=np.int64) * (Q//2)
    u = np.einsum('ijk,jk->ik', A.transpose(1,0,2), r) % Q
    v = (np.sum(t*r, axis=0) + m) % Q
    cle = hashlib.sha256(m.tobytes()).digest()
    return cle, (u, v)

def decaps(sk, ct, k):
    s = sk
    u, v = ct
    m_rec = (v - np.sum(s*u, axis=0)) % Q
    m_bits = np.array([1 if min(int(x),Q-int(x))>Q//4 else 0 for x in m_rec]) * (Q//2)
    cle = hashlib.sha256(m_bits.astype(np.int64).tobytes()).digest()
    return cle

if __name__ == "__main__":
    print("Test Kyber\n")
    for nom, params in VARIANTES.items():
        k = params["k"]
        pk, sk = keygen(k)
        cle_bob, ct = encaps(pk, k)
        cle_alice = decaps(sk, ct, k)
        print(f"  {nom} -> {'OK' if cle_bob==cle_alice else 'ERREUR'}")