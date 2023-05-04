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


parser = argparse.ArgumentParser(
                    prog='CRIPY',
                    description='Votai')

parser.add_argument('-R', '--result',
                    action='store_true', required=False)
args = parser.parse_args()


name = input("Enter your name > ")
h = hashlib.new('sha256')
h.update(name.encode())
name = h.hexdigest()

Candidats = [
    "Pierre Olivier Mercier",
    "Sebastien Bombal",
    "Constance Beguier",
    "Jean Lassal"
]

if not args.result:
    print("Candidates value :")
    for k, v in enumerate(Candidats):
        print("-", k, v)

    vote = int(input("Vote for > ")) % 4


# Generate Pyfhel
HE = Pyfhel()

# Generate and encrypt data
plainvalue = np.array([0] * 4096)
if not args.result:
    plainvalue[vote] = 1


r = requests.get(
        url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/pk?name={name}'
    )

if "Error" in r.text:
    print(r.text)
    exit(1)

res = json.loads(r.text)
token = res.get('token', '42')

HE.from_bytes_context(res.get('context').encode("cp437"))
HE.from_bytes_public_key(res.get('pkey').encode("cp437"))


cyphervalue = HE.encrypt(plainvalue)
s_cyphervalue = cyphervalue.to_bytes()


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


print("Checking results")
r = requests.get(
        url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/results'
    )

result = r.text[1:-1].split()
result = [ int(r) for r in result ]
winner = Candidats[result.index(max(result))]
print(f"Winner is : {winner}")