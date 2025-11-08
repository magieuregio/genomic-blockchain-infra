const { ethers } = require("ethers");
const fs = require("fs");

// --- CONFIG ---
require('dotenv').config();
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const AMOY_RPC = process.env.AMOY_RPC;
const CONTRACT_ADDRESS = process.env.CONTRACT_ADDRESS;
const ABI = JSON.parse(fs.readFileSync("./abis/GenomicDataNFTv2.json"));

// Load all metadata CIDs (replace with your own array or load from JSON)
const metadataURIs = [
  "ipfs://QmeCUNoVsTt3ahobF1tEEETixQHZRrjeqSK2FWbTF7SRnz",
  "ipfs://QmWJNmVv3j6udNqFV6zTVd2fMviN3KodTpppPmY1FKTcMc",
  "ipfs://QmdbNmmAwoJykWuTLTVB7pwB6CxG3hkMAhZx5HhDoxFypw",
  "ipfs://Qma8eJiQVrmzcGhWAc11v5X8zZeb25T6n4KTsDFb6qLtT5",
  "ipfs://QmUG9YmTyHcTPL6sayaPLYzZQRxTyjxvWkcxVaF1hn6Pon",
  "ipfs://QmQKKv5H9p2vYEetKzjiHDYw5ZqXrUuxPHuvpvWZysU3sj",
  "ipfs://QmWoYnsCKit1EMuMRTWQKunGwuKKnqHU6W2X9orL4uQkZa",
  "ipfs://QmSnF3qibexrye6stuArkFdtxPjpYEbnEVAfEnwiBc9kaM",
  "ipfs://QmXrLZ7uUziVGhgcAic7x1RNPWyep4nKde8hbkoTtx8sDv",
  "ipfs://QmPjMysi3JR2pGAgfqc2d944eJ95xnRzdLhrfK621A97v7"
];
const magPrice = ethers.parseUnits("50", 18); // 50 MAG, 18 decimals

// --- SCRIPT ---

async function main() {
  const provider = new ethers.JsonRpcProvider(AMOY_RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, wallet);

  for (let i = 0; i < metadataURIs.length; i++) {
    const tx = await contract.mintDataset(metadataURIs[i], magPrice);
    console.log(`Minting NFT ${i + 1}...`);
    await tx.wait();
    console.log(`Minted NFT ${i + 1} with metadata: ${metadataURIs[i]}`);
  }
  console.log("All NFTs minted!");
}

main().catch(console.error);
