import json
import os
from collections import OrderedDict
from distutils.dir_util import copy_tree

from fastjsonschema import validate
from jinja2 import Environment, FileSystemLoader

import constants
from models import APIExampleModel, APIModel, APICollectionModel


class DocumentGenerator:
    side_tree = OrderedDict()
    api_info = []
    api_collection: APICollectionModel
    api_id_counter: int
    response_id: int
    env_file = None

    def __init__(self):
        super().__init__()

    def generate_doc(self, collection_file_name, environment_file_name=None, output_dir=None):
        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, constants.TEMPLATES_DIR)
        template = self.get_template(templates_dir)

        json_collection = self.validate_collection(collection_file_name)
        if environment_file_name is not None:
            self.env_file = self.get_json_file(environment_file_name)

        self.api_collection = APICollectionModel()

        self.api_collection.name = json_collection[constants.INFO][constants.NAME]
        self.api_collection.description = json_collection[constants.INFO].get(constants.DESCRIPTION, '')
        self.api_collection.schema = json_collection[constants.INFO][constants.SCHEMA]

        self.side_tree = []
        self.api_id_counter = 0
        self.response_id = 0
        self.add_items(self.side_tree, json_collection)

        if output_dir is None:
            output_dir = os.path.join(root, constants.OUTPUT_DIR)

        filename = os.path.join(output_dir, constants.OUTPUT_FILE_NAME)
        css_dir = os.path.join(root, constants.TEMPLATES_DIR, constants.CSS_DIR)
        js_dir = os.path.join(root, constants.TEMPLATES_DIR, constants.JS_DIR)

        copy_tree(css_dir, os.path.join(output_dir, constants.CSS_DIR))
        copy_tree(js_dir, os.path.join(output_dir, constants.JS_DIR))

        with open(filename, 'w') as fh:
            fh.write(template.render(
                collection=self.api_collection,
                side_tree=self.side_tree,
                api_info=self.api_info
            ))

    @staticmethod
    def get_template(templates_dir):
        env = Environment(loader=FileSystemLoader(templates_dir))
        return env.get_template(constants.TEMPLATE_FILE_NAME)

    @staticmethod
    def get_json_file(file_name):
        with open(file_name) as f:
            json_file = json.load(f)
        return json_file

    @staticmethod
    def validate_collection(file_name) -> json:
        root = os.path.dirname(os.path.abspath(__file__))
        schema_filename = os.path.join(root, constants.POSTMAN_SCHEMA_DIR, constants.POSTMAN_JSON_SCHEMA)

        json_collection = DocumentGenerator.get_json_file(file_name)

        json_schema = DocumentGenerator.get_json_file(schema_filename)

        validate(json_schema, json_collection)
        return json_collection

    @staticmethod
    def escape_string(value):
        return value.replace('\"', '\\"')

    @staticmethod
    def apply_env_values(json_collection, json_env):
        if json_env is None:
            return json_collection
        collection_string = json.dumps(json_collection)

        for item in json_env['values']:
            key = '{{' + str(item['key']) + '}}'
            value = DocumentGenerator.escape_string(str(item['value']))

            collection_string = collection_string.replace(key, value)

        return json.loads(collection_string)

    @staticmethod
    def apply_env_values_string(string_value, json_env):
        if json_env is None:
            return string_value

        for item in json_env['values']:
            key = '{{' + str(item['key']) + '}}'
            value = DocumentGenerator.escape_string(str(item['value']))

            string_value = string_value.replace(key, value)

        return string_value

    def add_items(self, tree, json_node):
        for item in json_node['item']:
            if item.get('item', None) is not None:
                node = dict()
                node['text'] = item.get(constants.NAME, constants.NOT_FOUND)
                subnodes = []
                self.add_items(subnodes, item)
                node['nodes'] = subnodes
                node['icon'] = constants.FOLDER_ICON
                node['selectable'] = 'false'
                tree.append(node)

            else:
                self.api_id_counter = self.api_id_counter + 1
                node = dict()
                node['text'] = item.get(constants.NAME, constants.NOT_FOUND)
                node['href'] = '#' + str(self.api_id_counter)
                node[constants.METHOD] = item.get(constants.REQUEST).get(constants.METHOD, 'None')
                tree.append(node)
                self.add_apis(item)

    def add_apis(self, item):
        api = APIModel()
        api.id = self.api_id_counter
        api.name = item.get(constants.NAME, constants.NOT_FOUND)
        if item.get(constants.REQUEST).get(constants.DESCRIPTION, None) is not None:
            api.description = item.get(constants.REQUEST).get(constants.DESCRIPTION)
        if item.get(constants.REQUEST).get(constants.BODY, None) is not None:
            api.body = item.get(constants.REQUEST).get(constants.BODY).get(constants.RAW, None)

        if api.body is not None:
            api.body = '\n' + api.body.strip()  # append a line break for better formatting of jsons

        api.method = item.get(constants.REQUEST).get(constants.METHOD)
        if item.get(constants.REQUEST).get(constants.URL, None) is not None:
            api.url = item.get(constants.REQUEST).get(constants.URL).get(constants.RAW)
        api.examples = self.get_examples(api, item.get(constants.RESPONSE, []))
        self.api_info.append(api)

    def get_examples(self, api, json_responses) -> list:
        examples = []

        if self.env_file is not None:
            json_responses = self.apply_env_values(json_responses, self.env_file)

        for res in json_responses:
            self.response_id = self.response_id + 1
            api_example = APIExampleModel()
            api_example.request_id = str(self.api_id_counter)
            api_example.id = 'response_' + str(self.response_id)
            api_example.name = res.get(constants.NAME, constants.NOT_FOUND)
            api_example.method = res.get(constants.ORIGINAL_REQUEST).get(constants.METHOD)
            api_example.url = res.get(constants.ORIGINAL_REQUEST).get(constants.URL).get(constants.RAW)
            if api_example.url is not None:
                api_example.request_body = '\n' + api_example.method + ' ' + api_example.url
            if res.get(constants.ORIGINAL_REQUEST).get(constants.BODY, None) is not None:
                api_example.request_body = api_example.request_body + '\n' + res.get(constants.ORIGINAL_REQUEST).get(
                    constants.BODY).get(constants.RAW, None)

            api_example.status = res.get(constants.STATUS)
            api_example.code = res.get(constants.CODE)
            api_example.response_body = '\n' + res.get(constants.BODY, '')
            examples.append(api_example)

        if len(examples) == 0:

            self.response_id = self.response_id + 1
            api_example = APIExampleModel()
            api_example.request_id = str(self.api_id_counter)
            api_example.id = 'response_' + str(self.response_id)
            api_example.name = api.name
            api_example.method = api.method
            if api.url is not None:
                api_example.url = self.apply_env_values_string(api.url, self.env_file)

            if api_example.url is not None:
                api_example.request_body = '\n' + api_example.method + ' ' + api_example.url
            if api.body is not None:
                api_example.request_body = api_example.request_body + '\n' + self.apply_env_values(api.body, self.env_file)
            examples.append(api_example)

        return examples

