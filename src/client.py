##
# Author(s)
# - Pierre BLAESS
# - Adrien LANGOU
# - Aurélien REBOURG
# - Lucas THESE
##

import numpy as np
from Pyfhel import Pyfhel, PyCtxt

import requests
import hashlib
import argparse
import json


AUTH_SERVER_URL = "127.0.0.1"
AUTH_SERVER_PORT = 9000


ADDITION_SERVER_URL = "127.0.0.1"
ADDITION_SERVER_PORT = 9001

Candidates = [
    "Pierre Olivier Mercier",
    "Sebastien Bombal",
    "Constance Beguier",
    "Jean Lassal"
]


# Parse arguments
# usage: `python3 client.py -R` to ask for the results
#        `python3 client.py ` to add a vote 
parser = argparse.ArgumentParser(
                    prog='CRIPY',
                    description='Votai')

parser.add_argument('-R', '--result',
                    help="Ask the authenticate server to get the results of the vote",
                    action='store_true', required=False)
args = parser.parse_args()

class Logger():
    def __init__(self) -> None:
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'

        self.prompt = "[E-Voting Client]"

    def info(self, text):
        print(f"{self.OKBLUE}{self.prompt}{self.ENDC}",
             f"{text}")

    def ok(self, text):
        print(f"{self.OKGREEN}{self.prompt}{self.ENDC}",
             f"{text}")

    def server_error(self, text):
        print(f"{self.FAIL}{self.prompt}{self.ENDC}",
              f"{text}")
        exit(1)

log = Logger()

def get_results():
    """! Ask the __authenticate__ server to get the results of the vote
    @param None
    @return Winner name
    """
    log.info("Asking the server for vote results")
    r = requests.get(
            url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/results'
        )
    
    if 'Error' in r.text:
        log.server_error(r.text)


    result = r.text[1:-1].split()
    result = [ int(r) for r in result ]
    winner = Candidates[result.index(max(result))]
    log.ok(f"Winner is : {winner}\n")
    for k, v in enumerate(Candidates):
        log.ok(f"{v} has {result[k]} vote(s).")
    
    return winner


def user_inputs():
    """! Ask the user for inputs (name, vote)
    @param None
    @return name: str, vote: int
    """
    log.info("Please enter your name :")
    name = input("> ")

    h = hashlib.new('sha256')
    h.update(name.encode())
    name = h.hexdigest()

    log.info("Here are the candidates :")
    for k, v in enumerate(Candidates):
        print("-", k, v)

    log.info("Please enter a candidate key :")
    vote = int(input("> ")) % 4

    return name, vote


def auth_client():
    """! Ask the __authentication__ server to authenticate the client and send the public key.
    @param None
    @return token: str, context: str, pkey: str
    """
    r = requests.get(
        url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/pk?name={name}'
    )

    if "Error" in r.text:
        log.server_error(r.text)


    res = json.loads(r.text)
    
    token = res.get('token', '42')
    context = res.get('context')
    pkey = res.get('pkey')
    return token, context, pkey


def encrypt_vote(HE, candidate_index):
    """! Encrypt the vote vector using server public key and context.
    @param HE  :  Server homogenous encryption object.
    @param candidate_index  :  User vote index in the Candidates array.
    @return s_cyphervalue  :  serialized encrypted vote vector 
    """
    # Generate and encrypt data
    plainvalue = np.array([0] * 4096)
    if not args.result:
        plainvalue[candidate_index] = 1

    # Encrypt then serialize to send to the network
    cyphervalue = HE.encrypt(plainvalue)
    s_cyphervalue = cyphervalue.to_bytes()

    return s_cyphervalue


def send_vote(encrypted_vote, token):
    """! Send the user vote to the __addition__ server
    @param encrypted_vote  :  User serialized and encrypted vote.
    @param token  :  Client token used to authenticate to the server  
    @return Boolean of success or Error
    """
    r = requests.post(
            url=f'http://{ADDITION_SERVER_URL}:{ADDITION_SERVER_PORT}/vote',
            json={
                'cyphervalue': encrypted_vote.decode("cp437"),
                'token': token
            }
        )

    if ("Error" in r.text):
        log.server_error(r.text)

    log.ok("Your vote has successfully been completed.")
    return True


if __name__ == "__main__":
    # If the user ask for the results, ask and print them
    # Otherwise vote
    if args.result:
        get_results()
        exit(0)

    # Ask user
    name, uservote = user_inputs()

    # Ask Authenticate server
    anonymoustoken, context, pkey = auth_client()

    # Generate Pyfhel Object
    HE = Pyfhel()

    HE.from_bytes_context(context.encode("cp437"))
    HE.from_bytes_public_key(pkey.encode("cp437"))

    # Encrypt the vote value and send it to the server
    s_cyphervalue = encrypt_vote(HE, uservote)
    send_vote(s_cyphervalue, anonymoustoken)

