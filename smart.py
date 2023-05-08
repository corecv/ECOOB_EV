from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def get_Tz(users):
    """Tz is a list of lists (a list per user) with the timezones in which each user is home and has the possibility to charge.
    A Timezone can be, for instance, (9th of march 10:30, 9th of march 12:45). They are tuples of integer indices."""
    Tz = []
    for user in users:
        availability = user.get('availability_profile')
        status = 0
        start = 0
        stop = 0
        Tz_user = []
        for t in range(len(availability)):
            if availability[t] == 1 and status==0:
                start = t
                status = 1
            elif availability[t] == 0 and status==1: #in deze t laadt hij niet meer, maar in de vorige wel nog -> stop = t
                stop = t
                status = 0
                Tz_user.append((start,stop))

        Tz.append(Tz_user)

    return Tz

def get_Z(users):
    """Returns a list of number of times the car is at the chargingstation within simulation period (T) per user."""
    Z = []
    for user in users:
        Z.append(len(user.get("demandprof")))

    return Z


def get_demand(users):
    """Returns a list of demandprofiles per user. The demand profile of a user contains the amount the user wants to charge per timezone Z"""
    demand = []
    for user in users:
        demand.append(user.get("demandprof"))
    
    return demand



def get_smart_profiles(users, df, cap):
    """Optimization model. Returns optimal charging profiles s.t. the availabilities & the other constraints, aiming to maximize comfort."""  
    model = LpProblem(name='laadpaalstudie', sense=LpMinimize)
    T = len(df)
    Z = get_Z(users)
    C = len(users) #total number of users = total number of charging stations
    Tz = get_Tz(users)
    demand = get_demand(users)
    # demand = [[3000*4,5000*4],[1000*4,2000*4,6000*4]] #in Watt-kwartier
    max_charge_rate = 22

    zcharge = LpVariable.dicts('zcharge', [(c,z) for c in range(C) for z in range(Z[c])], lowBound=0, upBound= max_charge_rate)#[max_charge_rates[c] for c in range(C)])
    tcharge = LpVariable.dicts('tcharge', [(c,t) for c in range(C) for t in range(T)], lowBound=0, upBound=max_charge_rate)#[max_charge_rates[c] for c in range(C)])

    obj = lpSum([(demand[c][z] - zcharge[(c,z)]) for c in range(C) for z in range(Z[c])])
    model += obj


    for t in range(T):
        model += (lpSum(tcharge[(c,t)] for c in range(C)) + np.array(df['Gemeenschappelijk verbruik in kW'].iloc[t]) - np.array(df['Productie in kW'].iloc[t]) <= cap)
        
    for c in range(C):
        for z in range(Z[c]):
            model += (zcharge[(c,z)] == lpSum([tcharge[(c,t)] for t in range(Tz[c][z][0],Tz[c][z][1])]))

            model += (zcharge[(c,z)] <= demand[c][z])



    # Solve the problem
    status = model.solve(use_mps=False)
    assert model.status == 1

    # print(f"status: {model.status}, {LpStatus[model.status]}")


    # print(f"objective: {model.objective.value()}")


    # for var in model.variables():
    #     print(f"{var.name}: {var.value()}")

    # for c in range(C):
    #     Z_user = []
    #     for z in range (Z[c]):
    #         Z_user.append(zcharge[(c,z)].value())
    #     users[c]['charged_Z'] = Z_user

    for c in range(C):
        users[c]['smart_profile'] = [0]*T
        for t in range(T):
            users[c]['smart_profile'][t] = tcharge[(c,t)].value()

    return users