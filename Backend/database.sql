-- Drop tables if they exist
DROP TABLE IF EXISTS BelongsTo, ConnectingAirports, HasRoutes, TempRoutes, TempAirports, FlightPassengers, Flights, Schedule,
Itineraries, Preferences, LoyaltyProgram, Users, Airplanes, Cities, Airports, Airline;

-- Users table
CREATE TABLE Users (
  userID int AUTO_INCREMENT,
  fullName VARCHAR(128) NOT NULL, -- 128 characters seems more than reasonable for a full name
  phoneNumber VARCHAR(25) NOT NULL, -- Could allow multiple phone numbers; kept as 1 for project scope
  addressFirstLine VARCHAR(64) NOT NULL,
  addressLastLine VARCHAR(64) NOT NULL,
  addressPostcode VARCHAR(10) NOT NULL,
  billingFirstLine VARCHAR(64) NOT NULL,
  billingLastLine VARCHAR(64) NOT NULL,
  billingPostcode VARCHAR(10) NOT NULL,
  birthDate DATE NOT NULL,
  gender ENUM('M', 'F', 'NB') NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  
  PRIMARY KEY (userID),
  UNIQUE (phoneNumber)
);

-- Airline table
CREATE TABLE Airline (
    airlineID int,
    airlineName VARCHAR(128) NOT NULL,
    iata VARCHAR(5) NOT NULL,
    icao VARCHAR(5),
    country VARCHAR(64), -- The longest English country name is 56 characters

    PRIMARY KEY (airlineID)
);

CREATE INDEX idx_airline_name ON Airline(airlineName);
CREATE INDEX idx_airline_iata ON Airline(iata);

-- Loyalty Program table
CREATE TABLE LoyaltyProgram(
    userID int,
    loyaltyProgram VARCHAR(20),
    loyaltyAirlineID int NOT NULL,
    loyaltyPoints INT NOT NULL DEFAULT 100,

    PRIMARY KEY (userID, loyaltyProgram),
    FOREIGN KEY (loyaltyAirlineID) REFERENCES Airline (airlineID)
);

-- Airplanes table
CREATE TABLE Airplanes (
  airplaneName VARCHAR(128) NOT NULL,
  iata VARCHAR(5) NOT NULL,
  icao VARCHAR(5),

  PRIMARY KEY (airplaneName)
);

-- Cities table
CREATE TABLE Cities (
  cityID INT AUTO_INCREMENT,
  cityName VARCHAR(85) NOT NULL, -- Guinness World Record for longest place name @ 85 characters
  country VARCHAR(64) NOT NULL,
  timezone VARCHAR(50) NOT NULL, -- Adjusting char length as needed

  PRIMARY KEY (cityID),
  UNIQUE (cityName, country),
  INDEX idx_city_name_country (cityName, country)
);

-- Airports table
CREATE TABLE Airports (
  airportID int,
  airportName VARCHAR(100) NOT NULL, -- Longest airport name at 72 characters
  cityID INT NOT NULL,
  iata VARCHAR(5) NOT NULL,
  icao VARCHAR(5),

  PRIMARY KEY (airportID),
  FOREIGN KEY (cityID) REFERENCES Cities (cityID) ON DELETE CASCADE
);

CREATE INDEX idx_airports_iata ON Airports(iata);
CREATE INDEX idx_airports_airport_name ON Airports(airportName);

-- Flights table
CREATE TABLE Flights (
  flightID VARCHAR(35),
  airplaneName VARCHAR(128) NOT NULL,
  flightTime TIME NOT NULL,
  arrivalTime TIME NOT NULL,
  departureTime TIME NOT NULL,

  PRIMARY KEY (flightID),
  
  FOREIGN KEY (airplaneName) REFERENCES Airplanes (airplaneName) ON DELETE CASCADE
);

CREATE TABLE FlightPassengers (
  flightID VARCHAR(35),
  userID int,

  PRIMARY KEY (flightID, userID),

  FOREIGN KEY (flightID) REFERENCES Flights (flightID) ON DELETE CASCADE,
  FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE
);

-- Preferences table
CREATE TABLE Preferences (
  -- All optional except PK
  preferenceNumber int, -- User can have multiple presets
  userID int,
  preferredFlyingClass ENUM('coach', 'premium coach', 'business', 'first'),
  preferredLayoverTime TIME,
  preferredDepartureTime TIME,
  preferredArrivalTime TIME,
  preferredDuration INT,
  preferLowEmission tinyint(1),
  preferredGroundTransportation VARCHAR(20),
  preferredHotelChain VARCHAR(20),

  PRIMARY KEY (preferenceNumber, userID),

  FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE
);

-- ConnectingAirports table
CREATE TABLE ConnectingAirports(
    preferenceNumber int,
    userID int,
    connectingAirport int NOT NULL,
    airportName VARCHAR(100) NOT NULL,

    PRIMARY KEY (preferenceNumber, userID, connectingAirport),

    FOREIGN KEY (preferenceNumber, userID) REFERENCES Preferences (preferenceNumber, userID) ON DELETE CASCADE,
    FOREIGN KEY (connectingAirport) REFERENCES Airports (airportID) ON DELETE CASCADE,
    FOREIGN KEY (airportName) REFERENCES Airports (airportName) -- ON DELETE CASCADE?
);

-- HasRoutes table
CREATE TABLE HasRoutes (
    airlineID int,
    sourceAirportID int,
    destinationAirportID int,

    PRIMARY KEY (airlineID, sourceAirportID, destinationAirportID),
    
    FOREIGN KEY (airlineID) REFERENCES Airline (airlineID),
    FOREIGN KEY (sourceAirportID) REFERENCES Airports (airportID),
    FOREIGN KEY (destinationAirportID) REFERENCES Airports (airportID)
);

-- BelongsTo table
CREATE TABLE BelongsTo (
   airlineID int,
   airplaneName VARCHAR(128),

   PRIMARY KEY (airlineID, airplaneName),
   FOREIGN KEY (airlineID) REFERENCES Airline (airlineID) ON DELETE CASCADE,
   FOREIGN KEY (airplaneName) REFERENCES Airplanes (airplaneName) ON DELETE CASCADE
);

CREATE TABLE Schedule (
  legId VARCHAR(35), -- Some 32-digit hexadecimal number
  startingAirport VARCHAR(5) NOT NULL, -- Using IATA code
  destinationAirport VARCHAR(5) NOT NULL, -- Using IATA code
  flightDate DATE NOT NULL,
  travelDuration VARCHAR(50) NOT NULL, -- ISO 8601 duration format, no fixed length it seems; will be conservative
  elapsedDays int NOT NULL,
  isBasicEconomy tinyint(1) NOT NULL,
  isRefundable tinyint(1) NOT NULL,
  isNonStop tinyint(1) NOT NULL,
  baseFare FLOAT NOT NULL,
  totalFare FLOAT NOT NULL,
  seatsRemaining INT NOT NULL,

  -- Segment strings are long; maybe 128 is a safe bet
  segmentsDepartureTimeRaw VARCHAR(128) NOT NULL,
  segmentsArrivalTimeRaw VARCHAR(128) NOT NULL,
  segmentsArrivalAirportCode VARCHAR(128) NOT NULL,
  segmentsDepartureAirportCode VARCHAR(128) NOT NULL,
  segmentsAirlineName VARCHAR(128) NOT NULL,
  segmentsAirlineCode VARCHAR(128) NOT NULL,
  segmentsEquipmentDescription VARCHAR(128) NOT NULL,
  segmentsDurationInSeconds VARCHAR(128) NOT NULL,
  segmentsCabinCode VARCHAR(128) NOT NULL,

  PRIMARY KEY (legId),
  FOREIGN KEY (startingAirport) REFERENCES Airports (iata),
  FOREIGN KEY (destinationAirport) REFERENCES Airports (iata)
);

-- Itineraries table
CREATE TABLE Itineraries (
  userID int,
  flightID VARCHAR(35),
  flyingClass ENUM('coach', 'premium coach', 'business', 'first') NOT NULL,
  airlineName VARCHAR(128) NOT NULL, -- Should be airlineID, but airline IATA is also unique and saves us work

  PRIMARY KEY (userID, flightID),

  FOREIGN KEY (userID) REFERENCES Users (userID) ON DELETE CASCADE,
  FOREIGN KEY (flightID) REFERENCES Schedule (legId) ON DELETE CASCADE,
  FOREIGN KEY (airlineName) REFERENCES Airline (airlineName) ON DELETE CASCADE
);

-- CREATE TABLE LayoverTimes (

-- );

-- ------------------ TRIGGERS ------------------------

DROP TRIGGER IF EXISTS check_iata_before_insert;
DROP TRIGGER IF EXISTS check_iata_before_update;


DELIMITER $$

CREATE TRIGGER check_iata_before_insert
BEFORE INSERT ON Airline
FOR EACH ROW
BEGIN
  IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Either iata or icao must be provided on insert.';
  END IF;
END$$

CREATE TRIGGER check_iata_before_update
BEFORE UPDATE ON Airline
FOR EACH ROW
BEGIN
  IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Either iata or icao must be provided on update.';
  END IF;
END$$

DELIMITER ;

-- ----------------------- LOADING DATA ---------------------------------

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airlines.csv'
IGNORE INTO TABLE Airline
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
  airlineName = CASE
                  WHEN @temp_name = 'Delta Air Lines' THEN 'Delta'
                  WHEN @temp_name = 'Unknown' THEN NULL
                  ELSE @temp_name
                END,
  iata = NULLIF(@temp_IATA, '-'),
  icao = NULLIF(@temp_ICAO, ''),
  country = NULLIF(@temp_Country, '\\N');

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Airplanes.csv'
IGNORE INTO TABLE Airplanes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(
  airplaneName,
  @iata,
  @icao
)
SET
  iata = NULLIF(@iata, '\N'),
  icao = NULLIF(@icao, '\N');
  
-- Load data into Cities table (only city-related columns, ignore the rest)
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airports.csv'
IGNORE INTO TABLE Cities
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@dummy, @dummy, cityName, country, @dummy, @dummy, @dummy, @dummy, @dummy, timezone, @dummy, @dummy, @dummy, @dummy);

-- Create a temporary table to hold all data from CSV
CREATE TABLE TempAirports (
	airportID int,
  airportName VARCHAR(100) NOT NULL,
  cityName VARCHAR(85) NOT NULL,
  country VARCHAR(64) NOT NULL,
  iata VARCHAR(5) NOT NULL,
  icao VARCHAR(5)
);

-- Load data into the temporary table
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/airports.csv'
IGNORE INTO TABLE TempAirports
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(airportID, airportName, cityName, country, iata, icao, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);

-- Insert data into Airports with a join to get cityID
INSERT INTO Airports (airportID, airportName, cityID, iata, icao)
SELECT t.airportID, t.airportName, c.cityID, t.iata, t.icao
FROM TempAirports t
JOIN Cities c ON t.cityName = c.cityName AND t.country = c.country;

-- Drop the temporary table
DROP TABLE TempAirports;

-- Create a temporary table to hold all data from CSV
CREATE TABLE TempRoutes (
  airlineName VARCHAR(100),
  airlineID INT,
  sourceAirport VARCHAR(100),
  sourceAirportID INT,
  destinationAirport VARCHAR(100),
  destinationAirportID INT,
  codeShare VARCHAR(50),
  stops INT,
  equipment VARCHAR(100)
);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/routes.csv'
IGNORE INTO TABLE TempRoutes
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(airlineName,
 @airlineID, 
 sourceAirport, 
 @sourceAirportID, 
 destinationAirport, 
 @destinationAirportID, 
 codeShare, 
 stops, 
 equipment)
SET
  airlineID = NULLIF(@airlineID, '\N'),
  sourceAirportID = NULLIF(@sourceAirportID, '\N'),
  destinationAirportID = NULLIF(@destinationAirportID, '\N');

INSERT INTO HasRoutes (airlineID, sourceAirportID, destinationAirportID)
SELECT t.airlineID, t.sourceAirportID, t.destinationAirportID
FROM TempRoutes t
WHERE t.airlineID IS NOT NULL
  AND t.sourceAirportID IS NOT NULL 
  AND t.destinationAirportID IS NOT NULL
  AND EXISTS (SELECT 1 FROM Airports a WHERE a.airportID = t.sourceAirportID)
  AND EXISTS (SELECT 1 FROM Airports a WHERE a.airportID = t.destinationAirportID);

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Itineraries_small.csv'
IGNORE INTO TABLE Schedule
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 LINES
(
  legId,
  @searchDate,
  @flightDate,
  startingAirport,
  destinationAirport,
  @fareBasisCode,
  travelDuration,
  elapsedDays,
  @isBasicEconomy,
  @isRefundable,
  @isNonStop,
  baseFare,
  totalFare,
  seatsRemaining,
  @totalTravelDistance,
  @segmentsDepartureTimeEpochSeconds,
  segmentsDepartureTimeRaw,
  @segmentsArrivalTimeEpochSeconds,
  segmentsArrivalTimeRaw,
  segmentsArrivalAirportCode,
  segmentsDepartureAirportCode,
  segmentsAirlineName,
  segmentsAirlineCode,
  segmentsEquipmentDescription,
  segmentsDurationInSeconds,
  @segmentsDistance,
  segmentsCabinCode
)
SET
  flightDate = CASE
                  WHEN @flightDate LIKE '%/%/%' THEN STR_TO_DATE(@flightDate, '%d/%m/%Y')
                  WHEN @flightDate LIKE '%-%-%' THEN STR_TO_DATE(@flightDate, '%Y-%m-%d')
                  ELSE NULL
                END,
  isBasicEconomy = CASE WHEN @isNonStop = 'TRUE' THEN 1 ELSE 0 END,              
  isRefundable = CASE WHEN @isNonStop = 'TRUE' THEN 1 ELSE 0 END,
  isNonStop = CASE WHEN @isNonStop = 'TRUE' THEN 1 ELSE 0 END;
