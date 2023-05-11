import pandas as pd
import numpy as np
from smart import get_smart_profiles, get_Tz
from dumb import get_dumb_profiles
from random import choice


def get_production_consumption(enddatetime = '2017-12-31 23:45:00'):
    startdatetime='2017-01-01 00:00:00'
    df = pd.read_csv('Productie en verbruik info Core.csv', delimiter=';')
    df.Datum = pd.to_datetime(df.Datum + ' ' + df.Tijd)
    df.rename(columns={'Datum':'timestamp'}, inplace=True)
    df.drop(['Tijd'], axis = 1, inplace = True)
    df.set_index('timestamp', inplace=True)

    return df.loc[startdatetime:enddatetime]


def get_availability_profiles(df):

    df_av = pd.read_excel('Laadprofielen.xlsx', sheet_name='State of Charge', header=None)
    # Select rows 4 and onwards and columns D through AA
    df_av = df_av.iloc[3:, 3:45]
    # Reset column names
    df_av.columns = df_av.iloc[0]
    df_av = df_av[1:]

    for column in df_av.columns:
        col_year = list(df_av[column])*52 + list(df_av[column])[:96]
        df[column] = col_year[:len(df)]

    return df


def get_prices(df, dynamic_prices):
    df_prices = pd.read_csv('BelpexFilter.csv', delimiter=';')
    df_prices.rename(columns={'Date':'timestamp'}, inplace=True)
    df_prices.timestamp = pd.to_datetime(df_prices.timestamp)
    df_prices.sort_values('timestamp', inplace=True)
    df_prices.set_index('timestamp', inplace=True)
    df_prices = df_prices.asfreq('H')
    df_prices = df_prices.resample('15T').interpolate()    
    df_prices.energy_price = df_prices.energy_price*1e-3 + 0.204*1e-3 #€/kWh
    df = pd.concat([df, df_prices.loc[df.index[0]:df.index[-1]]], axis=1)
    if dynamic_prices == False:
        df.energy_price = np.mean(df_prices.energy_price)
        print("#############################################################################",'\n',df.energy_price)

    return df


def get_demandprof(user, df):
    """..."""
    demand = []
    Tz = get_Tz([user])[0]
    user['Tz'] = Tz
    for tz in Tz:
        demand.append((df[user.get('rand_profile')+' SOC [kWh]'].iloc[tz[0]], df[user.get('rand_profile')+' SOC [kWh]'].iloc[tz[1]-1]))
    return demand


def simulation(users,general):

    dynamic_prices = general.get('dynamic prices')
    capaciteitspiek = general.get('caplimit')
    PV_schaal = general.get('PVschaling')

    df = get_production_consumption(enddatetime='2017-01-01 23:45:00')
    df['Productie in kW'] = df['Productie in kW']*PV_schaal
    df = get_availability_profiles(df)
    df = get_prices(df,dynamic_prices)
    for user in users:
        user['rand_profile'] = str(user.get("usertype"))+ choice(['A','B','C'])
        user['loadprof'] = df[user.get('rand_profile')]
        user['demandprof'] = get_demandprof(user, df)

 

    users = get_dumb_profiles(users,df, capaciteitspiek)
    users = get_smart_profiles(users,df, capaciteitspiek)


    #########################
    ### Metrics berekenen ###
    #########################

    ### SelfConsumption & excess energy

    self_consumption_smart = 0
    excess_energy_smart = 0
    self_consumption_dumb = 0
    excess_energy_dumb = 0

    for t in range(len(df)):
        #smart
        production = df['Productie in kW'].iloc[t]
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([user['smart_profile'][t] for user in users])
        if production <= consumption:
            self_consumption_smart += production
        else:
            self_consumption_smart += consumption
            excess_energy_smart += production-consumption

        ##dumb
        production = df['Productie in kW'].iloc[t]
        # print(len(df), len(users[0]['smart_profile']), len(users[0]['dumb_profile']))
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([user['dumb_profile'][t] for user in users])
        if production <= consumption:
            self_consumption_dumb += production
        else:
            self_consumption_dumb += consumption
            excess_energy_dumb += production-consumption

    general['self_consumption_smart'] = self_consumption_smart/sum(df['Productie in kW'])
    general['self_consumption_dumb'] = self_consumption_dumb/sum(df['Productie in kW'])
    general['excess_energy_dumb'] = excess_energy_dumb
    general['excess_energy_smart'] = excess_energy_smart

    # ### Charging Cost
    for user in users:
        chargingcostarray = np.array(user['smart_profile'])*np.array(df.energy_price)
        chargingcostarray[chargingcostarray == 0] = np.nan
        user["energy cost smart"] = round(np.nanmean(chargingcostarray),2)
        chargingcostarray = np.array(user['dumb_profile'])*np.array(df.energy_price)
        chargingcostarray[chargingcostarray == 0] = np.nan        
        user["energy cost dumb"] = round(np.nansum(chargingcostarray),2)
        user["energy cost svd"] = user.get('energy cost dumb')/user.get('energy cost smart')
        user['energy cost savings'] = user.get('energy cost dumb') - user.get('energy cost smart')


    ### Charging Comfort
        
    for user in users:
            comfortdumb = []
            comfortsmart = []
            startstop = user.get('Tz')
            dem = user.get('demandprof')
            smart = user.get('smart_profile')
            dumb = user.get('dumb_profile')

            for t in range(len(startstop)):
                charged_d= sum(dumb[startstop[t][0]:startstop[t][1]])
                charged_s = sum(smart[startstop[t][0]:startstop[t][1]])
                comfortdumb.append((dem[t][0] + charged_d)/dem[t][1])
                comfortsmart.append((dem[t][0] + charged_s)/dem[t][1])
            
            avg_d = sum(comfortdumb)/len(comfortdumb)
            avg_s = sum(comfortsmart)/len(comfortsmart)
            user['dumb_comfort'] = round(avg_d,2)
            user['smart_comfort'] = round(avg_s,2)


    return (df ,general)
