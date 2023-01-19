pragma solidity ^0.8.0;

// SPDX-License-Identifier: BUSL-1.1

import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { ISlotSettlementRegistry } from "../munged/interfaces/ISlotSettlementRegistry.sol";
import { IStakeHouseUniverse } from "../munged/interfaces/IStakeHouseUniverse.sol";
import { MainnetConstants, GoerliConstants } from "@blockswaplab/stakehouse-solidity-api/contracts/Constants.sol";

/// @title Implementable Stakehouse protocol smart contract consumer without worrying about the interfaces or addresses
abstract contract StakehouseAPI {

    /// @dev Get the interface connected to the SLOT registry smart contract
    function getSlotRegistry() internal view virtual returns (ISlotSettlementRegistry slotSettlementRegistry) {
        uint256 chainId = _getChainId();

        if(chainId == MainnetConstants.CHAIN_ID) {
            slotSettlementRegistry = ISlotSettlementRegistry(MainnetConstants.SlotSettlementRegistry);
        }

        else if (chainId == GoerliConstants.CHAIN_ID) {
            slotSettlementRegistry = ISlotSettlementRegistry(GoerliConstants.SlotSettlementRegistry);
        }

        else {
            _unsupported();
        }
    }

    /// @dev Get the interface connected to the Stakehouse universe smart contract
    function getStakeHouseUniverse() internal view virtual returns (IStakeHouseUniverse universe) {
        uint256 chainId = _getChainId();

        if(chainId == MainnetConstants.CHAIN_ID) {
            universe = IStakeHouseUniverse(MainnetConstants.StakeHouseUniverse);
        }

        else if (chainId == GoerliConstants.CHAIN_ID) {
            universe = IStakeHouseUniverse(GoerliConstants.StakeHouseUniverse);
        }

        else {
            _unsupported();
        }
    }

    /// @dev If the network does not match one of the choices stop the flow
    function _unsupported() internal pure {
        revert('Network unsupported');
    }

    /// @dev Helper function to get the id of the current chain
    function _getChainId() internal view returns (uint256 chainId) {
        assembly {
            chainId := chainid()
        }
    }
}
