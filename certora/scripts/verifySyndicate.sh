unset RULE
unset MSG

if [[ "$1" ]]
then
    RULE="--rule $1"
fi

if [[ "$2" ]]
then
    MSG="- $2"
fi

certoraRun certora/harnesses/SyndicateHarness.sol \
    certora/harnesses/MockStakeHouseUniverse.sol \
    certora/harnesses/MockStakeHouseRegistry.sol \
    certora/harnesses/MockSlotSettlementRegistry.sol \
    certora/harnesses/MocksETH.sol \
    --verify SyndicateHarness:certora/specs/Syndicate.spec \
    --optimistic_loop \
    --loop_iter 2 \
    --packages @blockswaplab=node_modules/@blockswaplab @openzeppelin=node_modules/@openzeppelin \
    --send_only \
    --optimize 1 \
    --settings -optimisticFallback=true \
    --rule_sanity basic \
    --cache syndicate \
    $RULE \
    --msg "Syndicate: $1 $MSG"
