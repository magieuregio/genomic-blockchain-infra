from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import json, glob, hashlib, os

KEK_PUB_PEM = "kek_public.pem"  # Place your public RSA key here

def encrypt_file(npy_path, aad: bytes):
    with open(npy_path, "rb") as f:
        plaintext = f.read()
    dek = get_random_bytes(32)  # AES-256
    cipher = AES.new(dek, AES.MODE_EAX)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    # RSA-wrap DEK
    with open(KEK_PUB_PEM, "rb") as f:
        pub = RSA.import_key(f.read())
    rsa = PKCS1_OAEP.new(pub)
    dek_enc = rsa.encrypt(dek)
    blob = {
        "version": "1.0",
        "alg": "AES-256-EAX",
        "aad_hex": aad.hex(),
        "nonce_hex": cipher.nonce.hex(),
        "tag_hex": tag.hex(),
        "dek_wrapped_hex": dek_enc.hex(),
        "sha256_cipher": hashlib.sha256(ciphertext).hexdigest()
    }
    out_bin = npy_path.replace("_k5_embed.npy", "_k5_embed_encrypted.bin")
    with open(out_bin, "wb") as f:
        f.write(cipher.nonce + tag + ciphertext)
    with open(npy_path.replace("_k5_embed.npy", "_k5_embed_enc_manifest.json"), "w") as f:
        json.dump(blob, f, indent=2)
    print("Encrypted:", out_bin)

# EXAMPLE - replace with actual projectId/tokenId/consentHash!
projectId = "MAG-2025-LYM-01"
tokenId = "0"
consentHash = "0xabcde..."
AAD = f"{projectId}|{tokenId}|{consentHash}".encode()

for npy in sorted(glob.glob("../embedding/sample_*_k5_embed.npy")):
    encrypt_file(npy, AAD)
