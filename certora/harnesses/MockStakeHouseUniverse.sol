pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

interface IStakeHouseRegistry {

    function getMemberInfo(bytes32 _memberId) external view returns (
        address applicant,
        uint256 knotMemberIndex,
        uint16 flags,
        bool isActive
    );
}

interface ISlotSettlementRegistry {
    function stakeHouseShareTokens(address _stakeHouse) external view returns (address);
}

contract MockStakeHouseUniverse {
    type blsKey is bytes32;
    /// @notice Address of SLOT minting and management contract
    ISlotSettlementRegistry public slotRegistry;

    /// @notice Member ID -> assigned StakeHouse. Iron rule is that member can only be active in 1 StakeHouse
    mapping(blsKey => address) public memberKnotToStakeHouse;

    constructor(address _slotRegistryLogic) {     
        require(_slotRegistryLogic != address(0), "SLOT registry cannot be zero");
        
        slotRegistry = ISlotSettlementRegistry(_slotRegistryLogic);
    }

    function stakeHouseKnotInfo(blsKey _memberId) public view returns (
        address stakeHouse,     // Address of registered StakeHouse
        address sETHAddress,    // Address of sETH address associated with StakeHouse
        address applicant,      // Address of ETH account that added the member to the StakeHouse
        uint256 knotMemberIndex,// KNOT Index of the member within the StakeHouse
        uint256 flags,          // Flags associated with the member
        bool isActive           // Whether the member is active or knot
    ) {
        require(memberKnotToStakeHouse[_memberId] != address(0), "Member is not assigned to any StakeHouse");
        address _stakeHouse = memberKnotToStakeHouse[_memberId];
        address _sETHAddress = slotRegistry.stakeHouseShareTokens(_stakeHouse);

        (
            address _applicant,
            uint256 _knotMemberIndex,
            uint256 _flags,
            bool _isActive
        ) = IStakeHouseRegistry(_stakeHouse).getMemberInfo(blsKey.unwrap(_memberId));

        return (
            _stakeHouse,
            _sETHAddress,
            _applicant,
            _knotMemberIndex,
            _flags,
            _isActive
        );
    }
}