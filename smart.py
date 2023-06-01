import cvxpy as cp
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable, CPLEX_CMD
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def get_Tz(user_list):
    """Tz is a list of lists (a list per user) with the timezones in which each user is home and has the possibility to charge.
    A Timezone can be, for instance, (9th of march 10:30, 9th of march 12:45). They are tuples of integer indices."""
    Tz = []
    for user in user_list:
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

def get_Z(user_list):
    """Returns a list of number of times the car is at the chargingstation within simulation period (T) per user."""
    Z = []
    for user in user_list:
        Z.append(len(user.get("demandprof")))

    return Z


def get_demand(user_list):
    """Returns a list of demandprofiles per user. The demand profile of a user contains the amount the user wants to charge per timezone Z"""
    demand = []
    for user in user_list:
        demand.append([round(user.get("demandprof")[z][1]-user.get("demandprof")[z][0],2) for z in range(len(user.get("demandprof")))])
    
    return demand



def get_smart_profiles(user_list, df, cap,chargeR,sim):
    """Optimization model. Returns optimal charging profiles s.t. the availabilities & the other constraints, aiming to maximize comfort."""  
    if sim ==2: print(' ### defining problem variables')

    # Define problem variables
    T = len(df)
    Z = get_Z(user_list)
    Z_max = max(Z)
    C = len(user_list)
    Tz = get_Tz(user_list)
    demand_brak = get_demand(user_list)
    demand = np.zeros((C,Z_max))
    for c in range(C):
        for z in range(Z[c]):
            demand[c,z] = demand_brak[c][z]
    df = df.dropna(axis=1)


    if sim ==2: print(' ### generating model')

    model = LpProblem(name='laadpaalstudie', sense=LpMinimize)


    zcharge = LpVariable.dicts('zcharge', [(c,z) for c in range(C) for z in range(Z[c])], lowBound=0)
    tcharge = LpVariable.dicts('tcharge', [(c,t) for c in range(C) for t in range(T)], lowBound=0, upBound=chargeR)
    
    if sim ==2: print(' ### generating objective functions')
    obj = lpSum([(demand[c,z] - zcharge[(c,z)])*(user_list[c].get('priority')/2 +1) for c in range(C) for z in range(Z[c])]) #*(user_list[c].get('priority')/2 +1)
    obj += lpSum((lpSum(tcharge[(c,t)] for c in range(C)) + df['Gemeenschappelijk verbruik in kW'].iloc[t] - df['Productie in kW'].iloc[t])*df['energy_price'].iloc[t] for t in range(T))
    model += obj


    for t in range(T):
        model += (lpSum(tcharge[(c,t)] for c in range(C)) + df['Gemeenschappelijk verbruik in kW'].iloc[t] - df['Productie in kW'].iloc[t] <= cap)    
        for c in range(C):
            model += (tcharge[(c,t)] == tcharge[(c,t)]*user_list[c].get('loadprof')[t])
    for c in range(C):
        for z in range(Z[c]):
            model += (zcharge[(c,z)] == lpSum([tcharge[(c,t)] for t in range(Tz[c][z][0],Tz[c][z][1])]))

            model += (zcharge[(c,z)] <= demand[c,z])
            

    if sim ==2: print(' ### solving the problem')

    # Solve the problem
    status = model.solve()

    if sim ==2: print(f"status: {model.status}, {LpStatus[model.status]}")


    tcharge_arr = np.zeros((C,T))
    for c in range(C):
        for t in range(T):
            tcharge_arr[(c,t)] = tcharge[(c,t)].value()

    if sim ==2: print(' ### inserting smart profile in user_list')


    for c in range(C):
        user_list[c]['smart_profile'] = [0]*T
        for t in range(T):
            user_list[c]['smart_profile'][t] = tcharge[(c,t)].value()  

    return user_list