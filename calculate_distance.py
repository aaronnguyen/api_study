"""
Earth radius is defined in meters, thus all results will be in meters.
"""
import math

EARTHRADIUS = 6371000


def calc_latlong_distance(coordinates1, coordinates2):
    """
    #### Input:
    - Start Coordinate pairs [Latitude, Longitude]
    - End Coordinate pairs [Latitude, Longitude]

    #### Output:
    - Distance in meters

    #### Desc:
    [Found the equation in the link below. Ported from Java to Python.](https://stackoverflow.com/questions/837872/calculate-distance-in-meters-when-you-know-longitude-and-latitude-in-java)
    """
    lat1 = coordinates1[0]
    lng1 = coordinates1[1]
    lat2 = coordinates2[0]
    lng2 = coordinates2[1]

    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    area = (
        math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dLng / 2) * math.sin(dLng / 2)
    )
    circumf = 2 * math.atan2(math.sqrt(area), math.sqrt(1 - area))
    distance = EARTHRADIUS * circumf

    return distance


# Definately spent way too much time on trying to work the equation backwards.
# Decided to just look up a solution and work it into the project.
def _findCoor_by_distAndBearing(anchor_lat, anchor_long, distance, degree_idx):
    """
    #### Input:
    - Starting Latitude Coordinate
    - Starting Longitude Coordinate
    - Distance in meters
    - Degree Index (degrees of a circle)

    #### Output:
    - [Latitude, Longitude] of end point.

    #### Desc:
    [Found the equation on StackOverflow](https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing)

    Was relearning how spherical circumference calculations worked, spent way
    too much time (a few hours) trying to find missing variables using
    the function above. Decided to search for an implementation instead.

    Degrees bearing used to determine the midpoints of all sides of a square.
    This helps set the initial search zone for nearby rentals.
    If we implement an octagon, should be a small zone to search. Would do it
    here.
    """
    degree_bearing = {
        0: 0,
        90: 1.57,
        180: 3.14,
        240: 4.18
    }
    bearing = degree_bearing[degree_idx]

    # convert to radians
    radians_lat = math.radians(anchor_lat)
    radians_long = math.radians(anchor_long)

    dist_div_earthrad = distance / EARTHRADIUS

    result_lat = (
        math.asin(
            math.sin(radians_lat) * math.cos(dist_div_earthrad) +
            math.cos(radians_lat) * math.sin(dist_div_earthrad) *
            math.cos(bearing)))

    result_long = (
        radians_long + math.atan2(
            (math.sin(bearing) * math.sin(dist_div_earthrad) *
             math.cos(radians_lat)),
            (math.cos(dist_div_earthrad) - math.sin(radians_lat) *
             math.sin(result_lat))
        )
    )

    result_lat = math.degrees(result_lat)
    result_long = math.degrees(result_long)
    return result_lat, result_long


"""
Hardcoded functions to search for endpoint. to calculate the search range.

Bearings denote certain results:

- 0 as max latitude
- 90 as max longitude
- 180 as min latitude
- 240 as min longitude
"""


def find_max_latitude(anchor_lat, anchor_long, distance):
    return _findCoor_by_distAndBearing(
        anchor_lat, anchor_long, distance, 0
    )[0]


def find_max_longitude(anchor_lat, anchor_long, distance):
    return _findCoor_by_distAndBearing(
        anchor_lat, anchor_long, distance, 90
    )[1]


def find_min_latitude(anchor_lat, anchor_long, distance):
    return _findCoor_by_distAndBearing(
        anchor_lat, anchor_long, distance, 180
    )[0]


def find_min_longitude(anchor_lat, anchor_long, distance):
    return _findCoor_by_distAndBearing(
        anchor_lat, anchor_long, distance, 240
    )[1]
