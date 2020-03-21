"""
Simple API implementation within a single GET request.
Generally wrap these in a docker container and could deploy to cluster.
I use cherryPy because it was so simple to run, but heard Flask was pretty
good. So I decided to give it a try.

Wanted to try out connecting pymongo to flask, but was spending too much time
trying to connect to the server.

[Flask API](https://flask.palletsprojects.com/en/1.1.x/)
"""
from flask import Flask, jsonify, request
from fuzzywuzzy import fuzz

# Placed code into other files, I find the larger the py file, the harder
# it is to support.
from calculate_distance import (calc_latlong_distance, find_max_latitude,
                                find_max_longitude, find_min_latitude,
                                find_min_longitude)
from data_connection import dataconn

application = Flask(__name__)
dbconn = dataconn(json_quickload="data_fulldump.json")


def _find_rentals_nearby(latitude, longitude, dist_range):
    """
    #### Input:

    - Coordinates of the center of the search area.
    - Range distance extending outside of the center.

    #### Output:

    - Dict of rental ids using the distance as the key.
    - Sorted list of keys in asc order.

    #### Assumption:

    - range is the max dist, the user is willing to go.

    #### Ideas:

    Maybe we can cache some of these calculations? We could quickly
    calculate distance using pythagorean theorem. Although the Earth is curved,
    shouldn't be much of a difference in distance if nearby.
    When calculating distances, if the zone falls within a cached search range,
    we could use those locations from the search.  Then we could search the
    area that sits outside of the full search zone.
    """

    rentals_by_range = {}

    # make sure they are explicitly floats.
    latitude = float(latitude)
    longitude = float(longitude)

    """
    Find coordinate max min for lat and long.
    Range would be a circle a target coordinate.
    First build a square box around the search location then find rentals
    within that zone.  Only using it to reduce the search results.
    Then calculate the distance for each result, and if it falls within the
    distance range, the zone would turn into a circle.


    The more we breadown the search zone, the closer we could get to a circle.
    Maybe consider an octogon instead of a square?
    """
    max_lat = find_max_latitude(latitude, longitude, dist_range)
    max_lng = find_max_longitude(latitude, longitude, dist_range)
    min_lat = find_min_latitude(latitude, longitude, dist_range)
    min_lng = find_min_longitude(latitude, longitude, dist_range)

    """
    Currently we are iterating through all elements of the dataset to see
    if the rental property resides within the search zone limits.  We could
    reorganize the data here into smaller search areas.  Maybe breakdown into
    neighborhoods, then calculate the distance between different neighborhoods.
    THen when calculating the distance, we could search through certain areaas
    and their neighbors.
    """
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

    """
    Since we have the range as keys, we can sort the keys by distance and then
    search through the dict of lists by distance order.  Luckily we could use
    ints as dict keys.  If given time, could have figured out a better way to
    implement the search.  Original idea was to dump the data into MongoDB and
    search for the elements using the keys. Just using the sorted function in
    python, which seems to be pretty effecient already.
    """
    return rentals_by_range, sorted(list(rentals_by_range.keys()))


def _check_request_fields(dict_datarequest, lst_requiredfields):
    """
    #### Input:

    - Data request from the HTTP call (Just passed the whole thing in)
    - List of expected keys.

    #### Desc:

    Use set subtraction to figure out if we are missing any fields.
    """
    reqfields = set(lst_requiredfields) - set(dict_datarequest.keys())
    if len(reqfields) == 0:
        return True
    else:
        return False


def _fuzzy_match(query_str, row_desc):
    """
    #### Input:
    - 2 strings to compare

    #### Output:
    - An average of the result values based on all available checks.

    #### Desc:
    For brevity, will use fuzzy wuzzy lib to do fuzzy string match.
    Also allows API app to be more independent.  Will put link to lib's github
    in the README.

    Will use fuzzy search to match up query with the name listed in the row.
    Used at work before, better results using all four and averaging
    out the score. This is to compensate for human mispellings.

    #### Ideas:

    Could load data into elastic search and we could utilize more flexible
    search functions.
    """

    f_part_r_val = fuzz.partial_ratio(query_str, row_desc)
    f_r_val = fuzz.ratio(query_str, row_desc)
    tsortr_val = fuzz.token_sort_ratio(query_str, row_desc)
    tsetr_val = fuzz.token_set_ratio(query_str, row_desc)
    avg_score = (f_part_r_val + f_r_val + tsortr_val + tsetr_val) / 4

    return avg_score


def _fuzzy_search_query(query_str, lst_nearby_rentals):
    """
    #### Input:
    - query string to search
    - subset of data set to look within

    #### Output:
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

    # If working with a large set of keys, probably not the best idea to
    # sort the keys here and return.
    return fuzz_scores, sorted(list(fuzz_scores.keys()), reverse=True)


def _nearby_landmarks(query_str, coordinates, distance):
    """
    TODO: implement function.
    Could use the query to determine certain landmarks and find a location
    nearby it.  Could find rentals between the search location and the
    landmark.  Search could still be constrained by distance.
    """
    pass


def _find_nearby_helper(data):
    """
    #### Input:

    - Data dictionary from Flask request

    #### Output:

    - List of rentals, ordered by relevance to query than distance.

    #### Ideas:
    Search optimization: maybe search only 100m (maybe a percentage range?)
    around the target then do another search for locations 100m-1000m. Could
    create an interable object to fetch chunks.  No point in fetch all
    locations at once if user can't digest all the information at once.
    """

    lst_nearby_rentals, nearby_keys_sorted = _find_rentals_nearby(
        data['latitude'], data['longitude'], data['distance'])

    lst_relevence_scores = None
    relv_keys_sorted = None
    if "query" in data:
        # Sort the search based on query relevance
        # Will sort by relevance score. (closest to 100)
        # Cap match at 60%, if anything lower, don't include.
        # Don't need to pass in sorted range, since it is already close by
        lst_relevence_scores, relv_keys_sorted = _fuzzy_search_query(
            data["query"], lst_nearby_rentals)

    # TODO: Lots of other data we can filter by, but will focus on getting
    # it up and running.  Reduce the list by the filters passed in.
    lst_filtered_ids = None
    if "filter" in data:
        pass

    # Build the return list based on the parameters above.
    search_info = {}
    doc_id_list = []

    # How do we balance relevance and distance?
    # For now will just prioritize relevance over distance.
    # Only process it if we have the data for it.
    if lst_relevence_scores is not None:
        for r_key in relv_keys_sorted:
            for d_id in lst_relevence_scores[r_key]:
                search_info[d_id] = {
                    "rental_id": d_id,
                    "relevance": r_key
                }
                doc_id_list.append(d_id)

    # Same as above, only process if we have the data.
    if lst_filtered_ids is not None:
        pass

    # Always process the nearby locations list.
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

        # Lookup should be instant since it is just looking for existence.
        # Since we are popping the keys out, there will be no duplicates
        # in the results.
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
