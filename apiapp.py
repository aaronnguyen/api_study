"""
## Flask RESTful API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""
import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

import logging
import requests
import json

from calculate_distance import calc_latlong_distance_range


application = Flask(__name__)


def _check_request_fields(dict_datarequest, lst_requiredfields):
    """
    Input:

    - Data request from the HTTP call (Just passed the whole thing in)
    - List of expected keys.
    """

    # Use set subtraction to figure out if we are missing any fields.
    reqfields = set(lst_requiredfields) - set(dict_datarequest.keys())
    if len(reqfields) == 0:
        return True
    else:
        return False


@application.route('/')
def index():
    return jsonify(status=True, message='Rental Serach API.')


@application.route('/findnearby', methods=['GET'])
def find_nearby():
    data = request.get_json(force=True)
    lst_reqfields = ["latitude", "longitude", "distance"]
    if _check_request_fields(data, lst_reqfields) is False:
        return jsonify(
            status=False, message='Missing required search fields.'), 400

    pass


def find_location_nearby(coordinates, distance):
    # going to assume distance is the max that user is willing to go.

    # build a box around the coordinates. then start removing all the corners.

    # order by closest location.
    pass


def fuzzy_search_description(query_str):
    # use fuzzy search and find a location according to query.
    pass


def landmarks(query_str, coordinates, distance):
    # example given was probably just querying the desc.
    # but an idea, find a location that is in between landmark and coord.
    # But constrained by distance.
    pass


