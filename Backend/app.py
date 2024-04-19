from flask import Flask, jsonify, request
from db import query_routes, query_airline_routes, query_routes_by_countries, query_by_country
from db import create_user, add_preferences_to_db, query_flight_details, get_user_preferences, add_itinerary_to_db
from db import get_analyze_price_trends, get_flight_data_for_clustering, get_data_for_apriori, get_data_for_correlation
from db import get_predict_flight
import json
import urllib.parse
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
import joblib

app = Flask(__name__)

# ------- Clustering Methods ------
# ---------------------------------

@app.route('/cluster_flights', methods=['GET'])
def cluster_flights():
    features = request.args.get('features', 'baseFare,totalFare,travelDuration')
    n_clusters = int(request.args.get('n_clusters', 3))
    selected_view = request.args.get('view', 'vFlightPrices')  # Get the selected view from query parameters

    # Convert features from comma-separated string to list
    feature_list = features.split(',')

    df = get_flight_data_for_clustering(feature_list, selected_view)

    if not df.empty:
        scaler = StandardScaler()
        # Only scale and fit features that exist in the dataframe
        valid_features = [
            feature for feature in feature_list if feature in df.columns]
        features = scaler.fit_transform(df[valid_features])
        kmeans = KMeans(n_clusters=n_clusters)
        df['cluster'] = kmeans.fit_predict(features)

        # Accessing the cluster centers
        centers = kmeans.cluster_centers_
        print("Cluster Centers:", centers)

        return jsonify(df.to_dict(orient='records'))
    else:
        return jsonify({'error': 'Failed to fetch data or data is empty'}), 500

# ------- Finding correlations -----
# ----------------------------------

@app.route('/correlations', methods=['GET'])
def correlations():
    feature1 = request.args.get('feature1', 'totalFare')  # Default to 'totalFare' if not specified
    feature2 = request.args.get('feature2', 'seatsRemaining')  # Default to 'seatsRemaining' if not specified
    
    df = get_data_for_correlation([feature1, feature2])
    if not df.empty:
        correlation_matrix = df[[feature1, feature2]].corr()
        return jsonify(correlation_matrix.to_dict())
    else:
        return jsonify({'error': 'Failed to fetch data or data is empty'}), 500

# --------- Apriori --------
# --------------------------


@app.route('/apriori', methods=['GET'])
def apriori_analysis():
    df = get_data_for_apriori()
    if not df.empty:
        te = TransactionEncoder()
        te_ary = te.fit(df).transform(df)
        df = pd.DataFrame(te_ary, columns=te.columns_)
        frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
        rules = association_rules(
            frequent_itemsets, metric="confidence", min_threshold=0.1)
        return jsonify(rules.to_dict(orient='records'))
    else:
        return jsonify({'error': 'Failed to fetch data or data is empty'}), 500

# --------- Validation -----
# --------------------------


@app.route('/cross_validate', methods=['GET'])
def cross_validate_model():
    X, y = get_model_training_data()
    if not X.empty and not y.empty:
        model = RandomForestClassifier()
        scores = cross_val_score(model, X, y, cv=5)
        return jsonify({'scores': scores.tolist(), 'average': scores.mean()})
    else:
        return jsonify({'error': 'Failed to fetch data or data is empty'}), 500

# --------- Classification ---------
# ----------------------------------
model = joblib.load('flight_delay_predictor.joblib')

@app.route('/predict_delay/<legID>', methods=['GET'])
def predict_delay(legID):
    # Fetch processed flight data
    processed_data = get_predict_flight(legID)
    
    if processed_data is not None:
        prediction = model.predict([processed_data])
        
        return jsonify({'delayed': bool(prediction[0])})
    else:
        return jsonify({'error': 'Failed to fetch or process flight data'}), 500

# --------- Other Routes ---------
# --------------------------------


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


@app.route('/analyze_price_trends', methods=['GET'])
def analyze_price_trends_endpoint():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        # Call the stored procedure and get the result
        result = get_analyze_price_trends(start_date, end_date)

        return jsonify(result)
    except Exception as e:
        print(str(e))

        return jsonify({'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
