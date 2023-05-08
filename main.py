###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *

#HTML inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek
nb_users_type1_bat50 = 0
nb_users_type1_bat70 = 1
nb_users_type2_bat50 = 1
nb_users_type2_bat70 = 0

capaciteitspiek = 25
# output van HTML:

usernames = [{'type':1, 'bat':50, 'nb':nb_users_type1_bat50},
             {'type':1, 'bat':70, 'nb':nb_users_type1_bat70},
             {'type':2, 'bat':50, 'nb':nb_users_type2_bat50},
             {'type':2, 'bat':70, 'nb':nb_users_type2_bat70},
             ]
users = []
for username in usernames:
    for nb in range(username.get('nb')):
        users.append({"username":'type'+str(username.get('type'))+'_bat'+str(username.get('bat'))+'nr'+str(username.get('nb')),"usertype":username.get('type'), "user":[2.75,username.get('bat')]})


# users = [
# {"user":[5,50],"loadprof":load1,"demandprof": [(0.4,1),(0.6,0.9)],"count":0,"soc":soc1},  #user = [maxrate,maxcapacity]
# {"user":[4,70],"loadprof":load2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"count":0,"soc":soc2}  #demandprof = (aantal laadbeurten, SOC beurt, SOC beurt,....)
# ]


#################
### Simulatie ###
#################
df = simulation(users, capaciteitspiek)
#dynamische tarieven vs laadcomfort: waarde meegeven
print(users)




#########################
### Output Parameters ###
#########################

#Zelfconsumptie PV-installatie
#Kostprijs vd elektriciteit per type
#Impact op comfort (% niet kunnen laden)
#Overschot energie