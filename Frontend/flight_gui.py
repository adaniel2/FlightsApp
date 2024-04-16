import tkinter as tk
from tkinter import ttk, messagebox
import requests
from style_config import configure_styles

import sys
sys.path.append('../Backend')  # Adds the Backend folder to the system path

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
        label1.config(text="Source Country:" if mode == "countries" else "Source IATA:")
        label2.config(text="Destination Country:" if mode == "countries" else "Destination IATA:")
        label2.pack(side='left', padx=(10, 0))
        destination_entry.pack(side='left', padx=(10, 0))
    elif mode == "airline":
        label1.config(text="Airline Name:")
    elif mode == "country":
        label1.config(text="Country Name:")

def search_routes():
    search_mode = search_mode_combobox.get()
    source = source_entry.get().strip()
    destination = destination_entry.get().strip() if search_mode in ["airports", "countries"] else ''

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
            tree.insert('', 'end', values=(route.get('sourceIATA', ''), route.get('destinationIATA', ''), route.get('airlineName', '')))
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
        ttk.Label(user_window, text=label).grid(row=idx, column=0, padx=10, pady=5)
        entry = ttk.Combobox(user_window, values=["M", "F", "NB"], state="readonly") if label == 'Gender' else ttk.Entry(user_window, width=25)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[label] = entry

    ttk.Button(user_window, text="Submit", command=lambda: submit_user_data(entries)).grid(row=len(labels), column=0, columnspan=2, pady=10)

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
            messagebox.showerror("Error", f"Failed to create user: {response.json().get('message')}")
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
    ttk.Label(pref_window, text=labels[0]).grid(row=0, column=0, padx=10, pady=5)
    flying_class_combobox = ttk.Combobox(pref_window, values=flying_classes, state="readonly")
    flying_class_combobox.grid(row=0, column=1, padx=10, pady=5)
    entries[labels[0]] = flying_class_combobox

    # Entries for other preferences
    for idx, label in enumerate(labels[1:], 1):
        ttk.Label(pref_window, text=label).grid(row=idx, column=0, padx=10, pady=5)
        entry = ttk.Entry(pref_window, width=25)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[label] = entry

    # Button to submit preferences
    ttk.Button(pref_window, text="Submit Preferences", command=lambda: submit_preferences_data(entries)).grid(row=len(labels), column=0, columnspan=2, pady=10)

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
            messagebox.showerror("Error", f"Failed to save preferences: {response.json().get('message')}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to save preferences: {e}")

# Setup input and interface elements
input_frame = ttk.Frame(root)
input_frame.pack(side='left', fill='x', expand=True)

label1 = ttk.Label(input_frame, text="Source IATA:")
label2 = ttk.Label(input_frame, text="Destination IATA:")
source_entry = ttk.Entry(input_frame, width=20)
destination_entry = ttk.Entry(input_frame, width=20)

search_mode_combobox = ttk.Combobox(root, values=["airports", "airline", "countries", "country"], state="readonly")
search_mode_combobox.set("airports")
search_mode_combobox.pack(side='left', padx=(10, 10))
search_mode_combobox.bind('<<ComboboxSelected>>', update_input_fields)

search_button = ttk.Button(root, text="Search", command=search_routes)
search_button.pack(side='left', padx=(10, 10))

columns = ('source', 'destination', 'airline')
tree = ttk.Treeview(root, columns=columns, show='headings')

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
preferences_menu.add_command(label="Edit Preferences", command=open_preferences_window)

root.mainloop()
