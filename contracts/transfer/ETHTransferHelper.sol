// SPDX-License-Identifier: BUSL-1.1

pragma solidity ^0.8.13;

/// @dev Contract that has the logic to take care of transferring ETH and can be overriden as needed
contract ETHTransferHelper {
    function _transferETH(address _recipient, uint256 _amount) internal virtual {
        (bool success,) = _recipient.call{value: _amount}("");
        require(success, "Failed to transfer");
    }
}