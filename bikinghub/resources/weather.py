import json
from datetime import datetime
from flask import Response, url_for
from flask_restful import Resource
from bikinghub.models import WeatherData, Location
from bikinghub.constants import (
    LINK_RELATIONS_URL,
    WEATHER_PROFILE,
    MASON_CONTENT,
    NAMESPACE,
)
from ..utils import create_weather_data, BodyBuilder, create_error_response


class WeatherCollection(Resource):

    def get(self):
        """ "
        Get all weather reports
        """
        all_weathers = WeatherData.query.all()
        if not all_weathers:
            return create_error_response(404, "No weather reports found.")

        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)  # Add namespace
        body.add_control
        body["items"] = []
        for weather in all_weathers:
            item = BodyBuilder(
                id=weather.id,
                rain=weather.rain,
                humidity=weather.humidity,
                wind_speed=weather.wind_speed,
                wind_direction=weather.wind_direction,
                temperature=weather.temperature,
                temperature_feel=weather.temperature_feel,
                cloud_cover=weather.cloud_cover,
                weather_description=weather.weather_description,
                location_id=weather.location_id,
                weather_time=(
                    weather.weather_time.isoformat()
                    if isinstance(weather.weather_time, datetime)
                    else weather.weather_time
                ),
            )
            location = Location.query.filter_by(id=weather.location_id).first()
            item.add_control(
                "self", url_for("api.locationitem", location=location) + "weather/"
            )  # Add self control
            item.add_control("profile", WEATHER_PROFILE)  # Add profile control
            body["items"].append(item)

        return Response(json.dumps(body), status=200, mimetype=MASON_CONTENT)

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
            weather_obj = create_weather_data(location)

        body = BodyBuilder()
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)  # Add namespace
        body.add_control(
            "self", url_for("api.weatheritem", location=location)
        )  # Add self control
        body.add_control("profile", WEATHER_PROFILE)  # Add profile control
        body.add_control(
            "collection", url_for("api.weathercollection")
        )  # Add collection control
        body.add_control(
            "location", url_for("api.locationitem", location=location)
        )  # Add location control

        body["items"] = weather_obj.serialize()

        return Response(json.dumps(body), status=200, mimetype=MASON_CONTENT)

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
