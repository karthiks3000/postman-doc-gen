from document_generator import DocumentGenerator
import argparse


def init_arg_parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [COLLECTION FILE PATH]",
        description='''Generates an HTML document from a Postman collection. Copies the resulting html file along with 
        css and js to an output directory in the same path, unless an output directory is specified.
        If an environment file is provided, applies the env values to the API examples. '''
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version=f"{parser.prog} Version 1.2.0"
    )
    parser.add_argument('collection', help='The Postman collection json')
    parser.add_argument('-e', '--env', help='The Postman environment json')
    parser.add_argument('-o', '--out', help='The output directory')
    parser.add_argument('-d', '--download', help='Enable download links to the collection and env files', default=False,
                        type=lambda x: (str(x).lower() in ['true', '1', 'yes']))

    return parser


if __name__ == '__main__':
    parser = init_arg_parse()
    args = parser.parse_args()
    d = DocumentGenerator()
    output_dir = d.generate_doc(args.collection, args.env, args.out, args.download)
    print("Success. Document generated at " + output_dir)