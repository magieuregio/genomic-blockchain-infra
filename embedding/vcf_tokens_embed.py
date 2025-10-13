import glob, mmh3, numpy as np

def variant_tokens(vcf_path):
    toks = []
    with open(vcf_path) as f:
        for line in f:
            if line.startswith("#"): continue
            fields = line.strip().split('\t')
            if len(fields) < 5:
                continue
            chrom, pos, _id, ref, alt = fields[:5]
            toks.append(f"{chrom}:{pos}:{ref}>{alt}")
    return toks

def token_hash_vector(tokens, dim=2048):
    vec = np.zeros(dim, dtype=np.float32)
    for t in tokens:
        i = mmh3.hash(t, signed=False) % dim
        vec[i] += 1.0
    s = vec.sum()
    return (vec/s) if s>0 else vec

for vcf in sorted(glob.glob("data/HG*.vcf")):
    toks = variant_tokens(vcf)
    vec = token_hash_vector(toks, dim=2048)
    out = vcf.replace(".vcf", "_variant_embed.npy")
    np.save(out, vec)
    print("Saved:", out)
