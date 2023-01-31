pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import "../munged/syndicate/Syndicate.sol";
import { ISlotSettlementRegistry } from "../munged/interfaces/ISlotSettlementRegistry.sol";
import { IStakeHouseUniverse } from "../munged/interfaces/IStakeHouseUniverse.sol";

contract SyndicateHarness is Syndicate {
    address registry;
    address universe;

    function registerKnotsToSyndicate(blsKey input) public {
        blsKey[] memory next_input = new blsKey[](1);
        next_input[0] = input;
        registerKnotsToSyndicate(next_input);
    }

    function registerKnotsToSyndicate(blsKey input1, blsKey input2) public {
        blsKey[] memory next_input = new blsKey[](2);
        next_input[0] = input1;
        next_input[1] = input2;
        registerKnotsToSyndicate(next_input);
    }

    function addPriorityStakers(address input) public {
        address[] memory next_input = new address[](1);
        next_input[0] = input;
        addPriorityStakers(next_input);
    }

    function addPriorityStakers(address input1, address input2) public {
        address[] memory next_input = new address[](2);
        next_input[0] = input1;
        next_input[1] = input2;
        addPriorityStakers(next_input);
    }

    function deRegisterKnots(blsKey input) public {
        blsKey[] memory next_input = new blsKey[](1);
        next_input[0] = input;
        deRegisterKnots(next_input);
    }

    function deRegisterKnots(blsKey input1, blsKey input2) public {
        blsKey[] memory next_input = new blsKey[](2);
        next_input[0] = input1;
        next_input[1] = input2;
        deRegisterKnots(next_input);
    }

    function stake(blsKey input1, uint256 input2, address input3) public {
        blsKey[] memory next_input1 = new blsKey[](1);
        next_input1[0] = input1;
        uint256[] memory next_input2 = new uint256[](1);
        next_input2[0] = input2;
        stake(next_input1, next_input2, input3);
    }

    function stake(blsKey input1, blsKey input2, uint256 input3, uint256 input4, address input5) public {
        blsKey[] memory next_input1 = new blsKey[](2);
        next_input1[0] = input1;
        next_input1[1] = input2;
        uint256[] memory next_input2 = new uint256[](2);
        next_input2[0] = input3;
        next_input2[1] = input4;
        stake(next_input1, next_input2, input5);
    }

    function unstake(address input1, address input2, blsKey input3, uint256 input4) public {
        blsKey[] memory next_input3 = new blsKey[](1);
        next_input3[0] = input3;
        uint256[] memory next_input4 = new uint256[](1);
        next_input4[0] = input4;
        unstake(input1, input2, next_input3, next_input4);
    }

    function unstake(address input1, address input2, blsKey input3, blsKey input4, uint256 input5, uint256 input6) public {
        blsKey[] memory next_input3 = new blsKey[](2);
        next_input3[0] = input3;
        next_input3[1] = input4;
        uint256[] memory next_input4 = new uint256[](2);
        next_input4[0] = input5;
        next_input4[1] = input6;
        unstake(input1, input2, next_input3, next_input4);
    }

    function claimAsStaker(address input1, blsKey input2) public {
        blsKey[] memory next_input2 = new blsKey[](1);
        next_input2[0] = input2;
        claimAsStaker(input1, next_input2);
    }

    function claimAsStaker(address input1, blsKey input2, blsKey input3) public {
        blsKey[] memory next_input2 = new blsKey[](2);
        next_input2[0] = input2;
        next_input2[1] = input3;
        claimAsStaker(input1, next_input2);
    }

    function claimAsCollateralizedSLOTOwner(address input1, blsKey input2) public {
        blsKey[] memory next_input2 = new blsKey[](1);
        next_input2[0] = input2;
        claimAsCollateralizedSLOTOwner(input1, next_input2);
    }

    function claimAsCollateralizedSLOTOwner(address input1, blsKey input2, blsKey input3) public {
        blsKey[] memory next_input2 = new blsKey[](2);
        next_input2[0] = input2;
        next_input2[1] = input3;
        claimAsCollateralizedSLOTOwner(input1, next_input2);
    }

    function batchUpdateCollateralizedSlotOwnersAccruedETH(blsKey _blsPubKey) public {
        blsKey[] memory _blsPubKeys = new blsKey[](1);
        _blsPubKeys[0] = _blsPubKey;
        batchUpdateCollateralizedSlotOwnersAccruedETH(_blsPubKeys);
    }

    function batchUpdateCollateralizedSlotOwnersAccruedETH(blsKey _blsPubKey1, blsKey _blsPubKey2) public {
        blsKey[] memory _blsPubKeys = new blsKey[](2);
        _blsPubKeys[0] = _blsPubKey1;
        _blsPubKeys[1] = _blsPubKey2;
        batchUpdateCollateralizedSlotOwnersAccruedETH(_blsPubKeys);
    }

    // overridden functions
    function getSlotRegistry() internal view override returns (ISlotSettlementRegistry slotSettlementRegistry) {
        return ISlotSettlementRegistry(registry);
    }

    function getStakeHouseUniverse() internal view override returns (IStakeHouseUniverse stakeHouseUniverse) {
        return IStakeHouseUniverse(universe);
    }
}

