
def get_dumb_profiles(users,df,cap,chargeR):
    common = df.iloc[:,1]
    pv = df.iloc[:,2]
    newprofs = [[] for _ in range(len(users))]
    socs = [[] for _ in range(len(users))]
    limit = []
    load = []
    counts = [0]*len(users)
    charge_rate= chargeR
    
    for t in range(len(df)):
        lim = cap - common[t] + pv[t]
        limit.append(lim)
        aloads = [charge_rate for user in users if user.get('loadprof')[t] == 1 ] # and socs[users.index(user)][t-1] != user.get('demandprof')[counts[users.index(user)]][1])]
        ls = sum(aloads)
        load.append(ls)
        active = len(aloads)
        peruser = lim/active if active>0 else lim

        for i in range(len(users)):
            user = users[i]
            count = counts[i] #user.get('count')
            # print(user.get('demandprof'))
            demand = user.get('demandprof')[count]  #(load0,load1)
            profile = newprofs[i]
            loadprof = user.get('loadprof') #.tolist()
            # print(loadprof)
            loadlevel= socs[i]
            load0 = demand[0]  #*userd[1]
            load1 = demand[1] #*userd[1]
            
            if loadprof[t] == 0:  #niet beschikbaar of geen speling in verbruik
                profile.append(0)  #nul aan het laadprofiel toevoegen
                loadlevel.append(0)
   
            elif loadprof[t] == 1:  #als er geladen kan worden en de batterij nog niet volzit (loadleveleinde maal capaciteit)
                if (t!=0 and loadprof[t-1] ==0) or t==0:
                    socb = load0
                else:
                    socb = loadlevel[t-1]
                if lim > 0:    
                    if socb != load1:
                        if peruser > charge_rate:
                            newcharge = charge_rate
                        elif peruser < charge_rate:
                            newcharge = peruser 
                        socn = socb + newcharge  #nieuwe soc, loadlevel van vorig tijdstip + laadhoeveelheid dit tijdstip
                        if socn >= load1:
                            profile.append(newcharge - (socn-load1))
                            loadlevel.append(load1) 
                        else:
                            profile.append(newcharge)
                            loadlevel.append(socn)
                    
                    elif socb == load1:
                        profile.append(0)
                        loadlevel.append(socb)
                elif lim <0:
                    profile.append(0)
                    loadlevel.append(socb)
            else:
                print("fout in verbruikverdeling")
            
            if (loadprof[t] == 1 and t+1 < len(loadprof) and loadprof[t+1] == 0) or (loadprof[t] == 1 and t == len(loadprof)-1):
                    counts[i] = count + 1 if count < (len(user.get('demandprof'))-1) else count
    for i in range(len(users)):
        users[i].update({"dumb_profile":newprofs[i]})
    return users 











 
