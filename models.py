import json


class APIExampleModel:
    id: str = None
    request_id: str = None
    name: str = None
    method: str = None
    request_body: str
    url: str = None
    status: str = None
    code: int = None
    response_body: str

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class APIModel:
    id: int = None
    name: str = None
    description: str = None
    method: str = None
    body: str = None
    url: str = None
    examples: list = []

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class APICollectionModel:
    name: str = None
    description: str = None
    schema: str = None

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
