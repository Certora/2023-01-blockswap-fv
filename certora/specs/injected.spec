import "./live.spec"

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

