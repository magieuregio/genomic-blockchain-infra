from Bio import SeqIO
import numpy as np, json, glob, hashlib
from itertools import product

def revcomp(s):
    comp = str.maketrans('ACGT', 'TGCA')
    return s.translate(comp)[::-1]

def canonical(kmer):
    rc = revcomp(kmer)
    return min(kmer, rc)

def kmer_vocab(k=5):
    bases = 'ACGT'
    return [''.join(p) for p in product(bases, repeat=k)]

def kmer_counts(seq, k=5):
    seq = seq.upper()
    bases = set('ACGT')
    counts = {}
    n_valid = 0
    n_n = 0
    for i in range(len(seq)-k+1):
        kmer = seq[i:i+k]
        if all(c in bases for c in kmer):
            n_valid += 1
            counts[kmer] = counts.get(kmer, 0) + 1
        else:
            n_n += 1
    return counts, n_valid, n_n

VOCAB = kmer_vocab(5)

for fasta in sorted(glob.glob("data/HG*.fa")):
    for rec in SeqIO.parse(fasta, "fasta"):
        counts, n_valid, n_n = kmer_counts(str(rec.seq), k=5)
        vec = np.zeros(len(VOCAB), dtype=np.float64)
        idx = {k:i for i,k in enumerate(VOCAB)}
        for kmer, count in counts.items():
            vec[idx[kmer]] = count
        total = vec.sum()
        vec_norm = (vec/total) if total>0 else vec
        out_npy = fasta.replace(".fa", "_k5_embed.npy")
        np.save(out_npy, vec_norm)
        manifest = {
            "file": out_npy,
            "vocab_size": len(VOCAB),
            "valid_kmers": int(n_valid),
            "n_N": int(n_n),
            "length": len(rec.seq),
            "sha256_plain": hashlib.sha256(vec_norm.tobytes()).hexdigest()
        }
        with open(fasta.replace(".fa", "_k5_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        print("Saved:", out_npy)
