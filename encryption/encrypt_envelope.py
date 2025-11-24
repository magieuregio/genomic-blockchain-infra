from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import json, glob, hashlib

KEK_PUB_PEM = "/home/bioinfo/SARA_FEIZYAB/blockchain/encryption/kek_public.pem"

projectId = "MAG-2025-LYM-01"
consentHash = "0xcd478b4633066ff3b0681ea586da81381fd097ae25d6aee1259e8ce13e93b5b"

with open(KEK_PUB_PEM, "rb") as f:
    kek_pub = RSA.import_key(f.read())

rsa_kek = PKCS1_OAEP.new(kek_pub)

for idx, npy in enumerate(sorted(glob.glob("data/HG*_k5_embed.npy"))):
    tokenId = str(idx)

    aad_str = f"{projectId}|{tokenId}|{consentHash}"
    AAD = aad_str.encode("utf-8")

    with open(npy, "rb") as f:
        plaintext = f.read()

    dek = get_random_bytes(32)          
    nonce = get_random_bytes(12)        

    cipher = AES.new(dek, AES.MODE_GCM, nonce=nonce)
    cipher.update(AAD)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    dek_enc = rsa_kek.encrypt(dek)

    out_bin = npy.replace(".npy", "_encrypted.bin")
    with open(out_bin, "wb") as f:
        f.write(nonce + tag + ciphertext)

    blob = {
        "version": "1.0",
        "alg": "AES-256-GCM",
        "projectId": projectId,
        "tokenId": tokenId,
        "consentHash": consentHash,
        "aad_hex": AAD.hex(),
        "nonce_hex": nonce.hex(),
        "tag_hex": tag.hex(),
        "dek_wrapped_hex": dek_enc.hex(),
        "sha256_cipher": hashlib.sha256(ciphertext).hexdigest(),
        "sha256_plain": hashlib.sha256(plaintext).hexdigest(),
        "ciphertext_file": out_bin.split("/")[-1],
    }

    manifest_path = npy.replace(".npy", "_enc_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(blob, f, indent=2)

    print(f"Encrypted {npy} as {out_bin} (tokenId {tokenId})")
