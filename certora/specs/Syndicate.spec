using MocksETH as sETHToken

methods {
    //// Regular methods
    totalETHReceived() returns (uint256) envfree
    isKnotRegistered(bytes32) returns (bool) envfree

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


/// Corrollary that can be used as requirement after sETH solvency is proven.
function sETHSolvencyCorrollary(address user1, address user2, bytes32 knot) returns bool {
    return sETHStakedBalanceForKnot(knot,user1) + sETHStakedBalanceForKnot(knot,user2) <= sETHTotalStakeForKnot(knot);
}

/**
 * An unregistered knot can not be deregistered.
 */
rule canNotDegisterUnregisteredKnot(method f) filtered {
    f -> notHarnessCall(f)
} {
    bytes32 knot; env e;
    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}

/**
 * Total ETH received must not decrease.
 */
rule totalEthReceivedMonotonicallyIncreases(method f) filtered {
    f -> notHarnessCall(f)
}{
    
    uint256 totalEthReceivedBefore = totalETHReceived();

    env e; calldataarg args;
    f(e, args);

    uint256 totalEthReceivedAfter = totalETHReceived();

    assert totalEthReceivedAfter >= totalEthReceivedBefore, "total ether received must not decrease";
}

/**
 * Address 0 must have zero sETH balance.
 */
invariant addressZeroHasNoBalance()
    sETHToken.balanceOf(0) == 0