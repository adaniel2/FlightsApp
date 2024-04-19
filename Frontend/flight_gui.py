import tkinter.simpledialog as sd
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from style_config import configure_styles
import datetime
import json
import urllib.parse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import itertools

import sys
sys.path.append('../Backend')  # Adds the Backend folder to the system path

flight_listbox = None

# Create the main window
root = tk.Tk()
root.title("Flights Planner")

configure_styles()  # Apply styles configured in style_config.py


def update_input_fields(event=None):
    mode = search_mode_combobox.get()
    # Clear previous entries and labels
    for widget in input_frame.winfo_children():
        widget.pack_forget()

    label1.config(text="Source:")
    label1.pack(side='left', padx=(10, 0))
    source_entry.pack(side='left', padx=(10, 0))

    if mode in ["airports", "countries"]:
        label1.config(text="Source Country:" if mode ==
                      "countries" else "Source IATA:")
        label2.config(text="Destination Country:" if mode ==
                      "countries" else "Destination IATA:")
        label2.pack(side='left', padx=(10, 0))
        destination_entry.pack(side='left', padx=(10, 0))
    elif mode == "airline":
        label1.config(text="Airline Name:")
    elif mode == "country":
        label1.config(text="Country Name:")


def search_routes():
    search_mode = search_mode_combobox.get()
    source = source_entry.get().strip()
    destination = destination_entry.get().strip() if search_mode in [
        "airports", "countries"] else ''

    url = f'http://127.0.0.1:5000/{search_mode.lower()}'
    if search_mode in ["airports", "countries"]:
        url += f'?source={source}&destination={destination}'
    elif search_mode == "airline":
        url += f'?airline_name={source}'
    elif search_mode == "country":
        url += f'?source_country={source}'

    response = requests.get(url)
    if response.status_code == 200:
        for i in tree.get_children():
            tree.delete(i)
        for route in response.json():
            tree.insert('', 'end', values=(route.get('sourceIATA', ''), route.get(
                'destinationIATA', ''), route.get('airlineName', '')))
    else:
        messagebox.showinfo("Result", response.json().get('message', 'Error'))


def create_user_window():
    user_window = tk.Toplevel(root)
    user_window.title("Create User")

    labels = ['Full Name', 'Phone Number', 'Address Line 1', 'Address Line 2',
              'Postcode', 'Billing Address Line 1', 'Billing Address Line 2',
              'Billing Postcode', 'Birth Date', 'Gender', 'Email']
    entries = {}

    for idx, label in enumerate(labels):
        ttk.Label(user_window, text=label).grid(
            row=idx, column=0, padx=10, pady=5)
        entry = ttk.Combobox(user_window, values=[
                             "M", "F", "NB"], state="readonly") if label == 'Gender' else ttk.Entry(user_window, width=25)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[label] = entry

    ttk.Button(user_window, text="Submit", command=lambda: submit_user_data(
        entries)).grid(row=len(labels), column=0, columnspan=2, pady=10)


def submit_user_data(entries):
    user_data = {
        'fullName': entries['Full Name'].get(),
        'phoneNumber': entries['Phone Number'].get(),
        'addressFirstLine': entries['Address Line 1'].get(),
        'addressLastLine': entries['Address Line 2'].get(),
        'addressPostcode': entries['Postcode'].get(),
        'billingFirstLine': entries['Billing Address Line 1'].get(),
        'billingLastLine': entries['Billing Address Line 2'].get(),
        'billingPostcode': entries['Billing Postcode'].get(),
        'birthDate': entries['Birth Date'].get(),
        'gender': entries['Gender'].get(),
        'email': entries['Email'].get()
    }

    for key, value in user_data.items():
        if not value:
            messagebox.showerror("Error", f"Please fill out the {key} field.")
            return

    url = 'http://127.0.0.1:5000/create_user'

    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201:
            messagebox.showinfo("Success", "User created successfully!")
            global current_user_id
            current_user_id = response.json().get('userID')
        else:
            messagebox.showerror(
                "Error", f"Failed to create user: {response.json().get('message')}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to create user: {e}")


def open_preferences_window():
    pref_window = tk.Toplevel(root)
    pref_window.title("User Preferences")

    # Define the fields for preferences
    labels = [
        'Preferred Flying Class', 'Preferred Layover Time (HH:MM)', 'Preferred Departure Time (HH:MM)',
        'Preferred Arrival Time (HH:MM)', 'Preferred Duration (Minutes)', 'Prefer Low Emission (1 for yes, 0 for no)',
        'Preferred Ground Transportation', 'Preferred Hotel Chain'
    ]
    entries = {}

    # Combobox for preferred flying class
    flying_classes = ["coach", "premium coach", "business", "first"]
    ttk.Label(pref_window, text=labels[0]).grid(
        row=0, column=0, padx=10, pady=5)
    flying_class_combobox = ttk.Combobox(
        pref_window, values=flying_classes, state="readonly")
    flying_class_combobox.grid(row=0, column=1, padx=10, pady=5)
    entries[labels[0]] = flying_class_combobox

    # Entries for other preferences
    for idx, label in enumerate(labels[1:], 1):
        ttk.Label(pref_window, text=label).grid(
            row=idx, column=0, padx=10, pady=5)
        entry = ttk.Entry(pref_window, width=25)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[label] = entry

    # Button to submit preferences
    ttk.Button(pref_window, text="Submit Preferences", command=lambda: submit_preferences_data(
        entries)).grid(row=len(labels), column=0, columnspan=2, pady=10)


def submit_preferences_data(entries):
    # Collect all preference data
    preferences_data = {
        'userID': current_user_id,
        'preferredFlyingClass': entries['Preferred Flying Class'].get(),
        'preferredLayoverTime': entries['Preferred Layover Time (HH:MM)'].get(),
        'preferredDepartureTime': entries['Preferred Departure Time (HH:MM)'].get(),
        'preferredArrivalTime': entries['Preferred Arrival Time (HH:MM)'].get(),
        'preferredDuration': entries['Preferred Duration (Minutes)'].get(),
        'preferLowEmission': entries['Prefer Low Emission (1 for yes, 0 for no)'].get(),
        'preferredGroundTransportation': entries['Preferred Ground Transportation'].get(),
        'preferredHotelChain': entries['Preferred Hotel Chain'].get()
    }

    # Send preference data to the backend
    url = 'http://127.0.0.1:5000/add_preferences'
    try:
        response = requests.post(url, json=preferences_data)
        if response.status_code == 201:
            messagebox.showinfo("Success", "Preferences saved successfully!")
        else:
            messagebox.showerror(
                "Error", f"Failed to save preferences: {response.json().get('message')}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to save preferences: {e}")

# Setup input and interface elements
input_frame = ttk.Frame(root)
input_frame.pack(side='left', fill='x', expand=True)

label1 = ttk.Label(input_frame, text="Source IATA:")
label2 = ttk.Label(input_frame, text="Destination IATA:")
source_entry = ttk.Entry(input_frame, width=20)
destination_entry = ttk.Entry(input_frame, width=20)

search_mode_combobox = ttk.Combobox(
    root, values=["airports", "airline", "countries", "country"], state="readonly")
search_mode_combobox.set("airports")
search_mode_combobox.pack(side='left', padx=(10, 10))
search_mode_combobox.bind('<<ComboboxSelected>>', update_input_fields)

search_button = ttk.Button(root, text="Search", command=search_routes)
search_button.pack(side='left', padx=(10, 10))

columns = ('source', 'destination', 'airline')
tree = ttk.Treeview(root, columns=columns, show='headings')


def parse_datetime(raw_datetime):
    """Parse and format the datetime string."""
    # Remove the milliseconds and timezone information for simplicity

    datetime_obj = datetime.datetime.strptime(
        raw_datetime.split('.')[0], "%Y-%m-%dT%H:%M:%S")

    # Format the datetime as 'Month day, Year, Hour:Minute AM/PM'
    return datetime_obj.strftime("%B %d, %Y, %I:%M %p")


def save_itinerary_details(flight_id, user_id):
    url = 'http://127.0.0.1:5000/add_to_itinerary'
    itinerary_data = {
        'userID': user_id,
        'flightID': flight_id
    }

    try:
        response = requests.post(url, json=itinerary_data)
        if response.status_code == 201:
            messagebox.showinfo(
                "Success", "Flight added to itinerary successfully!")
        else:
            messagebox.showerror("Error", response.json().get(
                'message', 'Failed to add flight to itinerary'))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", str(e))


def add_to_itinerary(selection):
    global flight_listbox  # Use the global declaration

    if selection:
        selection_index = flight_listbox.curselection()[0]
        display_text, flight_id = flight_listbox.get(
            selection_index)  # Corrected to unpack three values

        save_itinerary_details(flight_id, current_user_id)


def display_flight_details(source_iata, destination_iata, airline_name, is_non_stop, preferences):
    global flight_listbox  # Use the global declaration

    # Convert preferences dictionary into a JSON string
    preferences_json = json.dumps(preferences)
    # URL encode the JSON string
    encoded_preferences = urllib.parse.quote(preferences_json)

    url = f'http://127.0.0.1:5000/flight_details?source_iata={source_iata}&destination_iata={destination_iata}&airline_name={airline_name}&is_non_stop={is_non_stop}&prefs={encoded_preferences}'
    response = requests.get(url)

    if response.status_code == 200:
        flights_window = tk.Toplevel(root)
        flights_window.title(
            f"Flights for {airline_name} from {source_iata} to {destination_iata}")

        flight_listbox = tk.Listbox(flights_window, width=120)
        flight_listbox.pack()
        flight_listbox.delete(0, tk.END)  # Ensure the Listbox is cleared

        flights = response.json()

        if flights:
            for flight in flights:
                formatted_departure = parse_datetime(
                    flight['segmentsDepartureTimeRaw'])
                formatted_arrival = parse_datetime(
                    flight['segmentsArrivalTimeRaw'])

                display_text = (
                    f"Depart: {formatted_departure} - "
                    f"Arrive: {formatted_arrival} - "
                    f"Fare: ${flight['totalFare']:.2f} (Base: ${flight['baseFare']:.2f}) - "
                    f"Seats Left: {flight['seatsRemaining']} - "
                    f"Cabin: {flight['segmentsCabinCode']}"
                )

                flight_id = flight['legId']

                # Store display text, flight ID in the Listbox
                flight_listbox.insert(tk.END, (display_text, flight_id))
        else:
            flight_listbox.insert(
                tk.END, "No flights found matching the criteria.")

        right_click_menu = tk.Menu(flights_window, tearoff=0)
        right_click_menu.add_command(
            label="Add to Itinerary", command=lambda: add_to_itinerary(flight_listbox.curselection()))

        def on_right_click(event):
            try:
                selection_index = flight_listbox.nearest(event.y)
                flight_listbox.selection_clear(0, tk.END)
                flight_listbox.selection_set(selection_index)
                flight_listbox.activate(selection_index)
                selected_item = flight_listbox.get(selection_index)
                display_text, flight_id = selected_item  # Unpack the tuple
                right_click_menu.post(event.x_root, event.y_root)
            except Exception as e:
                print(f"Error: {e}")

        # Bind right-click event
        flight_listbox.bind('<Button-3>', on_right_click)
    else:
        error_message = response.json().get('message', 'Error fetching flight details')
        messagebox.showerror(
            "Error", f"Could not fetch flight details: {error_message}")


def on_route_select(event):
    if tree.selection():
        selected_item = tree.selection()[0]
        route_details = tree.item(selected_item, 'values')

        if len(route_details) >= 3:
            source_iata, destination_iata, airline_name = route_details[:3]

            preferences = choose_preference(current_user_id)

            if preferences:
                display_flight_details(
                    source_iata, destination_iata, airline_name, 1, preferences)
        else:
            messagebox.showerror(
                "Error", "Selected item does not contain enough data.")
    else:
        messagebox.showinfo("Info", "Please select a route from the list.")


def choose_preference(user_id):
    url = f'http://127.0.0.1:5000/get_preferences?userID={user_id}'
    response = requests.get(url)

    if response.status_code == 200:
        preferences = response.json()

        if len(preferences) > 1:
            # Create a mapping from preference ID to preference object for easy access
            preferences_dict = {
                str(pref['preferenceID']): pref for pref in preferences}

            # Creating a list of preference descriptions for the user to choose from
            options = {str(
                pref['preferenceID']): f"{pref['preferredFlyingClass']} (ID: {pref['preferenceID']})" for pref in preferences}

            option_list = [options[key] for key in sorted(options)]

            # Use simpledialog to ask user for their preference
            choice = sd.askstring(
                "Select Preference", "Select your preference preset:\n" + "\n".join(option_list))

            if choice and choice in preferences_dict:
                # Return preferences for preference ID
                return preferences_dict[choice]
            messagebox.showinfo("Info", "No valid selection made.")
            return None  # No selection or cancelled dialog
        elif preferences:
            # Only one preference, return its flying class directly
            return preferences[0]
        else:
            messagebox.showinfo("Info", "No preferences found.")
            return None
    else:
        messagebox.showerror(
            "Error", f"Failed to fetch preferences: {response.json().get('message', 'An error occurred')}")
        return None

def format_year_week(year_week_int):
    # Convert year_week format from 202216 to "2022-W16"
    year = year_week_int // 100
    week = year_week_int % 100

    return f"{year}-W{week:02d}"

def open_analyze_price_trends_window():
    trend_window = tk.Toplevel(root)
    trend_window.title("Analyze Price Trends")
    
    # Add date entry fields and a submit button
    ttk.Label(trend_window, text="Start Date (YYYY-MM-DD):").pack()
    start_date_entry = ttk.Entry(trend_window)
    start_date_entry.pack()
    
    ttk.Label(trend_window, text="End Date (YYYY-MM-DD):").pack()
    end_date_entry = ttk.Entry(trend_window)
    end_date_entry.pack()
    
    submit_button = ttk.Button(trend_window, text="Analyze", 
        command=lambda: analyze_price_trends(start_date_entry.get(), end_date_entry.get()))
    submit_button.pack()

# Function to send request and display results
def analyze_price_trends(start_date, end_date):
    # Send request to Flask backend
    url = 'http://127.0.0.1:5000/analyze_price_trends'
    params = {'start_date': start_date, 'end_date': end_date}
    response = requests.get(url, params=params)
    
    # Open a new window to display the JSON results
    results_window = tk.Toplevel(root)
    results_window.title("Trend Analysis Results")
    
    if response.status_code == 200:
        json_data = response.json()
        results_text = tk.Text(results_window)
        results_text.insert(tk.END, json.dumps(json_data, indent=2))
        results_text.pack()
        
        # Convert JSON data to DataFrame and process
        df = pd.DataFrame(json_data)
        df['formatted_year_week'] = df['month'].apply(format_year_week)
        df.sort_values(by=['formatted_year_week'], inplace=True)  # Ensure data is sorted by time
        
        # Open another window for the plot
        plot_window = tk.Toplevel(root)
        plot_window.title("Price Trend Plot by Cabin Class")
        
        # Create a figure for plotting
        figure = plt.Figure(figsize=(10, 6), dpi=100)
        ax = figure.add_subplot(111)
        
        # Plotting the average total fare trends by cabin class
        cabin_classes = df['cabinClass'].unique()
        for cabin in cabin_classes:
            subset = df[df['cabinClass'] == cabin]
            subset.plot(x='formatted_year_week', y='avgTotalFare', kind='line', ax=ax, label=cabin, marker='o', linestyle='-')
        
        ax.set_title('Average Total Fare Trends by Cabin Class')
        ax.set_xlabel('Year-Week')
        ax.set_ylabel('Average Total Fare')
        ax.legend(title='Cabin Class')
        
        # Embedding the plot in Tkinter
        canvas = FigureCanvasTkAgg(figure, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    else:
        messagebox.showerror("Error", "Failed to retrieve trends.")

def open_cluster_flights_window():
    cluster_window = tk.Toplevel(root)
    cluster_window.title("Cluster Flights")

    # Label and Dropdown for selecting the SQL View
    ttk.Label(cluster_window, text="Select SQL View:").pack()
    view_var = tk.StringVar(cluster_window)
    view_var.set("vFlightPrices")  # default value
    views_dropdown = ttk.OptionMenu(cluster_window, view_var, "vFlightPrices", "vFlightPrices", "vNonStopFlights")
    views_dropdown.pack()

    # Label and Entry for Features
    ttk.Label(cluster_window, text="Features (comma-separated):").pack()
    features_entry = ttk.Entry(cluster_window)
    features_entry.pack()
    features_entry.insert(0, "totalFare,travelDuration,segmentsCabinCode")  # Default value

    # Label and Entry for Number of Clusters
    ttk.Label(cluster_window, text="Number of Clusters:").pack()
    n_clusters_entry = ttk.Entry(cluster_window)
    n_clusters_entry.pack()
    n_clusters_entry.insert(0, "3")  # Default value

    # Button to submit and perform clustering
    submit_button = ttk.Button(cluster_window, text="Cluster",
                               command=lambda: perform_clustering(features_entry.get(), n_clusters_entry.get(), view_var.get()))
    submit_button.pack()

def generate_marker_dict(unique_categories):
    # Define a cycle of markers from matplotlib
    markers = itertools.cycle(('o', 's', '^', 'P', '*', 'X', 'D'))  # More markers can be added

    return {category: next(markers) for category in unique_categories}

def perform_clustering(features, n_clusters, selected_view):
    split_features = features.split(',')
    url = f'http://127.0.0.1:5000/cluster_flights?features={features}&n_clusters={n_clusters}&view={selected_view}'
    response = requests.get(url)

    results_window = tk.Toplevel(root)
    results_window.title("Clustering Results")

    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        # Handling categorical
        df['category: '] = df[[col for col in df.columns if f"{split_features[2]}_" in col]].idxmax(axis=1)
        df['category: '] = df['category: '].apply(lambda x: x.split('_')[-1])

        # Create a marker dictionary based on unique cabin codes
        unique_categories = df['category: '].unique()
        marker_dict = generate_marker_dict(unique_categories)

        # Create a figure for plotting
        figure = plt.Figure(figsize=(10, 10), dpi=100)
        ax = figure.add_subplot(111)

        # Create a scatter plot
        for category in unique_categories:
            subset = df[df['category: '] == category]
            sns.scatterplot(x=f"{split_features[0]}", y=f"{split_features[1]}", style='category: ',
                            markers=marker_dict, hue='cluster', data=subset, ax=ax, palette='viridis', legend='full')

        #ax.set_title('Scatter Plot of Total Fare vs. Travel Duration by Cabin Code')
        #ax.set_xlabel('Total Fare ($)')
        #ax.set_ylabel('Travel Duration (minutes)')

        # Get the legend object from the scatterplot
        leg = ax.get_legend()

        # Set the font size for the labels and title
        leg.set_title('Cluster', prop={'size': 13})  # Set font size for the legend title
        for text in leg.get_texts():
            text.set_fontsize('6')  # Set font size for the labels

        # Embedding the plot in Tkinter
        canvas = FigureCanvasTkAgg(figure, master=results_window)
        canvas.draw()
        canvas.get_tk_widget().pack()
        
    else:
        messagebox.showerror("Error", f"Failed to retrieve clustering results: {response.text}")

def open_correlation_analysis_window():
    correlation_window = tk.Toplevel(root)
    correlation_window.title("Correlation Analysis")

    # List of features available for correlation
    features = ['totalFare', 'seatsRemaining', 'baseFare', 'travelDuration']  # Add other relevant features

    # Setup dropdowns for selecting features to correlate
    ttk.Label(correlation_window, text="Select Feature 1:").grid(row=0, column=0, padx=10, pady=5)
    feature1_var = tk.StringVar()
    feature1_dropdown = ttk.Combobox(correlation_window, textvariable=feature1_var, values=features, state="readonly")
    feature1_dropdown.grid(row=0, column=1, padx=10, pady=5)
    feature1_dropdown.set('totalFare')  # Default value

    ttk.Label(correlation_window, text="Select Feature 2:").grid(row=1, column=0, padx=10, pady=5)
    feature2_var = tk.StringVar()
    feature2_dropdown = ttk.Combobox(correlation_window, textvariable=feature2_var, values=features, state="readonly")
    feature2_dropdown.grid(row=1, column=1, padx=10, pady=5)
    feature2_dropdown.set('seatsRemaining')  # Default value

    # Button to submit and fetch correlation
    submit_button = ttk.Button(correlation_window, text="Analyze Correlation",
                               command=lambda: fetch_and_display_correlation(feature1_var.get(), feature2_var.get()))
    submit_button.grid(row=2, column=0, columnspan=2, pady=10)

def fetch_and_display_correlation(feature1, feature2):
    url = f"http://127.0.0.1:5000/correlations?feature1={feature1}&feature2={feature2}"
    response = requests.get(url)
    if response.status_code == 200:
        correlation_data = response.json()
        print(correlation_data)  # This print is useful for debugging and can be removed in production.

        df_corr = pd.DataFrame(correlation_data)

        # Create a heatmap
        plt.figure(figsize=(8, 6))
        sns.heatmap(df_corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(f'Correlation between {feature1} and {feature2}')  # Dynamic title based on features
        plt.show()
    else:
        messagebox.showerror("Error", "Failed to fetch correlation data")

tree.bind('<<TreeviewSelect>>', on_route_select)

for col in columns:
    tree.heading(col, text=col.capitalize())
    tree.column(col, width=120)
tree.pack(side='left', fill='both', expand=True)

# Setup menus
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

users_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Users", menu=users_menu)
users_menu.add_command(label="Create User", command=create_user_window)

preferences_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Preferences", menu=preferences_menu)
preferences_menu.add_command(
    label="Edit Preferences", command=open_preferences_window)

# Menu item for Data Mining
data_mining_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Data Mining", menu=data_mining_menu)
data_mining_menu.add_command(label="Analyze Price Trends", command=open_analyze_price_trends_window)
data_mining_menu.add_command(label="Cluster Flights", command=open_cluster_flights_window)
data_mining_menu.add_command(label="Correlation Analysis", command=open_correlation_analysis_window)


root.mainloop()
