# Genomic Blockchain Infrastructure: Secure Storage & Access Platform

**Company:** Magi's Lab Srl  
**Contact:** [sara.feizyab@assomagi.org]  
**Version:** Research Prototype (Polygon Amoy Testnet)

---

## Overview

This repository presents a prototype for a secure, scalable infrastructure enabling **controlled access to genomic data** using blockchain and decentralized storage.

- **Vectorized genomic data** (privacy-preserving k-mer embeddings)
- **Encrypted, off-chain storage** (IPFS, pinning via Pinata/Web3.Storage)
- **Multi-NFT access control** (ERC-1155 on Polygon L2)
- **MAG utility token** (ERC-20, testnet faucet)
- **Consent compliance** (off-chain, proof on-chain)
- **Web3 UI prototype** (React/HTML demo)
- **Python preprocessing tools** (embedding, encryption)

**Purpose:**  
Accelerate research, ensure privacy, and guarantee integrity of sensitive genomic datasets for academic research.

---

## Architecture

**Main Components:**
1. **Genomic Data Vectorization:**  
   Converts VCF/FASTQ to normalized k-mer embeddings (privacy-enhancing, research utility preserved).
2. **Encryption:**  
   Each embedding is encrypted using envelope AES+RSA; key management is handled off-chain.
3. **Decentralized Storage (IPFS):**  
   Only encrypted data plus manifest is uploaded and pinned; CIDs guarantee content integrity.
4. **NFT & MAG Token Access Control:**  
   - ERC-1155 NFTs represent dataset access rights.
   - MAG (ERC-20, testnet) required to claim NFTs.
   - Ownership is recorded on Polygon (Mumbai).
5. **Web3 Interface:**  
   React/Ethers.js UI lets users mint/claim NFTs and access CIDs.
6. **Consent Management (off-chain):**  
   All user consents, notifications, and revocations are handled off-chain, storing only proofs/hashes on-chain.
7. **Analysis Tools Integration:**  
   Vectorized data is immediately compatible with Python ML/bioinformatics tools (NumPy, scikit-learn, TensorFlow).

---


.....