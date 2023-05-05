import pandas as pd
import numpy as np
from smart import get_smart_profiles, get_Tz
from dumb import get_dumb_profiles


def get_production_consumption(startdatetime='2017-01-01 00:00:00', enddatetime = '2017-12-31 23:45:00'):
    df = pd.read_csv('Productie en verbruik info Core.csv', delimiter=';')
    df.Datum = pd.to_datetime(df.Datum + ' ' + df.Tijd)
    df.rename(columns={'Datum':'timestamp'}, inplace=True)
    df.drop(['Tijd'], axis = 1, inplace = True)
    df.set_index('timestamp', inplace=True)

    return df.loc[startdatetime:enddatetime]


def get_availability_profiles(df): #types = [type1, type2]
    df_av = pd.read_csv('availability_profiles.csv', delimiter=',')
    for type in df_av.columns:
        df[type] = df_av[type].loc[str(df.index[0]):str(df.index[-1])]

    return df


def get_demandprof(user, df):
    """..."""
    demand = []
    Tz = get_Tz([user])
    for tz in Tz:
        demand.append((df[f'availability_type{user.get("usertype")}'].iloc[tz[0]], df[f'availability_type{user.get("usertype")}'].iloc[tz[1]]))
    return


def simulation(users, capaciteitspiek):

    df = get_production_consumption(enddatetime='2022-01-01 23:45:00')
    df = get_availability_profiles(df)
    for user in users:
        user['loadprof'] = df[f'availability_type{user.get("usertype")}']
        user['demandprof'] = get_demandprof(user, df)


    # users = [

    # {"user":[5,50],"loadprof":load1,"demandprof": [(0.4,1),(0.6,0.9)],"count":0,"soc":soc1},  #user = [maxrate,maxcapacity]
    # {"user":[4,70],"loadprof":load2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"count":0,"soc":soc2}  #demandprof = (aantal laadbeurten, SOC beurt, SOC beurt,....)
    # ]

    df_dumb = get_dumb_profiles(users,df, capaciteitspiek)
    df_smart = get_smart_profiles(users,df, capaciteitspiek)


    #########################
    ### Metrics berekenen ###
    #########################

    ### SelfConsumption & excess energy

    self_consumption_smart = 0
    excess_energy_smart = 0
    self_consumption_dumb = 0
    excess_energy_dumb = 0

    for t in len(df):
        ##smart
        production = df['Productie in kW'].iloc[t]
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([df_smart[user.get('username')].iloc[t] for user in users])
        if production <= consumption:
            self_consumption_smart += production
        else:
            self_consumption_smart += consumption
            excess_energy_smart += production-consumption

        ##dumb
        production = df['Productie in kW'].iloc[t]
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([df_dumb[user.get('username')].iloc[t] for user in users])
        if production <= consumption:
            self_consumption_dumb += production
        else:
            self_consumption_dumb += consumption
            excess_energy_dumb += production-consumption

    self_consumption_smart = self_consumption_smart/sum(df['Productie in kW'])
    self_consumption_dumb = self_consumption_dumb/sum(df['Productie in kW'])


    ### Charging Cost
    for user in users:
        chargingcostarray = np.array(df_smart[user.get('username')])*np.array(df['energy_price'])
        chargingcostarray[chargingcostarray == 0] = np.nan
        user["energy cost per kWh smart"] = np.nanmean(chargingcostarray)
        chargingcostarray = np.array(df_dumb[user.get('username')])*np.array(df['energy_price'])
        chargingcostarray[chargingcostarray == 0] = np.nan        
        user["energy cost per kWh dumb"] = np.nanmean(chargingcostarray)


    ### Charging Comfort
    for user in users:
        user['comfort'] = np.mean([user['charged_Z'][z]/user['demand'][z] for z in range(len(user['demand']))])


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


#user = [maxrate,maxcapacity]
#demandprof = ( SOC begin, SOC waarmee we willen eindigen)
#count is een variabele om bij te houden bij welke laadbeurt we zitten, dit getal selecteerd de juiste tuple uit demandprof
#passfail, een lijst om bij te houden hoeveel procent er geladen is in die beurt afhankelijk van de overeenkomstige demandprof, als dit =1 dan is alles wat gevraagd is geladen kunnen worden. 
# users = [

# {"user":[5,70],"loadprof":load1,"soc":soc1,"demandprof": [(0.4,1),(0.6,0.9)],"passfail":[],"count":0},  
# {"user":[4,60],"loadprof":load2,"soc":soc2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"passfail":[],"count":0},
# {"user":[6,60],"loadprof":load2,"soc":soc2,"demandprof": [(0.3,1),(0.1,0.9),(0.4,1),(0.4,1),(0.8,1)],"passfail":[],"count":0},
# {"user":[4,70],"loadprof":load1,"soc":soc2,"demandprof": [(0.5,1),(0.1,1)],"passfail":[],"count":0}  


# ]


