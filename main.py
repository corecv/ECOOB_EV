###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *

#HTML inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek
nb_users_type1 = 10
nb_users_type2 = 0
nb_users_type3 = 1
nb_users_type4 = 0
nb_users_type5 = 1
nb_users_type6 = 0
nb_users_type7 = 1

capaciteitspiek = 22
dynamic_prices = False
PV_schaal = 1

###########################
# HIERONDER NIETS MEER AANPASSEN!
###########################
# output van HTML:

usernames = [{'type':1, 'nb':nb_users_type1},
             {'type':2, 'nb':nb_users_type2},
             {'type':3, 'nb':nb_users_type3},
             {'type':4, 'nb':nb_users_type4},
             {'type':5, 'nb':nb_users_type5},
             {'type':6, 'nb':nb_users_type6},
             {'type':7, 'nb':nb_users_type7}
             ]
users = []
for username in usernames:
    for nb in range(username.get('nb')):
        users.append({"username":'type'+str(username.get('type'))+'nr'+str(username.get('nb')),"usertype":username.get('type')})




#################
### Simulatie ###
#################
df = simulation(users, capaciteitspiek, dynamic_prices, PV_schaal)
#dynamische tarieven vs laadcomfort: waarde meegeven
print("test test test",users)




#########################
### Output Parameters ###
#########################
print("INPUTGEGEVENS SIMULATIE")
print("capaciteitslimiet",capaciteitspiek)
print("types gebruikers en aantal:")
for user in usernames:
    if user.get('nb') !=0:
        print(f"Type gebruiker: {user.get('type')} Aantal {user.get('nb')}")
print("gedetailleerde types:")
valcounts = {}

# Loop through the list of dictionaries
for my_dict in users:
    # Get the value for the key to count
    value = my_dict.get('rand_profile')
    # If the value is not in the dictionary yet, add it with a count of 1
    if value not in valcounts:
        valcounts[value] = 1
    # If the value is already in the dictionary, increment its count
    else:
        valcounts[value] += 1
print(valcounts)

print('--------------------------------------------------------------------------')
print('RESULTATEN SIMULATIE')

#Zelfconsumptie PV-installatie
#Kostprijs vd elektriciteit per type
#Impact op comfort (% niet kunnen laden)
#Overschot energie