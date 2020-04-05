import os
import json
from collections import OrderedDict
from models import ResponseModel, APIModel, APICollectionModel
from jinja2 import Environment, FileSystemLoader


class DocumentGenerator():
    side_tree = OrderedDict()
    api_info = []
    api_collection: APICollectionModel
    api_id_counter: int

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

        self.side_tree = []
        self.api_id_counter = 0
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
                node = {}
                node['text'] = item.get('name')
                subnodes = []
                self.add_items(subnodes, item)
                node['nodes'] = subnodes
                node['icon'] = 'fas fa-folder'
                node['selectable'] = 'false'
                tree.append(node)

            else:
                self.api_id_counter = self.api_id_counter + 1
                node = {}
                node['text'] = item.get('name')
                node['href'] = '#' + str(self.api_id_counter)
                node['method'] = item.get('request').get('method')
                tree.append(node)
                api = APIModel()
                api.id = self.api_id_counter
                api.name = item.get('name')
                api.description = item.get('description')
                if item.get('request').get('body', None) is not None:
                    api.body = item.get('request').get('body').get('raw')
                api.method = item.get('request').get('method')
                api.url = item.get('request').get('url').get('raw')
                api.responses = self.get_responses(item.get('response', []))
                self.api_info.append(api)

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
