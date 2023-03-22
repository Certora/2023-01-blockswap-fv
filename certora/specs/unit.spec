import "./base.spec"

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

    uint256 seTHBalanceAfter = sETHToken.balanceOf(sETHRecipient);

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
    bytes32 knot;
    require _sETHAmount > 0;

    uint256 contractBalanceBefore = sETHToken.balanceOf(currentContract);
    uint256 unclaimedFreeFloatingETHShareBefore = calculateUnclaimedFreeFloatingETHShare(_blsPubKey, e.msg.sender);
    uint256 totalStakeBefore = sETHTotalStakeForKnot(_blsPubKey);
    uint256 stakedBalanceBefore = sETHStakedBalanceForKnot(_blsPubKey, e.msg.sender);
    uint256 sETHBalanceBefore = sETHToken.balanceOf(_sETHRecipient);
    uint256 recipentBalanceBefore = sETHToken.balanceOf(_sETHRecipient);

    unstake(e, _unclaimedETHRecipient, _sETHRecipient, _blsPubKey, _sETHAmount);

    uint256 recipentBalanceAfter = sETHToken.balanceOf(_sETHRecipient);
    uint256 contractBalanceAfter = sETHToken.balanceOf(currentContract);
    uint256 unclaimedFreeFloatingETHShareAfter = calculateUnclaimedFreeFloatingETHShare(_blsPubKey, e.msg.sender);
    uint256 totalStakeAfter = sETHTotalStakeForKnot(_blsPubKey);
    uint256 stakedBalanceAfter = sETHStakedBalanceForKnot(_blsPubKey, e.msg.sender);
    uint256 sETHBalanceAfter = sETHToken.balanceOf(_sETHRecipient);

    assert totalStakeBefore - totalStakeAfter == _sETHAmount, "unstaking must decrease stake for knot by unstaked amount";
    assert stakedBalanceBefore - stakedBalanceAfter == _sETHAmount, "unstaking must decrease staked balance by unstaked amount";
    assert unclaimedFreeFloatingETHShareBefore > 0 <=> unclaimedFreeFloatingETHShareAfter < unclaimedFreeFloatingETHShareBefore, "Unclaimed ETH not reduced";
    assert (recipentBalanceAfter == recipentBalanceBefore + _sETHAmount && contractBalanceAfter == contractBalanceBefore - _sETHAmount, "Failed to Transfer sETH");
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
    uint256 lastSeenBefore = calculateETHForFreeFloatingOrCollateralizedHolders();

    updateAccruedETHPerShares();

    uint256 accumulatedAfter = accumulatedETHPerFreeFloatingShare();
    uint256 lastSeenAfter = calculateETHForFreeFloatingOrCollateralizedHolders();


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
    require getActivenessOfKnot(e, knot);

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

    uint256 unclaimed = calculateUnclaimedFreeFloatingETHShare(knot, e.msg.sender);

    claimAsStaker(e,e.msg.sender,knot);

    uint256 unclaimedAfter = calculateUnclaimedFreeFloatingETHShare(knot, e.msg.sender);

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