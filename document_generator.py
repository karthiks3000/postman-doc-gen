import os
import json
from collections import OrderedDict
from APIModel import APIModel

class DocumentGenerator():
    side_tree = OrderedDict()
    api_info = []

    def __init__(self):
        super().__init__()
    
    def generate_doc(self):
        root = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(root, 'postman_collection.json')
        with open(filename) as f:
            json_collection = json.load(f)

        collection_title = json_collection['info']['name']
        collection_desc = json_collection['info']['description']
        side_tree = OrderedDict()
        self.add_items(self.side_tree, json_collection)

        print(json.dumps(side_tree, indent=4))
        # print(self.api_info)

    def add_items(self, tree, json_node):
        for item in json_node['item']:
            if(item.get('item', None) != None):
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

                self.api_info.append(api)
                # print(api.toJSON())


d = DocumentGenerator()
d.generate_doc()