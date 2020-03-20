"""
## Flask API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""
import json
import logging
import os

import requests
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from calculate_distance import (calc_latlong_distance, find_max_latitude,
                                find_max_longitude, find_min_latitude,
                                find_min_longitude)

application = Flask(__name__)

# Development
DATASET = json.load("data_limiteddata.json", "r")


def _find_rentals_nearby(latitude, longitude, dist_range):

    # going to assume distance is the max that user is willing to go.
    # build a box around the coordinates. then start removing all the corners.
    # order by closest location.
    lst_nearby_rentals = []
    rentals_by_range = {}

    # Find coordinate max min for lat and long
    # Range would be a circle a target coordinate
    # Build a square box around the search location for easier implementation.
    #   using a box to reduce the search space.
    # Just search areas around this zone and calculate the distance
    #   This will return a circle
    #   The more we break down the zones
    #       the more we can get closer to a circle search.
    max_lat = find_max_latitude(latitude, longitude, dist_range)
    max_lng = find_max_longitude(latitude, longitude, dist_range)
    min_lat = find_min_latitude(latitude, longitude, dist_range)
    min_lng = find_min_longitude(latitude, longitude, dist_range)

    # calculate lat long dist.
    # currenlty very slow, iterating through all elements and checking the values
    # when implementing the db search, we can search for entries based on range
    # Should be faster then iterating through a list line by line.
    # If project is expaneded, could breakdown datasets into zones. counties. etc.
    for row in DATASET:
        r_lat = int(row['latitude'])
        r_lng = int(row['longitude'])

        # if the entry is within the zone.
        if ((r_lat >= min_lat and r_lat <= max_lat) or
                (r_lng >= min_lng and r_lng <= max_lng)):
            dist = calc_latlong_distance([r_lat, r_lng], [latitude, longitude])
            if dist <= dist_range:
                lst_nearby_rentals(row["id"])

                # create a reference of ids based on distance.
                # when we sort the keys, we should have a list of closest
                #   to farthest locations.
                if dist not in rentals_by_range:
                    rentals_by_range[dist] = []
                rentals_by_range[dist].append(row["id"])

    # sort lat longs diff by value.
    #   saved the keys as ints means we can sort them easily.
    #   probably a better way to do this.
    list_nearby_rental_ids = []
    for range_key in sorted(list(rentals_by_range.keys())):

        # Since they are all lists, just extend them into the output.
        list_nearby_rental_ids.extend(rentals_by_range[range_key])

    # get rental info by id # based on lat long diff
    return list_nearby_rental_ids



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

    lst_nearby_rentals = _find_rentals_nearby(
        data['latitude'], data['longitude'], data['distance'])

    return jsonify(status=True, data=lst_nearby_rentals)



def fuzzy_search_description(query_str):
    # use fuzzy search and find a location according to query.
    pass


def landmarks(query_str, coordinates, distance):
    # example given was probably just querying the desc.
    # but an idea, find a location that is in between landmark and coord.
    # But constrained by distance.
    pass



if __name__ == "__main__":
    _find_rentals_nearby(40.71344, -73.99037, 2000)
