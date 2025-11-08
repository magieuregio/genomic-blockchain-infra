import { deploy } from './ethers-lib.ts'

(async () => {
  try {
    const result = await deploy('MAGToken', ['1000000']); // 1M tokens
    console.log(`MAGToken deployed at: ${result.target}`);
  } catch (e) {
    if (e instanceof Error) {
      console.log(e.message);
    } else {
      console.log(String(e));
    }
  }
})();
