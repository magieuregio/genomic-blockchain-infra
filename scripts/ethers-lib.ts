import { ethers, BaseContract } from "ethers";
import * as fs from "fs";
import * as path from "path";

require('dotenv').config();
const PRIVATE_KEY = process.env.PRIVATE_KEY as string;
const AMOY_RPC = process.env.AMOY_RPC;

/**
 * Deploy the given contract
 * @param {string} contractName name of the contract to deploy
 * @param {Array<any>} args list of constructor parameters
 * @returns {Promise<ethers.Contract>} deployed contract
 */
export const deploy = async (
  contractName: string,
  args: Array<any>
): Promise<BaseContract> => {
  // Load ABI and bytecode from artifacts
  const artifactsPath = path.join(__dirname, '../artifacts/', `${contractName}.json`);
  const metadata = JSON.parse(fs.readFileSync(artifactsPath, 'utf8'));

  // Setup provider and wallet (FILL IN)
  const provider = new ethers.JsonRpcProvider(AMOY_RPC);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

  // Deploy
  const factory = new ethers.ContractFactory(metadata.abi, metadata.bytecode, wallet);
  const contract = await factory.deploy(...args);
  await contract.waitForDeployment(); // ethers v6
  return contract;
};

module.exports = { deploy };
