import json
from flask import Response
from flask_restful import Resource
from werkzeug.exceptions import NotFound
from bikinghub.models import WeatherData
from ..utils import create_weather_data


class WeatherCollection(Resource):

    def get(self):
        """ "
        Get all weather reports
        """
        all_weathers = WeatherData.query.all()
        if not all_weathers:
            raise NotFound
        weather_datas = [weather.serialize() for weather in all_weathers]

        return Response(
            json.dumps(weather_datas), status=200, mimetype="application/json"
        )

    # def post(self, location):
    #    """
    #    Create a new weather report
    #    """
    #    try:
    #        validate(request.json, WeatherData.json_schema())
    #    except ValidationError as e:
    #        raise BadRequest(str(e)) from e
    #    except UnsupportedMediaType as e:
    #        raise UnsupportedMediaType(str(e)) from e


#
#    # weather.deserialize(request.json)
#    # weather.location_id = location.id
#    # db.session.add(weather)
#    # db.session.commit()
#
#    return Response(
#        status=201,
#        headers={"weather_data": url_for(
#            weather.LocationWeather,
#            location=location.id,
#            weather=weather.id
#            )
#        }
#    )


class WeatherItem(Resource):

    def get(self, location):
        """
        Get a specific weather report for a location
        """
        weather_obj = (
            WeatherData.query.filter_by(location_id=location.id)
            .order_by(WeatherData.weather_time.desc())
            .first()
        )
        if not weather_obj:
            weather_obj = create_weather_data(location.serialize())
        body = weather_obj.serialize()
        return Response(json.dumps(body), status=200, mimetype="application/json")

    # def put(self, location, weather):
    #    """
    #    Update a specific weather report for a location
    #    """


#
#    try:
#        validate(request.json, WeatherData.json_schema())
#    except ValidationError as e:
#        raise BadRequest(str(e)) from e
#    except UnsupportedMediaType as e:
#        raise UnsupportedMediaType(str(e)) from e
#    weather_obj = WeatherData.query.filter_by(location_id=location).first()
#    if not weather_obj:
#        raise NotFound
#    weather.deserialize(request.json)
#    db.session.commit()
#
#    return Response(
#    201,
#    headers={"weather_data": url_for(weather.LocationWeather,
#    location=location.id,
#    weather=weather)
#    })
#
# def delete(self, location):
#    """
#    Delete a specific weather report for a location
#    """
#    weather_obj = WeatherData.query.filter_by(location_id=location).first()
#    if not weather_obj:
#        raise NotFound
#    db.session.delete(weather_obj)
#    db.session.commit()
#    return Response(204)
