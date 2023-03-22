import "./invariant.spec"

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
