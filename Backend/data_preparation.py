import pandas as pd
from db import get_flight_delay_data

def prepare_data():
    df = get_flight_delay_data()
    
    # Convert time duration from string to total minutes
    df_prepared = preprocess_data(df)

    # Save the prepared data to a CSV file
    df_prepared.to_csv('prepared_data.csv', index=False)
    print("Data types after conversion:", df_prepared.dtypes)

def preprocess_data(data, is_prediction=False):
    if is_prediction:
        rename_dict = {
            'segmentsDepartureTimeRaw': 'DepTime',
            'segmentsArrivalTimeRaw': 'ArrTime',
            'segmentsAirlineCode': 'IATA_Code_Operating_Airline',
            'startingAirport': 'Origin',
            'destinationAirport': 'Dest'
        }
        data.rename(columns=rename_dict, inplace=True)
    
    # Ensure the data is in timedelta format and then convert
    for col in ['DepTime', 'ArrTime']:
        if data[col].dtype == 'object':
            data[col] = pd.to_timedelta(data[col], errors='coerce')
        if pd.api.types.is_timedelta64_dtype(data[col]):
            data[col] = convert_timedelta_to_minutes(data[col])

    # Apply the same categorical handling as in training
    data = pd.get_dummies(data, columns=['IATA_Code_Operating_Airline', 'Origin', 'Dest'])

    # Fill missing values with mean for numeric columns as done in training
    numeric_cols = data.select_dtypes(include=['number']).columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

    return data

def convert_timedelta_to_minutes(timedelta_series):
    # Convert timedelta series to total minutes
    return timedelta_series.dt.total_seconds() / 60

if __name__ == '__main__':
    prepare_data()
