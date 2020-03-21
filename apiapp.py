"""
## Flask API

Caching: when needed to scale. Some areas we can implement:
- Add potential here

"""
# import logging

from flask import Flask, jsonify, request
# from flask_pymongo import PyMongo
from fuzzywuzzy import fuzz

from calculate_distance import (calc_latlong_distance, find_max_latitude,
                                find_max_longitude, find_min_latitude,
                                find_min_longitude)
from data_connection import dataconn

application = Flask(__name__)
dbconn = dataconn(json_quickload="data_fulldump.json")


def _find_rentals_nearby(latitude, longitude, dist_range):
    """
    Input:
    - Coordinates of the center of the search area.
    - Range distance extending outside of the center.

    Output:
    - Dict of rental ids using the distance as the key.
    - Sorted list of keys in asc order.
    """

    # going to assume distance is the max that user is willing to go.
    # build a box around the coordinates. then start removing all the corners.
    # order by closest location.
    rentals_by_range = {}

    # Explicit of float
    latitude = float(latitude)
    longitude = float(longitude)

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
    # currently very slow
    #   iterating through all elements and checking the values
    # when implementing the db search,
    #   we can search for entries based on range
    # Should be faster then iterating through a list line by line.
    # If project is expanded,
    #   breakdown datasets into zones. counties. etc.
    # TODO: a real iterable obj here
    for row in dbconn.get_data_row_iter():
        r_lat = float(row['latitude'])
        r_lng = float(row['longitude'])

        # if the entry is within the zone.
        if ((r_lat >= min_lat and r_lat <= max_lat) or
                (r_lng >= min_lng and r_lng <= max_lng)):
            dist = calc_latlong_distance([r_lat, r_lng], [latitude, longitude])
            if dist <= dist_range:

                # create a reference of ids based on distance.
                # when we sort the keys, we should have a list of closest
                #   to farthest locations.
                if dist not in rentals_by_range:
                    rentals_by_range[dist] = []
                rentals_by_range[dist].append(row["id"])

    # sort lat longs diff by value.
    #   saved the keys as ints means we can sort them easily.
    #   instead of building a totally new list object
    #   just add the sorted keys to the already created dict.
    # just using the sorted function in python. timsort seems pretty effecient.
    # NOTE: originally added the sorted list of keys into the dict.
    #   Just returning it as 2 items.
    # get rental info by id # based on lat long diff
    # TODO: maybe save some of these calculations?
    #   We could quickly calculate distance using pythagorean theorem
    #   although the Earth is curved, shouldn't be much
    #       difference in distance if nearby.
    #   Maybe when calculating distances, if the zone falls within a cached
    #   search range, then we can use those locations from that search.
    #   Maybe search that first? to save lookup? then search for new locations
    #   outside of the already searched area.
    return rentals_by_range, sorted(list(rentals_by_range.keys()))


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


# TODO: could load data into elastic search and we could utilize
#   flexible search functions.
# For brevity, will use fuzzy wuzzy lib to do fuzzy string match.
#   Reduce host complexity as well.
# https://github.com/seatgeek/fuzzywuzzy
def _fuzzy_match(query_str, row_desc):
    """
    Input:
    - 2 strings to compare

    Output:
    - An average of the result values based on all available checks.
    """
    # use fuzzy search and find a location according to query.

    # Used at work before, better results using all four and averaging
    #   out the score. This is to compensate for human mispellings.
    f_part_r_val = fuzz.partial_ratio(query_str, row_desc)
    f_r_val = fuzz.ratio(query_str, row_desc)
    tsortr_val = fuzz.token_sort_ratio(query_str, row_desc)
    tsetr_val = fuzz.token_set_ratio(query_str, row_desc)
    avg_score = (f_part_r_val + f_r_val + tsortr_val + tsetr_val) / 4

    return avg_score


def _fuzzy_search_query(query_str, lst_nearby_rentals):
    """
    Input:
    - query string to search
    - subset of data set to look within

    Output:
    - dictionary
        - key: fuzzy search score
        - value: document id
    - sorted list of the scores keys in desc order.
    """
    fuzz_scores = {}
    for dist_key in lst_nearby_rentals:
        for doc_id in lst_nearby_rentals[dist_key]:
            fuzz_score = _fuzzy_match(
                query_str, dbconn.get_data_row_by_id(doc_id)["name"])
            if fuzz_score > 60:
                if fuzz_score not in fuzz_scores:
                    fuzz_scores[fuzz_score] = []
                fuzz_scores[fuzz_score].append(doc_id)

    # could save the keys while processing data
    #   for brevity, and effecient point across, just get keys and sort.
    #   reverse order, since we need desc.
    return fuzz_scores, sorted(list(fuzz_scores.keys()), reverse=True)


# TODO: impl
def _nearby_landmarks(query_str, coordinates, distance):
    # example given was probably just querying the desc.
    # but an idea, find a location that is in between landmark and coord.
    # But constrained by distance.
    pass


# Pull this out of the main api function. wanted to be able to focus on just
#   the api portion in the api function itself.
def _find_nearby_helper(data):

    # TODO: search optimization
    #   maybe search only 100m around the target
    #   then do another search for locations 100m-1000m
    #   etc until range is met. no point in fetching all locations at once
    #   if the user can't digest all the information at once.
    #       if a direct api call for external tool, then return all.
    lst_nearby_rentals, nearby_keys_sorted = _find_rentals_nearby(
        data['latitude'], data['longitude'], data['distance'])

    lst_relevence_scores = None
    relv_keys_sorted = None
    if "query" in data:
        # sort the search based on query relevance
        # how much of a match do we say is relevant?
        #   will sort by relevance score. (closest to 100)
        #   but will cap off at 60%
        # Don't need to pass in sorted range, since it is already close by
        lst_relevence_scores, relv_keys_sorted = _fuzzy_search_query(
            data["query"], lst_nearby_rentals)

    # TODO: Lots of other data we can filter by, but will focus on getting
    #   it up and running first.
    # reduce the list by the filters passed in
    lst_filtered_ids = None
    if "filter" in data:
        pass

    # Build the return list based on the parameters above.
    search_info = {}
    doc_id_list = []

    # NOTE: How do we balance relevance and distance?
    #   for now will just prioritize relevance over distance.
    #   Only process it if we have the data for it.
    if lst_relevence_scores is not None:
        for r_key in relv_keys_sorted:
            for d_id in lst_relevence_scores[r_key]:
                search_info[d_id] = {
                    "rental_id": d_id,
                    "relevance": r_key
                }
                doc_id_list.append(d_id)

    # same here, only process if we have the data.
    if lst_filtered_ids is not None:
        pass

    # always process the nearby location.
    for n_key in nearby_keys_sorted:
        for d_id in lst_nearby_rentals[n_key]:
            if d_id not in search_info:
                search_info[d_id] = {
                    "rental_id": d_id,
                    "distance": n_key
                }
            else:
                search_info[d_id]["distance"] = n_key

            # There will be duplicates, but we'll take care of that.
            doc_id_list.append(d_id)

    rebuild_search_list = []
    for d_id in doc_id_list:

        # search shoudl be instant since it is just looking for existence.
        # also handles dups by popping the key val out.
        if d_id in search_info:
            popped_data = search_info.pop(d_id)
            rebuild_search_list.append(popped_data)

    return rebuild_search_list


# FLASK API Routes
@application.route('/')
def index():
    return jsonify(status=True, message='Rental Serach API.')


@application.route('/findnearby', methods=['GET'])
def find_nearby():
    data = request.get_json(force=True)

    # Have a list of required fields and return error if not met.
    lst_reqfields = ["latitude", "longitude", "distance"]
    if _check_request_fields(data, lst_reqfields) is False:
        return jsonify(
            status=False, message='Missing required search fields.'), 400

    rebuild_search_list = _find_nearby_helper(data)
    return jsonify(status=True, data=rebuild_search_list)

    # TODO: return an error status if no results.
