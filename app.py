from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/flights", methods=["GET"])
def get_flights():
    url = "https://www.gatewayairport.com/flightstatus"
    
    try:
        # Add User-Agent header to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        # Send request with User-Agent and timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for non-200 status codes

    except requests.exceptions.RequestException as e:
        return f"Error fetching flight data: {e}", 500

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    flights = []
    for row in soup.select("table tbody tr"):
        columns = row.find_all('td')
        if len(columns) >= 5:  # Ensure there are at least 5 columns
            flight_number = columns[1].text.strip()  # Flight number
            airline_name = columns[0].text.strip()  # Airline name

            # Check for Allegiant Air logo
            img_tag = columns[0].find('img')
            if img_tag and "Images/AirlineLogos/G4.png" in img_tag.get('src', ''):
                airline_name = "Allegiant Air"
            
            origin = columns[2].text.strip()  # Origin
            status = columns[3].text.strip()  # Status (time, delayed, etc.)
            time = columns[4].text.strip()  # Scheduled/actual time

            flight_info = {
                "flight_number": flight_number,
                "airline": airline_name,
                "origin": origin,
                "status": status,
                "time": time
            }
            flights.append(flight_info)

    return jsonify(flights)


@app.route("/")
def home():
    return "Flight Tracker is running!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Get the PORT environment variable or default to 10000
    app.run(host="0.0.0.0", port=port)  # Bind to 0.0.0.0 to accept requests from anywhere