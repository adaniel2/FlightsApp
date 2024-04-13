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
        SELECT a1.iata AS SourceIATA, a2.iata AS DestinationIATA, al.airlinename AS Airline
        FROM hasroutes hr
        JOIN airports a1 ON hr.source_airport_id = a1.airport_id
        JOIN airports a2 ON hr.destination_airport_id = a2.airport_id
        JOIN airline al ON hr.airlineID = al.airlineID
        WHERE a1.iata = '{source_iata}' AND a2.iata = '{destination_iata}';
    """
    result = pd.read_sql(query, engine)
    return result

def query_airline_routes(airline_name):
    """
    Query available routes for a specific airline.
    """
    query = f"""
        SELECT al.airlinename AS Airline, a1.iata AS SourceIATA, a2.iata AS DestinationIATA
        FROM hasroutes hr
        JOIN airports a1 ON hr.source_airport_id = a1.airport_id
        JOIN airports a2 ON hr.destination_airport_id = a2.airport_id
        JOIN airline al ON hr.airlineID = al.airlineID
        WHERE al.airlinename = '{airline_name}';
    """
    result = pd.read_sql(query, engine)
    return result

def query_routes_by_countries(source_country, destination_country):
    """
    Query available routes between source and destination countries.
    """
    query = f"""
        SELECT c1.country AS SourceCountry, c2.country AS DestinationCountry, a1.iata AS SourceIATA, a2.iata AS DestinationIATA, al.airlinename AS Airline
        FROM hasroutes hr
        JOIN airports a1 ON hr.source_airport_id = a1.airport_id
        JOIN airports a2 ON hr.destination_airport_id = a2.airport_id
        JOIN cities c1 ON a1.city_id = c1.city_id
        JOIN cities c2 ON a2.city_id = c2.city_id
        JOIN airline al ON hr.airlineID = al.airlineID
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
            a1.airport_id AS SourceAirportID, 
            a1.iata AS SourceIATA, 
            a1.airportName AS SourceAirportName, 
            c1.cityName AS SourceCityName, 
            a2.iata AS DestinationIATA, 
            a2.airportName AS DestinationAirportName,
            c2.cityName AS DestinationCityName
        FROM airports a1
        JOIN cities c1 ON a1.city_id = c1.city_id
        JOIN hasroutes hr ON a1.airport_id = hr.source_airport_id
        JOIN airports a2 ON hr.destination_airport_id = a2.airport_id
        JOIN cities c2 ON a2.city_id = c2.city_id
        WHERE c1.country = '{country_name}';
    """
    result = pd.read_sql(query, engine)
    return result
