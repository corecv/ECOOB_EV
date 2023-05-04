from matplotlib import pyplot as plt# Dom laden: op elk tijdsstip t vraagt elke auto die wilt laden, max vermogen. Als boven cap: verschil met cap/#ladende auto's aftrekken van geladen vermogen.
import numpy as np
from profiles import users,time
import pandas as pd

df = pd.read_csv('Productie en verbruik info Core.csv', delimiter=';')
# df.head()
pd.to_datetime(df.Datum.iloc[0] + ' ' + df.Tijd.iloc[0])
df.Datum = pd.to_datetime(df.Datum + ' ' + df.Tijd)
df.rename(columns={'Datum':'timestamp'}, inplace=True)
df.drop(['Tijd'], axis = 1, inplace = True)
df.head()

common = df.iloc[0:96,1]
pv = df.iloc[0:96,2]

cap = 12

def dumpProfile(userlist,timesteps,cap):
    newprofs = [[] for _ in range(len(userlist))]
    limit = []
    load = []

    for t in range(len(timesteps)):
        # print(t)
        lim = cap - common[t] + pv[t]
        limit.append(lim)
        active = 0

        for user in userlist:
            count = user.get('count')
            demand = user.get('demandprof')[count]  #(soc0,soc1)
            profile = newprofs[userlist.index(user)]
            loadprof = user.get('loadprof')
            soc = user.get('soc')
            userd = user.get('user')
            soc0 = demand[0]*userd[1]
            soc1 = demand[1]*userd[1]


            if loadprof[t] == 0 or lim <0:  #niet beschikbaar of geen speling in verbruik
                profile.append(0)  #nul aan het laadprofiel toevoegen
                if t < len(loadprof)-1:
                    if loadprof[t+1] == 1:
                        soc[t] = soc0
                    else:
                        soc[t] = soc[t-1]
                else:
                    soc[t] = soc[t-1] 

               
            elif loadprof[t] == 1 and soc[t] != soc1:  #als er geladen kan worden en de batterij nog niet volzit (soc einde maal capaciteit)

                        socn = soc[t-1] + userd[0]  #nieuwe soc, soc van vorig tijdstip + laadhoeveelheid dit tijdstip
                        active += 1
                        if socn >= soc1:
                            profile.append(userd[0]- (socn-userd[1]))
                            soc[t] = userd[1]  
                        else:
                            profile.append(userd[0])
                            soc[t] = socn 
                
            elif loadprof[t] == 1 and soc[t] == soc1:  #als er geladen kan worden maar de batterij zit al vol
                profile.append(0)
                soc[t] = userd[1]
            
            else:
                print("fout in verbruikverdeling")
            
            user.update({"soc":soc})

            if (loadprof[t] == 1 and t+1 < len(loadprof) and loadprof[t+1] == 0) or (loadprof[t] == 1 and t == len(loadprof)-1):

                    socE = user.get('soc')[t]
                    demandE = demand[1]*userd[1]
                    a = user.get('passfail')
                    a.append(round(socE/demandE,5))
                    user.update({"passfail":a})

                    if (count+1) < len(user.get('demandprof')):
                        new = count + 1
                    elif (count+1) >= len(user.get('demandprof')):
                        new = count
                    user.update({"count":new})
                    
        
        loads = [prof[t] for prof in newprofs ]
        ls = sum(loads)
        
        load.append(ls)
        if ls > abs(lim):
            diff = lim
            dep = diff/active
            for prof in newprofs:
                if prof[t] != 0:
                    a = dep
                    prof[t] = a if a>0 else 0
                    userlist[newprofs.index(prof)].get('soc')[t] = userlist[newprofs.index(prof)].get('soc')[t-1]+dep
            nload = [prof[t] for prof in newprofs ]
            load[t] = sum(nload)
    
    profiles = {"steps":timesteps,"cap":cap,"profiles":newprofs,"limit":limit,"loads":load}
    
    print("")
    print("")
    print("######################################")
    print("vraag per timestep",load)
    print("######################################")
    for i in range (len(newprofs)):
        print("nieuwe laadprofielen user",i+1,newprofs[i])
        print("---------------------------------------------")
    
    print("######################################")

    for i in range(len(users)):
        print("state of charge user",i+1,users[i].get('soc'))
        print("---------------------------------------------")
    
    print('"""""""""""""""""""""""""""""""""""""')

    print("######################################")

    for i in range(len(users)):
        print("passfail",i+1,users[i].get('passfail'))
        print("---------------------------------------------")
    
    return profiles


def plot(data):
    time = data.get('steps')
    plt.axhline(data.get("cap"),linestyle="dashed",label="limiet")
    for profile in data.get('profiles'):
        plt.step(time,profile,label=str("laadprofiel user"+str(data.get('profiles').index(profile) +1)),where="post")
    # plt.step(time,users[0].get('loadprof'),where="post")
    plt.step(time,data.get('limit'),linestyle="dashed",where="post",label="limiet")
    plt.step(time,data.get('loads'),where="post",label="real load")
    plt.step(time,common,where="post",label="eigenverbruik")
    plt.step(time,pv,where="post",label="pv")

    plt.xticks(np.arange(0, 96, 1))
    # plt.yticks(np.arange(min(profiles.get("loads")), max(profiles.get("limit")), 5.0))
    plt.xlabel('time')
    plt.ylabel('kW')
    plt.grid(color = 'green', linestyle = '--', linewidth = 0.5,axis='y')
    plt.legend()
    plt.show()




profile = dumpProfile(users,time,cap)
plot(profile)











 
