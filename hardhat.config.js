require('dotenv').config();
require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-truffle5");
require('solidity-coverage');
require('@nomiclabs/hardhat-solhint');
require('hardhat-gas-reporter');
require('hardhat-contract-sizer');

const INFURA_PROJECT_ID = process.env.INFURA_PROJECT_ID;
const PRIVATE_KEY = process.env.G_PRIVATE_KEY;

let liveNetworks = {}

// If we have a private key, we can setup non dev networks
if (INFURA_PROJECT_ID && PRIVATE_KEY) {
  liveNetworks = {
    goerli: {
      url: `https://goerli.infura.io/v3/${INFURA_PROJECT_ID}`,
      accounts: [`0x${process.env.G_PRIVATE_KEY}`]
    }
  }
}

module.exports = {
  solidity: {
    version: "0.8.13",
    settings: {
      optimizer: {
        enabled: true,
        runs: 150
      }
    }
  },
  networks: {
    ...liveNetworks,
    coverage: {
      url: 'http://localhost:8555',
    },
    hardhat: {
      initialBaseFeePerGas: 1
    },
    localhost: {
      url: "http://127.0.0.1:8545"
    }
  },
  gasReporter: {
    currency: 'USD',
    gasPrice: 120,
    enabled: !!process.env.GAS_REPORT
  }
};
