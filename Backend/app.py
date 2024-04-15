from flask import Flask, jsonify, request
from db import query_routes, query_airline_routes, query_routes_by_countries, query_by_country, create_user

app = Flask(__name__)

@app.route('/create_user', methods=['POST'])
def create_user_route():
    user_data = request.json
    
    if create_user(user_data):
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'message': 'Failed to create user'}), 400

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

if __name__ == '__main__':
    app.run(debug=True)
