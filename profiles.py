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


def get_availability_profiles(df):

    df_av = pd.read_excel('Laadprofielen.xlsx', sheet_name='State of Charge', header=None)
    # Select rows 4 and onwards and columns D through AA
    df_av = df_av.iloc[3:, 3:26]
    # Reset column names
    df_av.columns = df_av.iloc[0]
    df_av = df_av[1:]

    ### Make it work

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

    for t in len(df):
        ##smart
        production = df['Productie in kW'].iloc[t]
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([user['smart_profile'][t] for user in users])
        if production <= consumption:
            self_consumption_smart += production
        else:
            self_consumption_smart += consumption
            excess_energy_smart += production-consumption

        ##dumb
        production = df['Productie in kW'].iloc[t]
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([user['dumb_profile'][t] for user in users])
        if production <= consumption:
            self_consumption_dumb += production
        else:
            self_consumption_dumb += consumption
            excess_energy_dumb += production-consumption

    self_consumption_smart = self_consumption_smart/sum(df['Productie in kW'])
    self_consumption_dumb = self_consumption_dumb/sum(df['Productie in kW'])


    ### Charging Cost
    for user in users:
        chargingcostarray = np.array(user['smart_profile'][t])*np.array(df['energy_price'])
        chargingcostarray[chargingcostarray == 0] = np.nan
        user["energy cost per kWh smart"] = np.nanmean(chargingcostarray)
        chargingcostarray = np.array(user['dumb_profile'][t])*np.array(df['energy_price'])
        chargingcostarray[chargingcostarray == 0] = np.nan        
        user["energy cost per kWh dumb"] = np.nanmean(chargingcostarray)


    ### Charging Comfort

    # def comfort(userlist):
        
    for user in users:
            comfortdumb = []
            comfortsmart = []
            startstop = user.get('startstop')
            dem = user.get('demandprof')
            smart = user.get('smart_profile')
            dumb = user.get('dumb_profile')

            for t in range(len(startstop)):
                charged_d= sum(dumb[startstop[0]:startstop[1]])
                charged_s = sum(smart[startstop[0]:startstop[1]])
                comfortdumb.append((dem[0] + charged_d)/dem[startstop[t][1]])
                comfortsmart.append((dem[0] + charged_s)/dem[startstop[t][1]])
            
            avg_d = sum(comfortdumb)/len(comfortdumb)
            avg_s = sum(comfortsmart)/len(comfortsmart)
            user['dumb_comfort'] = avg_d
            user['smart_comfort'] = avg_s

    return df


















