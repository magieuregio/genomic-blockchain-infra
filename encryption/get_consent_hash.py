import hashlib

with open("/home/bioinfo/SARA_FEIZYAB/blockchain/legal/Project-Specific Consent Form.pdf", "rb") as f:
    pdf_bytes = f.read()

consent_hash = "0x" + hashlib.sha256(pdf_bytes).hexdigest()
print("Consent hash:", consent_hash)
