from Pyfhel import Pyfhel, PyCtxt
from flask import *
import requests
import secrets
import datetime as dt
import argparse

from database import *

app = Flask(__name__)


parser = argparse.ArgumentParser(
                    prog='CRIPY',
                    description='Auth server')

parser.add_argument('--endtime', required=True)
args = parser.parse_args()

END_TIME = dt.datetime.now()
END_TIME += dt.timedelta(seconds=int(args.endtime))


ADDITION_SERVER_URL = "127.0.0.1"
ADDITION_SERVER_PORT = 9001

voters = {}

def already_voted(digest):
    global voters
    return voters.get(digest, False)


def set_vote(digest):
    global voters
    voters[digest] = True
    return True

@app.route("/results", methods=["GET"])
def result():
    if (dt.datetime.now() < END_TIME):
        return "Error the vote is not finished"
    r = requests.get(
        url=f'http://{ADDITION_SERVER_URL}:{ADDITION_SERVER_PORT}/results'
    )
    c_res = PyCtxt(pyfhel=HE, bytestring=r.text.encode('cp437'))
    res = HE.decrypt(c_res)
    return str(res[:4])


@app.route("/init", methods=["GET"])
def init_table():
    return {
            "pkey": HE.to_bytes_public_key().decode('cp437'),
            "context": HE.to_bytes_context().decode('cp437'),
            "endtime": END_TIME.timestamp()
            }


@app.route("/pk", methods=["GET"])
def get_publickey():
    name = request.args.get('name', None)
    if not name:
        return "Error no name specified"

    if already_voted(name):
        return "Error already voted"
    set_vote(name)

    token = secrets.token_hex(16)  
    
    obj = load_data()
    obj[token] = False
    save_data(obj)

    return {
            "pkey": HE.to_bytes_public_key().decode('cp437'),
            "context": HE.to_bytes_context().decode('cp437'),
            "token": token
        }


if __name__ == "__main__":
    HE = Pyfhel()
    HE.contextGen(scheme='bfv', n=2**12, t_bits=20)
    HE.keyGen()
    init_data()

    app.run(host="127.0.0.1", port=9000)