import { deploy } from './ethers-lib.ts'

(async () => {
  try {
    const result = await deploy('GenomicDataNFTv2', ['0x09be639bc0158ca03f041b2c6fc8b37c5abe6c89']);
    console.log(`GenomicDataNFTv2 deployed at: ${result.target}`);
  } catch (e) {
    if (e instanceof Error) {
      console.log(e.message);
    } else {
      console.log(String(e));
    }
  }
})();
