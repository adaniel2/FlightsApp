import tkinter as tk
from tkinter import ttk, messagebox
import requests
from style_config import configure_styles

# Create the main window
root = tk.Tk()
root.title("Flights Planner")

configure_styles() # apply styles configured in style_config.py

def search_routes():
    source_iata = source_iata_entry.get()
    destination_iata = destination_iata_entry.get()
    response = requests.get(f'http://127.0.0.1:5000/routes?source_iata={source_iata}&destination_iata={destination_iata}')
    
    if response.status_code == 200:
        # Clear the treeview
        for i in tree.get_children():
            tree.delete(i)
        # Insert new data into the treeview
        for route in response.json():
            tree.insert('', 'end', values=(
                route['SourceIATA'], 
                route['DestinationIATA'], 
                route['Airline']
            ))
    else:
        messagebox.showinfo("Result", response.json()['message'])

# Apply the style
source_iata_entry = ttk.Entry(root, width=20, style='TEntry')
source_iata_entry.pack(side='left', padx=(10, 0))
destination_iata_entry = ttk.Entry(root, width=20, style='TEntry')
destination_iata_entry.pack(side='left', padx=(10, 0))

search_button = ttk.Button(root, text="Search Routes", command=search_routes, style='TButton')
search_button.pack(side='left', padx=(10, 10))

# Set up the Treeview
columns = ('source', 'destination', 'airline')
tree = ttk.Treeview(root, columns=columns, show='headings', style='Treeview')

# Define headings
for col in columns:
    tree.heading(col, text=col.capitalize(), anchor='w')  # Align the text to the west (left)

# Configure the columns
for col in columns:
    tree.column(col, width=120, anchor='w')  # Align the column content to the west (left)

tree.pack(side='left', fill='both', expand=True)

# Run the GUI
root.mainloop()
