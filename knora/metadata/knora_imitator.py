from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

base = '/v2/metadata/'

projects = {}
arg_parser = reqparse.RequestParser()
arg_parser.add_argument("data", type=str)
arg_parser.add_argument("metadata", type=str)
# TODO: instead of this line, use the actual metadata as (is to be) specified


@app.route('/')
def home():
    return 'Knora Imitator running...'

class Project(Resource):
    def put(self):
        # parse arguments
        try:
            args = arg_parser.parse_args()
            return {"data_recieved": args['data'], "metadata_recieved": args['metadata']}
        except Exception as e:
            return "error"

api.add_resource(Project, base + 'project')

if __name__ == "__main__":
    app.run(debug=True)
