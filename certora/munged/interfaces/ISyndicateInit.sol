pragma solidity ^0.8.13;

// SPDX-License-Identifier: BUSL-1.1

/// @dev Interface for initializing a newly deployed Syndicate
interface ISyndicateInit {
    type blsKey is bytes32;

    function initialize(
        address _contractOwner,
        uint256 _priorityStakingEndBlock,
        address[] memory _priorityStakers,
        blsKey[] memory _blsPubKeysForSyndicateKnots
    ) external;
}