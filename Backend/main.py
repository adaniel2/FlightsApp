# import pandas as pd
# from sqlalchemy import create_engine

# # Define the connection parameters
# db_username = 'root'
# db_password = '!#%Sql981'
# db_host = 'localhost'
# db_port = '3306'
# db_name = 'flights'

# # Create a connection string
# connection_string = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

# # Create an engine to connect to the MySQL database
# engine = create_engine(connection_string)

# # Load the CSV file into a DataFrame
# csv_file_path = 'airplanes.csv'
# df = pd.read_csv(csv_file_path)

# df.rename(columns={'Name': 'airplane_name', 'IATA code': 'iata', 'ICAO code': 'icao'}, inplace=True)

# # Insert the data into the table
# table_name = 'airplanes'
# df.to_sql(table_name, engine, if_exists='append', index=False)

# -----------------------------------------------------------------------------------------------------

