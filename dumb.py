def get_dumb_profiles(users,df,cap):
    common = df.iloc[:,1]
    pv = df.iloc[:,2]
    newprofs = [[] for _ in range(len(users))]
    socs = [[] for _ in range(len(users))]
    limit = []
    load = []
    counts = [0]*len(users)
    chargeRate = 22/4

    
    for t in range(len(df)):
        lim = cap - common[t] + pv[t]
        limit.append(lim)
        aloads = [chargeRate for user in users if user.get('loadprof')[t] == 1]
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
            loadprof = user.get('loadprof')
            loadlevel= socs[i]
            load0 = demand[0]  #*userd[1]
            load1 = demand[1] #*userd[1]
            
            # print("PROFIEL USER",users.index(user))
            # print(i)

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
                        if peruser > chargeRate:
                            newcharge = chargeRate
                            # socn = socb + newcharge
                        elif peruser < chargeRate:
                            newcharge = peruser 
                        
                        socn = socb + newcharge  #nieuwe soc, loadlevelvan vorig tijdstip + laadhoeveelheid dit tijdstip
                        
                        if socn >= load1:

                            profile.append(newcharge- (socn-load1))
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
                    # print(user.get('user'),count)
    for i in range(len(users)):
        # l = newprofs[users.index(user)]
        users[i].update({"dumb_profile":newprofs[i]})

    # profiles = {"cap":cap,"profiles":newprofs,"limit":limit,"loads":load}
    # print("lenge dataframe",len(df))
    # for user in newprofs:
    #     print(len(user))
    #     print('#############################""')
    #     print(user)
    # print("")
    # print("")
    # print("######################################")
    # print("vraag per timestep",load)
    # print("######################################")
    # for i in range (len(newprofs)):
    #     print("nieuwe laadprofielen user",i+1,newprofs[i])
    #     print(users[i].get('loadprof').tolist())
    #     print("---------------------------------------------")
    
    # print("######################################")

    # for i in range(len(socs)):
    #     print("state of charge user",i+1,socs[i])
    #     print("---------------------------------------------")
    
    # print('"""""""""""""""""""""""""""""""""""""')
    # print(limit)
    # print("######################################")

    return users 





# def plot(data):
#     time = [0+i for i in range(len(data.get('profiles')[0]))]
#     plt.axhline(data.get("cap"),linestyle="dashed",label="limiet")
#     for profile in data.get('profiles'):
#         plt.step(time,profile,label=str("laadprofiel user"+str(data.get('profiles').index(profile) +1)),where="post")
#     plt.step(time,data.get('limit'),linestyle="dashed",where="post",label="limiet")
#     plt.step(time,data.get('loads'),where="post",label="real load")


#     plt.xticks(np.arange(0, 96, 1))
#     plt.xlabel('time')
#     plt.ylabel('kW')
#     plt.grid(color = 'green', linestyle = '--', linewidth = 0.5,axis='y')
#     plt.legend()
#     plt.show()

# def comfort(userlist):
        
#     for user in users:
#             comfortdumb = []
#             comfortsmart = []
#             startstop = user.get('Tz')
#             dem = user.get('demandprof')
#             smart = user.get('smart_profile')
#             dumb = user.get('dumb_profile')

#             for t in range(len(startstop)):
#                 charged_d= sum(dumb[startstop[t][0]:startstop[t][1]])
#                 charged_s = sum(smart[startstop[t][0]:startstop[t][1]])
#                 comfortdumb.append((dem[t][0] + charged_d)/dem[t][1])
#                 comfortsmart.append((dem[t][0] + charged_s)/dem[t][1])
            
#             avg_d = sum(comfortdumb)/len(comfortdumb)
#             avg_s = sum(comfortsmart)/len(comfortsmart)
#             user['dumb_comfort'] = avg_d
#             user['smart_comfort'] = avg_s






# load1 = [0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0]
# load2 = [1,0,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,1,1]
# load1 = [val for val in load1 for _ in (0, 1, 2, 3)]
# load2 = [val for val in load2 for _ in (0, 1, 2, 3)]


# users = [

# {"user":[5,70],"loadprof":load1,"demandprof": [(0.4,1),(0.6,0.9)],"startstop":[]},  
# {"user":[4,60],"loadprof":load2,"demandprof": [(0.5,1),(0.1,0.5),(0.6,1),(0.4,1),(0.5,1)],"passfail":[]},
# {"user":[6,60],"loadprof":load2,"demandprof": [(0.3,1),(0.1,0.5),(0.4,1),(0.4,1),(0.8,1)],"passfail":[]},
# {"user":[4,70],"loadprof":load1,"demandprof": [(0.5,1),(0.1,1)],"passfail":[]}  
# ]



# profile = get_dumb_profiles(users,df,cap)
# for u in profile[1]:
#     c = comfort(usersoc=u.get('soc'),userload=u.get('loadprof'),usercapacity=u.get('user')[1],demand=u.get('demandprof'))
#     # print("user",c)


# plot(profile[0])











 
