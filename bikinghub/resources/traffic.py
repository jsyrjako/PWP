from flask import Response
from flask_restful import Resource
from werkzeug.exceptions import NotFound
from bikinghub.models import TrafficData


class TrafficCollection(Resource):

    def get(self):
        pass


class TrafficItem(Resource):

    def get(self, traffic):
        traffic_obj = TrafficData.query.get(traffic).first()
        if not traffic_obj:
            raise NotFound
        traffic_doc = traffic_obj.serialize()
        return Response(traffic_doc, 200, mimetype="application/json")


class TrafficLocation(Resource):

    def put(self, traffic, location):
        """
        Add a traffic report to a location
        """
        raise NotImplementedError
