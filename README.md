# postman-doc
Generate HTML API documentation from a postman collection.

## Usage

- Download the latest release of the executable from <a href="https://github.com/karthiks3000/postman-doc-gen/releases"> here</a>.
- Open a new terminal and call the executable with the parameter -h to see the help info
    ![Screenshot](./img/iterm1.png?raw=true "Title")

- To generate documentation using a postman collection, use the following command -
    ```
    postman_doc_gen [path/to/collection] -o [path/to/output/folder] 
    ```
    
- The output folder should now show 3 things -
    1. index.html - this is the html documentation generated from the collection
    2. css - this is the css folder consisting of the necessary css files
    3. js - this is the javascript folder consisting of the required js files

- To apply environment values to the examples, use the following command - 
    ```
    postman_doc_gen [path/to/collection] -o [path/to/output/folder] -e [path/to/environment/json]
    ```
 
