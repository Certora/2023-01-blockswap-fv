using MocksETH as sETHToken
using MockStakeHouseRegistry as StakeHouseRegistry
using MockStakeHouseUniverse as StakeHouseUniverse
using MockSlotSettlementRegistry as SlotSettlementRegistry

methods {
    //// Regular methods / public variables
    calculateUnclaimedFreeFloatingETHShare(bytes32,address) returns (uint256) envfree
    sETHUserClaimForKnot(bytes32,address) returns (uint256) envfree
    totalETHReceived() returns (uint256) envfree
    calculateETHForFreeFloatingOrCollateralizedHolders() returns (uint256) envfree;
    getUnprocessedETHForAllCollateralizedSlot() returns (uint256) envfree;
    getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(bytes32) returns (uint256) envfree;
    updateAccruedETHPerShares() envfree;
    updatePriorityStakingBlock(uint256);
    previewUnclaimedETHAsFreeFloatingStaker(address, bytes32) returns (uint256) envfree;
    getUnprocessedETHForAllFreeFloatingSlot() returns (uint256) envfree;
    owner() returns (address) envfree;
    accumulatedETHPerFreeFloatingShare() returns (uint256) envfree;
    accumulatedETHPerCollateralizedSlotPerKnot() returns (uint256) envfree;
    lastSeenETHPerCollateralizedSlotPerKnot() returns (uint256) envfree;
    lastSeenETHPerFreeFloating() returns (uint256) envfree;
    totalFreeFloatingShares() returns (uint256) envfree;
    totalClaimed() returns (uint256) envfree;
    numberOfRegisteredKnots() returns (uint256) envfree;
    isKnotRegistered(bytes32) returns (bool) envfree;
    priorityStakingEndBlock() returns (uint256) envfree;
    isPriorityStaker(address) returns (bool) envfree;
    PRECISION() returns (uint256) envfree;
    isNoLongerPartOfSyndicate(bytes32) returns (bool) envfree;
    lastAccumulatedETHPerFreeFloatingShare(bytes32) returns (uint256) envfree;

    //// Resolving external calls
	// stakeHouseUniverse
	stakeHouseKnotInfo(bytes32) returns (address,address,address,uint256,uint256,bool) => DISPATCHER(true)
    memberKnotToStakeHouse(bytes32) returns (address) => DISPATCHER(true) // not used directly by Syndicate
    // stakeHouseRegistry
    getMemberInfo(bytes32) returns (address,uint256,uint16,bool) => DISPATCHER(true) // not used directly by Syndicate
    // slotSettlementRegistry
	stakeHouseShareTokens(address) returns (address)  => DISPATCHER(true)
	currentSlashedAmountOfSLOTForKnot(bytes32) returns (uint256)  => DISPATCHER(true)
	numberOfCollateralisedSlotOwnersForKnot(bytes32) returns (uint256)  => DISPATCHER(true)
	getCollateralisedOwnerAtIndex(bytes32, uint256) returns (address) => DISPATCHER(true)
	totalUserCollateralisedSLOTBalanceForKnot(address, address, bytes32) returns (uint256) => DISPATCHER(true)
    // sETH
    sETHToken.balanceOf(address) returns (uint256) envfree
    // ERC20
    name()                                returns (string)  => DISPATCHER(true)
    symbol()                              returns (string)  => DISPATCHER(true)
    decimals()                            returns (string) envfree => DISPATCHER(true)
    totalSupply()                         returns (uint256) => DISPATCHER(true)
    balanceOf(address)                    returns (uint256) => DISPATCHER(true)
    allowance(address,address)            returns (uint)    => DISPATCHER(true)
    approve(address,uint256)              returns (bool)    => DISPATCHER(true)
    transfer(address,uint256)             returns (bool)    => DISPATCHER(true)
    transferFrom(address,address,uint256) returns (bool)    => DISPATCHER(true)

    //// Harnessing
    // harnessed variables
    accruedEarningPerCollateralizedSlotOwnerOfKnot(bytes32,address) returns (uint256) envfree
    totalETHProcessedPerCollateralizedKnot(bytes32) returns (uint256) envfree
    sETHStakedBalanceForKnot(bytes32,address) returns (uint256) envfree
    sETHTotalStakeForKnot(bytes32) returns (uint256) envfree
    getETHBalance(address) returns (uint256) envfree
    getActivenessOfKnot(bytes32) returns (bool) envfree
    // harnessed functions
    deRegisterKnots(bytes32) 
    deRegisterKnots(bytes32,bytes32)
    stake(bytes32,uint256,address)
    stake(bytes32,bytes32,uint256,uint256,address)
    unstake(address,address,bytes32,uint256)
    unstake(address,address,bytes32,bytes32,uint256,uint256)
    claimAsStaker(address,bytes32)
    claimAsStaker(address,bytes32,bytes32)
    claimAsCollateralizedSLOTOwner(address,bytes32)
    claimAsCollateralizedSLOTOwner(address,bytes32,bytes32)
    registerKnotsToSyndicate(bytes32)
    registerKnotsToSyndicate(bytes32,bytes32)
    addPriorityStakers(address)
    addPriorityStakers(address,address)
    batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32)
    batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32,bytes32)
}

///////////////////// definitions

/// We defined additional functions to get around the complexity of defining dynamic arrays in cvl. We filter them in 
/// normal rules and invariants as they serve no purpose.
definition notHarnessCall(method f) returns bool = 
    f.selector != batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32).selector
    && f.selector != batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32,bytes32).selector
    && f.selector != deRegisterKnots(bytes32).selector
    && f.selector != deRegisterKnots(bytes32,bytes32).selector
    && f.selector != stake(bytes32,uint256,address).selector
    && f.selector != stake(bytes32,bytes32,uint256,uint256,address).selector
    && f.selector != unstake(address,address,bytes32,uint256).selector
    && f.selector != unstake(address,address,bytes32,bytes32,uint256,uint256).selector
    && f.selector != claimAsStaker(address,bytes32).selector
    && f.selector != claimAsStaker(address,bytes32,bytes32).selector
    && f.selector != claimAsCollateralizedSLOTOwner(address,bytes32).selector
    && f.selector != claimAsCollateralizedSLOTOwner(address,bytes32,bytes32).selector
    && f.selector != registerKnotsToSyndicate(bytes32).selector
    && f.selector != registerKnotsToSyndicate(bytes32,bytes32).selector
    && f.selector != addPriorityStakers(address).selector
    && f.selector != addPriorityStakers(address,address).selector;

//////////////////////// functions

/// Corrollary that can be used as requirement after sETH solvency is proven.
function sETHSolvencyCorrollary(address user1, address user2, bytes32 knot) returns bool {
    return sETHStakedBalanceForKnot(knot,user1) + sETHStakedBalanceForKnot(knot,user2) <= sETHTotalStakeForKnot(knot);
}

//////////////////////// Definitions

definition knotNotRegistered(bytes32 BLSPubKey) returns bool = 
    !isKnotRegistered(BLSPubKey) && !isNoLongerPartOfSyndicate(BLSPubKey);

definition knotRegistered(bytes32 BLSPubKey) returns bool = 
    isKnotRegistered(BLSPubKey) && !isNoLongerPartOfSyndicate(BLSPubKey);

definition knotDeRegistered(bytes32 BLSPubKey) returns bool = 
    isKnotRegistered(BLSPubKey) && isNoLongerPartOfSyndicate(BLSPubKey);

///////////// ------------ GHOSTS ------------- and 
///////////// ------------ HOOKS -------------

/**
* Ghost function with associated Hook equal to the number of registered Knots
* following isKnotRegistered mapping
*
* related solidity declaration : mapping(bytes32 => bool) public isKnotRegistered;
*/
ghost ghostKnotsRegisteredCount() returns uint256 {
    init_state axiom ghostKnotsRegisteredCount() == 0;
}
hook Sstore isKnotRegistered[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsRegisteredCount assuming ghostKnotsRegisteredCount@new() ==
        ghostKnotsRegisteredCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

/**
* Ghost function with associated Hook equal to the number of Knots no longer Syndicated
* following isNoLongerPartOfSyndicate mapping
*
* related solidity declaration : mapping(bytes32 => bool) public isNoLongerPartOfSyndicate;
*/
ghost ghostKnotsNotSyndicatedCount() returns uint256 {
    init_state axiom ghostKnotsNotSyndicatedCount() == 0;
}
hook Sstore isNoLongerPartOfSyndicate[KEY bytes32 k] bool newState (bool oldState) STORAGE {
    havoc ghostKnotsNotSyndicatedCount assuming ghostKnotsNotSyndicatedCount@new() ==
        ghostKnotsNotSyndicatedCount@old() + ( newState != oldState ? ( newState ? 1 : -1 ) : 0 );
}

/**
 * Accounts for the total stake of sETH
 */
ghost mathint sETHTotalStake {
    init_state axiom sETHTotalStake == 0 ;
}
    
/**
 * Hook to update the ghost sETHTotalStake on every change to the mapping sETHTotalStakeForKnot
 */
hook Sstore sETHTotalStakeForKnot[KEY bytes32 blsPubKey] uint256 newValue (uint256 oldValue) STORAGE {
    sETHTotalStake = sETHTotalStake + newValue - oldValue;
}

/**
 * Accounts for the total staked balance of sETH
 */
ghost mathint sETHTotalStakedBalance {
    init_state axiom sETHTotalStakedBalance == 0 ;
}

ghost mapping(bytes32 => uint256) ghostsETHTotalStakeForKnot;
    
/**
 * Hook to update the ghost sETHTotalStakedBalance on every change to the mapping sETHStakedBalanceForKnot
 */
hook Sstore sETHStakedBalanceForKnot[KEY bytes32 knot][KEY address account] uint256 newValue (uint256 oldValue) STORAGE {
    sETHTotalStakedBalance = sETHTotalStakedBalance + newValue - oldValue;
    ghostsETHTotalStakeForKnot[knot] = ghostsETHTotalStakeForKnot[knot] + newValue - oldValue;
}



