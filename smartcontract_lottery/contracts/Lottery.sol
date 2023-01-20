// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
// not using openzeppelin ownable, rather using chainlink version
// import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import "@chainlink/contracts/src/v0.8/VRFV2WrapperConsumerBase.sol";

contract Lottery is VRFV2WrapperConsumerBase, ConfirmedOwner {
    // these events are emitted and picked up by the chainlink node
    event RequestSent(uint256 requestId, uint32 numWords);
    event RequestFulfilled(
        uint256 requestId,
        uint256[] randomWords,
        uint256 payment
    );

    // past requests Id.
    uint256[] public requestIds;
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;
    // Address LINK - hardcoded for Goerli
    // address linkAddress = 0x326C977E6efc84E512bB9C30f76E30c160eD06FB;
    // address WRAPPER - hardcoded for Goerli
    // address wrapperAddress = 0x708701a1DfF4f478de54383E49a627eD4852C816;
    // ---------end of copied variables --------------------------------------------------------------

    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomWords;
    uint256 public usdEntryFee;
    uint256 internal fee; //oracle fee

    AggregatorV3Interface internal ethUsdPriceFeed;

    address linkAddress;
    address priceFeedAddress;
    address wrapperAddress;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(
        address _priceFeedAddress,
        address _linkAddress,
        address _wrapperAddress
    )
        ConfirmedOwner(msg.sender)
        VRFV2WrapperConsumerBase(_linkAddress, _wrapperAddress)
    {
        priceFeedAddress = _priceFeedAddress;
        linkAddress = _linkAddress;
        wrapperAddress = _wrapperAddress;
        usdEntryFee = 50 * 10**18;
        fee = 0.25 * 10**18;

        ethUsdPriceFeed = AggregatorV3Interface(priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "The lottery hasnt started yet..."
        );
        require(
            msg.value >= getEntranceFee(),
            "You have not met the minimum deposit"
        );
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10;
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
        //price feed returns a price with 8 decimals
        // eg eth/usd ==2000  returns 200000000
        // function returns costToEnter = price in wei
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "theres still a lottery going on"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(
            LINK.balanceOf(address(this)) > fee,
            "Not enough LINK - fill contract with faucet"
        );
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        uint256 requestId = requestRandomness(
            callbackGasLimit,
            requestConfirmations,
            numWords
        );

        emit RequestSent(requestId, numWords);
    }

    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Not calculating winner yet..."
        );
        requestIds.push(_requestId);
        uint256 indexOfWinner = _randomWords[0] % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // reset players to zero and prepare for a new lottery
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomWords = _randomWords[0];
    }

    function calcPrice() public view returns (uint256) {
        return VRF_V2_WRAPPER.calculateRequestPrice(100000);
    }
}
