

# # https://stackoverflow.com/questions/837872/calculate-distance-in-meters-when-you-know-longitude-and-latitude-in-java
#  public static float distFrom(float lat1, float lng1, float lat2, float lng2) {
#     double earthRadius = 6371000; //meters
#     double dLat = Math.toRadians(lat2-lat1);
#     double dLng = Math.toRadians(lng2-lng1);
#     double a = Math.sin(dLat/2) * Math.sin(dLat/2) +
#                Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
#                Math.sin(dLng/2) * Math.sin(dLng/2);
#     double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
#     float dist = (float) (earthRadius * c);

#     return dist;


import math


def calc_latlong_distance(float_lat, float_lng, range):
    earth_radius = 6371000

    return distance


def calc_latlong_distance(
        float_lat1, float_lng1, float_lat2, float_lng2, range):

    # In Meters
    earthRadius = 6371000

    dLat = math.radians(float_lat2 - float_lat1)
    dLng = math.radians(float_lng2 - float_lng1)
    a = (
        math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(math.radians(float_lat1)) *
        math.cos(math.radians(float_lat2)) *
        math.sin(dLng / 2) * math.sin(dLng / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    dist = earthRadius * c

    return dist


# use the equation above and just work backwards
def calc_max_min_lat(
        float_lat1, float_lng1, max_range):

    # same long, just find max min lat by dist.
    # float_lng2 = float_lng1

    # min_range = max_range * -1
    # irrelevant, since we can just do cmax * -1 below

    # In Meters
    earthRadius = 6371000

    # max_range = earthRadius * c
    # try to find c.
    cmax = max_range / earthRadius
    cmin = cmax * -1
    # we'll just worry about cmax for now.

    # cmax = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # cmax / 2 = math.atan2(sqrt(a), sqrt(1-a))

    dLat = math.radians(float_lat2 - float_lat1)
    # dLng = math.radians(float_lng1 - float_lng1)
    # = 0
    a = (
        math.sin(dLat / 2) * math.sin(dLat / 2) 

        # NOTE: since sin(0) is 0, this is all 0
        # +
        # math.cos(math.radians(float_lat1)) *
        # math.cos(math.radians(float_lat2)) *
        # math.sin(0 / 2) * math.sin(0 / 2)
        
    )



    # return dist
    return False