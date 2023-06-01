import numpy as np






def get_dumb_profiles(user_list,df,cap,chargeR,sim):
    if sim ==2: print(' ### algemene gegevens ophalen')

    common = df['Gemeenschappelijk verbruik in kW']
    pv = df['Productie in kW']
    newprofs = [[0]*len(df['Gemeenschappelijk verbruik in kW']) for _ in range(len(user_list))]
    socs = [0]*len(user_list)
    limit = []
    counts = [0]*len(user_list)
    charge_rate= chargeR

    def calculatecharge(user,cperuser,t): #user[user,index]
            b = user[1]
            cuser = user[0]
            count = counts[b] 
            demand = cuser.get('demandprof')[count]  #(load0,load1)
            loadprof = cuser.get('loadprof')
            soc = socs[b]
            load0 = demand[0]
            load1 = demand[1]
            full = False
            if (t!=0 and loadprof[t-1] ==0) or t==0:
                    socb = load0
            else:
                    socb = soc
            
            if socb < load1:
                if cperuser > charge_rate:
                        newcharge = charge_rate
                elif cperuser < charge_rate:
                        newcharge = cperuser 

                socn = socb + newcharge  #nieuwe soc, soc van vorig tijdstip + laadhoeveelheid dit tijdstip
                if socn >= load1:
                    a = newcharge - (socn-load1) if socn-load1 > 0 else 0
                    charge = a
                    full == True

                else:
                    charge = newcharge
                            
            elif socb >= load1:
                charge = 0
            return charge,full

    if sim ==2: print(' ### alle gebruikers doorlopen')

    for t in range(len(df['Gemeenschappelijk verbruik in kW'])):
        lim = cap - common[t] + pv[t]
        limit.append(lim)
        #actieve gebruikers toevoegen aan de lijst "ausers"
        ausers = []
        for i in range(len(user_list)):
            if user_list[i].get('loadprof')[t] == 1:
                ausers.append([user_list[i],i]) 
        
        #de lijst van actieve users doorlopen en toevoegen wat ze effectief moeten laden afhankelijk van batterijniveau, als een auto vol is wordt de user vervangen door np.nan
        if lim>0:
            chargeperuser = []  #lijst met wat elke user effectief kan laden, afhankelijk van zijn soc
            for i in range(len(ausers)):
                user = ausers[i]
                a = user[1]
                cuser = user[0]
                count = counts[a] 
                demand = cuser.get('demandprof')[count]  #(load0,load1)
                loadprof = cuser.get('loadprof')
                soc = socs[i]
                load0 = demand[0]
                load1 = demand[1]
                if (t!=0 and loadprof[t-1] ==0) or t==0:
                    socb = load0

                else:
                    socb = soc

                if socb >= load1:
                    ausers[i] = np.nan

            
            #de np.nan elementen verwijderen, nu blijven enkel de users over die effectief moeten laden (volledige charge rate of tot batterij vol is)
            ausers_new = []
            for element in ausers:
                if str(element) != "nan":
                    ausers_new.append(element)
    
            #per user is 
            peruser = lim/len(ausers_new) if len(ausers_new)>0 else lim
            maxloads = []
            for c in range(len(ausers_new)):
                c,f = calculatecharge(user=ausers_new[c],cperuser=peruser,t=t)
                if f == True: maxloads.append(ausers_new[c][1])
                chargeperuser.append(c)

            
            finalchargelist = []
            if round(sum(chargeperuser)) == lim:
                finalchargelist = chargeperuser
            
            elif sum(chargeperuser) < lim:
                
                newactive = len(ausers_new) - len(maxloads)
                extra = (lim - sum(chargeperuser))/newactive if newactive > 0 else 0
                for c in range(len(ausers_new)):
                    if ausers_new[c][1] in maxloads:
                         continue
                    # c,ex,f = calculatecharge(user=ausers_new[c],chargeperuser=peruser,t=t)
                    newc,f = calculatecharge(user = ausers_new[c],cperuser=peruser+extra,t=t)        
                    chargeperuser[c] = newc
                
                finalchargelist = chargeperuser




            else:
                if lim >0:
                    surplus = sum(chargeperuser)/lim
                    finalchargelist = [num/surplus for num in chargeperuser]
                elif lim <=0:    
                    finalchargelist = [0] *len(chargeperuser)
            # if t==0 or t==1 or t==20:
            #     print('-----------------------------',t)
            #     print('fullloads',len(maxloads))
            #     print('limiet',lim)
            #     print('flist',finalchargelist)
            #     print('lengte flist',len(finalchargelist))
            #     print('som flist',sum(finalchargelist))
        charginuser = 0
        charginindexes = [u[1] for u in ausers_new]
        for i in range(len(user_list)):
            user = user_list[i]
            count = counts[i] 
            demand = user.get('demandprof')[count]  #(load0,load1)
            profile = newprofs[i]
            loadprof = user.get('loadprof')
            soc = socs[i]
            load0 = demand[0]
            load1 = demand[1]
            if loadprof[t] == 0:  #niet beschikbaar of geen speling in verbruik
                profile[t]=0  #nul aan het laadprofiel toevoege
            
            elif loadprof[t] == 1:  #als er geladen kan worden en de batterij nog niet volzit (soceinde maal capaciteit)
                if (t!=0 and loadprof[t-1] ==0) or t==0:
                    socb = load0
                else:
                    socb = soc

                if lim > 0:
                    if i in charginindexes:    
                    # if socb < load1:
                        # print(len(finalchargelist))
                        # print('++user',charginuser)
                        profile[t]=finalchargelist[charginuser]
                        socs[i] = socb + finalchargelist[charginuser] 
                        charginuser = charginuser + 1
                    
                    # elif socb >= load1:
                    else:
                        profile[t]= 0
                        socs[i] = socb
                elif lim <= 0:
                    profile[t] = 0
                    socs[i] = socb


            else:
                print("fout in verbruikverdeling")
            
            if (loadprof[t] == 1 and t+1 < len(loadprof) and loadprof[t+1] == 0) or (loadprof[t] == 1 and t == len(loadprof)-1):
                    counts[i] = count + 1 if count < (len(user.get('demandprof'))-1) else count
    
    if sim ==2: print(' ### inserting dumb profile in user_list')

    for i in range(len(user_list)):
  
        user_list[i]['dumb_profile'] =newprofs[i]

    return user_list











 
