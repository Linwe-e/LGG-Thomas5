import logging
import azure.functions as func
import requests
import pyodbc
import os
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # iRail API Configuration for Liège-Guillemins station
    irail_api_url = "https://api.irail.be/liveboard/?station=Liège-Guillemins&format=json&lang=en"
    
    try:
        # 1. Fetch data from iRail API
        response = requests.get(irail_api_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        liveboard_data = response.json()
        
        departures = liveboard_data.get("departures", {}).get("departure", [])
        if not departures:
            return func.HttpResponse("No departure data found from iRail API.", status_code=200)

        # 2. Connect to Azure SQL Database using Managed Identity
        conn_str = os.environ["SqlConnectionString"]
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 3. Insert data into the database
        insert_count = 0
        for departure in departures:
            station_info = departure.get("stationinfo", {})
            vehicle_info = departure.get("vehicleinfo", {})
            
            # Convert timestamp to datetime
            departure_time = datetime.fromtimestamp(int(departure.get("time")))
            
            # SQL INSERT statement
            sql_insert = """
                INSERT INTO TrainDepartures (DepartureTime, StationName, Vehicle, Occupancy, Delay, Platform)
                VALUES (?, ?, ?, ?, ?, ?);
            """
            
            cursor.execute(sql_insert,
                           departure_time,
                           station_info.get("name"),
                           vehicle_info.get("shortname"),
                           departure.get("occupancy", {}).get("name") if departure.get("occupancy") else None,
                           int(departure.get("delay", 0)),
                           departure.get("platform")
                          )
            insert_count += 1
        
        conn.commit()
        cursor.close()
        conn.close()

        return func.HttpResponse(f"Successfully inserted {insert_count} records into the database.", status_code=200)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from iRail API: {e}")
        return func.HttpResponse("Error fetching data from iRail API.", status_code=500)
    
    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return func.HttpResponse("Error connecting to or writing to the database.", status_code=500)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return func.HttpResponse("An unexpected error occurred.", status_code=500)
