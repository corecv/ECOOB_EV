###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *

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