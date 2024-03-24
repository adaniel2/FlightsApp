CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop tables if they exist
DROP TABLE IF EXISTS users, itineraries, preferences, airplanes, flights, airports, cities, hotels, transportations, exists_in CASCADE, loyaltyProgram;

-- Users table
CREATE TABLE users (
  user_id UUID DEFAULT uuid_generate_v4 (),
  fullName VARCHAR(255) NOT NULL,
  phoneNumber VARCHAR(20),
  addressFirstLine VARCHAR(255),
  addressLastLine VARCHAR(255),
  addressPostcode VARCHAR(10),
  billingFirstLine VARCHAR(255),
  billingLastLine VARCHAR(255),
  billingPostcode VARCHAR(10),
  loyaltyProgram VARCHAR(255),
  birthDate DATE NOT NULL,
  gender CHAR(1) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  
  PRIMARY KEY (user_id),
  FOREIGN KEY (loyaltyProgram) REFERENCES loyaltyProgram (programID)
);

CREATE TABLE airline (
    airlineID UUID DEFAULT uuid_generate_v4 (),
    name VARCHAR(255) NOT NULL,
    iata VARCHAR(5),
    icao VARCHAR(5),
    country VARCHAR(255) NOT NULL,

    PRIMARY KEY (airlineID),
    CHECK (iata IS NOT NULL OR icao IS NOT NULL)
);

CREATE TABLE loyaltyProgram(
    programID UUID DEFAULT uuid_generate_v4 (),
    loyaltyNumber VARCHAR(20) NOT NULL,
    loyaltyAirline VARCHAR(20),
    loyaltyPoints INT NOT NULL,

    PRIMARY KEY (programID),
    FOREIGN KEY (loyaltyAirline) REFERENCES airline (airlineID)
);

-- Itineraries table
CREATE TABLE itineraries (
  itinerary_id UUID DEFAULT uuid_generate_v4 (),
  user_id UUID,
  flightId UUID,
  preference_id UUID,
  PRIMARY KEY (user_id, flightId),

  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL,
  FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE SET NULL,
);

CREATE TABLE connectingAirports(
    preference_id UUID,
    connectingAirport UUID,
    airport_id UUID DEFAULT uuid_generate_v4 (),
    airportName VARCHAR(255),

    PRIMARY KEY (preference_id, connectingAirport),
    FOREIGN KEY (preference_id) REFERENCES preferences (preference_id) ON DELETE CASCADE,
    FOREIGN KEY (connectingAirport) REFERENCES airports (airport_id) ON DELETE CASCADE,
);

-- Preferences table
CREATE TABLE preferences (
  preference_id UUID DEFAULT uuid_generate_v4 (),
  flyingClass VARCHAR(255),
  layoverTime TIME,
  departureTime TIME,
  arrivalTime TIME,
  duration INT,
  emission VARCHAR(255),

  PRIMARY KEY (preference_id),
  FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE,
  FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE,
);

-- Airplanes table
CREATE TABLE airplanes (
  airplane_id UUID DEFAULT uuid_generate_v4 (),
  iata VARCHAR(5),
  icao VARCHAR(5),
  name VARCHAR(25),
  PRIMARY KEY (airplane_id)
);

-- Flights table
CREATE TABLE flights (
  flight_id UUID DEFAULT uuid_generate_v4 (),
  airplane_id UUID,
  flightTime TIME,
  arrivalTime TIME,
  departureTime TIME,
  flyingClass VARCHAR(50),
  airline VARCHAR(255),
  itinerary_id UUID,

  PRIMARY KEY (flight_id),
  FOREIGN KEY (airplane_id) REFERENCES airplanes (airplane_id) ON DELETE SET NULL,
  FOREIGN KEY (itinerary_id) REFERENCES itineraries (itinerary_id) ON DELETE CASCADE
);

-- Airports table
CREATE TABLE airports (
  airport_id UUID DEFAULT uuid_generate_v4 (),
  airportName VARCHAR(255),
  city_id UUID,
  iata VARCHAR(5),
  icao VARCHAR(5),

  PRIMARY KEY (airport_id)
);

-- Cities table
CREATE TABLE cities (
  city_id UUID DEFAULT uuid_generate_v4 (),
  cityName VARCHAR(255),
  country VARCHAR(255),
  timezone VARCHAR(255),

  PRIMARY KEY (city_id)
);

-- ExistsIn table (relationship table between Airports and Cities)
CREATE TABLE exists_in (
  airport_id UUID,
  city_id UUID,
  PRIMARY KEY (airport_id, city_id),
  FOREIGN KEY (airport_id) REFERENCES airports (airport_id) ON DELETE CASCADE,
  FOREIGN KEY (city_id) REFERENCES cities (city_id) ON DELETE CASCADE
);

-- Hotels table
CREATE TABLE hotels (
  hotel_id UUID DEFAULT uuid_generate_v4 (),
  chain VARCHAR(255),
  PRIMARY KEY (hotel_id)
);

-- Transportations table
CREATE TABLE transportations (
  transportation_id UUID DEFAULT uuid_generate_v4 (),
  travelMode VARCHAR(255),
  PRIMARY KEY (transportation_id)
);

------------------------------------------ Triggers
CREATE OR REPLACE FUNCTION ensure_iata_icao()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if both iata and icao are NULL
  IF NEW.iata IS NULL AND NEW.icao IS NULL THEN
    RAISE EXCEPTION 'Either iata or icao must be provided.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger that uses the function
CREATE TRIGGER check_iata_icao_before_insert_or_update
BEFORE INSERT OR UPDATE ON airline
FOR EACH ROW EXECUTE FUNCTION ensure_iata_icao();
