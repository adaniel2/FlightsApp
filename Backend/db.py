import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the connection parameters
db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# Create a connection string
connection_string = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create an engine to connect to the MySQL database
engine = create_engine(connection_string)

# ------------------- Query functions -----------------------
# -----------------------------------------------------------

def query_routes(source_iata, destination_iata):
    """
    Query available routes from source to destination using IATA codes.
    """
    query = f"""
        SELECT a1.iata AS sourceIATA, a2.iata AS destinationIATA, al.airlineName
        FROM HasRoutes hr
        JOIN Airports a1 ON hr.sourceAirportID = a1.airportID
        JOIN Airports a2 ON hr.destinationAirportID = a2.airportID
        JOIN Airline al ON hr.airlineID = al.airlineID
        WHERE a1.iata = '{source_iata}' AND a2.iata = '{destination_iata}';
    """
    result = pd.read_sql(query, engine)

    return result

def query_airline_routes(airline_name):
    """
    Query available routes for a specific airline.
    """
    query = f"""
        SELECT al.airlineName, a1.iata AS sourceIATA, a2.iata AS destinationIATA
        FROM HasRoutes hr
        JOIN Airports a1 ON hr.sourceAirportID = a1.airportID
        JOIN Airports a2 ON hr.destinationAirportID = a2.airportID
        JOIN Airline al ON hr.airlineID = al.airlineID
        WHERE al.airlineName = '{airline_name}';
    """
    result = pd.read_sql(query, engine)

    return result

def query_routes_by_countries(source_country, destination_country):
    """
    Query available routes between source and destination countries.
    """
    query = f"""
        SELECT c1.country AS sourceCountry, c2.country AS destinationCountry, a1.iata AS sourceIATA, a2.iata AS destinationIATA, al.airlineName
        FROM HasRoutes hr
        JOIN Airports a1 ON hr.sourceAirportID = a1.airportID
        JOIN Airports a2 ON hr.destinationAirportID = a2.airportID
        JOIN Cities c1 ON a1.cityID = c1.cityID
        JOIN Cities c2 ON a2.cityID = c2.cityID
        JOIN Airline al ON hr.airlineID = al.airlineID
        WHERE c1.country = '{source_country}' AND c2.country = '{destination_country}';
    """
    result = pd.read_sql(query, engine)

    return result

def query_by_country(country_name):
    """
    Query all airports within a specific country and the routes they offer.
    """
    query = f"""
        SELECT 
            a1.airportID AS sourceAirportID, 
            a1.iata AS sourceIATA, 
            a1.airportName AS sourceAirportName, 
            c1.cityName AS sourceCityName, 
            a2.iata AS destinationIATA, 
            a2.airportName AS destinationAirportName,
            c2.cityName AS destinationCityName
        FROM Airports a1
        JOIN Cities c1 ON a1.cityID = c1.cityID
        JOIN HasRoutes hr ON a1.airportID = hr.sourceAirportID
        JOIN Airports a2 ON hr.destinationAirportID = a2.airportID
        JOIN Cities c2 ON a2.cityID = c2.cityID
        WHERE c1.country = '{country_name}';
    """
    result = pd.read_sql(query, engine)
    
    return result
