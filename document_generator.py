import os
import json
from collections import OrderedDict
from models import APIExampleModel, APIModel, APICollectionModel
from jinja2 import Environment, FileSystemLoader
from fastjsonschema import validate, JsonSchemaDefinitionException


class DocumentGenerator():
    side_tree = OrderedDict()
    api_info = []
    api_collection: APICollectionModel
    api_id_counter: int
    response_id: int

    def __init__(self):
        super().__init__()
    
    def generate_doc(self):
        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('index.html')

        json_collection = DocumentGenerator.validate_collection('postman_collection.json')

        self.api_collection = APICollectionModel()

        self.api_collection.name = json_collection['info']['name']
        self.api_collection.description = json_collection['info']['description']
        self.api_collection.schema = json_collection['info']['schema']

        self.side_tree = []
        self.api_id_counter = 0
        self.response_id = 0
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

    @staticmethod
    def validate_collection(file_name) -> json:
        root = os.path.dirname(os.path.abspath(__file__))
        postman_filename = os.path.join(root, file_name)
        schema_filename = os.path.join(root, 'schemas', 'schema_2_1_0.json')

        with open(postman_filename) as f:
            json_collection = json.load(f)

        with open(schema_filename) as f:
            json_schema = json.load(f)

        validate(json_schema, json_collection)
        return json_collection

    def add_items(self, tree, json_node):
        for item in json_node['item']:
            if item.get('item', None) is not None:
                node = {}
                node['text'] = item.get('name', '[Name Missing]')
                subnodes = []
                self.add_items(subnodes, item)
                node['nodes'] = subnodes
                node['icon'] = 'fas fa-folder'
                node['selectable'] = 'false'
                tree.append(node)

            else:
                self.api_id_counter = self.api_id_counter + 1
                node = {}
                node['text'] = item.get('name', '[Name Missing]')
                node['href'] = '#' + str(self.api_id_counter)
                node['method'] = item.get('request').get('method', 'None')
                tree.append(node)
                self.add_apis(item)

    def add_apis(self, item):
        api = APIModel()
        api.id = self.api_id_counter
        api.name = item.get('name', '[Name Missing]')
        if item.get('request').get('description', None) is not None:
            api.description = item.get('request').get('description')
        if item.get('request').get('body', None) is not None:
            api.body = item.get('request').get('body').get('raw', None)
        api.method = item.get('request').get('method')
        if item.get('request').get('url', None) is not None:
            api.url = item.get('request').get('url').get('raw')
        api.examples = self.get_examples(api, item.get('response', []))
        self.api_info.append(api)

    def get_examples(self, api, json_responses) -> list:
        examples = []

        for res in json_responses:
            self.response_id = self.response_id + 1
            api_example = APIExampleModel()
            api_example.request_id = str(self.api_id_counter)
            api_example.id = 'response_' + str(self.response_id)
            api_example.name = res.get('name', '[Name Missing]')
            api_example.method = res.get('originalRequest').get('method')
            if api.url is not None:
                api_example.request_body = '\n' + api.method + ' ' + api.url
            if res.get('originalRequest').get('body', None) is not None:
                api_example.request_body = api_example.request_body + '\n' + res.get('originalRequest').get('body').get('raw', None)
            api_example.url = res.get('originalRequest').get('url').get('raw')
            api_example.status = res.get('status')
            api_example.code = res.get('code')
            api_example.response_body = '\n' + res.get('body', '')
            examples.append(api_example)

        if len(examples) == 0:
            self.response_id = self.response_id + 1
            api_example = APIExampleModel()
            api_example.request_id = str(self.api_id_counter)
            api_example.id = 'response_' + str(self.response_id)
            api_example.name = api.name
            api_example.method = api.method
            api_example.request_body = '\n' + api.method + ' ' + api.url
            api_example.url = api.url
            examples.append(api_example)

        return examples


d = DocumentGenerator()
d.generate_doc()
