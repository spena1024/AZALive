from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route("/flights", methods=["GET"])
def get_flights():
    url = "https://www.gatewayairport.com/flightstatus"
    
    try:
        # Send request with timeout and raise error for bad responses
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for non-200 status codes

    except requests.exceptions.RequestException as e:
        # Return an error message with status 500 if request fails
        return f"Error fetching flight data: {e}", 500

    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    flights = []
    for row in soup.select("table tbody tr"):
        columns = row.find_all('td')
        print(f"Row content: {row}")  # Debug: Print the full row to see its HTML
        print(f"Number of columns: {len(columns)}")  # Debug: Print the number of columns

        if len(columns) >= 5:  # Ensure there are at least 5 columns
            flight_number = columns[1].text.strip()  # Flight number
            airline_name = columns[0].text.strip()  # Airline name
            
            # Check for Allegiant Air logo
            img_tag = columns[0].find('img')
            if img_tag and "Images/AirlineLogos/G4.png" in img_tag.get('src', ''):
                airline_name = "Allegiant Air"
            
            origin = columns[2].text.strip()  # Origin
            status = columns[3].text.strip()  # Status
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