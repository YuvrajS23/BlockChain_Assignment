// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;


contract Payment {
  mapping (uint => bool) public users; // list of users
  mapping (uint => string) public useridtoname; // mapping of user id to user name
  mapping (uint => mapping (uint => uint)) public balances; // mapping of user id to user id to balance

constructor() public {
  // constructor

}

function registerUser(uint user_id, string memory user_name) public {
  // It will register the user and add it to the list of available users to transact.

  users[user_id] = true;
  useridtoname[user_id] = user_name;
  
}

function createAcc(uint user_id_1, uint user_id_2, uint balance) public {
  // Create a joint account between two users and keep a track of individual contribution to the joint account.

  require(users[user_id_1] && users[user_id_2], "One or more users not registered.");
  balances[user_id_1][user_id_2] = balance;
  balances[user_id_2][user_id_1] = balance;
}

function sendAmount(uint user_id_1, uint user_id_2) public returns (bool){
  // Transfer the amount (only whole number, no decimal) from one user
  // to the other irrespective of having a joint account or not. If a user doesn’t have sufficient balance to
  // send the amount, it will reject the transaction and result in transaction failure.
  
  require(users[user_id_1] && users[user_id_2], "One or more users not registered.");
  require(balances[user_id_1][user_id_2] >= 1, "Insufficient balance");
  balances[user_id_1][user_id_2] -= 1;
  balances[user_id_2][user_id_1] += 1;
  return true;
}

function closeAccount(uint user_id_1, uint user_id_2) public {
  // Terminate the account between the two users passed as a parameter to the method call.

  require(users[user_id_1] && users[user_id_2], "One or more users not registered.");
  delete balances[user_id_1][user_id_2];
  delete balances[user_id_2][user_id_1];
}

function getBalance(uint user_id_1, uint user_id_2) public view returns (uint){
  // ReturnBthe balance of the joint account between the two users passed as a parameter to the method call.

  require(users[user_id_1] && users[user_id_2], "One or more users not registered.");
  return balances[user_id_1][user_id_2];
}
}