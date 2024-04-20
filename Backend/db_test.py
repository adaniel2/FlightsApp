import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

class TestDatabaseFunctions(unittest.TestCase):
    @patch('sqlalchemy.create_engine')
    def test_get_flight_delay_data_success(self, mock_engine):
        expected_df = pd.DataFrame({
            'FlightDate': ['2024-01-01'],
            'DepTime': ['12:00'],
            'ArrTime': ['15:00'],
            'DepDelayMinutes': [30],
            'ArrDelayMinutes': [45],
            'IATA_Code_Operating_Airline': ['AB'],
            'Origin': ['JFK'],
            'Dest': ['LAX']
        })
        
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = expected_df
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute.return_value.keys.return_value = expected_df.columns.tolist()

        from db import get_flight_delay_data  
        result_df = get_flight_delay_data()

        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('sqlalchemy.create_engine')
    def test_get_flight_delay_data_failure(self, mock_engine):
        mock_engine.return_value.connect.return_value.__enter__.return_value.execute.side_effect = Exception("Database Error")
        
        from db import get_flight_delay_data
        result_df = get_flight_delay_data()

        self.assertTrue(result_df.empty)

    @patch('sqlalchemy.create_engine')
    def test_create_user_success(self, mock_engine):
        mock_conn = mock_engine.return_value.begin.return_value.__enter__.return_value
        mock_conn.execute.return_value.lastrowid = 100  

        from db import create_user
        user_data = {
            'fullName': "Test User",
            'phoneNumber': "1234567890",
            'addressFirstLine': "101 Test St",
            'addressLastLine': "Suite 10",
            'addressPostcode': "98765",
            'billingFirstLine': "101 Test St",
            'billingLastLine': "Suite 10",
            'billingPostcode': "98765",
            'birthDate': "1990-01-01",
            'gender': "M",
            'email': "test@example.com"
        }
        result = create_user(user_data)
        self.assertEqual(result, 100)  

    @patch('sqlalchemy.create_engine')
    def test_create_user_failure(self, mock_engine):
        mock_conn = mock_engine.return_value.begin.return_value.__enter__.return_value
        mock_conn.execute.side_effect = Exception("Database Insert Error")

        from db import create_user
        user_data = {
            'fullName': "Test User",
            'phoneNumber': "1234567890",            
        }
        result = create_user(user_data)
        self.assertFalse(result)

    @patch('pandas.read_sql')
    @patch('sqlalchemy.create_engine')
    def test_get_data_for_correlation(self, mock_engine, mock_read_sql):
        mock_df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6]
        })
        mock_read_sql.return_value = mock_df

        from db import get_data_for_correlation
        features = ['feature1', 'feature2']
        result_df = get_data_for_correlation(features)

        pd.testing.assert_frame_equal(result_df, mock_df)
        mock_read_sql.assert_called_once()

    @patch('pandas.read_sql')
    @patch('sqlalchemy.create_engine')
    def test_get_predict_flight(self, mock_engine, mock_read_sql):
        
        legID = 123
        mock_read_sql.return_value = pd.DataFrame({
            'flightDate': ['2024-01-01'],
            'segmentsDepartureTimeRaw': ['2024-01-01T12:00:00Z'],
            'segmentsArrivalTimeRaw': ['2024-01-01T15:00:00Z'],
            'segmentsAirlineCode': ['AB'],
            'startingAirport': ['JFK'],
            'destinationAirport': ['LAX']
        })

        from db import get_predict_flight

        
        with patch('db.preprocess_data_predict', return_value=pd.DataFrame()) as mock_preprocess:
            
            result = get_predict_flight(legID)

            mock_preprocess.assert_called_once()
            self.assertIsInstance(result, pd.DataFrame)


    @patch('sqlalchemy.create_engine')
    def test_get_user_preferences(self, mock_engine):
        
        user_id = 1
        mock_connection = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_connection.execute.return_value.fetchall.return_value = [
            (1, user_id, 'Economy', 180, '12:00', '15:00', 240, True, 'Uber', 'Hilton')
        ]

        from db import get_user_preferences
        
        preferences = get_user_preferences(user_id)

        self.assertIsInstance(preferences, list)
        self.assertGreater(len(preferences), 0)
        self.assertEqual(preferences[0]['userID'], user_id)

    @patch('pandas.read_sql')
    @patch('sqlalchemy.create_engine')
    def test_query_routes(self, mock_engine, mock_read_sql):
       
        expected_df = pd.DataFrame({
            'sourceIATA': ['JFK'],
            'destinationIATA': ['LAX'],
            'airlineName': ['Delta']
        })
        mock_read_sql.return_value = expected_df

        from db import query_routes
        
        result_df = query_routes('JFK', 'LAX')

        pd.testing


    @patch('pandas.read_sql')
    @patch('sqlalchemy.create_engine')
    def test_query_airline_routes(self, mock_engine, mock_read_sql):
       
        airline_name = "Delta"
        expected_df = pd.DataFrame({
            'airlineName': ['Delta'],
            'sourceIATA': ['JFK'],
            'destinationIATA': ['LAX']
        })
        mock_read_sql.return_value = expected_df

        from db import query_airline_routes
        
        result_df = query_airline_routes(airline_name)

        pd.testing.assert_frame_equal(result_df, expected_df)
        mock_read_sql.assert_called_once()

    def test_query_routes_by_countries(self, mock_engine, mock_read_sql):

        from db import query_routes_by_countries
        
        source_country = "USA"
        destination_country = "Canada"
        expected_df = pd.DataFrame({
            'sourceCountry': ['USA'],
            'destinationCountry': ['Canada'],
            'sourceIATA': ['JFK'],
            'destinationIATA': ['YYZ'],
            'airlineName': ['Air Canada']
        })
        mock_read_sql.return_value = expected_df
        
        result_df = query_routes_by_countries(source_country, destination_country)

        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_query_by_country(self, mock_engine, mock_read_sql):
        from db import query_by_country
        
        country_name = "USA"
        expected_df = pd.DataFrame({
            'sourceAirportID': [1],
            'sourceIATA': ['JFK'],
            'sourceAirportName': ['John F Kennedy International'],
            'sourceCityName': ['New York'],
            'destinationIATA': ['LAX'],
            'destinationAirportName': ['Los Angeles International'],
            'destinationCityName': ['Los Angeles']
        })
        mock_read_sql.return_value = expected_df
        
        result_df = query_by_country(country_name)

        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('sqlalchemy.create_engine')
    def test_query_flight_details(self, mock_engine):
        from db import query_flight_details
        
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.fetchall.return_value = []  
        
        result = query_flight_details("JFK", "LAX", "Delta", True, {})

        self.assertEqual(result, [])

    def test_add_itinerary_to_db(self, mock_engine):

        from db import add_itinerary_to_db
        
        itinerary_data = {'legID': 123, 'userID': 1}
        mock_conn = mock_engine.return_value.begin.return_value.__enter__.return_value
        mock_conn.execute.return_value.fetchone.return_value = [123, 'JFK', 'LAX']  
        
        result = add_itinerary_to_db(itinerary_data)

        self.assertTrue(result)

    def test_get_analyze_price_trends(self, mock_engine):

        from db import get_analyze_price_trends
        
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        expected_results = [{'month': 'January', 'avgBaseFare': 100, 'avgTotalFare': 120, 'cabinClass': 'Economy'}]
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.fetchall.return_value = [(1, 'Economy', 100, 120)]
        
        results = get_analyze_price_trends(start_date, end_date)

        self.assertEqual(results, expected_results)

    def test_iso8601_duration_to_minutes(self):
        from db import iso8601_duration_to_minutes
        self.assertEqual(iso8601_duration_to_minutes("PT2H30M"), 150)
        self.assertEqual(iso8601_duration_to_minutes("PT45M"), 45)
        self.assertEqual(iso8601_duration_to_minutes("PT3H"), 180)
        self.assertEqual(iso8601_duration_to_minutes("Invalid"), 0)

    def test_calculate_layover_time(self):
        from db import calculate_layover_time
        previous_arrival = "2024-01-01T12:00:00.000Z"
        current_departure = "2024-01-01T15:00:00.000Z"
        expected_minutes = 180
        result = calculate_layover_time(previous_arrival, current_departure)
        self.assertEqual(result, expected_minutes)











