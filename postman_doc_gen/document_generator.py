import json
import os
import shutil
from collections import OrderedDict
from distutils.dir_util import copy_tree

import markdown

import bleach
from fastjsonschema import validate
from jinja2 import Environment, FileSystemLoader

from constants import *
from models import APIExampleModel, APIModel, APICollectionModel, APIBodyModel, KeyValueModel


class DocumentGenerator:
    side_tree = OrderedDict()
    api_info = []
    api_collection: APICollectionModel
    api_id_counter: int
    response_id: int
    env_file = None

    def __init__(self):
        super().__init__()

    def generate_doc(self, collection_file_name: str, environment_file_name: str = None, output_dir: object = None,
                     download_enabled: bool = False) -> object:
        """
        :param collection_file_name: [Required] postman collection json
        :param environment_file_name: [Optional] postman environment json
        :param output_dir: [Optional] defaults to current directory
        :return: the output directory used
        """

        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, TEMPLATES_DIR)
        template = self.get_template(templates_dir)

        json_collection = self.validate_collection(collection_file_name)
        if environment_file_name is not None:
            self.env_file = self.get_json_file(environment_file_name)

        if output_dir is None:
            output_dir = os.path.join(root, OUTPUT_DIR)

        filename = os.path.join(output_dir, OUTPUT_FILE_NAME)
        css_dir = os.path.join(root, TEMPLATES_DIR, CSS_DIR)
        js_dir = os.path.join(root, TEMPLATES_DIR, JS_DIR)
        collection_destination = os.path.join(output_dir, os.path.basename(collection_file_name))

        self.api_collection = APICollectionModel()

        self.api_collection.name = json_collection[INFO][NAME]
        self.api_collection.description = json_collection[INFO].get(DESCRIPTION, '')
        self.api_collection.schema = json_collection[INFO][SCHEMA]
        self.api_collection.file_name = os.path.basename(collection_file_name)

        self.side_tree = []
        self.api_id_counter = 0
        self.response_id = 0
        self.add_items(self.side_tree, json_collection)

        if environment_file_name is not None and download_enabled:
            self.api_collection.env_file_name = os.path.basename(environment_file_name)
            env_destination = os.path.join(output_dir, os.path.basename(environment_file_name))
            DocumentGenerator.copy_file(environment_file_name, env_destination)

        if download_enabled:
            DocumentGenerator.copy_file(collection_file_name, collection_destination)
        copy_tree(css_dir, os.path.join(output_dir, CSS_DIR))
        copy_tree(js_dir, os.path.join(output_dir, JS_DIR))

        with open(filename, 'w') as fh:
            fh.write(template.render(
                download_enabled=download_enabled,
                collection=self.api_collection,
                side_tree=self.side_tree,
                api_info=self.api_info
            ))

        return output_dir

    @staticmethod
    def copy_file(src, dest):
        try:
            shutil.copyfile(src, dest)
        except shutil.SameFileError:
            pass

    @staticmethod
    def get_template(templates_dir):
        """
        Loads the JINJA 2 template file and returns it
        :param templates_dir: the directory containing the template
        :return: the JINJA 2 template
        """
        env = Environment(loader=FileSystemLoader(templates_dir))
        return env.get_template(TEMPLATE_FILE_NAME)

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
        schema_filename = os.path.join(root, POSTMAN_SCHEMA_DIR, POSTMAN_JSON_SCHEMA)

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
        if value is None:
            return None
        return value.replace('\"', '\\"').replace('<', '&lt;').replace('>', '&gt;')

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
                node['text'] = item.get(NAME, NOT_FOUND)
                sub_nodes = []
                self.add_items(sub_nodes, item)
                node['nodes'] = sub_nodes
                node['icon'] = FOLDER_ICON
                node['selectable'] = 'false'
                tree.append(node)

            else:
                self.api_id_counter = self.api_id_counter + 1
                node = dict()
                node['text'] = item.get(NAME, NOT_FOUND)
                node['href'] = '#' + str(self.api_id_counter)
                node[METHOD] = item.get(REQUEST, {}).get(METHOD, 'None')
                tree.append(node)
                self.add_apis(item)

    def add_apis(self, item: json):
        """
        Creates an APIModel and adds it to api_info
        :param item: json node representing an api
        """
        api = APIModel()
        api.id = self.api_id_counter
        api.name = item.get(NAME, NOT_FOUND)
        api.body = None
        if item.get(REQUEST, {}).get(DESCRIPTION, None) is not None:
            api.description = item.get(REQUEST, {}).get(DESCRIPTION, None)
            api.description = self.markdown_to_html(api.description)

        if item.get(REQUEST, {}).get(BODY, None) is not None:
            api.body = self.get_body(item.get(REQUEST).get(BODY))

        if api.body is not None and api.body.raw is not None:
            api.body.raw = '\n' + api.body.raw.strip()  # append a line break for better formatting of jsons
            api.body.raw = bleach.clean(api.body.raw)

        api.method = item.get(REQUEST, {}).get(METHOD, None)

        headers = item.get(REQUEST, {}).get(HEADER, None)
        if headers is not None:
            api.headers = DocumentGenerator.get_key_values(headers)

        if item.get(REQUEST, {}).get(URL, None) is not None:
            api.url = item.get(REQUEST, {}).get(URL, {}).get(RAW, None)

            query_params = item.get(REQUEST, {}).get(URL, {}).get(QUERY, None)
            if query_params is not None:
                api.params = DocumentGenerator.get_key_values(query_params)

            path_variables = item.get(REQUEST, {}).get(URL, {}).get(PATH_VARIABLE, None)
            if path_variables is not None:
                api.path_variables = DocumentGenerator.get_key_values(path_variables)

        api.examples = self.get_examples(api, item.get(RESPONSE, []))
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
            api_example.name = res.get(NAME, NOT_FOUND)
            api_example.method = res.get(ORIGINAL_REQUEST, {}).get(METHOD, None)
            api_example.url = res.get(ORIGINAL_REQUEST, {}).get(URL, {}).get(RAW, None)
            api_example.request_body = None

            if api_example.method is not None:
                api_example.request_body = '\n' + api_example.method

            if api_example.url is not None and api_example.request_body is not None:
                api_example.request_body = api_example.request_body + ' ' + api_example.url

            if res.get(ORIGINAL_REQUEST, {}).get(BODY, None) is not None:
                api_example.request_body = (api_example.request_body if api_example.request_body is not None else '') \
                    + '\n' + res.get(ORIGINAL_REQUEST).get(BODY).get(RAW, '')

                api_example.request_body = bleach.clean(api_example.request_body)

            api_example.status = res.get(STATUS, None)
            api_example.code = res.get(CODE, None)

            api_example.response_body = res.get(BODY, None)
            if api_example.response_body is not None:
                api_example.response_body = '\n' + api_example.response_body
                api_example.response_body = bleach.clean(api_example.response_body)
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

            if api.body is not None and api.body.raw is not None:
                api_example.request_body = (api_example.request_body if api_example.request_body is not None else '') \
                                           + '\n' + self.apply_env_values(api.body.raw, self.env_file)

            examples.append(api_example)

        return examples

    @staticmethod
    def markdown_to_html(md_text):
        """
        Converts the markdown text to html
        :param md_text: the text with markdown
        :return: the converted html code
        """
        return markdown.markdown(md_text, extensions=['markdown.extensions.abbr',
                                                      'markdown.extensions.attr_list', 'markdown.extensions.def_list',
                                                      'markdown.extensions.fenced_code',
                                                      'markdown.extensions.footnotes',
                                                      'markdown.extensions.md_in_html', 'markdown.extensions.tables',
                                                      'markdown.extensions.admonition',
                                                      'markdown.extensions.codehilite',
                                                      'markdown.extensions.legacy_attrs',
                                                      'markdown.extensions.legacy_em',
                                                      'markdown.extensions.meta', 'markdown.extensions.nl2br',
                                                      'markdown.extensions.sane_lists', 'markdown.extensions.smarty',
                                                      'markdown.extensions.toc', 'markdown.extensions.wikilinks'],
                                 output_format='html5')

    @staticmethod
    def get_body(body: json) -> APIBodyModel:
        """
        Extracts the contents from the body json. Either raw or urlencoded
        :param body: the current APIModel object being explored
        :return: instance of APIBodyModel
        """
        api_body = APIBodyModel()
        api_body.mode = body.get(MODE, '')
        if body.get(RAW, None) is not None:
            api_body.raw = body.get(RAW)
        elif body.get(api_body.mode, None) is not None:
            api_body.key_values = DocumentGenerator.get_key_values(body.get(api_body.mode))

        return api_body

    @staticmethod
    def get_key_values(item_list: json) -> list:
        if item_list is None or len(item_list) == 0:
            return None

        key_value_list = []

        for item in item_list:
            value_string = DocumentGenerator.escape_string(item.get(VALUE))
            if type(item.get(DESCRIPTION)) == str:
                desc_string = DocumentGenerator.escape_string(item.get(DESCRIPTION))
            else:
                desc_string = DocumentGenerator.escape_string(
                    item.get(DESCRIPTION, {}).get(CONTENT, None))

            key_value_list.append(
                KeyValueModel(item.get(KEY), value_string, desc_string)
            )
        return key_value_list
