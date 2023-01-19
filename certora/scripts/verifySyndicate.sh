# Call this script from root, e.g. `sh certora/scripts/verifySyndicate.sh $1 $2`
# where $1 is a comment for the run that gives some background to the call and $2 is an 
# optional arguement used to specify a rule, without a specified rule all rules in the 
# spec will be ran.
if [[ "$2" ]]
then
    RULE="--rule $2"
fi

solc-select use 0.8.13

certoraRun  certora/harnesses/SyndicateHarness.sol \
    certora/harnesses/MockStakeHouseUniverse.sol \
    certora/harnesses/MockStakeHouseRegistry.sol \
    certora/harnesses/MockSlotSettlementRegistry.sol \
    certora/harnesses/MocksETH.sol \
    --verify SyndicateHarness:certora/specs/Syndicate.spec \
    --cloud master \
    --optimistic_loop \
    --optimize 1 \
    --loop_iter 3 \
    $RULE \
    --rule_sanity \
    --settings -optimisticFallback=true \
    --packages @blockswaplab=node_modules/@blockswaplab @openzeppelin=node_modules/@openzeppelin \
    --msg "Syndicate $1 $2"