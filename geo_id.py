"""
Geo-ID module for LinkedIn job search.
Provides location name to geo-id mapping and helper functions.
"""

# Common LinkedIn geoId codes
GEO_ID_MAP = {
    # Countries
    'United States': '103644278',
    'USA': '103644278',
    'US': '103644278',
    'United Kingdom': '104738473',
    'UK': '104738473',
    'Germany': '104514075',
    'France': '104016111',
    'India': '102713980',
    'Canada': '103720260',
    'Australia': '104057199',
    'Netherlands': '102890883',
    'Spain': '104277358',
    'Italy': '103350519',
    'Poland': '104735516',
    'Ireland': '100993843',
    'Belgium': '102890971',
    'Switzerland': '106693',
    'Sweden': '105186',
    'Norway': '103819153',
    'Denmark': '104396',
    'Austria': '101282230',
    'Portugal': '105113',
    'Czech Republic': '105145199',
    'Brazil': '103469679',
    'Mexico': '103361397',
    'Japan': '102028474',
    'Singapore': '104010088',
    
    # Indian Cities
    'Bangalore': '105214831',
    'Hyderabad': '105556991',
    'Pune': '102983800',
    'Chennai': '104234821',
    'Delhi-NCR': '104842695',
    'Delhi': '104842695',
    'Gurgaon': '104842695',
    'Noida': '104842695',
    'Mumbai': '104295023',
    'Kochi': '104284485',
    'Ahmedabad': '102910963',
    'Kolkata': '104265433',
    'Jaipur': '102940209',
    'Chandigarh': '104111544',
    'Surat': '104054340',
    'Lucknow': '102883759',
    'Indore': '102872003',
    'Nagpur': '104077668',
    'Vadodara': '106728703',
    'Visakhapatnam': '104143520',
    'Coimbatore': '103096512',
    'Ludhiana': '102937664',
    'Bhopal': '102896782',
    'Patna': '102969123',
    'Nashik': '104256002',
    'Rajkot': '102933880',
    'Agra': '102922546',
    'Kanpur': '102880584',
    'Faridabad': '103051479',
    'Meerut': '103086813',
    'Vadodara': '104578719',
    'Jamshedpur': '102945365',
    'Allahabad': '102894623',
    'Ranchi': '102965208',
    'Howrah': '104071540',
    'Varanasi': '102939675',
    'Thane': '103000781',
    'Aurangabad': '104121573',
    'Dhanbad': '104010336',
    'Amritsar': '103047302',
    'Navi Mumbai': '103132330',
    'Pimpri-': '103076125',
    'Gwalior': '102896650',
    'Jodhpur': '102899343',
    'Madurai': '102999876',
    'Rajahmundry': '103055432',
    'Aligarh': '102876543',
    'Bilaspur': '102980123',
    'Udaipur': '102886754',
    'Mysore': '103112345',
    
    
    # US Cities (add common ones)
    'New York': '103644278',  # Using US geoId for now, can be refined with city-specific IDs
    'San Francisco': '103644278',
    'Los Angeles': '103644278',
    'Chicago': '103644278',
    'Seattle': '103644278',
    'Boston': '103644278',
    'Austin': '103644278',
    'Denver': '103644278',
    'Washington': '103644278',
    'Dallas': '103644278',
}


def get_geo_id(location):
    """
    Get geo-id for a given location name.
    
    Args:
        location (str): Location name (e.g., "United States", "New York")
    
    Returns:
        str or None: Geo-id string if found, None otherwise
    """
    if not location:
        return None
    
    # Normalize location string (strip, lowercase for lookup)
    location_normalized = location.strip()
    
    # Direct lookup
    if location_normalized in GEO_ID_MAP:
        return GEO_ID_MAP[location_normalized]
    
    # Case-insensitive lookup
    location_lower = location_normalized.lower()
    for key, geo_id in GEO_ID_MAP.items():
        if key.lower() == location_lower:
            return geo_id
    
    return None


def get_geo_ids(locations):
    """
    Get geo-ids for multiple location names.
    
    Args:
        locations (str or list): Location name(s) (single string or list of strings, or numeric geo-ids)
    
    Returns:
        list: List of geo-id strings (None values are filtered out)
    """
    if locations is None:
        return []
    
    if isinstance(locations, str):
        locations_list = [locations]
    else:
        locations_list = locations
    
    geo_ids = []
    for location in locations_list:
        if not location:
            continue
            
        location = location.strip()
        
        # Check if it's already a numeric geo-id
        if location.isdigit():
            geo_ids.append(location)
        else:
            # Try to get geo-id from location name
            geo_id = get_geo_id(location)
            if geo_id:
                geo_ids.append(geo_id)
            else:
                # Location not found, log warning
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Location '{location}' not found in geo-id map and is not a numeric geo-id. Skipping.")
    
    return geo_ids


def list_available_locations():
    """
    List all available location names in the geo-id map.
    
    Returns:
        dict: Dictionary mapping location names to geo-ids
    """
    return GEO_ID_MAP.copy()


def add_geo_id(location, geo_id):
    """
    Add a custom location to geo-id mapping.
    
    Args:
        location (str): Location name
        geo_id (str): LinkedIn geo-id (numeric string)
    """
    GEO_ID_MAP[location.strip()] = str(geo_id).strip()

