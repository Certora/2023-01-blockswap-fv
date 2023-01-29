pragma solidity 0.8.13;

// SPDX-License-Identifier: MIT

import { ERC20PermitUpgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/draft-ERC20PermitUpgradeable.sol";
import { ISlotSettlementRegistry } from "../munged/interfaces/ISlotSettlementRegistry.sol";
import { ScaledMath } from "../munged/libraries/ScaledMath.sol";

contract  MocksETH is ERC20PermitUpgradeable {
    using ScaledMath for uint256;

    /// @notice Address of registry of all SLOT tokens
    ISlotSettlementRegistry public slotRegistry;
    uint256 public constant BASE_EXCHANGE_RATE = 3 ether;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() initializer {}

    /// @notice Used in place of a constructor to support proxies
    /// @dev Can only be called once
    function init() external initializer {
        slotRegistry = ISlotSettlementRegistry(msg.sender);

        __ERC20_init(
            "sETH",
            "sETH"
        );

        __ERC20Permit_init("sETH");
    }

    /// @notice Mints a given amount of tokens
    /// @dev Only slot settlement registry module can call
    /// @param _recipient of the tokens
    /// @param _amount of tokens to mint
    function mint(address _recipient, uint256 _amount) external {
        require(msg.sender == address(slotRegistry), "mint: Only SLOT registry");
        _mint(_recipient, _amount);
    }

    /// @notice Burns a given amount of tokens
    /// @dev Only slot settlement registry module can call
    /// @param _owner of the tokens
    /// @param _amount of tokens to burn
    function burn(address _owner, uint256 _amount) external {
        require(msg.sender == address(slotRegistry), "burn: Only SLOT registry");
        _burn(_owner, _amount);
    }

    /// @notice Get the address of the associated Stakehouse registry
    function stakehouse() public view returns (address) {
        return slotRegistry.shareTokensToStakeHouse(
            address(this)
        );
    }

    /// @notice Total collateralised SLOT associated with Stakehouse
    function stakehouseCollateralisedSlot() public view returns (uint256) {
        return slotRegistry.circulatingCollateralisedSlot(stakehouse());
    }

    /// @notice For an account with sETH, the amount of SLOT backing those tokens based on actual balance
    /// @param _owner Account containing sETH tokens
    function slot(address _owner) external view returns (uint256) {
        if (_owner == address(slotRegistry)) {
            return stakehouseCollateralisedSlot();
        }

        return slotRegistry.slotForSETHBalance(stakehouse(), balanceOf(_owner));
    }

    /// @notice For an account with sETH, the amount of SLOT backing those tokens based on active balance
    /// @param _owner Account containing sETH tokens
    function slotForActiveBalance(address _owner) external view returns (uint256) {
        if (_owner == address(slotRegistry)) {
            return stakehouseCollateralisedSlot();
        }

        return balanceOf(_owner).sDivision(BASE_EXCHANGE_RATE);
    }

    /// @notice sETH balance of owner factoring in the latest exchange rate of the Stakehouse
    /// @param _owner Account containing sETH tokens
    function activeBalanceOf(address _owner) public view returns (uint256) {
        uint256 sETHBalance = slotRegistry.sETHForSLOTBalance(stakehouse(), balanceOf(_owner));
        return sETHBalance.sDivision(BASE_EXCHANGE_RATE);
    }

    function transfer(address recipient, uint256 amount) public virtual override returns (bool val) {
        if (balanceOf(msg.sender) >= amount) {
            return super.transfer(recipient, amount);
        }         
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public virtual override returns (bool val) {
        if (balanceOf(sender) >= amount) {
            super.transferFrom(sender, recipient, amount);
            return true;
        }         
    }
}