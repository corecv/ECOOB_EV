###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
import openpyxl
#inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek

#gebruikers van het type 1
nb_users_type1_no_priority = 14  
nb_users_type1_priority = 17 

#gebruikers van het type 2
nb_users_type2_no_priority = 16 
nb_users_type2_priority = 15

#gebruikers van het type 3
nb_users_type3_no_priority = 17 
nb_users_type3_priority = 20 

#gebruikers van het type 5
nb_users_type4_no_priority = 22 
nb_users_type4_priority = 19 

#gebruikers van het type 5
nb_users_type5_no_priority =12 
nb_users_type5_priority = 13 

#gebruikers van het type 6
nb_users_type6_no_priority = 9 
nb_users_type6_priority = 8 

#gebruikers van het type 7
nb_users_type7_priority = 8 

#input gegevens van het gebouw 
capaciteitspiek = 22.15 #minstens 22.15, anders kan het standaardverbruik niet altijd geleverd worden. Dit moet minimaal het verbruik van het gebouw zijn.
dynamic_prices = True
PV_schaal = 1

#voor een laadpaal van 22kW is de laadsnelheid per kwartier = 22/4 = 5.5 (kWh --> kWkwartier)
charge_rate = 5.5 #kWh per kwartier


#######################################
### HIERONDER NIETS MEER AANPASSEN! ###
#######################################


systemInfo = {"caplimit":capaciteitspiek,"PVschaling":PV_schaal,"dynamic prices":dynamic_prices,'chargerate':charge_rate}

usernames = [{'type':1,'pr':"", 'nb':nb_users_type1_no_priority, 'priority':0},
             {'type':1,'pr':'_P', 'nb':nb_users_type1_priority, 'priority':1},
             {'type':2,'pr':"", 'nb':nb_users_type2_no_priority, 'priority':0},
             {'type':2,'pr':'_P', 'nb':nb_users_type2_priority, 'priority':1},
             {'type':3,'pr':"", 'nb':nb_users_type3_no_priority, 'priority':0},
             {'type':3,'pr':'_P', 'nb':nb_users_type3_priority, 'priority':1},
             {'type':4,'pr':"", 'nb':nb_users_type4_no_priority, 'priority':0},
             {'type':4,'pr':'_P', 'nb':nb_users_type4_priority, 'priority':1},
             {'type':5,'pr':"", 'nb':nb_users_type5_no_priority, 'priority':0},
             {'type':5,'pr':'_P', 'nb':nb_users_type5_priority, 'priority':1},
             {'type':6,'pr':"", 'nb':nb_users_type6_no_priority, 'priority':0},
             {'type':6,'pr':'_P', 'nb':nb_users_type6_priority, 'priority':1},
             {'type':7,'pr':'_P', 'nb':nb_users_type7_priority, 'priority':2}
             ]
users = []
for username in usernames:
    for nb in range(username.get('nb')):
        users.append({"username":'type'+str(username.get('type'))+'nr'+str(username.get('nb')),"usertype":username.get('type'), "priority":username.get('priority'),'pr':username.get('pr')})


#################
### Simulatie ###
#################
df,general,users = simulation(users,general=systemInfo)
#dynamische tarieven vs laadcomfort: waarde meegeven

#########################
### Output Parameters ###
#########################
inputgegevens = {}
inputgegevens['Capaciteitslimiet'] = general.get('caplimit')
inputgegevens['PV schaling'] = general.get('PVschaling')
inputgegevens['Dynamische prijzen'] = general.get('dynamic prices')
inputgegevens['Laadsnelheid'] = general.get('chargerate')

generaltypecount = {}
detailedtypecount = {}
s = 0
# Loop through the list of dictionaries
for my_dict in users:
    # Get the value for the key to countp
    b = str(my_dict.get('usertype'))
    r = my_dict.get('rand_profile')
    p = "" if my_dict.get('priority') == 0 else "_P"
    gen = b + p
    value = r + p
    # If the value is not in the dictionary yet, add it with a count of 1
    if gen not in generaltypecount:
        generaltypecount[gen] = 1
    else:
        generaltypecount[gen] += 1

    if value not in detailedtypecount:
        detailedtypecount[value] = 1
    # If the value is already in the dictionary, increment its count
    else:
        detailedtypecount[value] += 1
s = sum(generaltypecount.values())
def generalinfo():
    print('')
    print("===INPUTGEGEVENS SIMULATIE===")
    for k,v in inputgegevens.items():
        print(k,':',v)
    print("===types gebruikers en aantal: _P = met prioriteit")
    for k,v in generaltypecount.items():
        print(' Gebruiker: type',k,' aantal:',v) 
    print("Totaal aantal gebruikers",s)
    print("")
    print("===gedetailleerde types: _P = met prioriteit")
    for k,v in detailedtypecount.items():
        print(' Gebruiker: type',k,' aantal:',v) 
    print('--------------------------------------------------------------------------')
    print('RESULTATEN SIMULATIE')
    print("Algemene resultaten")
    print("Zelfconsumptie dom laden",general.get('self_consumption_dumb')*100,' %')
    print("Zelfconsumptie slim laden",general.get('self_consumption_smart')*100,' %')
    print("Overschot energie dom laden",general.get('excess_energy_dumb'), 'kWh')
    print("Overschot energie slim laden",general.get('excess_energy_smart'), 'kWh')
resultsperuser = []
def peruser():
    for i in range(len(users)):
        user = users[i]
        list = []
        list.append(user.get('rand_profile') + user.get('pr'))
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
def pertype():
    for type in generaltypecount.keys():
        instances = [us for us in users if (str(us.get('usertype'))+us.get('pr')) == type]
        number = len(instances)
        list = []
        list.append(type)
        list.append(number)
        list.append(round(sum([sum(inst.get('dumb_profile')) for inst in instances])/number,3))
        list.append(round(sum([inst.get('energy cost dumb') for inst in instances])/number,3))
        list.append(round(sum(([inst.get('dumb_comfort') for inst in instances]))/number,3))
        list.append(round(sum([sum(inst.get('smart_profile')) for inst in instances])/number,3))
        list.append(round(sum([inst.get('energy cost smart') for inst in instances])/number,3))
        list.append(round(sum(([inst.get('smart_comfort') for inst in instances]))/number,3))
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

#hieronder wordt de volgorde van de print statements bepaald, een van deze functies in comments plaatsen wilt ook zeggen dat deze niet geprint wordt (soms overzichtelijker)
peruser()
pertype()
generalinfo()


###################################
### Output files - Pdf & Excell ###
###################################

def generatepdf(filename):
  
    with open('report.html', 'r') as file:
        template = Template(file.read())
    html = template.render(simulation = filename,dict1 = inputgegevens,dict2=generaltypecount,dict3 = detailedtypecount,list1=resultspertype)

    # Generate the PDF from the HTML template
    pdf_bytes = HTML(string=html,base_url="").write_pdf()

    # Save the PDF to a file
    with open(os.path.join('pdf_results',f'{filename}.pdf'), 'wb') as f:
        f.write(pdf_bytes)

def generatespread(filename):
    values = [li[2:] for li in resultspertype]
    rows = [li[0] for li in resultspertype]
    cols = ['Energiegebruik dom','Energiekost dom','Gem comfort dom','Energiegebruik slim','Energiekost slim','Gem comfort slim']
    
    genVal = [i for i in inputgegevens.values()]
    genRows = [i for i in inputgegevens.keys()]
    typeVal = sorted([i for i in detailedtypecount.values()])
    typeRow = sorted([ i for i in detailedtypecount.keys()])
    genVal = genVal + typeVal
    genRows = genRows + typeRow

    userVal = [li[1:7] for li in resultsperuser]
    userRow = [li[0] for li in resultsperuser]

    fr = pd.DataFrame(values,index=rows,columns=cols)
    fr2= pd.DataFrame(genVal,index=genRows,columns=["Value"])
    fr3 = pd.DataFrame(userVal,index=userRow,columns = cols)
    
    with pd.ExcelWriter(os.path.join('excell_results',f'{filename}.xlsx')) as writer:
        fr2.to_excel(writer,sheet_name='GeneralInfo')
        fr.to_excel(writer,sheet_name='ResulstPerType')
        fr3.to_excel(writer,sheet_name='ResulstPerUser')

time = datetime.now()
simname = "Sim_cap-" + str(systemInfo.get('caplimit')) +"_Users-" + str(len(users)) +"_" + str(time.strftime("%d-%m-%Y-%H-%M"))
generatepdf(filename = simname)
generatespread(filename=simname)

############################
### Finalisation message ###
############################
print("")
print("")
print('##########################################################')
print('==========================================================')
print('SIMULATIE-',simname, '-IS AFGEROND')
print('In het mapje \"pdf_results\" kan je een pdf file vinden met de naam "',simname,'" waarin uitgebreidere resulaten weergegeven zijn')
print("")
print('In het mapje \"excell_results\" kan je een excell file vinden met de naam "',simname,'" waarin de resulaten overzichtelijk weergegeven zijn, van hieruit kan verder gewerkt worden')
print('==========================================================')
print('##########################################################')