import tkinter as tk
from tkinter import *
from tkinter import filedialog
import pandas as pd
import os
from helper import TRANSLATION, DEFAULT_CHECKS
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

TESTING = False
ROW = 23
PLOT_ROW = 3 
AB_FLOW_THRESH = 1 # gph
TURBINE_FUEL_CONSUMPTION_CONST = .187343 # gpm
TIME_INDEX = 0

# print(data.loc[: ,vars[0]])

root_csv_directory = os.path.join(os.getcwd(), "CSV")
hard_code_csv = os.path.join(root_csv_directory, "cutterhead_log_2021-10-05_14-25-07_-0500.csv")
check_keeper = {}
data = []
plot_keeper = {}

root = tk.Tk()
root.geometry('600x650')
root.resizable(True, True)
root.title('Cleanup and Visualization')

newWindow = 0
plot_canvas = FigureCanvasTkAgg()

def get_csv():
	return filedialog.askopenfilename(parent=root, initialdir=root_csv_directory, title='Please select a file.')

def make_dataframe(csv_name):
	return pd.read_csv(csv_name, engine='python', sep=';', quotechar='"', on_bad_lines='skip')

def increment_grid(r, c, lines):
	r += 1
	if r > lines:
			r = r % (lines+1)
			c += 1
	return r,c

def plot_increment(r, c, lines):
	c += 1
	if c > lines:
		c =c % (lines+1)
		r += 1
	return r,c

def export():
	global data
	global check_keeper
	for key in check_keeper.keys():
		if check_keeper[key].get() == 0:
			del data[key]

	data.to_csv(os.path.join(os.path.join(os.getcwd(), 'Output CSV'), 'new.csv'), sep=';', index=False)

	# Close the window
	root.destroy()

def openNewWindow():
	global newWindow	

	newWindow = Toplevel(root)
	newWindow.title("Visualize and Plot")
	newWindow.geometry('800x500')

def populateNewWindow():
	global newWindow
	r = 0
	c = 0

	global check_keeper
	global flow_data
	global plot_keeper
	for key in check_keeper.keys():
		if(check_keeper[key].get() > 0):
			# Check to see if we have a colloquial definition of the variable
			if key.lower() in TRANSLATION.keys():
				name = TRANSLATION[key.lower()]
			else:
				name = key
			plot_keeper[key] = IntVar()
			
			# Creat the check button for the included value
			tk.Checkbutton(newWindow,
					  	   text=name,
					  	   variable=plot_keeper[key]).grid(row=r, column=c, sticky='W')
			plot_keeper[key].set(0)

			# Increment grid index
			r, c = plot_increment(r, c, PLOT_ROW)

	# Make Plot Button
	Button(newWindow, text='Plot', command=plot_selected, font=('Arial', 14)).grid(row=r, column=c, sticky='W')
	r, c = plot_increment(r, c, PLOT_ROW)

	# Insert a placeholder for the future graph
	fig = Figure(figsize = (7, 3), dpi = 100)

	# adding the subplot
	plot1 = fig.add_subplot()

	# creating the Tkinter canvas
	# containing the Matplotlib figure
	plot_canvas = FigureCanvasTkAgg(fig, master=newWindow)  
	plot_canvas.draw()

	c, r = newWindow.grid_size()

	# placing the canvas on the Tkinter window
	plot_canvas.get_tk_widget().grid(row=r+1, columnspan=PLOT_ROW+1)

	# creating the Matplotlib toolbar
	toolbarFrame = Frame(master=newWindow)
	toolbarFrame.grid(row=r+2, columnspan=PLOT_ROW+1)
	toolbar = NavigationToolbar2Tk(plot_canvas, toolbarFrame)

def plot_selected():
	global newWindow
	global plot_keeper
	global data

	to_render = []

	for key in plot_keeper.keys():
		if plot_keeper[key].get() > 0:
			to_render.append(key)

	render_selected(to_render)

def render_selected(keys):
	global data
	global newWindow
	global plot_canvas

	fig = Figure(figsize = (7, 3), dpi = 100)

	# adding the subplot
	plot1 = fig.add_subplot()

	y = [[0]*len(keys)] * len(data.loc[:, keys[0]].tolist())
	for i in range(len(keys)):
		y[i] = data.loc[:, keys[i]].tolist()

	# plotting the graph
	# plot1.plot(y)
	for i in range(len(keys)):
		plot1.plot(y[i])

	plot1.legend(keys)

	# creating the Tkinter canvas
	# containing the Matplotlib figure
	plot_canvas = FigureCanvasTkAgg(fig, master=newWindow)  
	plot_canvas.draw()

	c,r = newWindow.grid_size()

	# placing the canvas on the Tkinter window
	plot_canvas.get_tk_widget().grid(row=r-2, columnspan=PLOT_ROW+1)

	# creating the Matplotlib toolbar
	toolbarFrame = Frame(master=newWindow)
	toolbarFrame.grid(row=r-1, columnspan=PLOT_ROW+1)
	toolbar = NavigationToolbar2Tk(plot_canvas, toolbarFrame)

def visualize():
	openNewWindow()
	populateNewWindow()

def create_window():
	# Storing all the variables from the .csv
	vars = []
	
	# Pull down the global variable that keeps track of which variabels are checked
	global check_keeper
	global data
	global TIME_INDEX

	# Extract all the column headers
	for col in data:
		vars.append(col)
		check_keeper[col] = IntVar()
	# Variables for setting up the checkbox grid
	r = 0
	c = 0
	
	# Label for the checkboxes
	Label(root, text="Raw variables from .csv", font=('Arial', 14)).grid(row=r, column=c, sticky='W')
	r, c = increment_grid(r, c, ROW)

	for i, var in enumerate(vars):
		# Check to see if this is the time data
		if "Elapsed Time" in vars:
			TIME_INDEX = i

		# Check to see if we have a colloquial definition of the variable
		if var.lower() in TRANSLATION.keys():
			name = TRANSLATION[var.lower()]
		else:
			name = var
		# Create the check button
		tk.Checkbutton(root,
					   text=name,
					   variable=check_keeper[var]).grid(row=r, column=c, sticky='W')
		check_keeper[var].set(0)

		# Check defaults for calculations
		for val in DEFAULT_CHECKS:
			check_keeper[vars[TIME_INDEX]].set(1)
			if val in vars:
				check_keeper[val].set(1)


		# Increment the row counter and check overfow
		r, c = increment_grid(r, c, ROW)

	# Create labels for calculated variables
	Label(root, text="Calculated Variables", font=('Arial', 14)).grid(row=r, column=c, sticky='W')
	r, c = increment_grid(r, c, ROW)

	# ----------AB total fuel consumption and length of run------------
	if 'ab_flow_meter' in vars:
		
		# Extract the relevant data for this calculation
		flow_data = data.loc[:, 'ab_flow_meter'].tolist()
		time_data = data.loc[:, vars[TIME_INDEX]].tolist()
		flow_data = [x for x in flow_data if x > AB_FLOW_THRESH]
		time_data = [time_data[i] for i,x in enumerate(flow_data) if x > AB_FLOW_THRESH]
		
		time_elapsed = abs(time_data[-1] - time_data[0])
		minutes = math.floor(time_elapsed / 60)
		seconds = int(time_elapsed % 60)

		# Create the label for time
		s = "Length of Run: " + str(minutes) + " Minutes and " + str(seconds) + " Seconds"
		Label(root, text=s, font=('Arial', 10)).grid(row=r, column=c, sticky='W')
		r, c = increment_grid(r, c, ROW)

		# Create label for AB Fuel Consumption
		average_flow = sum(flow_data) / len(flow_data)
		total_AB = average_flow * (time_elapsed / 3600)
		
		s = "Average AB Fuel Flow Rate: " + str(round(average_flow, 2)) + " gph"
		Label(root, text=s, font=('Arial', 10)).grid(row=r, column=c, sticky='W')
		r, c = increment_grid(r, c, ROW)

		s = "Total AB Fuel Consumption: " + str(round(total_AB, 2)) + " gallons"
		Label(root, text=s, font=('Arial', 10)).grid(row=r, column=c, sticky='W')
		r, c = increment_grid(r, c, ROW)

		# ----------Turbine total fuel consumption----------
		turbine_fuel_consump = (TURBINE_FUEL_CONSUMPTION_CONST) * (time_elapsed / 60)

		s = "Total Turbine Fuel Consumption: " + str(round(turbine_fuel_consump, 2)) + " gallons"
		Label(root, text=s, font=('Arial', 10)).grid(row=r, column=c, sticky='W')
		r, c = increment_grid(r, c, ROW)

		# ----------System total fuel consumption----------
		total_fuel_consump = turbine_fuel_consump + total_AB

		s = "Total Fuel Consumption: " + str(round(total_fuel_consump, 2)) + " gallons"
		Label(root, text=s, font=('Arial', 10)).grid(row=r, column=c, sticky='W')
		r, c = increment_grid(r, c, ROW)

	# ----------Water consumption----------
	# TODO: fill out this data once I have water data

	# Create visualize button
	Button(root, text='Visualize', command=visualize, font=('Arial', 14)).grid(row=r, column=c, sticky='W')
	r, c = increment_grid(r, c, ROW)

	# Create export button
	Button(root, text='Export as .csv', command=export, font=('Arial', 14)).grid(row=r, column=c, sticky='W')
	r, c = increment_grid(r, c, ROW)



def setup():
	global data
	if TESTING:
		data = make_dataframe(hard_code_csv)
	else:	
		csv_name = get_csv()
		data = make_dataframe(csv_name)
	create_window()
	root.mainloop()

	

if __name__ == '__main__':
	setup()


# TODO

# allow for custom naming of exported csv
# Allow for uploading and exporting multiple csvs
# Popup alert to notify of successful export after the button is clicked.

# Afterburner efficiency -- Input
# Turbine efficiency --> Input
# Volume bored --> Input

# Specific energy of test run