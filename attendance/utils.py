import math

def is_within_radius(user_lat, user_lng, org_lat, org_lng, radius_m):
    """Check if user is within org radius using Haversine formula."""
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(math.radians, [user_lat, user_lng, org_lat, org_lng])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance <= radius_m
