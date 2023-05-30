###########################################################################
### Dit is de file waarin je de parameters voor de simulatie kan kiezen ###
###########################################################################
from profiles import *
import pandas as pd
import numpy as np
from datetime import datetime

#inputs: aantal laadpalen, aantal per type, aantal autotype per type user + cap piek

######################
### Gebruiksinputs ###
######################

#gebruikers van het type 1
nb_users_type1_no_priority = 10
nb_users_type1_priority =11

#gebruikers van het type 2
nb_users_type2_no_priority = 0
nb_users_type2_priority = 0

#gebruikers van het type 3
nb_users_type3_no_priority = 0
nb_users_type3_priority = 4

#gebruikers van het type 4
nb_users_type4_no_priority = 9
nb_users_type4_priority = 4

#gebruikers van het type 5
nb_users_type5_no_priority =0
nb_users_type5_priority = 0

#gebruikers van het type 6
nb_users_type6_no_priority = 1
nb_users_type6_priority = 1

#gebruikers van het type 7
nb_users_type7_priority =7


#input gegevens van het gebouw 
capaciteitspiek = 25 #[kW] #minstens 22.15, anders kan het standaardverbruik niet altijd geleverd worden. Dit moet minimaal het verbruik van het gebouw zijn.
dynamic_prices = True
PV_schaal = 1

#voor een laadpaal van 22kW is de laadsnelheid per kwartier = 22/4 = 5.5 (kWh --> kWkwartier)
charge_rate = 5.5 #kW per kwartier

#results: duid hieronder aan welke soort documenten u wenst te genereren
pdf = True
excell = True 

#######################################
### HIERONDER NIETS MEER AANPASSEN! ###
#######################################
if pdf == True:
    from weasyprint import HTML
    from jinja2 import Template

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
inputgegevens['Capaciteitslimiet [kWh]'] = general.get('caplimit')
inputgegevens['PV schaling'] = general.get('PVschaling')
inputgegevens['Dynamische prijzen'] = general.get('dynamic prices')
inputgegevens['Laadsnelheid [kW/kwartier]'] = general.get('chargerate')

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
    print("Zelfconsumptie dom laden",general.get('self_consumption_dumb'),' %')
    print("Overschot energie dom laden",general.get('excess_energy_dumb'), 'kWh')
    print("totale energiekost dom laden",general.get('total energy cost dumb'), '€')
    print("Zelfconsumptie slim laden",general.get('self_consumption_smart'),' %')
    print("Overschot energie slim laden",general.get('excess_energy_smart'), 'kWh')
    print("totale energiekost slim laden",general.get('total energy cost smart'), '€')
resultsperuser = []
def peruser():
    for i in range(len(users)):
        user = users[i]
        list = []
        list.append(user.get('rand_profile') + user.get('pr'))
        list.append(round(np.nansum(user.get('dumb_profile'))/4,3))
        list.append(round(user.get('energy cost dumb'),3))
        list.append(user.get('dumb_comfort'))
        list.append(round(np.nansum(user.get('smart_profile'))/4,3))
        list.append(round(user.get('energy cost smart'),3))
        list.append(round(user.get('smart_comfort'),3))
        list.append(i+1)
        list.append(user.get('dumb_profile'))
        list.append(user.get('smart_profile'))
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
        list.append(round(sum([np.nansum(inst.get('dumb_profile'))/4 for inst in instances])/number,3))
        list.append(round(sum([inst.get('energy cost dumb') for inst in instances])/number,3))
        list.append(round(sum(([inst.get('dumb_comfort') for inst in instances]))/number,3))
        list.append(round(sum([np.nansum(inst.get('smart_profile'))/4 for inst in instances])/number,3))
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
pvoutput = [general['self_consumption_dumb'],general['excess_energy_dumb'],general['self_consumption_smart'],general['excess_energy_smart'],general['total energy cost dumb'],general['total energy cost smart']]
def generatepdf(filename):
  
    with open('report.html', 'r') as file:
        template = Template(file.read())
    html = template.render(simulation = filename,t = time,dict1 = inputgegevens,dict2=generaltypecount,dict3 = detailedtypecount,list4 = pvoutput,list1=resultspertype)

    # Generate the PDF from the HTML template
    pdf_bytes = HTML(string=html,base_url="").write_pdf()

    # Save the PDF to a file
    with open(os.path.join('pdf_results',f'{filename}.pdf'), 'wb') as f:
        f.write(pdf_bytes)

def generatespread(filename):
    values = [li[2:] for li in resultspertype]
    rows = [li[0] for li in resultspertype]
    cols = ['Energiegebruik dom [kWh]','Energiekost dom [€]','Comfort dom [%]','Energiegebruik slim [kWh]','Energiekost slim [€]','Comfort slim [%]']
    
    units = ["kW","/","/","kW per kwartier","%","kWh","%","kWh","kWh","kWh","€","€"]
    genVal,genRows = [],[]
    for k,v in general.items():
        if k == "consumption dumb" or k == "consumption smart":
            continue
        else:
            genVal.append(v)
            genRows.append(k)
    # genVal = [i for i in general.values()]
    # genRows = [i for i in general.keys()]
    detailedtypecountsorted = {k:detailedtypecount[k] for k in sorted(detailedtypecount)}
    typeVal = [i for i in detailedtypecountsorted.values()]
    typeRow = [ i for i in detailedtypecountsorted.keys()]
    genVal = genVal + typeVal
    genRows = genRows + typeRow
    for i in range(len(typeVal)):
        units.append("aantal") 
   

    userVal = [li[1:7] for li in resultsperuser]
    userRow = [li[0] for li in resultsperuser]
    # userloadprof = [li[8] for li in resultsperuser]
    # userloadprofs = [li[9] for li in resultsperuser]
    # userid = [str(1+i) for i in range(len(resultsperuser))]



    fr = pd.DataFrame(values,index=rows,columns=cols)
    fr2= pd.DataFrame([genVal,units],index=['Value', 'Units'], columns = genRows).T #,columns=["Value","Units"])
    fr3 = pd.DataFrame(userVal,index=userRow,columns = cols)
    fr4 = pd.DataFrame([general['consumption dumb'],general['consumption smart']],index=['consumption dumb','consumption smart']).T
    # fr5 = pd.DataFrame(userloadprof,index=userid).T
    # fr6 = pd.DataFrame(userloadprofs,index=userid).T


    with pd.ExcelWriter(os.path.join('excell_results',f'{filename}.xlsx')) as writer:
        fr2.to_excel(writer,sheet_name='GeneralInfo')
        fr.to_excel(writer,sheet_name='ResulstPerType')
        fr3.to_excel(writer,sheet_name='ResulstPerUser')
        fr4.to_excel(writer,sheet_name='Consumption')
        # fr5.to_excel(writer,sheet_name='ConsumptionUser')
        # fr6.to_excel(writer,sheet_name='ConsumptionUserSmart')

time = datetime.now()
time = time.strftime("%d%m%Y-%H-%M")
simname = "Sim_cap-" + str(systemInfo.get('caplimit')) +"_Users-" + str(len(users)) +"_" + str(time)

if pdf == True:
    print('### generating pdf')
    generatepdf(filename = simname)
if excell == True:
    print('### generating spreadsheet')

    generatespread(filename=simname)



############################
### Finalisation message ###
############################
print("")
print("")
print('##########################################################')
print('==========================================================')
print('SIMULATIE-',simname, '-IS AFGEROND')
if pdf == True:
    print('In het mapje \"pdf_results\" kan je een pdf file vinden met de naam "',simname,'" waarin uitgebreidere resulaten weergegeven zijn')
    print("")
if excell == True:
    print('In het mapje \"excell_results\" kan je een excell file vinden met de naam "',simname,'" waarin de resulaten overzichtelijk weergegeven zijn, van hieruit kan verder gewerkt worden')
print('==========================================================')
print('##########################################################')

