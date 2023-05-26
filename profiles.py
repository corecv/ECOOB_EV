import pandas as pd
import numpy as np
import os
from smart import get_smart_profiles, get_Tz
from dumb import get_dumb_profiles
from random import choice
from time import time


def get_production_consumption(enddatetime = '2017-12-31 23:00:00'):
    startdatetime='2017-01-01 00:00:00'
    df = pd.read_csv(os.path.join('data','Productie en verbruik info Core.csv'), delimiter=';')
    df.Datum = pd.to_datetime(df.Datum + ' ' + df.Tijd)
    df.rename(columns={'Datum':'timestamp'}, inplace=True)
    df.drop(['Tijd'], axis = 1, inplace = True)
    df.set_index('timestamp', inplace=True)
    df = df.asfreq('15T')
    df.interpolate(inplace=True)

    return df.loc[startdatetime:enddatetime]


def get_availability_profiles(df):

    df_av = pd.read_excel(os.path.join('data','Laadprofielen.xlsx'), sheet_name='3. State of Charge', header=None)
    # Select rows 4 and onwards and columns D through AS
    df_av = df_av.iloc[3:, 3:45]
    # Reset column names
    df_av.columns = df_av.iloc[0]
    df_av = df_av[1:]

    for column in df_av.columns:
        col_year = list(df_av[column])*52 + list(df_av[column])[:96]
        df[column] = col_year[:len(df)]

    return df


def get_prices(df, dynamic_prices, capaciteitspiek, nb_users):
    df_prices = pd.read_csv(os.path.join('data','BelpexFilter.csv'), delimiter=';')
    df_prices.rename(columns={'Date':'timestamps'}, inplace=True)
    df_prices.timestamps = pd.to_datetime(df_prices.timestamps)
    df_prices.sort_values('timestamps', inplace=True)
    df_prices.set_index('timestamps', inplace=True)
    df_prices = df_prices.asfreq('H')
    df_prices = df_prices.resample('15T').interpolate()    
    df_prices.energy_price = (df_prices.energy_price*1e-3 + 0.204*1e-3)*4.3 + 40.4*capaciteitspiek/(365*96*nb_users) 
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
    charge_rate = general.get('chargerate')
    print('### verbruik en productieprofiel ophalen')
    df = get_production_consumption()
    df['Productie in kW'] = df['Productie in kW']*PV_schaal
    print('### beschikbaarheidsprofielen ophalen')

    df = get_availability_profiles(df)
    print('### prijzen ophalen')

    df = get_prices(df,dynamic_prices, capaciteitspiek, len(users))
    shoppingstations = []
    for user in users:
        user['rand_profile'] = str(user.get("usertype"))+ 'C' #choice(['A','B','C'])
        user['loadprof'] = df[user.get('rand_profile')]
        user['demandprof'] = get_demandprof(user, df)
        if user.get('usertype') == 7:
            shoppingstations.append(user)

    for ss in shoppingstations:
        loadprofcopy = list(df[ss.get('rand_profile')+' SOC [kWh]'])
        for t in range(len(loadprofcopy)-1):
            if np.isnan(loadprofcopy[t]):
                loadprofcopy[t] = 0
            elif np.isnan(loadprofcopy[t+1]):
                loadprofcopy[t] = 0
            else:
                loadprofcopy[t] = loadprofcopy[t+1]-loadprofcopy[t]
 
        loadprofcopy[-1] = 0

        ss['chargeprof'] = loadprofcopy


    consumptie = np.array(df['Gemeenschappelijk verbruik in kW'])
    productie = np.array(df['Productie in kW'])      
    for t in range(len(df)):
        if capaciteitspiek > consumptie[t] - productie[t] + sum([ss.get('chargeprof')[t] for ss in shoppingstations]):
            consumptie[t] += sum([ss.get('chargeprof')[t] for ss in shoppingstations])
        else:
            diff = consumptie[t] - productie[t] + sum([ss.get('chargeprof')[t] for ss in shoppingstations]) - capaciteitspiek
            diff_per_ss = diff/len(shoppingstations)
            for ss in shoppingstations:
                ss['chargeprof'][t] = max(ss['chargeprof'][t]-diff_per_ss,0)
            consumptie[t] = capaciteitspiek + productie[t]
    for ss in shoppingstations:
        ss['dumb_profile'] = ss.get('chargeprof')
        ss['smart_profile'] = ss.get('chargeprof')
    df['Gemeenschappelijk verbruik in kW'] = consumptie
    df['Productie in kW'] = productie

    users = [user for user in users if user.get('usertype') !=7]
    print("#### calculating dumb profile ###")
    users = get_dumb_profiles(users,df, capaciteitspiek,chargeR=charge_rate)
    print("#### calculating smart profile ###")

    users = get_smart_profiles(users,df, capaciteitspiek,chargeR=charge_rate)

    users = users + shoppingstations


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

        #dumb
        consumption = df['Gemeenschappelijk verbruik in kW'].iloc[t] + sum([user['dumb_profile'][t] for user in users])
        if production <= consumption:
            self_consumption_dumb += production
        else:
            self_consumption_dumb += consumption
            excess_energy_dumb += (production-consumption)

    
    general['self_consumption_dumb'] = round((self_consumption_dumb/sum(df['Productie in kW'].iloc))*100,3)
    general['excess_energy_dumb'] = round(excess_energy_dumb/4,3)
    general['self_consumption_smart'] = round((self_consumption_smart/sum(df['Productie in kW'].iloc))*100,3)
    general['excess_energy_smart'] = round(excess_energy_smart/4,3)
    
    total_d = list([])
    total_s= list([])
    for t in range(len(df['Gemeenschappelijk verbruik in kW'])):
        total_d.append(df['Gemeenschappelijk verbruik in kW'].iloc[t])
        total_s.append(df['Gemeenschappelijk verbruik in kW'].iloc[t])
        total_d[t] -= df['Productie in kW'].iloc[t] #+ sum([u['dumb_profile'][t] for u in users])
        total_s[t] -= df['Productie in kW'].iloc[t] #+ sum([u['smart_profile'][t] for u in users])
        for u in users:
            total_d[t] += u['dumb_profile'][t]
            total_s[t] += u['smart_profile'][t]
    general['consumption dumb'] = total_d
    general['consumption smart'] = total_s
    general['total consumption dumb'] = sum(total_d)/4
    general['total consumption smart'] = sum(total_s)/4



    # ### Charging Cost
    total_d = 0
    total_s = 0
    for user in users:
        chargingcostarray = np.array(user['smart_profile'])*np.array(df.energy_price)
        chargingcostarray[chargingcostarray == 0] = np.nan
        user["energy cost smart"] = round(np.nansum(chargingcostarray),2)
        chargingcostarray = np.array(user['dumb_profile'])*np.array(df.energy_price)
        chargingcostarray[chargingcostarray == 0] = np.nan        
        user["energy cost dumb"] = round(np.nansum(chargingcostarray),2)
        user["energy cost svd"] = user.get('energy cost dumb')/user.get('energy cost smart')
        user['energy cost savings'] = user.get('energy cost dumb') - user.get('energy cost smart')
        total_d += user['energy cost dumb']
        total_s += user['energy cost smart']
    general['total energy cost dumb'] = round(total_d)
    general['total energy cost smart'] = round(total_s)



    ### Charging Comfort
    
    for user in users:
        comfortdumb = []
        comfortsmart = []
        totcharge = 0
        dem = user.get('demandprof')
        smart = sum(user.get('smart_profile'))
        dumb = sum(user.get('dumb_profile'))
        for i in range(len(dem)):
            totcharge += dem[i][1] - dem[i][0]
        comfortdumb.append(dumb/totcharge)
        comfortsmart.append(smart/totcharge)
        avg_d = round((sum(comfortdumb)/len(comfortdumb))*100,3)
        avg_s = round((sum(comfortsmart)/len(comfortsmart))*100,3)
        user['dumb_comfort'] = avg_d
        user['smart_comfort'] = avg_s
    # for user in users:
    #         comfortdumb = []
    #         comfortsmart = []
    #         startstop = user.get('Tz')
    #         dem = user.get('demandprof')
    #         smart = user.get('smart_profile')
    #         dumb = user.get('dumb_profile')

    #         for t in range(len(startstop)):
    #             charged_d= sum(dumb[startstop[t][0]:startstop[t][1]])
    #             charged_s = sum(smart[startstop[t][0]:startstop[t][1]])
    #             comfortdumb.append((dem[t][0] + charged_d)/dem[t][1])
    #             comfortsmart.append((dem[t][0] + charged_s)/dem[t][1])
            
    #         avg_d = sum(comfortdumb)/len(comfortdumb)
    #         avg_s = sum(comfortsmart)/len(comfortsmart)
    #         user['dumb_comfort'] = round(avg_d,5)
    #         user['smart_comfort'] = round(avg_s,5)


    return (df ,general,users)
