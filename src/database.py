from pathlib import Path
import json

DATABASE = "db.json"


def save_data(data_obj):
    if not data_obj:
        return False
    with open(DATABASE, "w+") as fp:
        fp.write(json.dumps(data_obj, indent=4))
    return True


def load_data():
    global DATABASE

    if not Path(DATABASE).exists():
        with open(DATABASE, "w+") as fpcreate:
            pass

    with open(DATABASE, "r+") as fp:
        r = fp.read()
    try:
        dataobj = json.loads(r)
    except:
        dataobj = {}

    return dataobj


def init_data():
    dataobj = load_data()
    save_data(dataobj)

    return dataobj


def check_token(token: str):
    obj = load_data()
    if obj.get(token, True) == False:
        # Vote valid
       obj[token] = True
       save_data(obj)
       return True
    return False
    