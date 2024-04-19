-- Drop the existing view if it exists
DROP VIEW IF EXISTS vFlightPrices;

-- -------- All flights --------
CREATE VIEW vFlightPrices AS
SELECT 
  s.legID, 
  a1.airportName AS DepartureAirport, 
  a2.airportName AS ArrivalAirport,
  s.flightDate, 
  s.baseFare, 
  s.totalFare,
  s.segmentsCabinCode,
  s.isNonStop
FROM 
  Legs s
  JOIN Airports a1 ON s.startingAirport = a1.iata
  JOIN Airports a2 ON s.destinationAirport = a2.iata;

-- Drop the procedure if it exists to avoid conflicts during creation
DROP PROCEDURE IF EXISTS AnalyzePriceTrends;

DELIMITER $$

CREATE PROCEDURE AnalyzePriceTrends(IN start_date DATE, IN end_date DATE)
BEGIN
  SELECT 
    YEARWEEK(s.flightDate) AS YearWeek,  -- This groups by week
    s.segmentsCabinCode AS CabinClass,
    AVG(s.baseFare) AS AvgBaseFare, 
    AVG(s.totalFare) AS AvgTotalFare
  FROM 
    vFlightPrices s
  WHERE 
    s.flightDate BETWEEN start_date AND end_date AND
    s.isNonStop = 1
  GROUP BY 
    YearWeek, CabinClass
  ORDER BY 
    CabinClass, YearWeek;
END$$

DELIMITER ;

-- --------- Non-stop flights -----------

-- Drop the existing view if it exists
DROP VIEW IF EXISTS vNonStopFlights;

-- Create a new view that includes relevant information for the analysis
CREATE VIEW vNonStopFlights AS
SELECT 
  s.flightDate, 
  s.travelDuration, 
  s.isNonStop, 
  s.baseFare, 
  s.totalFare, 
  s.seatsRemaining, 
  s.segmentsDepartureTimeRaw, 
  s.segmentsArrivalTimeRaw, 
  s.segmentsDurationInSeconds, 
  s.segmentsCabinCode
FROM 
  Legs s
WHERE 
  s.isNonStop = 1;
  
  -- ------- Delays Data ----------
  DROP VIEW IF EXISTS vFlightDelays;

  