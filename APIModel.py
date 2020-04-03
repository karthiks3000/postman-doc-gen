import json
class APIModel():
    name:str
    description:str
    method:str
    body:str
    url:str

    def __init__(self):
        super().__init__()
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    

