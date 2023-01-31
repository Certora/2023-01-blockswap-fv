pragma solidity 0.8.13;

contract MockSlotSettlementRegistry  {
    type blsKey is bytes32;

     /// @notice StakeHouse registry address -> sETH share token for the StakeHouse
    mapping(address => address) public stakeHouseShareTokens;

    /// @notice Current amount of SLOT that has been slashed from collateralised slot owner(s) which has not been purchased yet
    mapping(blsKey => uint256) private _currentSlashedAmountOfSLOTForKnot;


    /// @notice Total collateralised SLOT owned by an account for a given KNOT in a Stakehouse
    /// @dev Stakehouse address -> user account -> Knot ID (bls pub key) -> SLOT balance collateralised against the KNOT
    mapping(address => mapping(address => mapping(blsKey => uint256))) private _totalUserCollateralisedSLOTBalanceForKnot;


    mapping(blsKey => uint256) _numberOfCollateralisedSlotOwnersForKnot;
    
    mapping(blsKey => mapping(uint256 => address)) collateralisedOwnerAtIndex;

    /// @notice Fetch a collateralised SLOT owner address for a specific KNOT at a specific index
    function getCollateralisedOwnerAtIndex(blsKey _blsPublicKey, uint256 _index) external view returns (address) {
        return collateralisedOwnerAtIndex[_blsPublicKey][_index];
    }


    /// @notice Total number of collateralised SLOT owners for a given KNOT
    /// @param _blsPublicKey BLS public key of the KNOT
    function numberOfCollateralisedSlotOwnersForKnot(blsKey  _blsPublicKey) external view returns (uint256) {
        return _numberOfCollateralisedSlotOwnersForKnot[_blsPublicKey];
    }

    function totalUserCollateralisedSLOTBalanceForKnot( address stakeHouse, address owner, blsKey blsPubKey ) public returns (uint256) {
        return _totalUserCollateralisedSLOTBalanceForKnot[stakeHouse][owner][blsPubKey];
    }

    function currentSlashedAmountOfSLOTForKnot( blsKey blsPubKey ) public returns (uint256) 
    { 
        return _currentSlashedAmountOfSLOTForKnot[blsPubKey];
    }
}
