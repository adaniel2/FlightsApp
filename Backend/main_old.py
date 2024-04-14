# -----------------------------------------------------------------------------------------------------
from db import query_routes, query_airline_routes, query_routes_by_countries, query_by_country

def main():
    print("Welcome to the Flight Query CLI!")

    while True:
        print("\nPlease choose an option:")
        print("1. Search by airports")
        print("2. Search by airline")
        print("3. Search by country")
        print("4. Search by countries")
        print("5. Exit")

        choice = input("Enter your choice (1, 2, 3, 4, or 5): ")

        if choice == '1':
            source_iata = input("Enter the source airport IATA code: ")
            destination_iata = input("Enter the destination airport IATA code: ")
            routes = query_routes(source_iata, destination_iata)
            if not routes.empty:
                print("Available routes:")
                print(routes)
            else:
                print("No routes found from", source_iata, "to", destination_iata)
        elif choice == '2':
            airline_name = input("Enter the airline name: ")
            routes = query_airline_routes(airline_name)
            if not routes.empty:
                print(f"Available routes for {airline_name}:")
                print(routes)
            else:
                print(f"No routes found for {airline_name}")
        elif choice == '3':
            country_name = input("Enter the country name: ")
            routes = query_by_country(country_name)
            if not routes.empty:
                print(f"Available airports and routes in {country_name}:")
                print(routes)
            else:
                print(f"No routes found within {country_name}")
        elif choice == '4':
            source_country = input("Enter the source country name: ")
            destination_country = input("Enter the destination country name: ")
            routes = query_routes_by_countries(source_country, destination_country)
            
            if not routes.empty:
                print(f"Available routes from {source_country} to {destination_country}:")
                print(routes)
            else:
                print(f"No routes found from {source_country} to {destination_country}")
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
