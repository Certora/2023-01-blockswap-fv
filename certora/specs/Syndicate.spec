using MocksETH as sETHToken
using MockStakeHouseRegistry as StakeHouseRegistry
using MockStakeHouseUniverse as StakeHouseUniverse
using MockSlotSettlementRegistry as SlotSettlementRegistry

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

///////////// ------------ GHOSTS ------------- and 
///////////// ------------ HOOKS -------------

ghost mathint sum_sETHTotalStakeForKnot {
    init_state axiom sum_sETHTotalStakeForKnot == 0;
}
hook Sstore sETHTotalStakeForKnot[KEY bytes32 blsPubKey] uint256 new_value (uint256 old_value) STORAGE {
    sum_sETHTotalStakeForKnot = sum_sETHTotalStakeForKnot + new_value - old_value;
}

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
 * Ghost 1 to account for the total stake of sETH
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
 * Ghost 2 to account for the total stake of sETH
 */
ghost mathint sETHTotalStakedBalance {
    init_state axiom sETHTotalStakedBalance == 0 ;
}
    
/**
 * Hook to update the ghost sETHTotalStakedBalance on every change to the mapping sETHStakedBalanceForKnot
 */
hook Sstore sETHStakedBalanceForKnot[KEY bytes32 blsPubKey][KEY address account] uint256 newValue (uint256 oldValue) STORAGE {
    sETHTotalStakedBalance = sETHTotalStakedBalance + newValue - oldValue;
}

ghost mapping(bytes32 => uint256) ghostsETHTotalStakeForKnot;

hook Sstore sETHStakedBalanceForKnot[KEY bytes32 knot][KEY address user] uint256 staked (uint256 old_staked) STORAGE {
  ghostsETHTotalStakeForKnot[knot] = ghostsETHTotalStakeForKnot[knot] + staked - old_staked;
}




// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Unit Tests      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * @notice unit test if unstake to 2 address will be done as it should be like inside unstake 1 
 * @param unclaimedETHRecipent ETH recipent 
 * @param knot registered knot for staking
*/
// author: jraynaldi3
rule unstakeSplittedUnitTest(
    address unclaimedETHRecipent,
    bytes32 knot
    ) {
    env e; 

    //precondition 
    address a; address b; uint256 amount_a; uint256 amount_b;
    require amount_a > 0;
    require amount_b > 0;
    require a != b;
    require a != currentContract;
    require b != currentContract;

    //Before
    uint256 aBalanceBefore = sETHToken.balanceOf(a); 
    uint256 bBalanceBefore = sETHToken.balanceOf(b);

    //Function Called
    unstake(e , unclaimedETHRecipent, a, knot, amount_a);
    unstake(e , unclaimedETHRecipent, b, knot, amount_b);

    //After
    uint256 aBalanceAfter = sETHToken.balanceOf(a); 
    uint256 bBalanceAfter = sETHToken.balanceOf(b);

    //Summarized
    uint256 sumLeft = aBalanceBefore + bBalanceBefore + amount_a + amount_b;
    uint256 sumRight = aBalanceAfter + bBalanceAfter;
    //PostCondition
    assert  sumLeft == sumRight, "Unstake return different value";
}

/**
 * Contract seTH Balance should decrease after unstaking
 */
// author: iamckn
rule unstakingShouldDecreaseContractsETH(method f) filtered {
    f -> notHarnessCall(f)
}{
    address unclaimedETHRecipient; address sETHRecipient; bytes32 blsPubKey; uint256 sETHAmount; env e;

    require sETHAmount > 0;
    require sETHRecipient != currentContract;

    uint256 seTHBalanceBefore = sETHToken.balanceOf(currentContract);

    unstake(e, unclaimedETHRecipient, sETHRecipient, blsPubKey, sETHAmount);

    uint256 seTHBalanceAfter = sETHToken.balanceOf(currentContract);

    assert seTHBalanceAfter < seTHBalanceBefore, "Contract seTH Balance should decrease after unstaking";    
}

/**
 * seTH Balance of recipient should increase after unstaking
 */
// author: iamckn
rule seTHBalanceOfSenderIncreasesAfterUnstaking(method f) filtered {
    f -> notHarnessCall(f)
}{
    address unclaimedETHRecipient; address sETHRecipient; bytes32 blsPubKey; uint256 sETHAmount; env e;

    uint256 seTHBalanceBefore = sETHToken.balanceOf(sETHRecipient);

    require sETHAmount > 0;
    require sETHRecipient != currentContract;
    unstake(e, unclaimedETHRecipient, sETHRecipient, blsPubKey, sETHAmount);

    

    assert seTHBalanceAfter > seTHBalanceBefore, "seTH Balance of recipient should increase after unstaking";    
}

/**
 * @notice integrity of Stake
 * should complete these qualification
 * 1. Increase totalFreeFloatingShares by amount staked
 * 2. Increase sETHTotalStakeForKnot by amount staked
 * 3. Increase sETHStakedBalanceForKnot by amount staked
 * 4. Increase sETHUserClaimForKnot 
 * 5. transfer sETH from staker to contract
*/
rule integrityOfStake(
    bytes32 knot, 
    uint256 amount,
    address behalfOf
) {
    // PreCondition
    env e; 
    require amount > 0;
    require e.msg.sender != currentContract;
    // Prevent State Changes because of update
    updateAccruedETHPerShares();

    // Before
    uint256 _totalFreeFloatinShare = totalFreeFloatingShares();
    uint256 _sETHTotalStakeForKnot = sETHTotalStakeForKnot(knot);
    uint256 _sETHStakedBalanceForKnot = sETHStakedBalanceForKnot(knot, behalfOf);
    uint256 _sETHUserClaimForKnot = sETHUserClaimForKnot(knot, behalfOf);
    uint256 stakersETHBalanceBefore = sETHToken.balanceOf(e.msg.sender);
    uint256 contractsETHBalanceBefore = sETHToken.balanceOf(currentContract);

    //Function Called
    stake(e, knot,amount,behalfOf);

    //After
    uint256 totalFreeFloatinShare_ = totalFreeFloatingShares();
    uint256 sETHTotalStakeForKnot_ = sETHTotalStakeForKnot(knot);
    uint256 sETHStakedBalanceForKnot_ = sETHStakedBalanceForKnot(knot, behalfOf);
    uint256 sETHUserClaimForKnot_ = sETHUserClaimForKnot(knot, behalfOf);
    uint256 stakersETHBalanceAfter = sETHToken.balanceOf(e.msg.sender);
    uint256 contractsETHBalanceAfter = sETHToken.balanceOf(currentContract);

    //PostCondition
    assert _totalFreeFloatinShare + amount == totalFreeFloatinShare_, "Miss Calculation totalFreeFloatingShare";
    assert _sETHTotalStakeForKnot + amount == sETHTotalStakeForKnot_, "Miss Calculation sETHTotalStakeForKnot";
    assert _sETHStakedBalanceForKnot + amount == sETHStakedBalanceForKnot_, "Miss Calculation sETHStakedBalanceForKnot";
    assert _sETHUserClaimForKnot > 0 && accumulatedETHPerFreeFloatingShare() >= 10^24 => _sETHUserClaimForKnot < sETHUserClaimForKnot_, "Claim For Knot Reduced";
    assert stakersETHBalanceBefore - amount == stakersETHBalanceAfter && contractsETHBalanceBefore + amount == contractsETHBalanceAfter, "Not Transfered sETH";
}

/**
 * Unstaking accounting invariants:
 * - Must decrease total stake for knot by amount staked
 * - Must decreaase staked balance for msg.sender by amount staked
 */
// author: horsefacts
rule unstakingAccountingInvariants(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e;
    address _unclaimedETHRecipient;
    address _sETHRecipient;
    bytes32 _blsPubKey;
    uint256 _sETHAmount;
    require _sETHAmount > 0;

    uint256 contractBalanceBefore = sETHToken.balanceOf(currentContract);
    uint256 _unclaimedFreeFloatingETHShare = calculateUnclaimedFreeFloatingETHShare(e, knot, e.msg.sender);
    uint256 totalStakeBefore = sETHTotalStakeForKnot(_blsPubKey);
    uint256 stakedBalanceBefore = sETHStakedBalanceForKnot(_blsPubKey, e.msg.sender);
    uint256 sETHBalanceBefore = sETHToken.balanceOf(_sETHRecipient);
    uint256 recipentBalanceBefore = sETHToken.balanceOf(sETHRecipent);

    unstake(e, _unclaimedETHRecipient, _sETHRecipient, _blsPubKey, _sETHAmount);

    uint256 recipentBalanceAfter = sETHToken.balanceOf(sETHRecipent);
    uint256 contractBalanceAfter = sETHToken.balanceOf(currentContract);
    uint256 unclaimedFreeFloatingETHShare_ = calculateUnclaimedFreeFloatingETHShare(e, knot, e.msg.sender);
    uint256 totalStakeAfter = sETHTotalStakeForKnot(_blsPubKey);
    uint256 stakedBalanceAfter = sETHStakedBalanceForKnot(_blsPubKey, e.msg.sender);
    uint256 sETHBalanceAfter = sETHToken.balanceOf(_sETHRecipient);

    assert totalStakeBefore - totalStakeAfter == _sETHAmount, "unstaking must decrease stake for knot by unstaked amount";
    assert stakedBalanceBefore - stakedBalanceAfter == _sETHAmount, "unstaking must decrease staked balance by unstaked amount";
    assert _unclaimedFreeFloatingETHShare > 0 <=> unclaimedFreeFloatingETHShare_ < _unclaimedFreeFloatingETHShare, "Unclaimed ETH not reduced";
    assert (recipentBalanceAfter == recipentBalanceBefore + amount && contractBalanceAfter == contractBalanceBefore - amount, "Failed to Transfer sETH");
}

/**
 * free floating shares are not processed if there are no staked shares
 */
// author: horsefacts
rule freeFloatingShareStateDoesNotChangeWhenNoStakedShares(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; bytes32 _blsPubKey;
    uint256 freeFloatingShares = totalFreeFloatingShares();
    require freeFloatingShares == 0;

    uint256 accumulatedBefore = accumulatedETHPerFreeFloatingShare();
    uint256 lastSeenBefore = calculateETHForFreeFloatingOrCollateralizedHolders(e);

    updateAccruedETHPerShares(e);

    uint256 accumulatedAfter = accumulatedETHPerFreeFloatingShare();
    uint256 lastSeenAfter = calculateETHForFreeFloatingOrCollateralizedHolders(e);


    assert accumulatedBefore == accumulatedAfter, "must not change free floating share state when no shares are staked";
    assert lastSeenBefore == lastSeenAfter, "must not change free floating share state when no shares are staked";
}

/**
 * Registering additional knots should reduce the amount of ETH per collateralized share.
 */
// author: horsefacts
rule registerKnotsDilutesUnprocessedETHForAllCollateralizedSlot(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; bytes32 _blsKey;

    uint256 totalEthReceivedBefore = totalETHReceived();
    // Internal calculation divides totalETHReceived by 2. Ensure ETH balance is more than 4 wei
    // to prevent rounding down to 1 wei in this calculation.
    require totalEthReceivedBefore > 4;

    uint256 lastSeenETHPerCollateralizedSlotPerKnotBefore = lastSeenETHPerCollateralizedSlotPerKnot();
    require lastSeenETHPerCollateralizedSlotPerKnotBefore < totalEthReceivedBefore;

    uint256 allocationBefore = getUnprocessedETHForAllCollateralizedSlot();
    require allocationBefore > 0;

    registerKnotsToSyndicate(e, _blsKey);

    uint256 allocationAfter = getUnprocessedETHForAllCollateralizedSlot();

    assert allocationAfter < allocationBefore, "adding registered knots must dilute share per knot";
}

/* lastAccumulatedETHPerFreeFloatingShare cannot changed once a knot has been deregistered */
// author: coqlover
rule lastAccumulatedETHPerFreeFloatingShareCannotChangeOnceDeregistered(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e;
    calldataarg args;
    bytes32 blsPubKey;
    address staker;
    require isKnotRegistered(blsPubKey);
    require isNoLongerPartOfSyndicate(blsPubKey);
    uint startValue = lastAccumulatedETHPerFreeFloatingShare(blsPubKey);
    f(e, args);
    uint endValue = lastAccumulatedETHPerFreeFloatingShare(blsPubKey);
    assert startValue == endValue, "Value snapshotted when deregistration cannot be changed!";
}


/*
 * When number of knots is > 0 and free floating shares > 0, after calling 
 *  `updateAccruedETHPerShares` the "last seen" values should be same for 
 *  collateralized and free floating.
 */
// author: AbhiGulati
rule ethForSlotTypesIsEqualAfterUpdateAccrued() {
    require numberOfRegisteredKnots() > 0;
    require totalFreeFloatingShares() > 0;

    updateAccruedETHPerShares();

    assert lastSeenETHPerCollateralizedSlotPerKnot() == lastSeenETHPerFreeFloating();
}

/*
 * Amount of ETH received by staker after calling `claimAsStaker` is the same
 *  regardless of whether `updateAccruedETHPerShares` is called immediately
 *  prior.
 */
// author: AbhiGulati
rule claimAsStakerUpdatesAccrued() {
    env e;
    address user;
    bytes32 blsKey1;
    bytes32 blsKey2;

    storage init = lastStorage;

    claimAsStaker(e, user, blsKey1, blsKey2);
    uint userBalance1 = getETHBalance(user);

    updateAccruedETHPerShares() at init;
    claimAsStaker(e, user, blsKey1, blsKey2);
    uint userBalance2 = getETHBalance(user);

    assert userBalance1 == userBalance2;
}

/**
 * deregistering a node reduces totalFreeFloatingShares and numberOfRegisteredKnots
 */
// author: Elpacos
rule deRegisteringUpdatesCountsCorrectly() {
    bytes32 knot; env e;

    uint256 totalFreeFloatingSharesBefore = totalFreeFloatingShares();
    uint256 numberOfRegisteredKnotsBefore = numberOfRegisteredKnots();

    deRegisterKnots(e, knot);
    
    uint256 totalFreeFloatingSharesAfter = totalFreeFloatingShares();
    uint256 numberOfRegisteredKnotsAfter = numberOfRegisteredKnots();

    assert totalFreeFloatingSharesBefore - totalFreeFloatingSharesAfter == sETHTotalStakeForKnot(knot);
    assert numberOfRegisteredKnotsBefore - numberOfRegisteredKnotsAfter == 1;
}

/**
 * Can only stake on active registered KNOTS
 */
// author: Elpacos 
rule onlyRegisteredActiveKnotsCanBeStaked(bytes32 key, address mike, uint256 amount) {
    env e; 

    stake(e, key, amount, mike);

    assert isKnotRegistered(key) && !isNoLongerPartOfSyndicate(key);
}


///  * Cannot unstake more than staked
// author: Elpacos 
rule canNotUnstakeMoreThanStakedMultipleKeys(address unclaimedRecipient, address ethRecipient, bytes32 key1, bytes32 key2, uint256 amount, uint256 amount2) {
    env e;

    uint256 sETHStakedBalanceForKnotBefore1 = sETHStakedBalanceForKnot(key1, e.msg.sender);
    uint256 sETHStakedBalanceForKnotBefore2 = sETHStakedBalanceForKnot(key2, e.msg.sender);

    unstake@withrevert(e, unclaimedRecipient, ethRecipient, key1, key2, amount, amount2);

    assert sETHStakedBalanceForKnotBefore1 < amount => lastReverted;
    assert sETHStakedBalanceForKnotBefore2 < amount2 => lastReverted;
}


/**
 * if a knot is registered, it cannot be marked as not registered.
 */
//author: neomoxx
rule knotRegisteredCannotBeDeregistered(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; bytes32 blsPubKey;

    require isKnotRegistered(blsPubKey);

    calldataarg args;
    f(e, args);

    assert isKnotRegistered(blsPubKey), "Knot should never be marked back as not registered";

}

/*
    A knot that is no longer part of the syndicate can not become part of the syndicate 
*/
// author: jessicapointing
rule noLongerPartOfSyndicateCannotBecomePartOfSyndicate(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    calldataarg args;
    bytes32 blsPubKey;

    bool noLongerPartOfSyndicateBefore = isNoLongerPartOfSyndicate(blsPubKey);
    require noLongerPartOfSyndicateBefore == true;

    f(e, args);

    bool noLongerPartOfSyndicateAfter = isNoLongerPartOfSyndicate(blsPubKey);

    assert noLongerPartOfSyndicateAfter == true;
}

/*
    registerKnotsToSyndicate updates to correct isActive, isNoLongerPartOfSyndicate, and isKnotRegistered states 
*/
// author: jessicapointing
rule registerKnotsToSyndicateUpdatesStates(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    bytes32 blsPubKey1;
    bytes32 blsPubKey2;
    bool noLongerPartOfSyndicateBefore1 = isNoLongerPartOfSyndicate(blsPubKey1);
    bool noLongerPartOfSyndicateBefore2 = isNoLongerPartOfSyndicate(blsPubKey2);
    require noLongerPartOfSyndicateBefore1 == false;
    require noLongerPartOfSyndicateBefore2 == false;
    registerKnotsToSyndicate(e, blsPubKey1, blsPubKey2);
    bool registered1 = isKnotRegistered(blsPubKey1);
    bool registered2 = isKnotRegistered(blsPubKey2);
    bool noLongerPartOfSyndicateAfter1 = isNoLongerPartOfSyndicate(blsPubKey1);
    bool noLongerPartOfSyndicateAfter2 = isNoLongerPartOfSyndicate(blsPubKey2);
    bool active1 = getActivenessOfKnot(e, blsPubKey1);
    bool active2 = getActivenessOfKnot(e, blsPubKey2);

    assert registered1 == true && registered2 == true 
    && noLongerPartOfSyndicateAfter1 == false && noLongerPartOfSyndicateAfter2 == false
    && active1 == true && active2 == true;
}

/*
    deRegisterKnots updates to correct isActive, isNoLongerPartOfSyndicate, and isKnotRegistered states  
*/
// author: jessicapointing
rule deRegisterKnotsUpdatesStates(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    bytes32 blsPubKey1;
    bytes32 blsPubKey2;
    deRegisterKnots(e, blsPubKey1, blsPubKey2);
    bool noLongerPartOfSyndicateAfter1 = isNoLongerPartOfSyndicate(blsPubKey1);
    bool noLongerPartOfSyndicateAfter2 = isNoLongerPartOfSyndicate(blsPubKey2);

    assert noLongerPartOfSyndicateAfter1 == true && noLongerPartOfSyndicateAfter2 == true;
}

/*
    An inactive knot can not register   
*/
// author: jessicapointing
rule inActiveKnotCannotRegister(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    bytes32 blsPubKey;
    require getActivenessOfKnot(e, blsPubKey) == false;
    registerKnotsToSyndicate@withrevert(e, blsPubKey);
    assert lastReverted, "registerKnotsToSyndicate must revert if knot is inactive";
}

/*
 * Staker can not ClaimAsCollateralizedSLOTOwner twice 
 */
// author: jessicapointing
rule cannotClaimAsCollateralizedSLOTOwnerTwice(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    address recipient;
    bytes32 blsPubKey;
    uint256 recipientETHBalanceBefore = getETHBalance(recipient);
    claimAsCollateralizedSLOTOwner(e, recipient, blsPubKey);
    uint256 recipientETHBalanceAfterFirstClaim = getETHBalance(recipient);
    claimAsCollateralizedSLOTOwner(e,recipient,blsPubKey);
    uint256 recipientETHBalanceAfterSecondClaim = getETHBalance(recipient);

    assert recipientETHBalanceAfterFirstClaim >= recipientETHBalanceBefore;
    assert recipientETHBalanceAfterSecondClaim == recipientETHBalanceAfterFirstClaim;
}

/*
 *   Staker can not claim stake twice
 */
// author: jessicapointing
rule cannotClaimAsStakerTwice(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    address recipient;
    bytes32 blsPubKey;
    uint256 recipientETHBalanceBefore = getETHBalance(recipient);
    claimAsStaker(e, recipient, blsPubKey);
    uint256 recipientETHBalanceAfterFirstClaim = getETHBalance(recipient);
    claimAsStaker(e,recipient,blsPubKey);
    uint256 recipientETHBalanceAfterSecondClaim = getETHBalance(recipient);

    assert recipientETHBalanceAfterFirstClaim >= recipientETHBalanceBefore;
    assert recipientETHBalanceAfterSecondClaim == recipientETHBalanceAfterFirstClaim;
}

/**
* can not register already registered knot
*/
// author: JustDravee
rule knotCanNotBeRegisteredIfHasNoOwners()
{
    env e;
    bytes32 knot;
    require SlotSettlementRegistry.numberOfCollateralisedSlotOwnersForKnot(e,knot) == 0;
    
    registerKnotsToSyndicate@withrevert(e,knot);
    bool reverted = lastReverted;

    assert reverted, "Knot was registered with no SLOT owners";
}


/**
* numberOfRegisteredKnots holds upon register and deregieter
*/
// author: JustDravee
rule numberOfRegisteredKnotsHolds(bytes32 knot)
{
    env e;
    
    uint256 registeredKnotsBefore = numberOfRegisteredKnots();

    registerKnotsToSyndicate(e,knot);
    deRegisterKnots(e,knot);

    uint256 registeredKnotsAfter = numberOfRegisteredKnots();

    assert registeredKnotsBefore == registeredKnotsAfter, "numberOfRegisteredKnots doesn't hold as expected";

}

/**
* can not register inactive knot
*/
// author: JustDravee
rule inactiveKnotCanNotBeRegistered()
{
    env e;
    bytes32 knot;
    require !StakeHouseRegistry.active(knot);

    registerKnotsToSyndicate@withrevert(e,knot);
    bool reverted = lastReverted;

    assert reverted, "Inactive knot was registered";
}

/**
* When staking block is in future, only those listed in the priority staker list can stake sETH
*/
// author: koolexcrypto
rule onlyPriorityStakerStake()
{
    
    env e;
    bytes32 knot;
    address priorityStaker;
    address normalStaker;
    uint256 amount;

    require priorityStakingEndBlock() > e.block.number;
    require !isPriorityStaker(normalStaker);
    require e.msg.value == 0;

    stake@withrevert(e,knot,amount,priorityStaker);
    bool priorityReverted = lastReverted;
    stake@withrevert(e,knot,amount,normalStaker);
    bool normalReverted = lastReverted;

    assert normalReverted, "stake must revert if block in future and staker is not priority";
    assert !priorityReverted => isPriorityStaker(priorityStaker), "stake not reverting must mean staker is not priority";
}

/**
* Staker gets exactly the same sETH token amount upon stake and unstake.
*/
// author: koolexcrypto
rule StakerReceivesExactsETH(bytes32 blsPubKey,address staker,uint256 amount)
{
    env e;
    require e.msg.sender == staker;
    require sETHToken.balanceOf(staker) == amount;

    stake(e,blsPubKey,amount,staker);
    unstake(e,staker,staker,blsPubKey,amount);

    assert sETHToken.balanceOf(staker) == amount, "Staker got more/less sETH";

}

/**
 * unclaimed User Share must be zero after claiming as a staker.
 */
// author: koolexcrypto
rule zeroUnclaimedUserShareAfterClaiming()
{
    
    env e;
    bytes32 knot;
    uint256 amount;
    
    // Safe Assumptions
    require e.msg.sender != 0;
    require e.msg.sender != currentContract;
    require e.msg.value == 0;

    uint256 unclaimed = calculateUnclaimedFreeFloatingETHShare(e,knot, e.msg.sender);

    claimAsStaker(e,e.msg.sender,knot);

    uint256 unclaimedAfter = calculateUnclaimedFreeFloatingETHShare(e,knot, e.msg.sender);

    assert unclaimed > 0 => unclaimedAfter == 0 ,"Unclaimed User Share is not zero after claiming";
}

/**
 * Others cannot claim my rewards
 */
 rule othersCannotClaimMyRewards() {
    env e;
    address me;
    bytes32 key;
    // Assume the actor and the me address are distinct
    require e.msg.sender != me;
    require e.msg.sender != currentContract;
    require me != currentContract;

    uint256 unclaimedUserShareBefore = calculateUnclaimedFreeFloatingETHShare(key, me);

    claimAsStaker(e, me, key);

    uint256 unclaimedUserShareAfter = calculateUnclaimedFreeFloatingETHShare(key, me);

    assert unclaimedUserShareAfter >= unclaimedUserShareBefore, "Others cannot claim my rewards";
 }

/**
 * unstake: after execution, ETH balance of recipient varies by the same amount as totalClaimed.
 */
// author: neomoxx
rule unstakePostBalances() {

    env e;

    address recipient;
    address sETHRecipient;
    bytes32 blsPubKey;
    uint256 sETHAmount;

    uint256 recipientBalanceBefore = getETHBalance(recipient);
    uint256 totalClaimedBefore = totalClaimed();

    require numberOfRegisteredKnots() > 0;

    unstake(e, recipient, sETHRecipient, blsPubKey, sETHAmount);

    assert totalClaimed() - totalClaimedBefore == getETHBalance(recipient) - recipientBalanceBefore, "ETH balance of recipient after unstake is wrong";
    
}

/*
 * A successful call to `unstake` in which the caller requests a positive amount
 *  should result in an increase to the recipient's ETH balance.
 * Note: This rule fails when bug1.patch is applied
 */ 
// author: AbhiGulanti
rule unstakingIncreasesSETHAmount() {
    env e;
    address _unclaimedETHRecipient; address _sETHRecipient;
    bytes32 blsKey; uint256 sETHAmount;

    require sETHAmount > 0;
    require _sETHRecipient != currentContract;

    uint _sETHBalance = sETHToken.balanceOf(_sETHRecipient);

    unstake(e, _unclaimedETHRecipient, _sETHRecipient, blsKey, sETHAmount);

    uint sETHBalance_ = sETHToken.balanceOf(_sETHRecipient);

    assert sETHBalance_ > _sETHBalance;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Parametric Rules      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * change in isRegistered implies change in numberOfRegisteredKnots
 */
// author: rechlis
rule isRegisteredVsNumberofRegistered(method f, env e, bytes32 knot)filtered {
    f -> notHarnessCall(f)}{

    bool isRegisteredBefore = isKnotRegistered(knot);
    uint RegisteredKnotsBefore = numberOfRegisteredKnots(e);

    calldataarg args;
    f(e,args);

    assert isRegisteredBefore != isKnotRegistered(knot) => RegisteredKnotsBefore != numberOfRegisteredKnots(e);
}
/**
 * lastSeenETHPerFreeFloating is monotonic
 */
// author: rechlis
rule lastSeenETH(method f) filtered {
    f -> notHarnessCall(f)}{
    env e;

    uint lastSeebEthBefore = lastSeenETHPerFreeFloating(e);

    calldataarg args;
    f(e,args);

    assert lastSeenETHPerFreeFloating(e) >= lastSeebEthBefore;
}

/**
 * @notice if condition is fullfilled total ETH in either collateral slot or free floating slot should same
 * condition: totalFreeFloatingShares > 0
*/
// author: jraynaldi3
rule totalETHPerSlotShouldSame(method f) filtered {
    f-> notHarnessCall(f)
} {
    env e; calldataarg args;
    updateAccruedETHPerShares();
    uint256 total = totalFreeFloatingShares();
    if total == 0 {
        require lastSeenETHPerFreeFloating() == 0;
    }
    require numberOfRegisteredKnots() > 0;
    require totalFreeFloatingShares() > 0 => lastSeenETHPerCollateralizedSlotPerKnot() == lastSeenETHPerFreeFloating();

    f(e, args);

    updateAccruedETHPerShares();

    assert totalFreeFloatingShares() > 0 => lastSeenETHPerCollateralizedSlotPerKnot() == lastSeenETHPerFreeFloating();
}

// But no more than 1?
// author: coqlover
rule imprecisionIsBounded(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e;
    calldataarg args;
    bytes32 blsPubKey;
    address staker;
    require isKnotRegistered(blsPubKey);
    require isNoLongerPartOfSyndicate(blsPubKey);
    requireInvariant lastAccumulatedETHPerFreeFloatingShare_is_not_0_when_deregistered(blsPubKey);
    updateAccruedETHPerShares(e);
    uint256 a = sETHUserClaimForKnot(blsPubKey, staker);
    uint256 b = (lastAccumulatedETHPerFreeFloatingShare(blsPubKey) * sETHStakedBalanceForKnot(blsPubKey, staker)) / PRECISION();
    require ((a-b <= 1) && (b-a <= 1));
    f(e, args);
    assert ((a-b <= 1) && (b-a <= 1)),
    "Impression cannot be more than 1?";
}

/**
 * Can always unstake after staking
 */
// author: carrotsmuggler
rule canAlwaysUnstakeAfterStake (method f) filtered {
    f -> notHarnessCall(f)
}{
    address user; env e; calldataarg args; env x;
    bytes32 blspubkey; uint256 sethAmount;

    require(e.msg.sender != x.msg.sender);
    require sETHSolvencyCorrollary(e.msg.sender,x.msg.sender,blspubkey);

    stake(e, blspubkey, sethAmount, e.msg.sender);
    f(x, args);
    uint256 totalsETHBefore = sETHToken.balanceOf(e.msg.sender);
    unstake(e, e.msg.sender, e.msg.sender, blspubkey, sethAmount);
    uint256 totalsETHAfter = sETHToken.balanceOf(e.msg.sender);

    assert  totalsETHAfter == totalsETHBefore + sethAmount, "Should always be able to unstake after stake";
}

/**
* These public variables and functions() must allways increase
*
* accumulatedETHPerFreeFloatingShare
* accumulatedETHPerCollateralizedSlotPerKnot
¨* lastSeenETHPerCollateralizedSlotPerKnot
* lastSeenETHPerFreeFloating
*¨ totalClaimed
*
* totalETHReceived()
* calculateETHForFreeFloatingOrCollateralizedHolders()
*/
// author: zapaz
rule increasesAll(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args; bytes32 blsPubKey; address addr;

    mathint amount1Before = accumulatedETHPerFreeFloatingShare();
    mathint amount2Before = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3Before = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount4Before = lastSeenETHPerFreeFloating();
    mathint amount5Before = totalClaimed();
    mathint amount6Before = totalETHReceived();
    mathint amount7Before = calculateETHForFreeFloatingOrCollateralizedHolders();
    mathint amount8Before = accruedEarningPerCollateralizedSlotOwnerOfKnot(blsPubKey, addr);

    f(e, args);

    mathint amount1After  = accumulatedETHPerFreeFloatingShare();
    mathint amount2After  = accumulatedETHPerCollateralizedSlotPerKnot();
    mathint amount3After  = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint amount4After  = lastSeenETHPerFreeFloating();
    mathint amount5After  = totalClaimed();
    mathint amount6After  = totalETHReceived();
    mathint amount7After  = calculateETHForFreeFloatingOrCollateralizedHolders();
    mathint amount8After  = accruedEarningPerCollateralizedSlotOwnerOfKnot(blsPubKey, addr);

    assert amount1After  >= amount1Before;
    assert amount2After  >= amount2Before;
    assert amount3After  >= amount3Before;
    assert amount4After  >= amount4Before;
    assert amount5After  >= amount5Before;
    assert amount6After  >= amount6Before;
    assert amount7After  >= amount7Before;
    assert amount8After  >= amount8Before;
}

/*
 * An inactive knot can not become active
 */
// author: jessicapointing
rule inactiveKnotCannotBecomeActive(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    calldataarg args;
    bytes32 blsPubKey;

    bool isActiveBefore = getActivenessOfKnot(e, blsPubKey);
    require isActiveBefore == false;

    f(e, args);

    bool isActiveAfter = getActivenessOfKnot(e, blsPubKey);

    assert isActiveAfter == false;          
}



/**
* Staker invariants (e.g.sETHUserClaimForKnot and sETHStakedBalanceForKnot ) must never decrease via any action taken by another actor.
*/
rule stakerInvariantsMustNeverDecrease(method f,bytes32 knot,address staker) filtered {
    f -> notHarnessCall(f)
}{
    env e;
    require e.msg.sender != staker;

    uint256 sETHUserClaimForKnot = sETHUserClaimForKnot(knot,staker);
    uint256 sETHStakedBalanceForKnot = sETHStakedBalanceForKnot(knot,staker);

    calldataarg args;
    f(e, args);

    uint256 sETHUserClaimForKnotAfter = sETHUserClaimForKnot(knot,staker);
    uint256 sETHStakedBalanceForKnotAfter = sETHStakedBalanceForKnot(knot,staker);

    assert sETHUserClaimForKnot <= sETHUserClaimForKnotAfter, "sETHUserClaimForKnot doesn't hold as expected";
    assert sETHStakedBalanceForKnot <= sETHStakedBalanceForKnotAfter, "sETHStakedBalanceForKnot doesn't hold as expected";

}

/**
 * Others can only increase my balance
 */
// author: Elpacos
 rule othersCanOnlyIncreaseMyBalance(method f) {
    env e; calldataarg args;
    address me;
    // Assume the actor and the me address are distinct
    require e.msg.sender != me;
    // Assume the actor and the current contract are distinct
    require e.msg.sender != currentContract;

    // Assume the me address and the current contract are distinct
    require me != currentContract;

    uint256 balanceBefore = sETHToken.balanceOf(me);
    f(e, args);
    uint256 balanceAfter = sETHToken.balanceOf(me);

    assert balanceAfter >= balanceBefore, "others can only increase my balance";

 }

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Invariants      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * last seen is GE than accumulated 
 */
// author: rechlis
invariant lastseenVsAccumulated(env e)
    lastSeenETHPerCollateralizedSlotPerKnot(e) >= accumulatedETHPerCollateralizedSlotPerKnot(e)
filtered { f -> notHarnessCall(f) }

/**
 * knot not registered implies all its monitored velues should be zero
 */
// author: rechlis
invariant knotNotRegistered(method f, env e, bytes32 knot, address user)
    !isKnotRegistered(knot) => 
            sETHTotalStakeForKnot(knot) == 0                &&
            sETHStakedBalanceForKnot(knot, user) == 0       &&
            sETHUserClaimForKnot(e, knot, user) == 0        &&
            claimedPerCollateralizedSlotOwnerOfKnot(e, knot, user) == 0
filtered { f -> notHarnessCall(f) }

/**
 * totalClaimed GE knot claimed
 */
// author: rechlis
invariant claimedPerCollateralizedVsTotal(method f, env e, bytes32 knot, address user)
    claimedPerCollateralizedSlotOwnerOfKnot(e, knot, user) <= totalClaimed(e)
    filtered { f -> notHarnessCall(f) }

/**
 * Knots should not have more than 12 ether staked. (not needed, leaving for learning experience --- Using ghost function to bind knot stake to a previously valid state).
 */
// author: pvgo80
invariant knotsMustNotHaveMoreThanTwelveETHStakedInvariant(bytes32 knot)
    12 * 10^18 >= sETHTotalStakeForKnot(knot)

/**
 * 12 = sum_of_all_knot_users. Requiring a valid state before checking the invariant.
 */
// author: pvgo80
invariant usersShouldNotHaveMoreThanTwelveEthPerKnotInvariant(bytes32 knot, address user)
    12 * 10^18 >= sETHStakedBalanceForKnot(knot, user)
    {
        preserved with (env e){
            require sETHStakedBalanceForKnot(knot, user) <= sETHTotalStakeForKnot(knot);
        }
    }

/**
 * @notice if total free floating share is 0 then all sETH staked balance must be 0 too
 * @note Not using ghost or hook, instead in some spesific function call I define an preserved expressions
*/
// author: jraynaldi3
invariant sameZeroTotalAndIndividualFreeFloatingShares(bytes32 knot, address user) 
    totalFreeFloatingShares() == 0 => sETHStakedBalanceForKnot(knot, user) == 0
    filtered {
        f-> onlyHarnessCall(f)
    } 
    {
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2, bytes32 knot3) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved deRegisterKnots( bytes32 knot2) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved deRegisterKnots(bytes32 knot2, bytes32 knot3) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved claimAsCollateralizedSLOTOwner( address _addr, bytes32 knot2) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved claimAsCollateralizedSLOTOwner(address _addr, bytes32 knot2, bytes32 knot3) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        
        preserved unstake(address recipent1,address recipent2,bytes32 knot2 ,uint256 amount) with (env e2) {
            require amount + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved unstake(address recipent1 ,address recipent2 ,bytes32 knot2,bytes32 knot3 ,uint256 amount1 ,uint256 amount2) with (env e2) {
            require amount1 + amount2 + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
    }

/**
 * @notice if theres any knot registered then numberOfRegisteredKnot should greater than zero 
 * @note Not using ghost or hook, instead in some spesific function call I define an preserved expressions
*/
// author: jraynaldi3
invariant numberOfRegisteredKnotCorellation(bytes32 knot)
    knotRegistered(knot) => numberOfRegisteredKnots() > 0
    filtered {
        f-> onlyHarnessCall(f)
    } 
    {
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2) with (env e2){
            require knot2 != knot => numberOfRegisteredKnots() > 1;
        }
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2, bytes32 knot3) with (env e2){
            require knot2 != knot || knot3 != knot => numberOfRegisteredKnots() > 2;
        }
        preserved deRegisterKnots( bytes32 knot2) with (env e2){
            require knot2 != knot => numberOfRegisteredKnots() > 1;
        }
        preserved deRegisterKnots(bytes32 knot2, bytes32 knot3) with (env e2) {
            require knot2 != knot || knot3 != knot => numberOfRegisteredKnots() > 2;
        }
        preserved claimAsCollateralizedSLOTOwner( address _addr, bytes32 knot2) with (env e2) {
            require knot2 != knot => numberOfRegisteredKnots() > 1;
        }
        preserved claimAsCollateralizedSLOTOwner(address _addr, bytes32 knot2, bytes32 knot3) with (env e2) {
            require knot2 != knot || knot3 != knot => numberOfRegisteredKnots() > 2;
        }      
    }

/**
 * @notice free floating balance of individual staker should less than total staked balance 
 * @note Not using ghost or hook, instead in some spesific function call I define an preserved expressions
*/
// author: jraynaldi3
invariant individualLessThanTotalFreeFloatingShares(bytes32 knot, address user)
    sETHStakedBalanceForKnot(knot, user) <= totalFreeFloatingShares()
    filtered {
        f-> onlyHarnessCall(f)
    } 
        {
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved batchUpdateCollateralizedSlotOwnersAccruedETH(bytes32 knot2, bytes32 knot3) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved deRegisterKnots( bytes32 knot2) with (env e2){
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved deRegisterKnots(bytes32 knot2, bytes32 knot3) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved claimAsCollateralizedSLOTOwner( address _addr, bytes32 knot2) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved claimAsCollateralizedSLOTOwner(address _addr, bytes32 knot2, bytes32 knot3) with (env e2) {
            require sETHTotalStakeForKnot(knot2) + sETHTotalStakeForKnot(knot3) + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        
        preserved unstake(address recipent1,address recipent2,bytes32 knot2 ,uint256 amount) with (env e2) {
            require amount + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
        preserved unstake(address recipent1 ,address recipent2 ,bytes32 knot2,bytes32 knot3 ,uint256 amount1 ,uint256 amount2) with (env e2) {
            require amount1 + amount2 + sETHStakedBalanceForKnot(knot, user) < totalFreeFloatingShares();
        }
    }

/* The balance of the contract is always above what is kept track of */
// author: coqlover
invariant sETHSolvency()
    sETHToken.balanceOf(currentContract) >= sum_sETHTotalStakeForKnot
    { preserved with (env e) { require e.msg.sender != currentContract; } }

/// lastAccumulatedETHPerFreeFloatingShare should only be nonzero if knot is deregistered
// author: zapaz
invariant lastAccumulatedIsNoLongerSyndicated(bytes32 k)
  lastAccumulatedETHPerFreeFloatingShare(k) > 0 => isNoLongerPartOfSyndicate(k)
    filtered { f -> notHarnessCall(f) }

/**
 * Check Sum of two balances is allways less than Total :
 * Given one user, for any other random user making whatever calls,
 * their combined sETH balances stays less than Total
 */
// author: zapaz
invariant sETHSolvencyCorrollary(address user, address random, bytes32 knot)
    random != user => sETHStakedBalanceForKnot(knot, user) +
                      sETHStakedBalanceForKnot(knot, random) <= sETHTotalStakeForKnot(knot)
    filtered { f -> notHarnessCall(f) }
    {
        preserved with(env e) {
            require e.msg.sender == random;
        }
    }

/**
* Check that for any Knot and User, Zero Staked amount implies Zero Claim amount
*/
// author: zapaz
invariant sETHBalanceZeroThenClaimAlso(bytes32 k, address addr)
    sETHStakedBalanceForKnot(k, addr) == 0 => sETHUserClaimForKnot(k,addr) == 0
    filtered { f -> notHarnessCall(f) }

/**
 * numberOfRegisteredKnots must be equal to the number of registered Knots minus those registered who are no longer part of the Syndicated
 */
// author: zapaz
invariant knotsSyndicatedCount()
    numberOfRegisteredKnots() == ghostKnotsRegisteredCount() - ghostKnotsNotSyndicatedCount()
    filtered { f -> notHarnessCall(f) }

/*
 *  A KNOT which has not yet been deRegistered will not have a value 
 *   set for lastAccumulatedETHPerFreeFloatingShare
 */ 
// author: AbhiGulati
invariant notDeregisteredKnotHasNoLastAccumulatedETHPerFreeFloatingShare(bytes32 blsKey)
    !isNoLongerPartOfSyndicate(blsKey) => lastAccumulatedETHPerFreeFloatingShare(blsKey) == 0

/*
 *  The lastAccumulatedETHPerFreeFloatingShare for any KNOT is always less than
 *   the global accumulatedETHPerFreeFloatingShare
 */
// author: AbhiGulati
invariant accumulatedETHPerFreeFloatingShare_gt_lastAccumulatedETHPerFreeFloatingShare(bytes32 blsKey)
    lastAccumulatedETHPerFreeFloatingShare(blsKey) <= accumulatedETHPerFreeFloatingShare()

/*
 * Sum of stakes for all stakers in KNOT equals `sETHTotalStakeForKnot`
 */
// author: AbhiGulati
invariant totalStakeForKnotEqualsSumOfStakesBalances(bytes32 blsKey)
    sumOfStakesForKnot[blsKey] == sETHTotalStakeForKnot(blsKey)

/**
 * totalETHProcessedPerCollateralizedKnot always less than or equal than accumulatedETHPerCollateralizedSlotPerKnot.
 */
// author: neomoxx
invariant accumulatedETHPerCollateralizedSlotPerKnotGTEtotalETHProcessedPerCollateralizedKnot(bytes32 blsPubKey)
    totalETHProcessedPerCollateralizedKnot(blsPubKey) <= accumulatedETHPerCollateralizedSlotPerKnot()

/**
 * sETHTotalStake and sETHTotalStakedBalance must match.
 */
// author: neomoxx
invariant sETHTotalStakeGhostsMatch()
    sETHTotalStake == sETHTotalStakedBalance

/**
 * calculateETHForFreeFloatingOrCollateralizedHolders must be always greater or equal than lastSeenETHPerCollateralizedSlotPerKnot.
 */
// author: neomoxx, edited
invariant calculatedETHGTElastSeenETHPerCollateralizedSlotPerKnot()
    calculateETHForFreeFloatingOrCollateralizedHolders() => lastSeenETHPerCollateralizedSlotPerKnot()
    filtered { f -> notHarnessCall(f) }

invariant calculatedETHGTElastSeenETHPerFreeFloating()
    calculateETHForFreeFloatingOrCollateralizedHolders() => lastSeenETHPerFreeFloating()
    filtered { f -> notHarnessCall(f) }

/**
 * If knot is no longer part of syndicate, it must be registered
 */
// author: neomoxx
invariant noLongerPartOfSyndicateImpliesRegistered(bytes32 blsPubKey)
    isNoLongerPartOfSyndicate(blsPubKey) => isKnotRegistered(blsPubKey)
    filtered { f -> notHarnessCall(f) }

/**
 * Can't stake on behalf of Address 0
 */
invariant noStakeOnBehalfOfAddressZero(bytes32 _blsPubKey)
    sETHStakedBalanceForKnot(_blsPubKey, 0) == 0
    filtered { f -> notHarnessCall(f) }

/**
* validate sETHStakedBalanceForKnot is updated when sETHStakedBalanceForKnot gets updated for a user
**/
invariant sETHStakedBalanceForKnotInvariant()
    sETHTotalStakeForKnot(knot) == ghostsETHTotalStakeForKnot[knot]
    filtered { f -> notHarnessCall(f) }

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Live Bug Catching Rules      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 *  After any function call, if a knot is deregistered it should be stored in lastAccumulatedETHPerFreeFloatingShare the last accumulatedETHPerFreeFloatingShare
 */
// author: neomoxx
rule lastAccumulatedETHPerFreeFloatingShareMustAccountForAccruedETH(method f) filtered {
    f -> notHarnessCall(f)
}{

    env e;

    bytes32 blsPubKey;

    require isKnotRegistered(blsPubKey);
    require !isNoLongerPartOfSyndicate(blsPubKey);
    require lastAccumulatedETHPerFreeFloatingShare(blsPubKey) == 0;

    calldataarg args;
    f(e, args);

    require isNoLongerPartOfSyndicate(blsPubKey);

    updateAccruedETHPerShares(e);

    assert lastAccumulatedETHPerFreeFloatingShare(blsPubKey) == accumulatedETHPerFreeFloatingShare(), "Knot deregistered, but lastAccumulatedETHPerFreeFloatingShare has a wrong value";

}

/// Cannot stake if knot is inactive
// author: jessicapointing
rule cannotStakeIfKnotIsInactive(method f) filtered {
    f -> notHarnessCall(f)
} {
    bytes32 blsPubKey; 
    uint256 sETHAmount;
    address onBehalfOf;
    env e;

    require getActivenessOfKnot(e,blsPubKey) == false;

    stake@withrevert(e, blsPubKey, sETHAmount, onBehalfOf);

    assert lastReverted, "stake must revert if knot is inactive";
}

/// An inactive knot should no longer be part of the syndicate
// author: jessicapointing
rule inactiveKnotShouldNoLongerBePartOfSyndicate(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    calldataarg args;
    bytes32 blsPubKey;
    uint256 sETHAmount;
    address onBehalfOf;

    bool getActivenessOfKnotBefore = getActivenessOfKnot(e, blsPubKey);
    bool noLongerPartOfSyndicateBefore = isNoLongerPartOfSyndicate(blsPubKey);
    bool registeredBefore = isKnotRegistered(blsPubKey);
    require getActivenessOfKnotBefore == false;
    require noLongerPartOfSyndicateBefore == false;
    require registeredBefore == true;

    stake(e, blsPubKey, sETHAmount, onBehalfOf);

    bool getActivenessOfKnotAfter = getActivenessOfKnot(e, blsPubKey);
    bool noLongerPartOfSyndicateAfter = isNoLongerPartOfSyndicate(blsPubKey);

    assert noLongerPartOfSyndicateAfter == true;
}

/// This checks that adding two address as priority stakers shouldn't revert,
/// regardless of the fact that address1 is greater or lesser than address2.
// author: JustDravee
rule addingTwoDifferentPriorityStackers(address _priorityStaker1, address _priorityStaker2) {
    // Excluding address(0)
    require(_priorityStaker1 != 0 && _priorityStaker2 != 0);
    // Avoiding duplicates and making sure the address at index i - 1 is greater than the address at index i
    require(_priorityStaker1 > _priorityStaker2);
    // Making sure they aren't already Priority Stakers
    require(!isPriorityStaker(_priorityStaker1) && !isPriorityStaker(_priorityStaker2));
    env e;

    // Adding any 2 Priority stakers address
    addPriorityStakers@withrevert(e, _priorityStaker1, _priorityStaker2);
    // The rule will fail due to this assertion being unreachable with the bug
    assert(true, "This is unreacheable");
}

/// When the liquid staking manager (Syndicate owner) calls deRegisterKnots to 
/// deregister a knot, and if the knot is inactive, the function will always 
/// revert.
// author: koolexcrypto
rule deregisterInactiveKnotShouldSucceed()
{
    env e;
    bytes32 knot;
    
    require e.msg.sender == owner();
    require e.msg.value == 0;
    // safe assumptions 
    require StakeHouseUniverse.memberKnotToStakeHouse(knot) != 0;
    require isKnotRegistered(knot);
    require !isNoLongerPartOfSyndicate(knot);
    require accumulatedETHPerCollateralizedSlotPerKnot() == 0;
    require totalETHProcessedPerCollateralizedKnot(knot) == 0;
    require totalFreeFloatingShares() == 0;
    require sETHTotalStakeForKnot(knot) == 0;
    require lastSeenETHPerCollateralizedSlotPerKnot() == 0;
    require totalClaimed() == 0;
    require getEthBalance(currentContract) == 0;
    require numberOfRegisteredKnots() == 1; 

    deRegisterKnots@withrevert(e,knot);
    bool reverted = lastReverted;

    assert !StakeHouseRegistry.active(knot) => !reverted;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Injected Bug Catching Rules      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug0      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/// sETHUserClaimForKnot does not decrease if `unstake` was not called. 
// author: jessicapointing
rule sETHUserClaimForKnotDoesNotDecrease(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    calldataarg args;
    address onBehalfOf;
    bytes32 blsPubKey;
    uint256 sETHBefore = sETHUserClaimForKnot(blsPubKey,onBehalfOf);
    f(e, args);
    uint256 sETHAfter = sETHUserClaimForKnot(blsPubKey, onBehalfOf);
    assert f.selector != unstake(address,address,bytes32[],uint256[]).selector
        => sETHAfter >= sETHBefore;
}

/// Functions that should update accrued ETH per shares must update it.
// author: Elpacos
rule lastSeenETHUpdated(method f) filtered {
    f -> f.selector == updateAccruedETHPerShares().selector || 
        f.selector == addPriorityStakers(address).selector ||
        f.selector == updatePriorityStakingBlock(uint256).selector ||
        f.selector == updateAccruedETHPerShares().selector ||
        f.selector == unstake(address,address,bytes32,uint256).selector ||
        f.selector == claimAsCollateralizedSLOTOwner(address,bytes32).selector ||
        f.selector == claimAsStaker(address,bytes32).selector 
} {
    env e; calldataarg args;

    f(e, args);

    assert numberOfRegisteredKnots() > 0 => lastSeenETHPerCollateralizedSlotPerKnot() == totalETHReceived() / 2, "last seen ETH per collateralized slot per knot must be updated";
    assert totalFreeFloatingShares() > 0 && numberOfRegisteredKnots() > 0 => lastSeenETHPerFreeFloating() == totalETHReceived() / 2, "last seen ETH per free floating share must be updated";
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug1      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/*
 * calculateUnclaimedFreeFloatingETHShare returns zero if staked balance is less than minimum amount
 */
// author: jessicapointing
rule calculateUnclaimedFreeFloatingETHShareReturnsZeroIfStakedBalanceLessThanMin(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    address user;
    bytes32 blsPubKey;
    uint256 minAmount = 10^9;
    require e.msg.value == 0;

    require sETHStakedBalanceForKnot(blsPubKey, user) < minAmount;
    uint256 unclaimedETH = calculateUnclaimedFreeFloatingETHShare@withrevert(e, blsPubKey, user);
    assert unclaimedETH == 0;
}

/// Untstake reverts when transfer fails (in this case because the sETH balance 
/// of the current contract is less than the sETH amount)
// author: jessicapointing
rule unstakeRevertsWhenTransferFails(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;

    address unclaimedETHRecipient;
    address sETHRecipient;
    bytes32 blsPubKey;
    uint256 sETHAmount;

    require sETHToken.balanceOf(currentContract) < sETHAmount;

    unstake@withrevert(e, unclaimedETHRecipient,sETHRecipient,blsPubKey,sETHAmount);

    assert lastReverted, "unstake must revert if transfer fails (in this case because the sETH balance is less than the sETH amount)";
}

/// @notice If the syndicate contract does not have enough sETH balance unstake() should revert
// author: 8ahoz
rule UnstakeRevertsWithInsufficientSETHBalance(env e, bytes32 knot, uint256 amount){

    require sETHToken.balanceOf(currentContract) < amount;

    unstake@withrevert(e, e.msg.sender, e.msg.sender, knot, amount);
    
    assert lastReverted, "unstake() does not revert as it should"; 

}

/// Unstaking should increase the Recipient's balance and decrease the total 
/// amount of free floating sETH staked
// author: JustDravee
rule integrityOfUnstake (
        address _unclaimedETHRecipient,
        address _sETHRecipient,
        bytes32 _blsPubKey,
        uint256 _sETHAmount) {
	env e;

    require(_sETHRecipient != currentContract);
    uint256 balanceBefore = sETHToken.balanceOf(_sETHRecipient);

    unstake(e, _unclaimedETHRecipient,
        _sETHRecipient,
        _blsPubKey,
        _sETHAmount
        );

    uint256 balanceAfter = sETHToken.balanceOf(_sETHRecipient);
    uint256 calculatedBalanceAfter = balanceBefore + _sETHAmount;
    assert balanceAfter == calculatedBalanceAfter, "Recipient's sETH did not increase";
}

/// Staker receives sETH token upon unstake.
// author: koolexcrypto
rule receivesETHOnUnstake()
{
    
    env e;
    bytes32 knot;
    address staker;
    uint256 amount;

    require e.msg.sender == staker;
    require e.msg.value == 0;

    uint256 amountBefore = sETHToken.balanceOf(staker);

    unstake(e,staker,staker,knot,amount);

    uint256 amountAfter = sETHToken.balanceOf(staker);

    assert amountAfter == amountBefore + amount, "Staker didn't receive the expected sETH";
}

/// revert if transferring sETH token fails upon unstake.
// author: koolexcrypto
rule revertIfsETHTransferFailOnUnstake()
{
    
    env e;
    bytes32 knot;
    uint256 amount;

    // Safe assumptions
    require e.msg.sender != 0;
    require currentContract != 0;
    require e.msg.sender != currentContract;
    require e.msg.value == 0;
    require sETHStakedBalanceForKnot(knot,e.msg.sender) >= amount;
    // This condition just to cause transfer failure 
    require sETHToken.balanceOf(currentContract) < amount;

    uint256 stakerBalanceBefore = sETHToken.balanceOf(e.msg.sender);
    uint256 contractBalanceBefore = sETHToken.balanceOf(currentContract);

    unstake@withrevert(e,e.msg.sender,e.msg.sender,knot,amount);
    bool reverted = lastReverted;

    assert sETHToken.balanceOf(e.msg.sender) != stakerBalanceBefore + amount => reverted , "unstake didn't revert on failed transfer";
    assert sETHToken.balanceOf(currentContract) != contractBalanceBefore - amount => reverted , "unstake didn't revert on failed transfer";

}
 
/// Unstake with an amount greater than the contract's ETH balance will revert 
/// (this rule should be violated when bug 1 is inserted)
// author: Elpacos
rule unstakeWithAmountGreaterThanContractBalanceReverts(address unclaimedRecipient, address ethRecipient, bytes32 key, uint256 amount) {
    env e;

    uint256 balanceBefore = sETHToken.balanceOf(currentContract);

    unstake@withrevert(e, unclaimedRecipient, ethRecipient, key, amount);

    assert balanceBefore < amount => lastReverted;
}

/// Correct amount is transferred to the ethRecipient after unstaking.
// author: Elpacos
rule correctAmountTransferredAfterUnstaking(address unclaimedRecipient, address ethRecipient, bytes32 key, uint256 amount) {
    env e;
    // Syndicate contract cannot call himself
    require currentContract != e.msg.sender;
    require currentContract != ethRecipient;


    uint256 balanceBefore = sETHToken.balanceOf(ethRecipient);
     uint256 balanceSyndicateBefore = sETHToken.balanceOf(currentContract);

    unstake(e, unclaimedRecipient, ethRecipient, key, amount);

    assert sETHToken.balanceOf(ethRecipient) == balanceBefore + amount;
    assert sETHToken.balanceOf(currentContract) == balanceSyndicateBefore - amount;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug2      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
 
/// totalFreeFloatingShares counts non deregistered knots only
// author: koolexcrypto
rule totalFreeFloatingSharesCountNonDeregisteredKnotsOnly()
{
    
    env e;
    bytes32 knot;
    address staker; 
    uint256 amount;
    require amount > 0;
    
    uint256 totalFreeFloatingShares = totalFreeFloatingShares();
    bool isDeregistered = isNoLongerPartOfSyndicate(knot);

    unstake(e,staker,staker,knot,amount);
    uint256 totalFreeFloatingSharesAfter = totalFreeFloatingShares();

    assert isDeregistered =>  totalFreeFloatingShares == totalFreeFloatingSharesAfter, "totalFreeFloatingShares deducted by a deregistered knot";
    assert !isDeregistered =>  totalFreeFloatingShares-amount == totalFreeFloatingSharesAfter, "totalFreeFloatingShares deducted by a deregistered knot";

}

/// Balance mappings are updated correctly after unstaking.
// author: Elpacos
rule mappingsAreUpdatedCorrectlyAfterUnstaking(address unclaimedRecipient, address ethRecipient, bytes32 key, uint256 amount) {
    env e;

    uint256 totalFreeFloatingSharesBefore = totalFreeFloatingShares();
    uint256 sETHTotalStakeForKnotBefore = sETHTotalStakeForKnot(key);
    uint256 sETHStakedBalanceForKnotBefore = sETHStakedBalanceForKnot(key, e.msg.sender);

    unstake(e, unclaimedRecipient, ethRecipient, key, amount);

    uint256 accumulatedETHPerShare = lastAccumulatedETHPerFreeFloatingShare(key) > 0 ? lastAccumulatedETHPerFreeFloatingShare(key) : accumulatedETHPerFreeFloatingShare(); 

    assert sETHStakedBalanceForKnot(key, e.msg.sender) == sETHStakedBalanceForKnotBefore - amount;
    assert sETHTotalStakeForKnot(key) == sETHTotalStakeForKnotBefore - amount;
    assert sETHUserClaimForKnot(key, e.msg.sender) == (accumulatedETHPerShare * sETHStakedBalanceForKnot(key, e.msg.sender)) / PRECISION();
    assert !isNoLongerPartOfSyndicate(key) => totalFreeFloatingShares() == totalFreeFloatingSharesBefore - amount;
    assert isNoLongerPartOfSyndicate(key) => totalFreeFloatingShares() == totalFreeFloatingSharesBefore;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug3      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug4      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug5      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * Total unprocessed eth should always be less than total received
 * this rule catch public injected bug 5
 */
// author: gzeoneth
rule totalUnprocessedETHLteTotalETHBalance(method f) filtered {
    f -> notHarnessCall(f)
}{
    env e; calldataarg args;
    f(e, args);
    mathint total_unprocessed_coll = getUnprocessedETHForAllCollateralizedSlot() * numberOfRegisteredKnots();
    mathint total_unprocessed_free = getUnprocessedETHForAllFreeFloatingSlot();
    mathint total_unprocessed = total_unprocessed_coll + total_unprocessed_free;
    mathint total_received = totalETHReceived();
    assert total_received >= total_unprocessed, "unprocessed should be less than or equal total";
}

/// Registering new knots should decrease the amount of ETH per collateralized share that hasn't yet been allocated to each share
// author: JustDravee
rule addingKnotsDecreasesShare(){
    env e; calldataarg args;
    uint256 unprocessedETHForAllCollateralizedSlotBefore = getUnprocessedETHForAllCollateralizedSlot();
    require(unprocessedETHForAllCollateralizedSlotBefore > 0);
    registerKnotsToSyndicate(e, args); //reverts on empty array
    uint256 unprocessedETHForAllCollateralizedSlotAfter = getUnprocessedETHForAllCollateralizedSlot();
    // Adding knots should decrease share
    assert unprocessedETHForAllCollateralizedSlotAfter < unprocessedETHForAllCollateralizedSlotBefore, "Adding knots should decrease share";
}

/// Check Correctness of amount of ETH per collateralized share that hasn't yet 
/// been allocated to each share
// author: koolexcrypto
rule correctAmountOfUnprocessedETHForAllCollateralizedSlot() {
    mathint calcETH = calculateETHForFreeFloatingOrCollateralizedHolders();
    mathint lastSeenETH = lastSeenETHPerCollateralizedSlotPerKnot();
    mathint registeredKnots = numberOfRegisteredKnots();
    mathint UnprocessedETH = getUnprocessedETHForAllCollateralizedSlot();
    assert UnprocessedETH == (calcETH-lastSeenETH)/registeredKnots;
}

/// @notice Registiring a new KNOT will decrease the unprocessed ETH for per colleteralized share\
// author: 8ahoz
rule NewKnotDecreasesETHForSLOT(env e, bytes32 knot) 
{
    uint256 amountBefore = getUnprocessedETHForAllCollateralizedSlot(e);

    registerKnotsToSyndicate(e, knot);

    uint256 amountAfter = getUnprocessedETHForAllCollateralizedSlot(e);
    
    assert amountBefore > 0 => amountAfter < amountBefore;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug6      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug7      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/// A knot that has been deregistered can not become registered
// author: jessicapointing
rule deregisteredKnotCannotRegister(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;
    bytes32 blsPubKey;
    deRegisterKnots(e, blsPubKey);
    registerKnotsToSyndicate@withrevert(e, blsPubKey);

    assert lastReverted, "registerKnotsToSyndicate must revert if knot is de registered";
}

/// Can not register already registered knot.
// author: koolexcrypto
rule knotCanNotBeRegisteredTwice()
{
    env e;
    bytes32 knot;

    registerKnotsToSyndicate(e,knot);
    registerKnotsToSyndicate@withrevert(e,knot);
    bool reverted = lastReverted;

    assert reverted, "Knot was registered twice";
}

/// An already registered knot can not be registered again.
// author: Elpacos
rule canNotRegisterRegisteredKnot(method f) {
    bytes32 knot; env e;
    require isKnotRegistered(knot);

    registerKnotsToSyndicate@withrevert(e, knot);

    assert lastReverted, "registerKnotsToSyndicate must revert if knot is already registered";
}

/// Can only be initialized once.
// author: Elpacos
rule canOnlyBeInitializedOnce() {
    env e;
    calldataarg args;

    initialize(e, args);

    initialize@withrevert(e, args);

    assert lastReverted;
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug8      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //


/// The recipient is transferred the correct amount of unclaimedUserShare after 
/// claiming
// author: Elpacos
rule correctAmountTransferedAfterClaim(address recipient, bytes32 key, bytes32 key2) {
    //need to update accrued ETH per shares before claiming in order to calculate the correct amount of unclaimedUserShare
    updateAccruedETHPerShares();
    env e;
    //require keys to be different in order to calculate unclaimedUserShare for both keys correctly
    require key != key2;
    //cache balance and unclaimedUserShare before claiming
    uint256 recipientBalanceBefore = balance(recipient);
    uint256 unclaimedUserShareKey1 = calculateUnclaimedFreeFloatingETHShare(key, e.msg.sender);
    uint256 unclaimedUserShareKey2 = calculateUnclaimedFreeFloatingETHShare(key2, e.msg.sender);

    claimAsStaker(e, recipient, key, key2);
    //cache balance and unclaimedUserShare after claiming
    uint256 recipientBalanceAfter = balance(recipient);

    assert recipientBalanceAfter == recipientBalanceBefore + unclaimedUserShareKey1 + unclaimedUserShareKey2, "recipient must be transferred the correct amount of unclaimedUserShare after claiming";
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Bug9      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * should always be able to preview unclaimed
 * this rule catch public injected bug 9
 */
// author: gzeoneth
rule shouldHaveZeroClaimAfterUnstakeAll {
    address user; bytes32 knot; uint256 amount;
    env e;
    mathint staked_before = sETHStakedBalanceForKnot(knot, user);
    require staked_before != 0;
    unstake(e, user, user, knot, to_uint256(staked_before));
    mathint staked_after = sETHStakedBalanceForKnot(knot, user);
    require staked_after == 0;
    mathint claim = sETHUserClaimForKnot(knot, user);
    assert claim == 0, "should have 0 claim after unstake all";
}

/**
 * User Stake balance to Zero implies User Claim to Zero
 */
// author: zapaz
rule bug9Rule(){
    env e; bytes32 k; uint256 amount; address ethTo;

    require sETHStakedBalanceForKnot(k, e.msg.sender) != 0;
    require sETHUserClaimForKnot(k,e.msg.sender) != 0;
    require amount > 10^12;

    unstake(e, e.msg.sender, ethTo, k, amount);

    mathint stakedAfter  = sETHStakedBalanceForKnot(k, e.msg.sender);
    mathint claimAfter   = sETHUserClaimForKnot(k,e.msg.sender);

    assert stakedAfter == 0 => claimAfter == 0,  "KO";
}

/// sETHUserClaimForKnot is updated correctly after unstaking
// author: jessicapointing
rule sETHUserClaimForKnotUpdatedAfterUnstaking(method f) filtered {
    f -> notHarnessCall(f)
} {
    env e;

    address unclaimedETHRecipient;
    address sETHRecipient;
    bytes32 blsPubKey;
    uint256 sETHAmount;
    uint256 PRECISION = 10^24;

    unstake(e, unclaimedETHRecipient, sETHRecipient, blsPubKey, sETHAmount);

    uint256 accumulatedETHPerShare = getCorrectAccumulatedETHPerFreeFloatingShareForBLSPublicKey(blsPubKey);
    assert sETHUserClaimForKnot(blsPubKey,e.msg.sender) == (accumulatedETHPerShare * sETHStakedBalanceForKnot(blsPubKey,e.msg.sender) / PRECISION);
}

/// @notice Staker should be able to unstake the whole amount in multiple steps
// author: 8ahoz
rule UnstakeWholeAmountInTwoSteps(env e, bytes32 knot, uint256 totalSETH, uint256 amount1, uint256 amount2) 
{
    require amount1 > 0;
    require amount2 > 0;
    require (amount1 + amount2) == totalSETH;

   
    stake(e, knot, totalSETH, e.msg.sender);
    unstake(e,  e.msg.sender, e.msg.sender, knot, amount1);
    unstake@withrevert(e,  e.msg.sender, e.msg.sender, knot, amount2);
    
    assert !lastReverted, "Staker is not able to unstake the staked amount in two steps";
}

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Initial Setup Rules      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/// An unregistered knot can not be deregistered.
rule canNotDegisterUnregisteredKnot(method f) filtered {
    f -> notHarnessCall(f)
} {
    bytes32 knot; env e;
    require !isKnotRegistered(knot);

    deRegisterKnots@withrevert(e, knot);

    assert lastReverted, "deRegisterKnots must revert if knot is not registered";
}


/// Total ETH received must not decrease.
rule totalEthReceivedMonotonicallyIncreases(method f) filtered {
    f -> notHarnessCall(f)
}{
    
    uint256 totalEthReceivedBefore = totalETHReceived();

    env e; calldataarg args;
    f(e, args);

    uint256 totalEthReceivedAfter = totalETHReceived();

    assert totalEthReceivedAfter >= totalEthReceivedBefore, "total ether received must not decrease";
}

/// Address 0 must have zero sETH balance.
invariant addressZeroHasNoBalance()
    sETHToken.balanceOf(0) == 0

