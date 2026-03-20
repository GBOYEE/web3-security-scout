pragma solidity ^0.8.0;
contract Reentrancy {
    uint256 public balance;
    function withdraw() external {
        uint256 amt = balance;
        (bool success, ) = msg.sender.call{value: amt}("");
        require(success);
        balance = 0;
    }
}
