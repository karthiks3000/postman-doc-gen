import os
import json
from collections import OrderedDict
from models import ResponseModel, APIModel, APICollectionModel
from jinja2 import Environment, FileSystemLoader


class DocumentGenerator():
    side_tree = OrderedDict()
    api_info = []
    api_collection: APICollectionModel

    def __init__(self):
        super().__init__()
    
    def generate_doc(self):
        root = os.path.dirname(os.path.abspath(__file__))
        postman_filename = os.path.join(root, 'postman_collection.json')
        templates_dir = os.path.join(root, 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('index.html')

        with open(postman_filename) as f:
            json_collection = json.load(f)

        self.api_collection = APICollectionModel()

        self.api_collection.name = json_collection['info']['name']
        self.api_collection.description = json_collection['info']['description']
        self.api_collection.schema = json_collection['info']['schema']

        self.side_tree = OrderedDict()
        self.add_items(self.side_tree, json_collection)

        # print(json.dumps(self.side_tree, indent=4))
        # print(self.api_collection.toJSON())

        filename = os.path.join(root, 'html', 'index.html')

        with open(filename, 'w') as fh:
            fh.write(template.render(
                collection=self.api_collection,
                side_tree=self.side_tree,
                api_info=self.api_info
            ))

    def add_items(self, tree, json_node):
        for item in json_node['item']:
            if item.get('item', None) is not None:
                tree[item.get('name')] = OrderedDict()
                self.add_items(tree[item['name']], item)
            else:
                tree[item.get('name')] = item.get('request').get('url').get('raw')
                api = APIModel()
                api.name = item.get('name')
                api.description = item.get('description')
                api.body = item.get('request').get('body')
                api.method = item.get('request').get('method')
                api.url = item.get('request').get('url').get('raw')
                api.responses = self.get_responses(item.get('response', []))
                self.api_info.append(api)
                # print(api.toJSON())

    def get_responses(self, json_responses) -> list:
        responses = []

        for res in json_responses:
            response = ResponseModel()
            response.name = res.get('name')
            response.method = res.get('originalRequest').get('method')
            if res.get('originalRequest').get('body', None) is not None:
                response.request_body = res.get('originalRequest').get('body', None).get('raw')
            response.url = res.get('originalRequest').get('url').get('raw')
            response.status = res.get('status')
            response.code = res.get('code')
            response.response_body = res.get('body')
            responses.append(response)

        return responses


d = DocumentGenerator()
d.generate_doc()
