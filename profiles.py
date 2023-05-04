import pandas as pd
import numpy as np


def get_production_consumption(startdatetime='2017-01-01 00:00:00', enddatetime = '2017-12-31 23:45:00'):
    df = pd.read_csv('Productie en verbruik info Core.csv', delimiter=';')
    df.Datum = pd.to_datetime(df.Datum + ' ' + df.Tijd)
    df.rename(columns={'Datum':'timestamp'}, inplace=True)
    df.drop(['Tijd'], axis = 1, inplace = True)
    df.set_index('timestamp', inplace=True)

    return df.loc[startdatetime:enddatetime]


def get_availability_profiles(df): #types = [type1, type2]
    df_av = pd.read_csv('availability_profiles.csv', delimiter=';')
    for type in df_av.columns:
        df[type] = df_av[type].loc[str(df.index[0]):str(df.index[-1])]
    return df



def simulation(users, capaciteitspiek):

    df = get_production_consumption(enddatetime='2022-01-01 23:45:00')
    df = get_availability_profiles(df)
    for user in users:
        user['loadprof'] = df[f'availability_type{user.get("usertype")}']
        user['demandprof'] = None


    users = [

    {"user":[5,50],"loadprof":load1,"demandprof": [(0.4,1),(0.6,0.9)],"count":0,"soc":soc1},  #user = [maxrate,maxcapacity]
    {"user":[4,70],"loadprof":load2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"count":0,"soc":soc2}  #demandprof = (aantal laadbeurten, SOC beurt, SOC beurt,....)
    ]

    # dumb = get_dumb_profile(users,df)
    # smart = get_smart_profile(users,df)

    # Metrics berekenen, evt plots maken en die returnen
    return df
















# load1 = [0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0]
# load2 = [1,0,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,1,1]
# load1 = [val for val in load1 for _ in (0, 1, 2, 3)]
# load2 = [val for val in load2 for _ in (0, 1, 2, 3)]
# soc1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# soc2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
# soc1 = [val for val in soc1 for _ in (0, 1, 2, 3)]
# soc2 = [val for val in soc2 for _ in (0, 1, 2, 3)]

# assert len(load1*365) == len(df)

# usernames = []
# for user1 in range(nb_user1):
#     usernames.append(f'user1_{user1}')
#     df[f'availability_user1_{user1}'] = load1*365

# for user2 in range(nb_user2):
#     usernames.append(f'user1_{user1}')
#     df[f'availability_user1_{user2}'] = load2*365

# assert len(load1*365) == len(df)