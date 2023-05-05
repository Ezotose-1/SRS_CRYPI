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


parser = argparse.ArgumentParser(
                    prog='CRIPY',
                    description='Votai')

parser.add_argument('-R', '--result',
                    action='store_true', required=False)
args = parser.parse_args()


def get_results():
    print("Checking results")
    r = requests.get(
            url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/results'
        )
    
    if 'Error' in r.text:
        print(r.text)
        exit(1)

    result = r.text[1:-1].split()
    result = [ int(r) for r in result ]
    winner = Candidates[result.index(max(result))]
    print(f"Winner is : {winner}\n")
    for k, v in enumerate(Candidates):
        print(f"{v} has {result[k]} vote(s).")
    
    return winner


def user_inputs():
    name = input("Enter your name > ")
    h = hashlib.new('sha256')
    h.update(name.encode())
    name = h.hexdigest()

    print("Candidates value :")
    for k, v in enumerate(Candidates):
        print("-", k, v)

    vote = int(input("Vote for > ")) % 4

    return name, vote


def auth_client():
    r = requests.get(
        url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/pk?name={name}'
    )

    if "Error" in r.text:
        print(r.text)
        exit(1)

    res = json.loads(r.text)
    
    token = res.get('token', '42')
    context = res.get('context')
    pkey = res.get('pkey')
    return token, context, pkey


def encrypt_vote(HE, candidate_index):
    # Generate and encrypt data
    plainvalue = np.array([0] * 4096)
    if not args.result:
        plainvalue[candidate_index] = 1

    # Encrypt then serialize to send to the network
    cyphervalue = HE.encrypt(plainvalue)
    s_cyphervalue = cyphervalue.to_bytes()

    return s_cyphervalue


def send_vote(encrypted_vote):
    print('Vote in progress')
    r = requests.post(
            url=f'http://{ADDITION_SERVER_URL}:{ADDITION_SERVER_PORT}/vote',
            json={
                'cyphervalue': s_cyphervalue.decode("cp437"),
                'token': token
            }
        )

    if ("Error" in r.text):
        print(r.text)
        exit(1)
    return True


if __name__ == "__main__":

    # If the user ask for the results, ask and print them
    # Otherwise vote
    if args.result:
        get_results()
        exit(0)

    # Ask user
    name, uservote = user_inputs()


    # Generate Pyfhel Object
    HE = Pyfhel()

    # Ask Authenticate server
    token, context, pkey = auth_client()

    HE.from_bytes_context(context.encode("cp437"))
    HE.from_bytes_public_key(pkey.encode("cp437"))

    # Encrypt the vote value and send it to the server
    s_cyphervalue = encrypt_vote(HE, uservote)
    send_vote(s_cyphervalue)

