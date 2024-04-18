from flask import Flask, jsonify, request
from db import query_routes, query_airline_routes, query_routes_by_countries, query_by_country
from db import create_user, add_preferences_to_db, query_flight_details, get_user_preferences, add_itinerary_to_db
import json
import urllib.parse

app = Flask(__name__)


@app.route('/add_to_itinerary', methods=['POST'])
def add_to_itinerary():
    itinerary_data = request.json

    try:
        # Call to a function that will execute the SQL command
        result = add_itinerary_to_db(itinerary_data)
        print(result)
        if result:
            return jsonify({'message': 'Itinerary added successfully'}), 201
        else:
            return jsonify({'message': 'Failed to add to itinerary'}), 400
    except Exception as e:
        print(str(e))
        return jsonify({'message': str(e)}), 500


@app.route('/create_user', methods=['POST'])
def create_user_route():
    user_data = request.json
    user_id = create_user(user_data)

    if user_id:
        return jsonify({'message': 'User created successfully', 'userID': user_id}), 201
    else:
        return jsonify({'message': 'Failed to create user'}), 400


@app.route('/add_preferences', methods=['POST'])
def add_preferences():
    prefs_data = request.json
    result = add_preferences_to_db(prefs_data)

    if result:
        return jsonify({'message': 'Preferences saved successfully'}), 201
    else:
        return jsonify({'message': 'Failed to save preferences'}), 400


@app.route('/get_preferences', methods=['GET'])
def get_preferences():
    user_id = request.args.get('userID')
    if not user_id:
        return jsonify({'error': 'Missing userID parameter'}), 400

    preferences = get_user_preferences(user_id)
    if preferences is not None:
        return jsonify(preferences)
    else:
        return jsonify({'error': 'Failed to retrieve preferences or database error'}), 500


@app.route('/airports')
def get_routes():
    source_iata = request.args.get('source')
    destination_iata = request.args.get('destination')

    if source_iata and destination_iata:
        routes = query_routes(source_iata, destination_iata)

        if not routes.empty:
            return jsonify(routes.to_dict(orient='records'))

        return jsonify({'message': 'No routes found'}), 404

    return jsonify({'message': 'Missing parameters'}), 400


@app.route('/airline')
def get_airline_routes():
    airline_name = request.args.get('airline_name')

    if airline_name:
        routes = query_airline_routes(airline_name)

        if not routes.empty:
            return jsonify(routes.to_dict(orient='records'))

        return jsonify({'message': 'No routes found'}), 404

    return jsonify({'message': 'Missing parameters'}), 400


@app.route('/country')
def get_country_routes():
    source_country = request.args.get('source_country')
    routes = query_by_country(source_country)

    if not routes.empty:
        return jsonify(routes.to_dict(orient='records'))

    return jsonify({'message': 'No routes found'}), 404


@app.route('/countries')
def get_routes_by_countries():
    source_country = request.args.get('source')
    destination_country = request.args.get('destination')

    if source_country and destination_country:
        routes = query_routes_by_countries(source_country, destination_country)

        if not routes.empty:
            return jsonify(routes.to_dict(orient='records'))

        return jsonify({'message': 'No routes found'}), 404

    return jsonify({'message': 'Missing parameters'}), 400


@app.route('/flight_details')
def get_flight_details():
    source_iata = request.args.get('source_iata')
    destination_iata = request.args.get('destination_iata')
    airline_name = request.args.get('airline_name')
    is_non_stop = request.args.get('is_non_stop')
    encoded_prefs = request.args.get('prefs', '')

    # Decode the preferences from URL encoding and parse JSON
    try:
        decoded_prefs = urllib.parse.unquote(encoded_prefs)
        preferences = json.loads(decoded_prefs)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Now use `preferences` as a normal dictionary
    print(preferences)

    flight_details = query_flight_details(
        source_iata, destination_iata, airline_name, is_non_stop, preferences)

    if flight_details:
        return jsonify(flight_details)

    return jsonify({'message': 'No flight details found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
