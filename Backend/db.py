import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import datetime
import re

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

def get_flight_data_for_clustering(features, selected_view):
    sql = f"SELECT {', '.join(features)} FROM {selected_view}"

    try:
        with engine.connect() as connection:
            df = pd.read_sql(sql, connection)

            if 'travelDuration' in features:
                df['travelDuration'] = df['travelDuration'].apply(
                    iso8601_duration_to_minutes)
                
            # Automatically handle one-hot encoding if 'segmentsCabinCode' is included
            if 'segmentsCabinCode' in features:
                df = pd.get_dummies(df, columns=['segmentsCabinCode'], drop_first=True)

            return df
    except Exception as e:
        print(f"Error fetching data for clustering: {str(e)}")

        return pd.DataFrame()

def get_data_for_correlation(features):
    sql = f"SELECT {', '.join(features)} FROM vNonStopFlights"

    try:
        with engine.connect() as connection:
            result = pd.read_sql(sql, connection)

            if 'travelDuration' in features:
                result['travelDuration'] = result['travelDuration'].apply(
                    iso8601_duration_to_minutes)

            return result
    except Exception as e:
        print(f"Error fetching data for correlation: {str(e)}")
        return pd.DataFrame()

    
def get_data_for_apriori():
    # This would ideally fetch transactional data; adjust the SQL as necessary
    sql = "SELECT transaction_id, item FROM TransactionTable"
    try:
        with engine.connect() as connection:
            result = pd.read_sql(sql, connection)
            return result
    except Exception as e:
        print(f"Error fetching data for Apriori: {str(e)}")
        return pd.DataFrame()

def create_user(user_data):
    sql = text("""
        INSERT INTO Users (
            fullName, phoneNumber, addressFirstLine, addressLastLine, addressPostcode,
            billingFirstLine, billingLastLine, billingPostcode, birthDate, gender, email
        ) VALUES (
            :fullName, :phoneNumber, :addressFirstLine, :addressLastLine, :addressPostcode,
            :billingFirstLine, :billingLastLine, :billingPostcode, :birthDate, :gender, :email
        )
    """)

    try:
        with engine.begin() as connection:
            result = connection.execute(sql, user_data)
            user_id = result.lastrowid
            return user_id
        return True
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return False

def clean_preferences_data(data):
    # Define fields that should be converted to None if they are empty strings
    fields_to_clean = ['preferredLayoverTime', 'preferredDepartureTime',
                       'preferredArrivalTime', 'preferredDuration', 
                       'preferLowEmission', 'preferredGroundTransportation', 
                       'preferredHotelChain']
    
    for field in fields_to_clean:
        if field in data and data[field] == '':
            data[field] = None  # Convert empty strings to None
    
    return data

def add_preferences_to_db(prefs_data):
    prefs_data = clean_preferences_data(prefs_data)

    # Query to get the maximum preferenceNumber for this userID
    max_pref_num_sql = text("""
        SELECT MAX(preferenceNumber) FROM Preferences WHERE userID = :userID
    """)

    # Query to insert the new preference
    insert_sql = text("""
        INSERT INTO Preferences (
            preferenceNumber, userID, preferredFlyingClass, preferredLayoverTime, preferredDepartureTime, 
            preferredArrivalTime, preferredDuration, preferLowEmission, 
            preferredGroundTransportation, preferredHotelChain
        ) VALUES (
            :preferenceNumber, :userID, :preferredFlyingClass, :preferredLayoverTime, :preferredDepartureTime, 
            :preferredArrivalTime, :preferredDuration, :preferLowEmission, 
            :preferredGroundTransportation, :preferredHotelChain
        )
    """)

    try:
        with engine.begin() as connection:
            # First, fetch the highest current preferenceNumber for this user
            result = connection.execute(
                max_pref_num_sql, {'userID': prefs_data['userID']})
            max_pref_number = result.scalar() or 0  # Use 0 if none found
            next_pref_number = max_pref_number + 1

            # Now, insert the new preference with the calculated preferenceNumber
            prefs_data['preferenceNumber'] = next_pref_number
            connection.execute(insert_sql, prefs_data)
        return True
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return False


def get_user_preferences(user_id):
    sql = text("""
        SELECT *
        FROM Preferences
        WHERE userID = :user_id
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(sql, {'user_id': user_id}).fetchall()
            column_names = ['preferenceID', 'userID', 'preferredFlyingClass', 'preferredLayoverTime', 'preferredDepartureTime',
                            'preferredArrivalTime', 'preferredDuration', 'preferLowEmission', 'preferredGroundTransportation', 'preferredHotelChain']
            preferences = []
            for row in result:
                preference = {}
                for idx, column in enumerate(column_names):
                    if isinstance(row[idx], datetime.timedelta):
                        # Convert timedelta to a total number of seconds
                        preference[column] = row[idx].total_seconds()
                    else:
                        preference[column] = row[idx]
                preferences.append(preference)
            return preferences
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return None


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


def query_flight_details(source_iata, destination_iata, airline_name, is_non_stop, preferences):
    """
    Query flight details including times and prices for a given route and airline,
    potentially incorporating user preferences.
    """
    from sqlalchemy.sql import text

    try:
        with engine.connect() as connection:
            # Get airline IATA code from the airline name
            airline_iata = connection.execute(
                text("SELECT iata FROM Airline WHERE airlineName = :airline_name"),
                {'airline_name': airline_name}
            ).scalar()

            if not airline_iata:
                return []  # No airline found with the given name

            # Base SQL query
            sql_query = """
                SELECT
                    legId, startingAirport, destinationAirport, flightDate,
                    travelDuration, elapsedDays, isBasicEconomy, isRefundable,
                    isNonStop, baseFare, totalFare, seatsRemaining,
                    segmentsDepartureTimeRaw, segmentsArrivalTimeRaw,
                    segmentsArrivalAirportCode, segmentsDepartureAirportCode,
                    segmentsAirlineCode, segmentsEquipmentDescription,
                    segmentsDurationInSeconds, segmentsCabinCode
                FROM Legs
                WHERE startingAirport = :source_iata
                  AND destinationAirport = :destination_iata
                  AND segmentsAirlineCode = :airline_iata
                  AND isNonStop = :is_non_stop
            """

            # Dynamic parameters for the SQL query
            params = {
                "source_iata": source_iata,
                "destination_iata": destination_iata,
                "airline_iata": airline_iata,
                "is_non_stop": is_non_stop,
            }

            # Add preference-based filters dynamically
            if 'preferredFlyingClass' in preferences and preferences['preferredFlyingClass']:
                sql_query += " AND segmentsCabinCode = :flying_class"
                params['flying_class'] = preferences['preferredFlyingClass']

            # Length of the flight
            if 'preferredDuration' in preferences and preferences['preferredDuration']:
                sql_query += " AND segmentsDurationInSeconds <= :duration"
                params['duration'] = preferences['preferredDuration'] * 60

            if 'preferredArrivalTime' in preferences and preferences['preferredArrivalTime']:
                sql_query += """
                AND TIME(STR_TO_DATE(segmentsArrivalTimeRaw, '%Y-%m-%dT%H:%i:%s')) <= TIME(:arrival_time)
                """
                # Convert float time (expressed in seconds since midnight) to HH:MM:SS format for SQL
                hours = int(preferences['preferredArrivalTime'] // 3600)
                minutes = int((preferences['preferredArrivalTime'] % 3600) // 60)
                formatted_time = f"{hours:02}:{minutes:02}:00"  # Format to HH:MM:SS
                params['arrival_time'] = formatted_time

            if 'preferredDepartureTime' in preferences and preferences['preferredDepartureTime']:
                # Convert float time (expressed in seconds since midnight) to HH:MM:SS format for SQL
                hours = int(preferences['preferredDepartureTime'] // 3600)
                minutes = int((preferences['preferredDepartureTime'] % 3600) // 60)
                formatted_time = f"{hours:02}:{minutes:02}:00"  # Format to HH:MM:SS

                # SQL condition to check the preferred departure time +/- 1 hour
                sql_query += """
                AND TIME(STR_TO_DATE(segmentsDepartureTimeRaw, '%Y-%m-%dT%H:%i:%s')) 
                BETWEEN TIME(:departure_time) - INTERVAL 1 HOUR AND TIME(:departure_time) + INTERVAL 1 HOUR
                """
                params['departure_time'] = formatted_time

            if 'preferredLayoverTime' in preferences and preferences['preferredLayoverTime']:
                # Convert seconds to minutes for easier comparison and readability in SQL
                minutes = preferences['preferredLayoverTime'] // 60

                # SQL condition to match the layover time
                sql_query += """
                AND layoverDurationMinutes = :layover_minutes
                """
                params['layover_minutes'] = minutes

            # Order the results
            sql_query += " ORDER BY flightDate, segmentsDepartureTimeRaw;"

            print(sql_query)

            # Execute the dynamic query
            legs_result = connection.execute(text(sql_query), params).fetchall()

            # Prepare data for return
            column_names = [
                'legId', 'startingAirport', 'destinationAirport', 'flightDate',
                'travelDuration', 'elapsedDays', 'isBasicEconomy', 'isRefundable',
                'isNonStop', 'baseFare', 'totalFare', 'seatsRemaining',
                'segmentsDepartureTimeRaw', 'segmentsArrivalTimeRaw',
                'segmentsArrivalAirportCode', 'segmentsDepartureAirportCode',
                'segmentsAirlineCode', 'segmentsEquipmentDescription',
                'segmentsDurationInSeconds', 'segmentsCabinCode'
            ]

            return [dict(zip(column_names, row)) for row in legs_result]

    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return []


def add_itinerary_to_db(itinerary_data):
    # Fetch flight details based on flightID
    flight_query = text("""
        SELECT
            legId, startingAirport, destinationAirport, flightDate,
            travelDuration, elapsedDays, isBasicEconomy, isRefundable,
            isNonStop, baseFare, totalFare, seatsRemaining,
            segmentsDepartureTimeRaw, segmentsArrivalTimeRaw,
            segmentsArrivalAirportCode, segmentsDepartureAirportCode,
            segmentsAirlineName, segmentsAirlineCode, segmentsEquipmentDescription,
            segmentsDurationInSeconds, segmentsCabinCode
        FROM Legs
        WHERE legId = :flightID
    """)

    try:
        with engine.begin() as connection:
            flight_details = connection.execute(
                flight_query, {'flightID': itinerary_data['flightID']}).fetchone()

            if flight_details:
                # Access elements by their indices
                # index for segmentsCabinCode
                segmentsCabinCode = flight_details[20]
                # index for segmentsAirlineName
                airlineName = flight_details[16]

                # Insert itinerary with essential details fetched from the flight details
                itinerary_sql = text("""
                    INSERT INTO Itineraries (userID, flightID, flyingClass, airlineName)
                    VALUES (:userID, :flightID, :flyingClass, :airlineName)
                """)
                itinerary_data.update({
                    'flyingClass': segmentsCabinCode,
                    'airlineName': airlineName,
                })
                connection.execute(itinerary_sql, itinerary_data)

                return True
            else:
                return False  # No flight details found, cannot insert itinerary
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return False

def get_analyze_price_trends(start_date, end_date):
    # SQL to call the stored procedure
    sql = text("CALL AnalyzePriceTrends(:start, :end)")
    
    with engine.connect() as conn:
        # Execute the stored procedure passing the parameters as a dictionary
        result = conn.execute(sql, {'start': start_date, 'end': end_date})
        # Fetching all results from the query
        rows = result.fetchall()
        
        # Convert each tuple in the list to a dictionary
        trends = [
            {'month': row[0], 'avgBaseFare': row[2], 'avgTotalFare': row[3], 'cabinClass': row[1]} 
            for row in rows
        ]
        
        return trends


def convert_row_to_dict(row, column_names):
    return dict(zip(column_names, row))

def iso8601_duration_to_minutes(duration_str):
    # Regex to extract hours and minutes from the ISO 8601 duration format
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?')
    parts = pattern.match(duration_str)
    
    if not parts:
        print(f"No match for {duration_str}")
        return 0
    
    parts = parts.groups()
    hours = int(parts[0]) if parts[0] else 0
    minutes = int(parts[1]) if parts[1] else 0
    
    total_minutes = hours * 60 + minutes
    
    return total_minutes
