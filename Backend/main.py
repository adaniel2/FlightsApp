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

# -----------------------------------------------------------------------------------------------------

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

def main():
    print("Welcome to the Flight Query CLI!")
    source_iata = input("Enter the source airport IATA code: ")
    destination_iata = input("Enter the destination airport IATA code: ")
    routes = query_routes(source_iata, destination_iata)
    if not routes.empty:
        print("Available routes:")
        print(routes)
    else:
        print("No routes found from", source_iata, "to", destination_iata)

if __name__ == "__main__":
    main()
