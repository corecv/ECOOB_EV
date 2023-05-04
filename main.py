###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *

import tkinter as tk
from tkinter import ttk

def button_clicked():
    try:
        num_charging_stations = int(charge_station_entry.get())
        if num_charging_stations < 0:
            raise ValueError
        print(f"User profile: {user_profile_var.get()}")
        print(f"Car type: {car_type_var.get()}")
        print(f"Number of charging stations: {num_charging_stations}")
    except ValueError:
        tk.messagebox.showerror("Invalid Input", "Please enter a positive integer for the number of charging stations.")

root = tk.Tk()
root.geometry("300x200")

user_profile_label = ttk.Label(root, text="User profile:")
user_profile_label.pack()
user_profile_var = tk.StringVar()
user_profile_dropdown = ttk.Combobox(root, textvariable=user_profile_var)
user_profile_dropdown['values'] = ('Type 1', 'Type 2', 'Type 3', 'Type 4', 'Type 5')
user_profile_dropdown.pack()

car_type_label = ttk.Label(root, text="Car type:")
car_type_label.pack()
car_type_var = tk.StringVar()
car_type_dropdown = ttk.Combobox(root, textvariable=car_type_var)
car_type_dropdown['values'] = ('Sports car', 'Family car', 'Electric car', 'SUV', 'Truck')
car_type_dropdown.pack()

charge_station_label = ttk.Label(root, text="Number of charging stations with this user profile & car type:")
charge_station_label.pack()
charge_station_entry = ttk.Entry(root)
charge_station_entry.pack()

button = ttk.Button(root, text="Add to simulation", command=button_clicked)
button.pack()

root.mainloop()

#HTML inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek

# output van HTML:
users = [ 
    {"usertype":1, "bat_specs":[5,50]},
    {"usertype":2, "bat_specs":[4,70]}
    ]
capaciteitspiek = 20

# users = [
# {"user":[5,50],"loadprof":load1,"demandprof": [(0.4,1),(0.6,0.9)],"count":0,"soc":soc1},  #user = [maxrate,maxcapacity]
# {"user":[4,70],"loadprof":load2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"count":0,"soc":soc2}  #demandprof = (aantal laadbeurten, SOC beurt, SOC beurt,....)
# ]


#################
### Simulatie ###
#################
df = simulation(users, capaciteitspiek)
#dynamische tarieven vs laadcomfort: waarde meegeven





#########################
### Output Parameters ###
#########################

#Zelfconsumptie PV-installatie
#Kostprijs vd elektriciteit per type
#Impact op comfort (% niet kunnen laden)
#Overschot energie