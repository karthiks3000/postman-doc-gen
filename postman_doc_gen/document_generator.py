import json
import os
from collections import OrderedDict
from distutils.dir_util import copy_tree

import constants
from fastjsonschema import validate
from jinja2 import Environment, FileSystemLoader
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

    def generate_doc(self, collection_file_name: object, environment_file_name: object = None, output_dir: object = None) -> object:
        """
        :param collection_file_name: [Required] postman collection json
        :param environment_file_name: [Optional] postman environment json
        :param output_dir: [Optional] defaults to current directory
        :return: the output directory used
        """

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

        return output_dir

    @staticmethod
    def get_template(templates_dir):
        """
        Loads the JINJA 2 template file and returns it
        :param templates_dir: the directory containing the template
        :return: the JINJA 2 template
        """
        env = Environment(loader=FileSystemLoader(templates_dir))
        return env.get_template(constants.TEMPLATE_FILE_NAME)

    @staticmethod
    def get_json_file(file_name):
        """
        Gets a json file at the specified path
        :param file_name: file path
        :return: the json file at path
        """
        with open(file_name) as f:
            json_file = json.load(f)
        return json_file

    @staticmethod
    def validate_collection(file_name) -> json:
        """
        Validates the postman collection against the postman schema (2.1.0)
        :param file_name: the postman collection file path
        :return: validated collection json
        """
        root = os.path.dirname(os.path.abspath(__file__))
        schema_filename = os.path.join(root, constants.POSTMAN_SCHEMA_DIR, constants.POSTMAN_JSON_SCHEMA)

        json_collection = DocumentGenerator.get_json_file(file_name)

        json_schema = DocumentGenerator.get_json_file(schema_filename)

        validate(json_schema, json_collection)
        return json_collection

    @staticmethod
    def escape_string(value):
        """
        Escapes the '\' character in the string
        :param value: string to format
        :return: formatted string
        """
        return value.replace('\"', '\\"')

    @staticmethod
    def apply_env_values(json_collection, json_env):
        """
        Applies the environment values to the postman collection examples
        :param json_collection: postman collection example json
        :param json_env: postman environment json
        :return: json with replaced values
        """
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
        """
        Applies the environment values to a string
        :param string_value: postman collection example json
        :param json_env: postman environment json
        :return: string with replaced values
        """
        if json_env is None:
            return string_value

        for item in json_env['values']:
            key = '{{' + str(item['key']) + '}}'
            value = DocumentGenerator.escape_string(str(item['value']))

            string_value = string_value.replace(key, value)

        return string_value

    def add_items(self, tree, json_node):
        """
        Recursive method to generate the documentation by exploring the json
        :param tree: dictionary with folders as key and sub folders & api's as values
        :param json_node: the current json node being explored
        """
        for item in json_node['item']:
            if item.get('item', None) is not None:
                node = dict()
                node['text'] = item.get(constants.NAME, constants.NOT_FOUND)
                sub_nodes = []
                self.add_items(sub_nodes, item)
                node['nodes'] = sub_nodes
                node['icon'] = constants.FOLDER_ICON
                node['selectable'] = 'false'
                tree.append(node)

            else:
                self.api_id_counter = self.api_id_counter + 1
                node = dict()
                node['text'] = item.get(constants.NAME, constants.NOT_FOUND)
                node['href'] = '#' + str(self.api_id_counter)
                node[constants.METHOD] = item.get(constants.REQUEST, {}).get(constants.METHOD, 'None')
                tree.append(node)
                self.add_apis(item)

    def add_apis(self, item: json):
        """
        Creates an APIModel and adds it to api_info
        :param item: json node representing an api
        """
        api = APIModel()
        api.id = self.api_id_counter
        api.name = item.get(constants.NAME, constants.NOT_FOUND)
        api.body = None
        if item.get(constants.REQUEST, {}).get(constants.DESCRIPTION, None) is not None:
            api.description = item.get(constants.REQUEST, {}).get(constants.DESCRIPTION, None)
        if item.get(constants.REQUEST, {}).get(constants.BODY, None) is not None:
            api.body = item.get(constants.REQUEST, {}).get(constants.BODY, {}).get(constants.RAW, None)

        if api.body is not None:
            api.body = '\n' + api.body.strip()  # append a line break for better formatting of jsons

        api.method = item.get(constants.REQUEST, {}).get(constants.METHOD, None)
        if item.get(constants.REQUEST, {}).get(constants.URL, None) is not None:
            api.url = item.get(constants.REQUEST, {}).get(constants.URL, {}).get(constants.RAW, None)
        api.examples = self.get_examples(api, item.get(constants.RESPONSE, []))
        self.api_info.append(api)

    def get_examples(self, api: APIModel, json_responses: list) -> list:
        """
        Extracts examples for the current api
        :param api: the current APIModel object being explored
        :param json_responses: list of available examples
        :return: list of APIExampleModel
        """
        examples = []

        if self.env_file is not None:
            json_responses = self.apply_env_values(json_responses, self.env_file)

        for res in json_responses:
            self.response_id = self.response_id + 1
            api_example = APIExampleModel()
            api_example.request_id = str(self.api_id_counter)
            api_example.id = 'response_' + str(self.response_id)
            api_example.name = res.get(constants.NAME, constants.NOT_FOUND)
            api_example.method = res.get(constants.ORIGINAL_REQUEST, {}).get(constants.METHOD, None)
            api_example.url = res.get(constants.ORIGINAL_REQUEST, {}).get(constants.URL, {}).get(constants.RAW, None)
            api_example.request_body = None

            if api_example.url is not None:
                api_example.request_body = '\n' + api_example.method + ' ' + api_example.url
            if res.get(constants.ORIGINAL_REQUEST, {}).get(constants.BODY, None) is not None:
                api_example.request_body = (api_example.request_body if api_example.request_body is not None else '') \
                    + '\n' + res.get(constants.ORIGINAL_REQUEST).get(constants.BODY).get(constants.RAW, None)

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
            api_example.url = None
            api_example.request_body = None

            if api.url is not None:
                api_example.url = self.apply_env_values_string(api.url, self.env_file)

            if api_example.url is not None and api_example.method is not None:
                api_example.request_body = '\n' + api_example.method + ' ' + api_example.url

            if api.body is not None:
                api_example.request_body = (api_example.request_body if api_example.request_body is not None else '') \
                                           + '\n' + self.apply_env_values(api.body, self.env_file)

            examples.append(api_example)

        return examples
