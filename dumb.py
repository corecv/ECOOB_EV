from matplotlib import pyplot as plt# Dom laden: op elk tijdsstip t vraagt elke auto die wilt laden, max vermogen. Als boven cap: verschil met cap/#ladende auto's aftrekken van geladen vermogen.
import numpy as np
from profiles import users
time = 24
cap = 8
#user[chargerate,maxcharge]

timeload = []

def dumpProfile(userlist,timesteps,cap):
    newprofs = [[] for _ in range(len(userlist))]
    totals = []

    for t in range(timesteps):
        print(t)
        # loads = []
        # for user in userlist:
        #     if user.get('soc')[t-1] == user.get('user')[1]:
        #         loads.append(0) 
        #     elif user.get('soc')[t-1] != user.get('user')[1]:
        #         loads.append(user.get('loadprof')[t]*user.get('user')[0])

            




        for user in userlist:
            count = user.get('count')
            demand = user.get('demandprof')[count]  #(soc0,soc1)
            profile = newprofs[userlist.index(user)]
            loadprof = user.get('loadprof')
            soc = user.get('soc')

            if loadprof[t] == 0:
                profile.append(0)
                soc[t] = 0
               

            elif loadprof[t] == 1 and soc[t] != user.get('user')[1]:

                    if loadprof[t-1] == 0:
                        soc[t] = demand[0]*user.get('user')[1] + user.get('user')[0]
                        if soc[t] >= user.get('user')[1]:
                            profile.append(user.get('user')[0]- (soc[t]-user.get('user')[1]))
                            soc[t] = user.get('user')[1]  
                        else:
                            profile.append(user.get('user')[0])


                    elif loadprof[t-1] == 1:
                        soc[t]= soc[t-1] + user.get('user')[0]
                        if soc[t] >= user.get('user')[1]:
                            profile.append(user.get('user')[1]- soc[t-1])
                            soc[t] = user.get('user')[1]
                        else:
                            profile.append(user.get('user')[0])
                
                    # if user.get('loadprof')[t+1] == 0:
                    #     n = user.get('count') + 1
                    #     user.update({'count':n})
  

                
            elif loadprof[t] == 1 and soc[t] == user.get("user")[1]:
                profile.append(0)
                soc[t] = user.get('user')[1]
            
            else:
                print("fout in verbruikverdeling")
            



            
            
            if t < (len(loadprof)-1):
                if loadprof[t] == 1 and loadprof[t+1] == 0:
                    if (count+1) < len(user.get('demandprof')):
                        new = count + 1
                        user.update({"count":new})
                    elif (count+1) == len(user.get('demandprof')):
                        new = count
                        user.update({"count":new})
            user.update({"soc":soc})
        
        loads = [prof[t] for prof in newprofs ]
        ls = sum(loads)
        totals.append(ls)
        if ls > cap:
            diff = ls - cap
            dep = diff/len(userlist)
            for prof in newprofs:
                prof[t] = prof[t] - dep
                userlist[newprofs.index(prof)].get('soc')[t] = userlist[newprofs.index(prof)].get('soc')[t]-dep
           


    profiles = {"cap":[cap]* timesteps,"sum":totals,"profiles":newprofs,"timevalues":timeload}
    print("######################################")
    print("vraag per timestep",totals)
    print("######################################")
    for i in range (len(newprofs)):
        print("nieuwe laadprofielen user",i+1,newprofs[i])
        print("---------------------------------------------")
    
    print("######################################")

    for i in range(len(users)):
        print("state of charge user",i+1,users[i].get('soc'))
        print("---------------------------------------------")
    




    print('"""""""""""""""""""""""""""""""""""""')
    
    #general plot
    t = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    plt.plot(profiles.get("cap"),linestyle="dashed",label="limiet")
    plt.step(t,profiles.get("sum"),linestyle="dashed",label="potentiele som",where="post")
    for profile in profiles.get('profiles'):
        plt.step(t,profile,label=str("laadprofiel user"+str(profiles.get('profiles').index(profile) +1)),where="post")
    # plt.step(t,users[0].get('loadprof'))
    # plt.step(t,users[1].get('loadprof'))

    plt.xticks(np.arange(0, 25, 1))
    plt.yticks(np.arange(min(profiles.get("sum")), max(profiles.get("sum"))+1, 1.0))
    plt.xlabel('time')
    plt.ylabel('kWh')
    plt.grid(color = 'green', linestyle = '--', linewidth = 0.5,axis='y')
    plt.legend()
    plt.show()

    
    return profiles




dumpProfile(users,time,cap)









 
