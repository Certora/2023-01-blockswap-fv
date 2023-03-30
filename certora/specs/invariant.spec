import "./parametric.spec"

// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷      Invariants      ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //
// ÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷ //

/**
 * last seen is GE than accumulated 
 */
// author: rechlis
invariant lastseenVsAccumulated()
    lastSeenETHPerCollateralizedSlotPerKnot() >= accumulatedETHPerCollateralizedSlotPerKnot()
    filtered { f -> notHarnessCall(f) }

/**
 * knot not registered implies all its monitored velues should be zero
 */
// author: rechlis
invariant knotNotRegistered(env e, bytes32 knot, address user)
    !isKnotRegistered(knot) => 
            sETHTotalStakeForKnot(knot) == 0                &&
            sETHStakedBalanceForKnot(knot, user) == 0       &&
            sETHUserClaimForKnot(knot, user) == 0        &&
            claimedPerCollateralizedSlotOwnerOfKnot(e, knot, user) == 0
    filtered { f -> notHarnessCall(f) }

/**
 * totalClaimed GE knot claimed
 */
// author: rechlis
invariant claimedPerCollateralizedVsTotal(env e, bytes32 knot, address user)
    claimedPerCollateralizedSlotOwnerOfKnot(e, knot, user) <= totalClaimed()
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
        f-> notHarnessCall(f)
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
        f-> notHarnessCall(f)
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
        f-> notHarnessCall(f)
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
    sETHToken.balanceOf(currentContract) >= sETHTotalStake
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
    ghostsETHTotalStakeForKnot[blsKey] == sETHTotalStakeForKnot(blsKey)

/**
 * totalETHProcessedPerCollateralizedKnot always less than or equal than accumulatedETHPerCollateralizedSlotPerKnot.
 */
// author: neomoxx
invariant accumulatedETHPerCollateralizedSlotPerKnotGTEtotalETHProcessedPerCollateralizedKnot(bytes32 blsPubKey)
    totalETHProcessedPerCollateralizedKnot(blsPubKey) <= accumulatedETHPerCollateralizedSlotPerKnot()
    filtered { f -> notHarnessCall(f) }

/**
 * sETHTotalStake and sETHTotalStakedBalance must match.
 */
// author: neomoxx
invariant sETHTotalStakeGhostsMatch()
    sETHTotalStake == sETHTotalStakedBalance
    filtered { f -> notHarnessCall(f) }

/**
 * calculateETHForFreeFloatingOrCollateralizedHolders must be always greater or equal than lastSeenETHPerCollateralizedSlotPerKnot.
 */
// author: neomoxx, edited
invariant calculatedETHGTElastSeenETHPerCollateralizedSlotPerKnot()
    calculateETHForFreeFloatingOrCollateralizedHolders() >= lastSeenETHPerCollateralizedSlotPerKnot()
    filtered { f -> notHarnessCall(f) }

invariant calculatedETHGTElastSeenETHPerFreeFloating()
    calculateETHForFreeFloatingOrCollateralizedHolders() >= lastSeenETHPerFreeFloating()
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
invariant sETHStakedBalanceForKnotInvariant(bytes32 knot)
    sETHTotalStakeForKnot(knot) == ghostsETHTotalStakeForKnot[knot]
    filtered { f -> notHarnessCall(f) }
