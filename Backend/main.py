import pandas as pd
from sqlalchemy import create_engine

# Define the connection parameters
db_username = 'root'
db_password = '!#%Sql981'
db_host = 'localhost'
db_port = '3306'
db_name = 'flights'

# Create a connection string
connection_string = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create an engine to connect to the MySQL database
engine = create_engine(connection_string)

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

def main():
    print("Welcome to the Flight Query CLI!")

    while True:
        print("\nPlease choose an option:")
        print("1. Search by airports")
        print("2. Search by airline")
        print("3. Search by country")
        print("4. Search by countries")
        print("5. Exit")

        choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

        if choice == '1':
            source_iata = input("Enter the source airport IATA code: ")
            destination_iata = input("Enter the destination airport IATA code: ")
            routes = query_routes(source_iata, destination_iata)
            if not routes.empty:
                print("Available routes:")
                print(routes)
            else:
                print("No routes found from", source_iata, "to", destination_iata)
        elif choice == '2':
            airline_name = input("Enter the airline name: ")
            routes = query_airline_routes(airline_name)
            if not routes.empty:
                print(f"Available routes for {airline_name}:")
                print(routes)
            else:
                print(f"No routes found for {airline_name}")
        elif choice == '3':
            country_name = input("Enter the country name: ")
            routes = query_airports_by_country(country_name)
            if not routes.empty:
                print(f"Available airports and routes in {country_name}:")
                print(routes)
            else:
                print(f"No routes found within {country_name}")
        elif choice == '4':
            source_country = input("Enter the source country name: ")
            destination_country = input("Enter the destination country name: ")
            routes = query_routes_by_countries(source_country, destination_country)
            if not routes.empty:
                print(f"Available routes from {source_country} to {destination_country}:")
                print(routes)
            else:
                print(f"No routes found from {source_country} to {destination_country}")
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
