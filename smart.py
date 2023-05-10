import cvxpy as cp

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def get_Tz(users):
    """Tz is a list of lists (a list per user) with the timezones in which each user is home and has the possibility to charge.
    A Timezone can be, for instance, (9th of march 10:30, 9th of march 12:45). They are tuples of integer indices."""
    Tz = []
    for user in users:
        availability = user.get('loadprof')
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
            elif availability[t] ==1 and t == (len(availability)-1):
                stop = t+1
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
        demand.append([round(user.get("demandprof")[z][1]-user.get("demandprof")[z][0],2) for z in range(len(user.get("demandprof")))])
    
    return demand



def get_smart_profiles(users, df, cap):
    """Optimization model. Returns optimal charging profiles s.t. the availabilities & the other constraints, aiming to maximize comfort."""  

    # Define problem variables
    T = len(df)
    Z = get_Z(users)
    Z_max = max(Z)
    C = len(users)
    Tz = get_Tz(users)
    demand_brak = get_demand(users)
    demand = np.zeros((C,Z_max))
    for c in range(C):
        for z in range(Z[c]):
            demand[c,z] = demand_brak[c][z]

    zcharge = cp.Variable((C,Z_max), nonneg=True)
    tcharge = cp.Variable((C,T), nonneg=True)

    # Define the objective function
    obj = cp.sum((demand - zcharge)**2)
    obj += cp.sum((cp.sum(tcharge, axis=0) + np.array(df['Gemeenschappelijk verbruik in kW']) - np.array(df['Productie in kW']))@np.array(df['energy_price']))

    # Define constraints
    constraints = []
    for t in range(T):
        constraints += [cp.sum(tcharge[:,t]) + df['Gemeenschappelijk verbruik in kW'].values[t] - df['Productie in kW'].values[t] <= cap]
        for c in range(C):
            constraints += [tcharge[c,t] <= 22/4]

    for c in range(C):
        for z in range(Z[c]):
            constraints += [zcharge[c,z] == cp.sum(tcharge[c, Tz[c][z][0]:Tz[c][z][1]])]
            constraints += [zcharge[c,z] <= demand[c,z]]

    # Define the problem instance and solve
    problem = cp.Problem(cp.Minimize(obj), constraints)
    status = problem.solve()

    # Check the status and print the solution
    assert problem.status == "optimal"


    for c in range(C):
        users[c]['smart_profile'] = [0]*T
        for t in range(T):
            users[c]['smart_profile'][t] = round(tcharge.value[c,t],2)

    return users