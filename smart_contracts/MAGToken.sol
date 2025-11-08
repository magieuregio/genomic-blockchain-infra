// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MAGToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MAGToken", "MAG") {
        // Mint initial supply to deployer, with 18 decimals
        _mint(msg.sender, initialSupply * 10**decimals());
    }
}
