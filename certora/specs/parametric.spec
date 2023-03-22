import "./unit.spec"

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