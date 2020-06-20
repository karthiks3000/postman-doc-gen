from setuptools import setup, find_packages

setup(name='postman_doc_gen',

      version='1.0.2',

      url='https://github.com/karthiks3000/postman-doc-gen.git',

      license='MIT',

      author='Karthik Subramanian',

      author_email='karthiks3000@yahoo.com',

      description='Converts a postman collection into an HTML documentation',

      packages=find_packages(exclude=['tests']),

      long_description=open('README.md').read(),

      zip_safe=False,

      setup_requires=['fastjsonschema>=2.14', 'Jinja2>=2.11', 'MarkupSafe>=1.1'],
      python_requires='>=3.0')
