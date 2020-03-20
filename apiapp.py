"""
## Flask RESTful API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""
import json
import logging
import os

import requests
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from calculate_distance import find_max_latitude
from calculate_distance import find_max_longitude
from calculate_distance import find_min_latitude
from calculate_distance import find_min_longitude


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

    # Find coordinate ranges for lats
    # Find coordinate ranges for longs
    max_lat = find_max_latitude(
        data["latitude"], data["longitude"], data["distance"])
    mat_lng = find_max_longitude(
        data["latitude"], data["longitude"], data["distance"])
    min_lat = find_min_latitude(
        data["latitude"], data["longitude"], data["distance"])
    min_lng = find_min_longitude(
        data["latitude"], data["longitude"], data["distance"])

    lst_nearby_rentals = []
    # calcualte lat long diffs

    # sort lat longs diff by value.

    # get rental info by id # based on lat long diff

    return jsonify(status=True, data=lst_nearby_rentals)


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

