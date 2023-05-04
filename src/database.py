import json
from pathlib import Path

DATABASE = "db.json"

"""
dict = {
    "Voters": {
        # Votant : A voté
        "Pierre": False, 
        "Lulu": False,
        "Adrien": False
    },

    "Candidats": {
        # Nom : Count
        "Macron": 0,
        "Poutine": 0,
        "Bashar Al Assad": 0,
    },
}
"""


class Database():
    def __init__(self) -> None:
        dataobj = self.get_data()
        self.save_data(dataobj)

        self.data = dataobj

    def save_data(self, data_obj):
        if not data_obj:
            return False
        with open(DATABASE, "w+") as fp:
            fp.write(json.dumps(data_obj, indent=4))
        return True


    def get_data(self):
        global DATABASE

        # Create if not exists
        if not Path(DATABASE).exists():
            with open(DATABASE, "w+") as openfp:
                pass

        with open(DATABASE, "r+") as fp:
            r = fp.read()
        try:
            dataobj = json.loads(r)
        except:
            dataobj = {}

        dataobj['Voters'] = dataobj.get("Voters", {})
        dataobj['Candidats'] = dataobj.get("Candidats", {})

        return dataobj


if (__name__ == "__main__"):
    d = Database()
    print(d.get_data())
