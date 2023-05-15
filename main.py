###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *

from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
#HTML inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek
nb_users_type1_no_priority = 2
nb_users_type1_priority = 2

nb_users_type2_no_priority = 3
nb_users_type2_priority = 3

nb_users_type3_no_priority = 2
nb_users_type3_priority = 2

nb_users_type4_no_priority = 4
nb_users_type4_priority = 4

nb_users_type5_no_priority = 1
nb_users_type5_priority = 1

nb_users_type6_no_priority = 2
nb_users_type6_priority = 2

nb_users_type7_priority = 1


capaciteitspiek = 22.15 #minstens 22.15, anders kan het standaardverbruik niet altijd geleverd worden
dynamic_prices = True
PV_schaal = 1

#######################################
### HIERONDER NIETS MEER AANPASSEN! ###
#######################################

systemInfo = {"caplimit":capaciteitspiek,"PVschaling":PV_schaal,"dynamic prices":dynamic_prices}

usernames = [{'type':1, 'nb':nb_users_type1_no_priority, 'priority':0},
             {'type':1, 'nb':nb_users_type1_priority, 'priority':1},
             {'type':2, 'nb':nb_users_type2_no_priority, 'priority':0},
             {'type':2, 'nb':nb_users_type2_priority, 'priority':1},
             {'type':3, 'nb':nb_users_type3_no_priority, 'priority':0},
             {'type':3, 'nb':nb_users_type3_priority, 'priority':1},
             {'type':4, 'nb':nb_users_type4_no_priority, 'priority':0},
             {'type':4, 'nb':nb_users_type4_priority, 'priority':1},
             {'type':5, 'nb':nb_users_type5_no_priority, 'priority':0},
             {'type':5, 'nb':nb_users_type5_priority, 'priority':1},
             {'type':6, 'nb':nb_users_type6_no_priority, 'priority':0},
             {'type':6, 'nb':nb_users_type6_priority, 'priority':1},
             {'type':7, 'nb':nb_users_type7_priority, 'priority':2}
             ]
users = []
for username in usernames:
    for nb in range(username.get('nb')):
        users.append({"username":'type'+str(username.get('type'))+'nr'+str(username.get('nb')),"usertype":username.get('type'), "priority":username.get('priority')})

time = datetime.now()
simname = "Sim_cap-" + str(systemInfo.get('caplimit')) +"_Users-" + str(len(users)) +"_" + str(time.strftime("%d-%m-%Y %H:%M"))



#################
### Simulatie ###
#################
df = simulation(users,general=systemInfo)
#dynamische tarieven vs laadcomfort: waarde meegeven

#########################
### Output Parameters ###
#########################
inputgegevens = {}
inputgegevens['Capaciteitslimiet'] = df[1].get('caplimit')
inputgegevens['PV schaling'] = df[1].get('PVschaling')
inputgegevens['Dynamische prijzen'] = df[1].get('dynamic prices')

print('')
print("===INPUTGEGEVENS SIMULATIE===")
print("capaciteitslimiet:",df[1].get('caplimit'),'kWh')
print("schaling PV:",df[1].get('PVschaling'))
print("dynamische prijzen:",df[1].get('dynamic prices'))
print("===types gebruikers en aantal:")
types = {}
s = 0
for user in usernames:
    if user.get('nb') !=0:
        print(f"    Gebruiker: {user.get('type')} Aantal {user.get('nb')}")
        if user.get('type') not in types.keys():
            types[user.get('type')] = user.get('nb')
        s = s + user.get('nb')
# types['totaal gebruikers'] = s
print("Totaal aantal gebruikers",s)
print("===gedetailleerde types:")

typecounts = {}
# Loop through the list of dictionaries
for my_dict in users:
    # Get the value for the key to countp
    value = my_dict.get('rand_profile')
    # If the value is not in the dictionary yet, add it with a count of 1
    if value not in typecounts:
        typecounts[value] = 1
    # If the value is already in the dictionary, increment its count
    else:
        typecounts[value] += 1
print(typecounts)

print('--------------------------------------------------------------------------')
print('RESULTATEN SIMULATIE')
print("Algemene resultaten")
print("Zelfconsumptie dom laden",df[1].get('self_consumption_dumb')*100,' %')
print("Zelfconsumptie slim laden",df[1].get('self_consumption_smart')*100,' %')
print("Overschot energie dom laden",df[1].get('excess_energy_dumb'), 'kWh')
print("Overschot energie slim laden",df[1].get('excess_energy_smart'), 'kWh')
resultsperuser = []
for i in range(len(users)):
    user = users[i]
    list = []
    list.append(user.get('rand_profile'))
    list.append(round(sum(user.get('dumb_profile')),3))
    list.append(round(user.get('energy cost dumb'),3))
    list.append(user.get('dumb_comfort'))
    list.append(round(sum(user.get('smart_profile')),3))
    list.append(round(user.get('energy cost smart'),3))
    list.append(user.get('smart_comfort'))
    list.append(i+1)
    resultsperuser.append(list)
    print("")
    print("Type profiel",list[0])
    print("===laden via domme sturing===")
    print(" Totaalverbruik:",list[1],"kWh")
    print(" Energiekost:",list[2],"€")
    print(" Gemiddeld comfort:",list[3])
    print("===laden via slimme sturing===")
    print(" Totaalverbruik:",list[4],"kWh")
    print(" Energiekost:",list[5],"€")
    print(" Gemiddeld comfort:",list[6])

resultspertype = []
for type in types.keys():
    instances = [us for us in users if us.get("usertype")== type]
    number = len(instances)
    list = []
    list.append(type)
    list.append(number)
    list.append(round(sum([sum(inst.get('dumb_profile'),3) for inst in instances])/number,3))
    list.append(round(sum([inst.get('energy cost dumb') for inst in instances])/number,3))
    list.append(sum(([inst.get('dumb_comfort') for inst in instances]))/number)
    list.append(round(sum([sum(inst.get('smart_profile'),3) for inst in instances])/number,3))
    list.append(round(sum([inst.get('energy cost smart') for inst in instances])/number,3))
    list.append(sum(([inst.get('smart_comfort') for inst in instances]))/number)
    resultspertype.append(list)
    print('')
    print("Resultaten voor gebruikers van het type:",type," aantal:",number)
    print("===Resultaten via domme sturing===") 
    print(' Gemiddeld totaalverbruik:',list[2],' kWh')
    print(' Gemiddelde verbruikskost:',list[3],' €')
    print(' Gemiddeld comfort:',list[4])
    print("===Resultaten via slimme sturing===")
    print(' Gemiddeld totaalverbruik:',list[5],' kWh')
    print(' Gemiddelde verbruikskost:',list[6], '€')
    print(' Gemiddeld comfort:',list[7])


def generatepdf(filename):
  
    with open('report.html', 'r') as file:
        template = Template(file.read())
    html = template.render(dict1 = inputgegevens,dict2=types,dict3 = typecounts, list2 = resultsperuser,list1=resultspertype)

    # Generate the PDF from the HTML template
    pdf_bytes = HTML(string=html).write_pdf()

    # Save the PDF to a file
    with open(f'pdf_results\{filename}.pdf', 'wb') as f:
        f.write(pdf_bytes)

generatepdf(filename = simname)
