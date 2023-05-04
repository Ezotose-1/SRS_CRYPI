import numpy as np
from Pyfhel import Pyfhel, PyCtxt
from flask import *
import requests
from datetime import datetime as dt

from database import *


app = Flask(__name__)

AUTH_SERVER_URL = "127.0.0.1"
AUTH_SERVER_PORT = "9000"

END_TIME = None

@app.route("/vote", methods=["POST"])
def vote_request():
    global ENCRYPT_RESULT, END_TIME
    if (END_TIME and dt.now() > END_TIME):
        return "Error the vote is finished"

    param = request.get_json()
    token = param.get("token")
    cyphervalue = param.get("cyphervalue").encode("cp437")

    if not check_token(token):
        return "Error token already voted"
    
    ENCRYPT_RESULT += PyCtxt(pyfhel=HE, bytestring=cyphervalue)

    return "ok"


@app.route("/results", methods=["GET"])
def vote_result():
    return ENCRYPT_RESULT.to_bytes().decode("cp437")


def load_init_table():
    global END_TIME
    r = requests.get(
        url=f'http://{AUTH_SERVER_URL}:{AUTH_SERVER_PORT}/init'
    )
    res = json.loads(r.text)
    
    HE.from_bytes_context(res.get('context').encode("cp437"))
    HE.from_bytes_public_key(res.get('pkey').encode("cp437"))
    END_TIME = dt.fromtimestamp(res.get('endtime'))

    x = np.array([0] * 4096)
    return HE.encrypt(x)


if __name__ == "__main__":
    HE = Pyfhel()
    try:
        ENCRYPT_RESULT = load_init_table()
    except:
        print(" * Cannot connect to authenticate server, please run it before.")
        print(" * usage : python3 src/server_auth.py")
        exit(1)

    app.run(host="127.0.0.1", port=9001)