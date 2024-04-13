import tkinter as tk
import requests
from tkinter import messagebox

def search_routes():
    source_iata = source_iata_entry.get()
    destination_iata = destination_iata_entry.get()
    response = requests.get(f'http://127.0.0.1:5000/routes?source_iata={source_iata}&destination_iata={destination_iata}')
    
    if response.status_code == 200:
        routes = response.json()
        result_text.set(str(routes))
    else:
        messagebox.showinfo("Result", response.json()['message'])

root = tk.Tk()
root.title("Flight Route Finder")

source_iata_entry = tk.Entry(root)
source_iata_entry.pack()
destination_iata_entry = tk.Entry(root)
destination_iata_entry.pack()

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text)
result_label.pack()

search_button = tk.Button(root, text="Search Routes", command=search_routes)
search_button.pack()

root.mainloop()
