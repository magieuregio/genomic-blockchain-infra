from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import json, glob, hashlib
import re

KEK_PUB_PEM = "/home/bioinfo/SARA_FEIZYAB/blockchain/encryption/kek_public.pem" 

projectId = "MAG-2025-LYM-01"
consentHash = "0xcd478b4633066ff3b0681ea586da81381fd097ae25ed6aee1259e8ce13e93b5b" 

for idx, npy in enumerate(sorted(glob.glob("data/HG*_variant_embed.npy"))):
    tokenId = str(idx)
    AAD = f"{projectId}|{tokenId}|{consentHash}".encode()
    
    with open(npy, "rb") as f:
        plaintext = f.read()
    dek = get_random_bytes(32)  # AES-256
    cipher = AES.new(dek, AES.MODE_EAX)
    cipher.update(AAD)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(KEK_PUB_PEM, "rb") as f:
        pub = RSA.import_key(f.read())
    rsa = PKCS1_OAEP.new(pub)
    dek_enc = rsa.encrypt(dek)
    blob = {
        "version": "1.0",
        "alg": "AES-256-EAX",
        "aad_hex": AAD.hex(),
        "nonce_hex": cipher.nonce.hex(),
        "tag_hex": tag.hex(),
        "dek_wrapped_hex": dek_enc.hex(),
        "sha256_cipher": hashlib.sha256(ciphertext).hexdigest()
    }
    out_bin = npy.replace(".npy", "_encrypted.bin")
    with open(out_bin, "wb") as f:
        f.write(cipher.nonce + tag + ciphertext)
    with open(npy.replace(".npy", "_enc_manifest.json"), "w") as f:
        json.dump(blob, f, indent=2)
    print(f"Encrypted {npy} as {out_bin} (tokenId {tokenId})")

