import unittest

from constants import RAW, URL_ENCODED
from document_generator import DocumentGenerator
from models import APIModel, APIBodyModel


class DocumentGeneratorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.json_env = {
            "id": "b052da30-a4fe-41be-9d36-c7eccd5fa7ef",
            "name": "Sample-Env",
            "values": [
                {
                    "key": "HOST",
                    "value": "https://cpd-service.dev.apps.scholastic.tech",
                    "enabled": True
                },
                {
                    "key": "SAMPLE_ID",
                    "value": 5964,
                    "enabled": True
                },
                {
                    "key": "SAMPLE_NAME",
                    "value": "Test",
                    "enabled": True
                }
            ]
        }

        self.request_body = APIBodyModel
        self.request_body.mode = RAW
        self.request_body.raw = "{\n\t\"id\": null,\n\t\"name\": {{SAMPLE_NAME}},\n\t\"array\": [\n\t\t{\n\t\t\t\"someId\":123\n\t\t}\n\t]\n\t\n}"
        self.request_body_formatted ="{\n\t\"id\": null,\n\t\"name\": Test,\n\t\"array\": [\n\t\t{\n\t\t\t\"someId\":123\n\t\t}\n\t]\n\t\n}"

        self.response_body = "{\n\t\"id\": {{SAMPLE_ID}},\n\t\"name\": {{SAMPLE_NAME}},\n\t\"array\": [\n\t\t{\n\t\t\t\"someId\":123\n\t\t}\n\t]\n\t\n}"
        self.response_body_formatted = "{\n\t\"id\": 5964,\n\t\"name\": Test,\n\t\"array\": [\n\t\t{\n\t\t\t\"someId\":123\n\t\t}\n\t]\n\t\n}"

        self.request_body_raw = {
            "mode": "raw",
            "raw": "{\n\t\"id\": null,\n\t\"name\": {{SAMPLE_NAME}},\n\t\"array\": [\n\t\t{\n\t\t\t\"someId\":123\n\t\t}\n\t]\n\t\n}",
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }

        self.json_responses = [
            {
                "name": "Example 1",
                "originalRequest": {
                    "method": "POST",
                    "header": [],
                    "body": self.request_body_raw,
                    "url": {
                        "raw": "{{HOST}}/sample/url/path",
                        "host": [
                            "{{HOST}}"
                        ],
                        "path": [
                            "sample",
                            "url",
                            "path"
                        ]
                    }
                },
                "_postman_previewlanguage": "json",
                "header": None,
                "cookie": [],
                "body": self.response_body
            },
            {
                "name": "Example 2",
                "_postman_previewlanguage": "json",
                "header": None,
                "cookie": [],
                "body": self.response_body
            }
        ]

        self.url_encoded_body_json = {
            "mode": "urlencoded",
            "urlencoded": [
                {
                    "key": "key1",
                    "value": "value1",
                    "description": "test description 1"
                },
                {
                    "key": "key2",
                    "value": "<string>"
                }
            ]
        }

        self.json_request = {
            "name": "Request 1",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/x-www-form-urlencoded"
                    }
                ],
                "body": self.url_encoded_body_json,
                "url": {
                    "raw": "{{HOST}}/sample/url/path?query_param=<string>",
                    "host": [
                        "{{HOST}}"
                    ],
                    "path": [
                        "sample",
                        "url",
                        "path"
                    ],
                    "query": [
                        {
                            "key": "query_param",
                            "value": "<string>",
                            "description": "Sample query description"
                        }
                    ],
                    "variable": [
                        {
                            "key": "request.url.host",
                            "value": "{{request.url.host}}",
                            "description": {
                                "content": "",
                                "type": "text/plain"
                            }
                        },
                        {
                            "key": "request.url.port",
                            "value": "{{request.url.port}}",
                            "description": {
                                "content": "",
                                "type": "text/plain"
                            }
                        }
                    ]
                },
                "description": "Sample request description"
            }
        }

        self.document_generator = DocumentGenerator()

    def test_escape_string(self):
        escaped_string = DocumentGenerator.escape_string('test\"this\"')
        self.assertEqual('test\\"this\\"', escaped_string)

    def test_apply_env_values(self):
        json_collection = {
            'testNumber': '{{SAMPLE_ID}}',
            'testUrl': '{{HOST}}',
            'testString': '{{SAMPLE_NAME}}'
        }

        formatted_json = DocumentGenerator.apply_env_values(json_collection, self.json_env)

        self.assertEqual('5964', formatted_json['testNumber'])
        self.assertEqual('https://cpd-service.dev.apps.scholastic.tech', formatted_json['testUrl'])
        self.assertEqual('Test', formatted_json['testString'])

    def test_apply_env_values_string(self):
        json_string = '{{HOST}}/test/{{SAMPLE_ID}}'

        formatted_string = DocumentGenerator.apply_env_values_string(json_string, self.json_env)

        self.assertEqual('https://cpd-service.dev.apps.scholastic.tech/test/5964', formatted_string)

    def test_get_examples(self):
        api = APIModel()
        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1

        examples = self.document_generator.get_examples(api, self.json_responses)
        self.assertEqual(2, len(examples))
        for api_example in examples:
            if api_example.name == 'Example 1':
                self.assertEqual('1', api_example.request_id)
                self.assertEqual('response_11', api_example.id)
                self.assertEqual('POST', api_example.method)
                self.assertEqual('{{HOST}}/sample/url/path', api_example.url)
                self.assertEqual('\nPOST {{HOST}}/sample/url/path\n' + self.request_body.raw, api_example.request_body)
                self.assertIsNone(api_example.status)
                self.assertIsNone(api_example.code)
                self.assertEqual('\n' + self.response_body, api_example.response_body)

            elif api_example.name == 'Example 2':
                self.assertEqual('1', api_example.request_id)
                self.assertEqual('response_12', api_example.id)
                self.assertIsNone(api_example.method)
                self.assertIsNone(api_example.url)
                self.assertIsNone(api_example.request_body)
                self.assertIsNone(api_example.status)
                self.assertIsNone(api_example.code)
                self.assertEqual('\n' + self.response_body, api_example.response_body)

    def test_get_examples_with_env(self):
        api = APIModel()
        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1
        self.document_generator.env_file = self.json_env

        examples = self.document_generator.get_examples(api, self.json_responses)
        self.assertEqual(2, len(examples))
        for api_example in examples:
            if api_example.name == 'Example 1':
                self.assertEqual('1', api_example.request_id)
                self.assertEqual('response_11', api_example.id)
                self.assertEqual('POST', api_example.method)
                self.assertEqual('https://cpd-service.dev.apps.scholastic.tech/sample/url/path', api_example.url)
                self.assertEqual('\nPOST https://cpd-service.dev.apps.scholastic.tech/sample/url/path\n'
                                 + self.request_body_formatted, api_example.request_body)
                self.assertIsNone(api_example.status)
                self.assertIsNone(api_example.code)
                self.assertEqual('\n' + self.response_body_formatted, api_example.response_body)
            elif api_example.name == 'Example 2':
                self.assertEqual('1', api_example.request_id)
                self.assertEqual('response_12', api_example.id)
                self.assertIsNone(api_example.method)
                self.assertIsNone(api_example.url)
                self.assertIsNone(api_example.request_body)
                self.assertIsNone(api_example.status)
                self.assertIsNone(api_example.code)
                self.assertEqual('\n' + self.response_body_formatted, api_example.response_body)

    def test_get_examples_from_api(self):
        api = APIModel()
        api.id = 11
        api.name = 'Example 1'
        api.url = '{{HOST}}/sample/url/path'
        api.body = self.request_body
        api.method = 'POST'

        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1

        examples = self.document_generator.get_examples(api, [])
        self.assertEqual(1, len(examples))
        api_example = examples[0]

        self.assertEqual('1', api_example.request_id)
        self.assertEqual('response_11', api_example.id)
        self.assertEqual('Example 1', api_example.name)
        self.assertEqual('POST', api_example.method)
        self.assertEqual('{{HOST}}/sample/url/path', api_example.url)
        self.assertEqual('\nPOST {{HOST}}/sample/url/path\n' + self.request_body.raw, api_example.request_body)
        self.assertIsNone(api_example.status)
        self.assertIsNone(api_example.code)

    def test_get_examples_from_api_no_body(self):
        api = APIModel()
        api.id = 11
        api.name = 'Example 1'
        api.url = None
        api.body = None
        api.method = 'POST'

        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1

        examples = self.document_generator.get_examples(api, [])
        self.assertEqual(1, len(examples))
        api_example = examples[0]

        self.assertEqual('1', api_example.request_id)
        self.assertEqual('response_11', api_example.id)
        self.assertEqual('Example 1', api_example.name)
        self.assertEqual('POST', api_example.method)
        self.assertIsNone(api_example.url)
        self.assertIsNone(api_example.request_body)
        self.assertIsNone(api_example.status)
        self.assertIsNone(api_example.code)

    def test_get_examples_from_api_only_url(self):
        api = APIModel()
        api.id = 11
        api.name = 'Example 1'
        api.url = '{{HOST}}/sample/url/path'
        api.body = None
        api.method = 'GET'

        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1

        examples = self.document_generator.get_examples(api, [])
        self.assertEqual(1, len(examples))
        api_example = examples[0]

        self.assertEqual('1', api_example.request_id)
        self.assertEqual('response_11', api_example.id)
        self.assertEqual('Example 1', api_example.name)
        self.assertEqual('GET', api_example.method)
        self.assertEqual('{{HOST}}/sample/url/path', api_example.url)
        self.assertEqual('\nGET {{HOST}}/sample/url/path', api_example.request_body)
        self.assertIsNone(api_example.status)
        self.assertIsNone(api_example.code)

    def test_get_examples_from_api_method_and_body(self):
        api = APIModel()
        api.id = 11
        api.name = 'Example 1'
        api.url = None
        api.body = self.request_body
        api.method = 'POST'

        self.document_generator.response_id = 10
        self.document_generator.api_id_counter = 1

        examples = self.document_generator.get_examples(api, [])
        self.assertEqual(1, len(examples))
        api_example = examples[0]

        self.assertEqual('1', api_example.request_id)
        self.assertEqual('response_11', api_example.id)
        self.assertEqual('Example 1', api_example.name)
        self.assertEqual('POST', api_example.method)
        self.assertIsNone(api_example.url)
        self.assertEqual('\n' + self.request_body.raw, api_example.request_body)
        self.assertIsNone(api_example.status)
        self.assertIsNone(api_example.code)

    def test_get_body_encoded(self):
        api_body = DocumentGenerator.get_body(self.url_encoded_body_json)
        self.assertEqual(URL_ENCODED, api_body.mode)
        self.assertEqual(2, len(api_body.key_values))
        self.assertEqual('key1', api_body.key_values[0].key)
        self.assertEqual('value1', api_body.key_values[0].value)
        self.assertEqual('test description 1', api_body.key_values[0].description)
        self.assertEqual('key2', api_body.key_values[1].key)
        self.assertEqual('&lt;string&gt;', api_body.key_values[1].value)
        self.assertIsNone(api_body.key_values[1].description)

    def test_get_body_raw(self):
        api_body = DocumentGenerator.get_body(self.request_body_raw)
        self.assertEqual(RAW, api_body.mode)
        self.assertIsNone(api_body.key_values)
        self.assertEqual(self.request_body.raw, api_body.raw)

    def test_add_api(self):
        self.document_generator.response_id = 0
        self.document_generator.api_id_counter = 1

        self.assertEqual(0, len(self.document_generator.api_info))

        self.document_generator.add_apis(self.json_request)

        self.assertEqual(1, len(self.document_generator.api_info))

        api_model: APIModel = self.document_generator.api_info[0]

        self.assertEqual(1, api_model.id)
        self.assertEqual("Request 1", api_model.name)
        self.assertEqual("Sample request description", api_model.description)
        self.assertEqual(URL_ENCODED, api_model.body.mode)
        self.assertEqual("POST", api_model.method)
        self.assertEqual(1, len(api_model.headers))
        self.assertEqual(1, len(api_model.params))
        self.assertEqual(2, len(api_model.path_variables))
        self.assertEqual("{{HOST}}/sample/url/path?query_param=<string>", api_model.url)

