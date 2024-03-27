-- Drop tables if they exist in reverse order of creation
DROP TABLE IF EXISTS belongsTo, exists_in, cities, airports, flights, airplanes, connectingAirports, preferences, itineraries, hasroutes, loyaltyProgram, airline, users;

-- Users table
CREATE TABLE users (
  user_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
  fullName VARCHAR(255) NOT NULL,
  phoneNumber VARCHAR(20),
  addressFirstLine VARCHAR(255),
  addressLastLine VARCHAR(255),
  addressPostcode VARCHAR(10),
  billingFirstLine VARCHAR(255),
  billingLastLine VARCHAR(255),
  billingPostcode VARCHAR(10),
  loyaltyProgram BINARY(16),
  birthDate DATE NOT NULL,
  gender CHAR(1) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  
  PRIMARY KEY (user_id)
);

-- Airline table
CREATE TABLE airline (
    airlineID int,
    airlinename VARCHAR(255),
    iata VARCHAR(5),
    icao VARCHAR(5),
    country VARCHAR(255),

    PRIMARY KEY (airlineID)
);

-- Loyalty Program table
CREATE TABLE loyaltyProgram(
    programID BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
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
  -- airplane_id INT AUTO_INCREMENT,
  airplane_name VARCHAR(255),
  iata VARCHAR(5),
  icao VARCHAR(5),

  PRIMARY KEY (airplane_name),
  INDEX idx_airplane_name (airplane_name) -- Add this line to create an index on airplane_name
);

-- Cities table
CREATE TABLE cities (
  city_id INT AUTO_INCREMENT,
  cityName VARCHAR(255),
  country VARCHAR(255),
  timezone VARCHAR(255),

  PRIMARY KEY (city_id)
);

-- Airports table
CREATE TABLE airports (
  airport_id int AUTO_INCREMENT,
  airportName VARCHAR(255),
  city_id INT,
  iata VARCHAR(5),
  icao VARCHAR(5),

  PRIMARY KEY (airport_id),
  FOREIGN KEY (city_id) REFERENCES cities (city_id) ON DELETE CASCADE
);

-- ExistsIn table (relationship table between Airports and Cities)
CREATE TABLE exists_in (
  airport_id BINARY(16),
  city_id BINARY(16),
  PRIMARY KEY (airport_id, city_id),
  FOREIGN KEY (airport_id) REFERENCES airports (airport_id) ON DELETE CASCADE,
  FOREIGN KEY (city_id) REFERENCES cities (city_id) ON DELETE CASCADE
);

-- Flights table
CREATE TABLE flights (
  flight_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
  airplane_name VARCHAR(50),
  flightTime TIME,
  arrivalTime TIME,
  departureTime TIME,
  flyingClass VARCHAR(50),
  airline BINARY(16),
  itinerary_id BINARY(16),

  PRIMARY KEY (flight_id),
  FOREIGN KEY (airplane_name) REFERENCES airplanes (airplane_name) ON DELETE SET NULL
  -- FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE -- Uncomment after creating itineraries table
);

-- Preferences table
CREATE TABLE preferences (
  preference_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
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
  itinerary_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
  user_id BINARY(16),
  flight_id BINARY(16),
  preference_id BINARY(16),
  PRIMARY KEY (itinerary_id),

  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
  FOREIGN KEY (flight_id) REFERENCES flights (flight_id) ON DELETE SET NULL,
  FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE SET NULL
);

-- Update Flights table to add foreign key for itineraries
ALTER TABLE flights ADD CONSTRAINT fk_itinerary_id FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE;

-- ConnectingAirports table
CREATE TABLE connectingAirports(
    preference_id BINARY(16),
    connectingAirport BINARY(16),
    airport_id BINARY(16) DEFAULT (UUID_TO_BIN(UUID())),
    airportName VARCHAR(255),

    PRIMARY KEY (preference_id, connectingAirport),
    FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE CASCADE,
    FOREIGN KEY (connectingAirport) REFERENCES airports (airport_id) ON DELETE CASCADE
);

-- HasRoutes table
CREATE TABLE hasroutes (
    airlineID int,
    airport_id BINARY(16),

    PRIMARY KEY (airlineID, airport_id),
    FOREIGN KEY (airlineID) REFERENCES airline (airlineID),
    FOREIGN KEY (airport_id) REFERENCES airports (airport_id)
);

-- BelongsTo table
CREATE TABLE belongsTo (
   airlineID int,
   name VARCHAR(30),
   PRIMARY KEY (airlineID, name),
   FOREIGN KEY (airlineID) REFERENCES airline (airlineID) ON DELETE CASCADE,
   FOREIGN KEY (name) REFERENCES airplanes (airplane_name) ON DELETE CASCADE
);

-- DELIMITER $$

-- CREATE TRIGGER check_iata_before_insert
-- BEFORE INSERT ON airline
-- FOR EACH ROW
-- BEGIN
--   IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
--     SIGNAL SQLSTATE '45000'
--     SET MESSAGE_TEXT = 'Either iata or icao must be provided on insert.';
--   END IF;
-- END$$

-- CREATE TRIGGER check_iata_before_update
-- BEFORE UPDATE ON airline
-- FOR EACH ROW
-- BEGIN
--   IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
--     SIGNAL SQLSTATE '45000'
--     SET MESSAGE_TEXT = 'Either iata or icao must be provided on update.';
--   END IF;
-- END$$

-- DELIMITER ;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airlines.csv'
IGNORE INTO TABLE airline
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
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
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(
  airplane_name,
  iata,
  icao
);
