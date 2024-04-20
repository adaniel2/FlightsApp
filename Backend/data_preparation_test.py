from data_preparation import convert_iso8601_to_minutes, convert_timedelta_to_minutes, preprocess_data
import pandas as pd

def test_convert_iso8601_to_minutes():
    assert convert_iso8601_to_minutes("2024-04-19T07:30:00+00:00") == 450, "Should be 450 minutes since midnight UTC"
    assert convert_iso8601_to_minutes("invalid-time") is None, "Should return None for invalid time"

test_convert_iso8601_to_minutes()


from unittest.mock import patch

def test_preprocess_data():
    test_data = {
        'segmentsDepartureTimeRaw': ['2024-04-19T07:30:00+00:00'],
        'segmentsArrivalTimeRaw': ['2024-04-19T09:30:00+00:00'],
        'flightDate': ['2024-04-19'],
        'segmentsAirlineCode': ['UA'],
        'startingAirport': ['JFK'],
        'destinationAirport': ['LAX']
    }
    df_test = pd.DataFrame(test_data)

    with patch('db.get_flight_delay_data', return_value=df_test):
        processed_data = preprocess_data(df_test, True) 

test_preprocess_data()


