import pandas as pd
from db import get_flight_delay_data
from sklearn.preprocessing import LabelEncoder
import joblib

def prepare_data():
    df = get_flight_delay_data()
   
    df_prepared = preprocess_data(df)
    
    df_prepared.to_csv('prepared_data.csv', index=False)
    print("Data types after conversion:", df_prepared.dtypes)

def dump_labelencoder(label_encoder):
    joblib.dump(label_encoder, 'label_encoder_IATA_Code_Operating_Airline.joblib')

def load_labelencoder():    
    label_encoder = joblib.load('label_encoder_IATA_Code_Operating_Airline.joblib')
    return label_encoder

def convert_iso8601_to_minutes(datetime_str):
    
    try:
        datetime_obj = pd.to_datetime(datetime_str, utc=True)
        datetime_obj = datetime_obj.tz_convert(None)
    except Exception as e:
        print(f"Failed to parse datetime: {e}")
        return None
 
    minutes_since_midnight = datetime_obj.hour * 60 + datetime_obj.minute
    return minutes_since_midnight

def preprocess_data(data, is_prediction=False):
    if is_prediction:
        print(data)
        for col in ['segmentsDepartureTimeRaw', 'segmentsArrivalTimeRaw']:
            print(data[col])
            data[col] = data[col].apply(convert_iso8601_to_minutes)
            print(data[col])
        rename_dict = {
            'flightDate':'FlightDate',
            'segmentsDepartureTimeRaw': 'DepTime',
            'segmentsArrivalTimeRaw': 'ArrTime',
            'segmentsAirlineCode': 'IATA_Code_Operating_Airline',
            'startingAirport': 'Origin',
            'destinationAirport': 'Dest'
        }
        data.rename(columns=rename_dict, inplace=True)
    
    # Ensure the data is in timedelta format and then convert
    if not is_prediction:
        for col in ['DepTime', 'ArrTime']:        
            if data[col].dtype == 'object':
                data[col] = pd.to_timedelta(data[col], errors='coerce')   
            if pd.api.types.is_timedelta64_dtype(data[col]):
                data[col] = convert_timedelta_to_minutes(data[col])
                print(data[col].dtype)
                print(data[col][0])

    
    categorical_cols = ['IATA_Code_Operating_Airline', 'Origin', 'Dest']
    label_encoder = LabelEncoder()
    for col in categorical_cols:
        data[col] = label_encoder.fit_transform(data[col])
    dump_labelencoder(label_encoder)

    # Fill missing values with mean for numeric columns as done in training
    numeric_cols = data.select_dtypes(include=['number']).columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

    return data

def preprocess_data_predict(data):
    for col in ['segmentsDepartureTimeRaw', 'segmentsArrivalTimeRaw']:
            print(data[col])
            data[col] = data[col].apply(convert_iso8601_to_minutes)
            print(data[col])
    rename_dict = {
            'flightDate':'FlightDate',
            'segmentsDepartureTimeRaw': 'DepTime',
            'segmentsArrivalTimeRaw': 'ArrTime',
            'segmentsAirlineCode': 'IATA_Code_Operating_Airline',
            'startingAirport': 'Origin',
            'destinationAirport': 'Dest'
        }
    data.rename(columns=rename_dict, inplace=True)
    
    categorical_cols = ['IATA_Code_Operating_Airline', 'Origin', 'Dest']
    label_encoder = LabelEncoder()
    for col in categorical_cols:
        data[col] = label_encoder.fit_transform(data[col])

    numeric_cols = data.select_dtypes(include=['number']).columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

    return data


def convert_timedelta_to_minutes(timedelta_series):
    # Convert timedelta series to total minutes
    return timedelta_series.dt.total_seconds() / 60

if __name__ == '__main__':
    prepare_data()
