import json
from web3 import Web3
import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

BALANCE_MEAN = 10 # mean balance of each user
NUM_TRANSACTIONS = 1000 # number of transactions to be made
SKIP_TRANSACTIONS = 100 # number of transactions to skip before recording the number of failed transactions

#connect to the local ethereum blockchain
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
w3 = Web3(provider)
#check if ethereum is connected
print(w3.is_connected())

#replace the address with your contract address (!very important)
deployed_contract_address = '0x7a0612855d36D70E569E71F12a4648F8a75C395F'

#path of the contract json file. edit it with your contract json file
compiled_contract_path ="build/contracts/Payment.json"
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']
contract = w3.eth.contract(address = deployed_contract_address, abi = contract_abi)



'''
#Calling a contract function createAcc(uint,uint,uint)
txn_receipt = contract.functions.createAcc(1, 2, 5).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
txn_receipt_json = json.loads(w3.to_json(txn_receipt))
print(txn_receipt_json) # print transaction hash

# print block info that has the transaction)
print(w3.eth.get_transaction(txn_receipt_json)) 

#Call a read only contract function by replacing transact() with call()

'''

# Function to close an account
def close_account(node1, node2, grph, contract):
    tmp_g = grph.copy()
    if not tmp_g.has_edge(node1, node2): # check if the edge exists
        return False
    tmp_g.remove_edge(node1, node2)
    if nx.is_connected(tmp_g): # check if the graph is still connected
        grph.remove_edge(node1, node2) # remove the edge from the original graph
        txn_receipt = contract.functions.closeAccount(node1, node2).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}) # call the contract function
        txn_receipt_json = json.loads(w3.to_json(txn_receipt)) 
        w3.eth.get_transaction(txn_receipt_json)
        return True 
    else:
        return False


#Add your Code here
num_nodes = 100
random.seed(42)

# Create the power law graph using the Barabasi-Albert model
while True:
    G = nx.barabasi_albert_graph(num_nodes, m=2, seed=42) # create the barabasi albert power law graph
    if nx.is_connected(G): # check if the graph is connected
        break
A = nx.adjacency_matrix(G).todense() # convert the graph to adjacency matrix for easy access
print(nx.is_connected(G))
nx.draw(G, with_labels=True) # draw the graph
plt.savefig("topology.png")

# register all the users
for i in range(num_nodes): 
    txn_receipt = contract.functions.registerUser(i, f"htg_{i}").transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})

# create all the accounts
for i in range(num_nodes):
    for j in range(i,num_nodes):
        if A[i][j] == 1:
            # Drawing from exponential distribution with mean 10
            print(f"Creating account between {i} and {j}")
            sample = np.random.exponential(10) # sample from exponential distribution
            txn_receipt = contract.functions.createAcc(i, j, int(sample/2)).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638}) # call the contract function
            txn_receipt_json = json.loads(w3.to_json(txn_receipt))
            w3.eth.get_transaction(txn_receipt_json)




num_failed_transactions = 0 # number of failed transactions
y_values = [] # list to store the number of failed transactions


# make transactions
for i in range(NUM_TRANSACTIONS):
    if (i+1)%SKIP_TRANSACTIONS == 0:
        y_values.append(SKIP_TRANSACTIONS - num_failed_transactions)
        num_failed_transactions = 0
    print(f"Transaction {i}")
    # sample a random node
    node1 = random.randint(0, num_nodes-1)
    while True:
        node2 = random.randint(0, num_nodes-1)
        if node1 != node2:
            break
    
    short_path = nx.shortest_path(G, source=node1, target=node2) # find the shortest path between the two nodes
    print(short_path)
    for k in range(len(short_path)-1):
        try:
            # make the transaction using a series of calls to the contract function sendAmount
            txn_receipt = contract.functions.sendAmount(short_path[k], short_path[k+1]).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
            txn_receipt_json = json.loads(w3.to_json(txn_receipt))
            w3.eth.get_transaction(txn_receipt_json)

        except:
            # if the transaction fails revert the transactions tillt the last successful transaction
            print(f"Transaction failed at {k}th transaction")
            num_failed_transactions += 1
            # revert transaction
            for j in range(k, 0, -1):
                txn_receipt = contract.functions.sendAmount(short_path[j], short_path[j-1]).transact({'txType':"0x3", 'from':w3.eth.accounts[0], 'gas':2409638})
                txn_receipt_json = json.loads(w3.to_json(txn_receipt))
                w3.eth.get_transaction(txn_receipt_json)

            print("Transaction failed")
            break


# plotting y_vals (failed transactions)
print(y_values)
plt.clf()
plt.plot(y_values, label="Succesful Transactions every 100 Transactions")
plt.xlabel("Number of 100 Transactions")
plt.ylabel("Number of Succesful Transactions")
plt.legend()
plt.savefig("failed_transactions.png")

# testing close account
do_break = False
for i in range(num_nodes):
    for j in range(num_nodes):
        if A[i][j] == 1:
            print(f"Trying  to close account between {i} and {j}")
            ret = close_account(i, j, G, contract)
            A = nx.adjacency_matrix(G).todense()
            if ret:
                print(f"Successfully closed account between {i} and {j}")
            else:
                print(f"Failed to close account between {i} and {j}, graph is not connected")
            do_break = True
            break
    if do_break:
        break

do_break = False
for i in range(num_nodes):
    for j in range(num_nodes):
        if A[i][j] != 1:
            print("Trying  to close account between {i} and {j}")
            ret = close_account(i, j, G, contract)
            if ret:
                print(f"Successfully closed account between {i} and {j}")
            else:
                print(f"Failed to close account between {i} and {j}, graph is not connected")
            do_break = True
            break
    if do_break:
        break