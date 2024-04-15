from flask import Flask, jsonify, request
from db import query_routes, query_airline_routes, query_routes_by_countries, query_by_country

app = Flask(__name__)

@app.route('/airports')
def get_routes():
    source_iata = request.args.get('source_iata')
    destination_iata = request.args.get('destination_iata')

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

@app.route('/country/<country_name>')
def get_country_routes(country_name):
    routes = query_by_country(country_name)

    if not routes.empty:
        return jsonify(routes.to_dict(orient='records'))
    
    return jsonify({'message': 'No routes found'}), 404

@app.route('/countries')
def get_routes_by_countries():
    source_country = request.args.get('source_country')
    destination_country = request.args.get('destination_country')

    if source_country and destination_country:
        routes = query_routes_by_countries(source_country, destination_country)

        if not routes.empty:
            return jsonify(routes.to_dict(orient='records'))
        
        return jsonify({'message': 'No routes found'}), 404
    
    return jsonify({'message': 'Missing parameters'}), 400

if __name__ == '__main__':
    app.run(debug=True)
