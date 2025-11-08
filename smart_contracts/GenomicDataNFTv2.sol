// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract GenomicDataNFTv2 is ERC1155, AccessControl, ReentrancyGuard {
    // Roles
    bytes32 public constant DATA_OWNER_ROLE = keccak256("DATA_OWNER_ROLE");
    bytes32 public constant RESEARCHER_ROLE = keccak256("RESEARCHER_ROLE");

    // External token (MAG)
    IERC20 public magToken;

    // Dataset & access structures
    struct DatasetMetadata {
        string ipfsCID;        // encrypted embedding / manifest CID (ipfs://...)
        address dataOwner;     // custodian that minted the dataset
        uint256 createdAt;     // block timestamp
        bool isActive;         // dataset active flag
    }

    enum RequestStatus { Pending, Approved, Denied, Expired }

    struct AccessRequest {
        address requester;
        uint256 tokenId;
        uint256 magOffered;        // MAG escrowed at request
        string researchPurpose;    // free-text purpose
        uint256 requestTime;
        RequestStatus status;
    }

    // Storage
    mapping(uint256 => DatasetMetadata) public datasets;
    mapping(uint256 => mapping(address => AccessRequest)) public accessRequests;
    mapping(uint256 => mapping(address => uint256)) public accessExpiry; // tokenId => researcher => expiry
    mapping(address => uint256[]) public userDatasets;

    // Counters & constants
    uint256 private _tokenIdCounter;
    uint256 public constant ACCESS_DURATION = 30 days;

    // Events
    event DatasetMinted(uint256 indexed tokenId, address indexed owner, string ipfsCID);
    event AccessRequested(uint256 indexed tokenId, address indexed requester, uint256 magOffered);
    event AccessGranted(uint256 indexed tokenId, address indexed requester, uint256 expiryTime);
    event AccessDenied(uint256 indexed tokenId, address indexed requester);
    event DataUsageLogged(uint256 indexed tokenId, address indexed researcher, string description);

    constructor(string memory baseURI, address _magToken) ERC1155(baseURI) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        magToken = IERC20(_magToken);
    }

    // Required multiple inheritance override
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    // Mint a new dataset NFT (soulbound to owner + later cloned for researcher access)
    function mintGenomicNFT(string memory ipfsCID) external returns (uint256) {
        uint256 tokenId = _tokenIdCounter++;

        // Mint 1 to the data owner
        _mint(msg.sender, tokenId, 1, "");

        datasets[tokenId] = DatasetMetadata({
            ipfsCID: ipfsCID,
            dataOwner: msg.sender,
            createdAt: block.timestamp,
            isActive: true
        });

        userDatasets[msg.sender].push(tokenId);
        _grantRole(DATA_OWNER_ROLE, msg.sender);

        emit DatasetMinted(tokenId, msg.sender, ipfsCID);
        return tokenId;
    }

    // Mapping for custom URIs (add this to your contract's state)
mapping(uint256 => string) private customURI;

// Set URI for a tokenId (can only be called by the data owner)
function setTokenURI(uint256 tokenId, string memory uri_) public {
    require(datasets[tokenId].dataOwner == msg.sender, "Only data owner");
    customURI[tokenId] = uri_;
    emit URI(uri_, tokenId);
}

// Override the uri() function
function uri(uint256 tokenId) public view override returns (string memory) {
    return customURI[tokenId];
}


    // Researcher escrows MAG and requests access
    function requestAccess(
        uint256 tokenId,
        uint256 magAmount,
        string memory researchPurpose
    ) external nonReentrant {
        require(datasets[tokenId].isActive, "Dataset not active");
        require(magAmount > 0, "Offer > 0 MAG");
        // researcher must have approved this contract to pull MAG
        require(magToken.allowance(msg.sender, address(this)) >= magAmount, "Approve MAG first");

        // pull MAG escrow into contract
        bool ok = magToken.transferFrom(msg.sender, address(this), magAmount);
        require(ok, "MAG transfer failed");

        accessRequests[tokenId][msg.sender] = AccessRequest({
            requester: msg.sender,
            tokenId: tokenId,
            magOffered: magAmount,
            researchPurpose: researchPurpose,
            requestTime: block.timestamp,
            status: RequestStatus.Pending
        });

        emit AccessRequested(tokenId, msg.sender, magAmount);
    }

    // Data owner approves, MAG is paid out, researcher receives a 1-of-1 access NFT clone, expiry set
    function approveAccess(uint256 tokenId, address researcher) external nonReentrant {
        require(datasets[tokenId].dataOwner == msg.sender, "Only data owner");
        AccessRequest storage req = accessRequests[tokenId][researcher];
        require(req.status == RequestStatus.Pending, "No pending request");

        req.status = RequestStatus.Approved;
        accessExpiry[tokenId][researcher] = block.timestamp + ACCESS_DURATION;

        // pay owner
        require(magToken.transfer(msg.sender, req.magOffered), "Payout failed");

        // mint 1 access token to researcher (same tokenId)
        _mint(researcher, tokenId, 1, "");

        emit AccessGranted(tokenId, researcher, accessExpiry[tokenId][researcher]);
    }

    // Data owner denies, refund MAG to requester
    function denyAccess(uint256 tokenId, address researcher) external nonReentrant {
        require(datasets[tokenId].dataOwner == msg.sender, "Only data owner");
        AccessRequest storage req = accessRequests[tokenId][researcher];
        require(req.status == RequestStatus.Pending, "No pending request");

        req.status = RequestStatus.Denied;

        // refund escrow
        require(magToken.transfer(researcher, req.magOffered), "Refund failed");

        emit AccessDenied(tokenId, researcher);
    }

    // Researcher can read the dataset CID if they currently hold an access NFT and are within expiry
    function retrieveDataCID(uint256 tokenId) external view returns (string memory) {
        require(balanceOf(msg.sender, tokenId) > 0, "No access NFT");
        require(block.timestamp < accessExpiry[tokenId][msg.sender], "Access expired");
        require(accessRequests[tokenId][msg.sender].status == RequestStatus.Approved, "Not approved");
        return datasets[tokenId].ipfsCID;
    }

    // Optional: simple usage logging (off-chain listeners can capture this)
    function logDataUsage(uint256 tokenId, string memory usageDescription) external {
        require(balanceOf(msg.sender, tokenId) > 0, "No access NFT");
        emit DataUsageLogged(tokenId, msg.sender, usageDescription);
    }

    // Admin toggle dataset active flag (e.g., maintenance)
    function setDatasetActive(uint256 tokenId, bool active) external {
        require(datasets[tokenId].dataOwner == msg.sender || hasRole(DEFAULT_ADMIN_ROLE, msg.sender), "Not allowed");
        datasets[tokenId].isActive = active;
    }

    // Helper: list datasets for a user
    function getUserDatasets(address user) external view returns (uint256[] memory) {
        return userDatasets[user];
    }
}
