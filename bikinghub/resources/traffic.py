from flask import Response
from flask_restful import Resource
from bikinghub.models import TrafficData
from bikinghub.utils import create_error_response


class TrafficCollection(Resource):
    """
    Not used
    """

    def get(self):
        pass


class TrafficItem(Resource):
    """
    Not used
    """

    def get(self, traffic):
        traffic_obj = TrafficData.query.get(traffic).first()
        if not traffic_obj:
            return create_error_response(404, "Not Found", "Traffic report not found")
        traffic_doc = traffic_obj.serialize()
        return Response(traffic_doc, 200, mimetype="application/json")


class TrafficLocation(Resource):
    """
    Not used
    """

    def put(self, traffic, location):
        """
        Add a traffic report to a location
        """
        raise NotImplementedError
