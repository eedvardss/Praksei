import requests
import sqlite3
google_maps_api_key = 'AIzaSyDmYwKurLlvovZuOfJ6pPLXidmf_yjDZzc'


def geocode_address(street, city):
    address = f"{street}, {city}, Latvia"
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': google_maps_api_key, 'components': 'country:LV'}
    response = requests.get(base_url, params=params)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:

        location = data['results'][0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        return None

conn = sqlite3.connect('project.db')
cursor = conn.cursor()


cursor.execute("SELECT id, street, city FROM real_estate WHERE street IS NOT NULL AND city IS NOT NULL")
rows = cursor.fetchall()

for row in rows:
    property_id, street, city = row
    coordinates = geocode_address(street, city)

    if coordinates:
        latitude, longitude = coordinates

        cursor.execute("UPDATE real_estate SET latitude=?, longitude=? WHERE id=?", (latitude, longitude, property_id))
        conn.commit()
        print(f"Property ID: {property_id}, Street: {street}, City: {city}, Coordinates: {latitude}, {longitude} - Updated")
    else:
        print(f"Property ID: {property_id}, Street: {street}, City: {city}, Coordinates not found")

conn.close()

