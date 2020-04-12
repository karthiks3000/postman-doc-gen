import json


class APIExampleModel:
    id: str
    request_id: str
    name: str
    method: str
    request_body: str
    url: str
    status: str
    code: int
    response_body: str

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class APIModel:
    id: int
    name: str
    description: str
    method: str
    body: str
    url: str
    examples: list

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class APICollectionModel:
    name: str
    description: str
    schema: str

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
