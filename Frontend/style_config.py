import tkinter as tk
from tkinter import ttk

def configure_styles():
    style = ttk.Style()
    style.theme_use('clam')

    # Configure style of Heading Labels
    style.configure('HeadingLabel', font=('Arial', 16), background='blue', foreground='white')

    # Treeview style
    style.configure("Treeview",
                    background="#E8E8E8",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="#D3D3D3")
    style.map('Treeview', background=[('selected', '#E8E8E8')])

    # Treeview Heading style
    style.configure("Treeview.Heading",
                    font=('Calibri', 13, 'bold'),
                    foreground='blue')

    # Increase the combobox font size
    style.configure('TCombobox', font=('Arial', 12))

    # Button style
    style.configure('TButton', font=('Arial', 12), background='blue', foreground='white')

    # Entry style
    style.configure('TEntry', font=('Arial', 12))
    