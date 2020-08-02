import json


class KeyValueModel:
    key: str = None
    description: str = None
    value: str = None

    def __init__(self, key, value, desc):
        self.key = key
        self.value = value
        self.description = desc


class APIBodyModel:
    mode: str = ''
    raw: str = None
    key_values: list = None


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
    body: APIBodyModel = None
    headers: list = None
    params: list = None
    path_variables: list = None

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
    file_name: str = None
    env_file_name: str = None

    def __init__(self):
        super().__init__()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
