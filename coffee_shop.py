import json
import requests
import os
from dotenv import load_dotenv
from geopy import distance
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon  


def distance_coffee_house(coffee_distance):
    return coffee_distance["distance"]


def main():
    load_dotenv()

    apikey = os.environ["YANDEX_API"]

    entering_location = input("Где вы находитесь? ")

    coords = fetch_coordinates(apikey, entering_location)

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        coffee_json = my_file.read()
        coffee = json.loads(coffee_json)

    coffee_with_distance = []

    for coffee_house in coffee:
        name = coffee_house["Name"]
        coordinates_coffee = coffee_house["geoData"]["coordinates"]
        coffee_coords = (coordinates_coffee[1], coordinates_coffee[0]) 
        mileage = (distance.distance(coords, coffee_coords).km)

        coffee_with_distance.append({
            "title": name,
            "distance": mileage,
            "latitude": coffee_coords[0],  
            "longitude": coffee_coords[1], 
        })

    sorted_coffee_house = sorted(coffee_with_distance, key=distance_coffee_house)

    slice_coffee_house = sorted_coffee_house[:5]

    m = folium.Map(location=(coords[0], coords[1]), zoom_start=15) 

    for coffee_house in slice_coffee_house:
        coffee_coords = (coffee_house["latitude"], coffee_house["longitude"])
        folium.Marker(
            location=coffee_coords,
            tooltip="Кофан здесь",
            popup=coffee_house["title"],
            icon=folium.Icon(icon="mug-hot", prefix='fa', color="black")
        ).add_to(m)

    m.save("index.html")


if __name__ == '__main__':
    main()
