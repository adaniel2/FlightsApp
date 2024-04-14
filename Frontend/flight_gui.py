import tkinter as tk
from tkinter import ttk, messagebox
import requests
from style_config import configure_styles

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
        if mode == "airports":
            label1.config(text="Source IATA:")
            label2.config(text="Destination IATA:")
        elif mode == "countries":
            label1.config(text="Source Country:")
            label2.config(text="Destination Country:")
        
        label2.pack(side='left', padx=(10, 0))
        destination_entry.pack(side='left', padx=(10, 0))
    elif mode == "airline":
        label1.config(text="Airline Name:")
    elif mode == "country":
        label1.config(text="Country Name:")

def search_routes():
    search_mode = search_mode_combobox.get()
    source = source_entry.get().strip()
    destination = destination_entry.get().strip()

    url = f'http://127.0.0.1:5000/{search_mode.lower()}?'

    if search_mode in ["airports", "countries"]:
        url += f'source_iata={source}&destination_iata={destination}'
    elif search_mode == "airline":
        url += f'airline_name={source}'
    elif search_mode == "country":
        url += f'country_name={source}'

    response = requests.get(url)
    
    if response.status_code == 200:
        for i in tree.get_children():
            tree.delete(i)
        for route in response.json():
            tree.insert('', 'end', values=(route.get('sourceIATA', ''), route.get('destinationIATA', ''), route.get('airlineName', '')))
    else:
        messagebox.showinfo("Result", response.json().get('message', 'Error'))

# Frame for input fields
input_frame = ttk.Frame(root)
input_frame.pack(side='left', fill='x', expand=True)

# Labels and Entries
label1 = ttk.Label(input_frame, text="Source IATA:")
label2 = ttk.Label(input_frame, text="Destination IATA:")
source_entry = ttk.Entry(input_frame, width=20)
destination_entry = ttk.Entry(input_frame, width=20)

# Combobox for selecting search mode
search_mode_combobox = ttk.Combobox(root, values=["airports", "airline", "countries", "country"], state="readonly")
search_mode_combobox.set("airports")
search_mode_combobox.pack(side='left', padx=(10, 10))
search_mode_combobox.bind('<<ComboboxSelected>>', update_input_fields)

# Initial packing
update_input_fields()

# Search button
search_button = ttk.Button(root, text="Search", command=search_routes)
search_button.pack(side='left', padx=(10, 10))

# Treeview for displaying results
columns = ('source', 'destination', 'airline')
tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    tree.heading(col, text=col.capitalize())
    tree.column(col, width=120)
tree.pack(side='left', fill='both', expand=True)

root.mainloop()
