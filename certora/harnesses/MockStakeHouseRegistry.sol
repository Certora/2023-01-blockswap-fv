pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT


/// @title StakeHouse core member registry. Functionality is built around this core
/// @dev Every member is known as a KNOT and the StakeHouse is a collection of KNOTs
contract MockStakeHouseRegistry {
   type blsKey is bytes32;

    /// @notice Member metadata struct - taking advantage of packing
    
    uint80 _knotMemberIndex; // index integer assigned to KNOT when added to the StakeHouse
    uint16 _flags; // flags tracking the state of the KNOT i.e. whether active, kicked and or rage quit
    
    
    /// @notice Member information packed into 1 var - ETH 1 applicant address, KNOT index pointer and flag info
    mapping(blsKey => address) public memberIDToApplicant;
    mapping(blsKey => bool) public active;

    /// @custom:oz-upgrades-unsafe-allow constructor
    
    function getMemberInfo(blsKey _memberId) public view returns (
        address applicant,      // Address of ETH account that added the member to the StakeHouse
        uint256 knotMemberIndex,// KNOT Index of the member within the StakeHouse
        uint16 flags,          // Flags associated with the member
        bool isActive           // Whether the member is active or knot
    ) {
        applicant = memberIDToApplicant[_memberId];
        knotMemberIndex = _knotMemberIndex;
        flags = _flags;
        isActive = active[_memberId];
    }

}
