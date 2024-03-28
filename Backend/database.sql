-- Drop tables if they exist in reverse order of creation
DROP TABLE IF EXISTS belongsTo, exists_in, cities, airports, flights, airplanes, connectingAirports, preferences, itineraries, hasroutes, loyaltyProgram, airline, users, temp_airports, temp_routes;

-- Users table
CREATE TABLE users (
  user_id int,
  fullName VARCHAR(255) NOT NULL,
  phoneNumber VARCHAR(20),
  addressFirstLine VARCHAR(255),
  addressLastLine VARCHAR(255),
  addressPostcode VARCHAR(10),
  billingFirstLine VARCHAR(255),
  billingLastLine VARCHAR(255),
  billingPostcode VARCHAR(10),
  loyaltyProgram int,
  birthDate DATE NOT NULL,
  gender CHAR(1) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  
  PRIMARY KEY (user_id)
);

-- Airline table
CREATE TABLE airline (
    airlineID int,
    airlinename VARCHAR(255) NOT NULL,
    iata VARCHAR(5),
    icao VARCHAR(5),
    country VARCHAR(255),

    PRIMARY KEY (airlineID)
);

-- Loyalty Program table
CREATE TABLE loyaltyProgram(
    programID int,
    loyaltyNumber VARCHAR(20) NOT NULL,
    loyaltyAirlineID int,
    loyaltyPoints INT NOT NULL,

    PRIMARY KEY (programID),
    FOREIGN KEY (loyaltyAirlineID) REFERENCES airline (airlineID)
);

-- Update Users table to add foreign key for loyaltyProgram
ALTER TABLE users ADD CONSTRAINT fk_loyaltyProgram FOREIGN KEY (loyaltyProgram) REFERENCES loyaltyProgram (programID);

-- Airplanes table
CREATE TABLE airplanes (
  airplane_id INT AUTO_INCREMENT,
  airplane_name VARCHAR(255),
  iata VARCHAR(50),
  icao VARCHAR(50),

  PRIMARY KEY (airplane_id),
  INDEX idx_airplane_name (airplane_name)
);

-- Cities table
CREATE TABLE cities (
  city_id INT AUTO_INCREMENT,
  cityName VARCHAR(255),
  country VARCHAR(255),
  timezone VARCHAR(255),

  PRIMARY KEY (city_id),
  UNIQUE (cityName, country),
  INDEX idx_city_name_country (cityName, country)
);

-- Airports table
CREATE TABLE airports (
  airport_id int,
  airportName VARCHAR(255),
  city_id INT,
  iata VARCHAR(5),
  icao VARCHAR(5),

  PRIMARY KEY (airport_id),
  FOREIGN KEY (city_id) REFERENCES cities (city_id) ON DELETE CASCADE
);

-- Flights table
CREATE TABLE flights (
  flight_id int,
  airplane_id int,
  flightTime TIME,
  arrivalTime TIME,
  departureTime TIME,
  flyingClass VARCHAR(50),
  airline int,
  itinerary_id int,

  PRIMARY KEY (flight_id),
  FOREIGN KEY (airplane_id) REFERENCES airplanes (airplane_id) ON DELETE SET NULL
  -- FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE -- Uncomment after creating itineraries table
);

-- Preferences table
CREATE TABLE preferences (
  preference_id int,
  flyingClass VARCHAR(255),
  layoverTime TIME,
  departureTime TIME,
  arrivalTime TIME,
  duration INT,
  emission VARCHAR(255),

  PRIMARY KEY (preference_id)
);

-- Itineraries table
CREATE TABLE itineraries (
  itinerary_id int,
  user_id int,
  flight_id int,
  preference_id int,
  PRIMARY KEY (itinerary_id),

  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
  FOREIGN KEY (flight_id) REFERENCES flights (flight_id) ON DELETE SET NULL,
  FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE SET NULL
);

-- Update Flights table to add foreign key for itineraries
ALTER TABLE flights ADD CONSTRAINT fk_itinerary_id FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE;

-- ConnectingAirports table
CREATE TABLE connectingAirports(
    preference_id int,
    connectingAirport int,
    airport_id int,
    airportName VARCHAR(255),

    PRIMARY KEY (preference_id, connectingAirport),
    FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE CASCADE,
    FOREIGN KEY (connectingAirport) REFERENCES airports (airport_id) ON DELETE CASCADE
);

-- HasRoutes table
CREATE TABLE hasroutes (
    airlineID int,
    source_airport_id int,
    destination_airport_id int,

    PRIMARY KEY (airlineID, source_airport_id, destination_airport_id),
    FOREIGN KEY (airlineID) REFERENCES airline (airlineID),
    FOREIGN KEY (source_airport_id) REFERENCES airports (airport_id),
    FOREIGN KEY (destination_airport_id) REFERENCES airports (airport_id)
);

-- BelongsTo table
CREATE TABLE belongsTo (
   airlineID int,
   name VARCHAR(30),
   PRIMARY KEY (airlineID, name),
   FOREIGN KEY (airlineID) REFERENCES airline (airlineID) ON DELETE CASCADE,
   FOREIGN KEY (name) REFERENCES airplanes (airplane_name) ON DELETE CASCADE
);

-- Schedule and Pricing tables
CREATE TABLE schedule (
  schedule_id INT AUTO_INCREMENT,
  airlineID INT,
  source_airport_id INT,
  destination_airport_id INT,
  flight_date_time DATETIME,
  segments_departure_time_raw DATETIME,
  segments_arrival_time_raw DATETIME,
  segments_duration_in_seconds INT,
  segments_equipment_description VARCHAR(255),
  is_non_stop TINYINT(1),

  PRIMARY KEY (airlineID, source_airport_id, destination_airport_id, flight_date_time),
  FOREIGN KEY (airlineID) REFERENCES airline (airlineID),
  FOREIGN KEY (source_airport_id) REFERENCES airports (airport_id),
  FOREIGN KEY (destination_airport_id) REFERENCES airports (airport_id)
);

CREATE TABLE pricing (
  pricing_id INT AUTO_INCREMENT,
  airlineID INT,
  source_airport_id INT,
  destination_airport_id INT,
  flying_class VARCHAR(50),
  base_fare FLOAT,

  PRIMARY KEY (airlineID, source_airport_id, destination_airport_id, flying_class),
  FOREIGN KEY (airlineID) REFERENCES airline (airlineID),
  FOREIGN KEY (source_airport_id) REFERENCES airports (airport_id),
  FOREIGN KEY (destination_airport_id) REFERENCES airports (airport_id)
);

-- -------- TRIGGERS --------

DELIMITER $$

CREATE TRIGGER check_iata_before_insert
BEFORE INSERT ON airline
FOR EACH ROW
BEGIN
  IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Either iata or icao must be provided on insert.';
  END IF;
END$$

CREATE TRIGGER check_iata_before_update
BEFORE UPDATE ON airline
FOR EACH ROW
BEGIN
  IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Either iata or icao must be provided on update.';
  END IF;
END$$

DELIMITER ;

-- --------------------- LOADING DATA ---------------------------------

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airlines.csv'
IGNORE INTO TABLE airline
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 3 LINES
(
  AirlineID,
  @temp_name,
  @dummy,  -- Alias column to be ignored.
  @temp_IATA,
  @temp_ICAO,
  @dummy,  -- Callsign column to be ignored.
  @temp_Country,
  @dummy   -- Active column to be ignored.
)
SET
  airlinename = NULLIF(@temp_name, 'Unknown'),
  iata = NULLIF(@temp_IATA, '-'),
  icao = NULLIF(@temp_ICAO, ''),
  country = NULLIF(@temp_Country, '\\N');

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airplanes.csv'
INTO TABLE airplanes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  airplane_name,
  @iata,
  @icao
)
SET
  iata = NULLIF(@iata, '\N'),
  icao = NULLIF(@icao, '\N');
  
-- Load data into cities table (only city-related columns, ignore the rest)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airports.csv'
IGNORE INTO TABLE cities
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, @dummy, cityName, country, @dummy, @dummy, @dummy, @dummy, @dummy, timezone, @dummy, @dummy, @dummy, @dummy);

-- Create a temporary table to hold all data from CSV
CREATE TABLE temp_airports (
  airport_id int,
    airportName VARCHAR(255),
    cityName VARCHAR(255),
    country VARCHAR(255),
    iata VARCHAR(5),
    icao VARCHAR(5)
);

-- Load data into the temporary table
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airports.csv'
INTO TABLE temp_airports
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(airport_id, airportName, cityName, country, iata, icao, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);

-- Insert data into airports with a join to get city_id
INSERT INTO airports (airport_id, airportName, city_id, iata, icao)
SELECT t.airport_id, t.airportName, c.city_id, t.iata, t.icao
FROM temp_airports t
JOIN cities c ON t.cityName = c.cityName AND t.country = c.country;

-- Drop the temporary table
DROP TABLE temp_airports;

-- Create a temporary table to hold all data from CSV
CREATE TABLE temp_routes (
  airline VARCHAR(255),
  airlineID INT,
  sourceAirport VARCHAR(255),
  sourceAirportID INT,
  destinationAirport VARCHAR(255),
  destinationAirportID INT,
  codeshare VARCHAR(255),
  stops INT,
  equipment VARCHAR(255)
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/routes.csv'
IGNORE INTO TABLE temp_routes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(airline, 
 @airlineID, 
 sourceAirport, 
 @sourceAirportID, 
 destinationAirport, 
 @destinationAirportID, 
 codeshare, 
 stops, 
 equipment)
SET
  airlineID = NULLIF(@airlineID, '\N'),
  sourceAirportID = NULLIF(@sourceAirportID, '\N'),
  destinationAirportID = NULLIF(@destinationAirportID, '\N');

INSERT INTO hasroutes (airlineID, source_airport_id, destination_airport_id)
SELECT t.airlineID, t.sourceAirportID, t.destinationAirportID
FROM temp_routes t
WHERE t.airlineID IS NOT NULL
  AND t.sourceAirportID IS NOT NULL 
  AND t.destinationAirportID IS NOT NULL
  AND EXISTS (SELECT 1 FROM airports a WHERE a.airport_id = t.sourceAirportID)
  AND EXISTS (SELECT 1 FROM airports a WHERE a.airport_id = t.destinationAirportID);
