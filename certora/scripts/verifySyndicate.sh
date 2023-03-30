# $1 is the file you want to run, so for example `sh certora/scripts/verifySyndicate.sh unit` will run the spec with the unit tests
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
    --verify SyndicateHarness:certora/specs/$1.spec \
    --cloud master \
    --optimistic_loop \
    --optimize 1 \
    --loop_iter 3 \
    $RULE \
    --rule_sanity \
    --settings -optimisticFallback=true \
    --packages @blockswaplab=node_modules/@blockswaplab @openzeppelin=node_modules/@openzeppelin \
    --msg "Syndicate $1 $2"