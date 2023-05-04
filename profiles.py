load1 = [0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0]
load2 = [1,0,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,0,1,1]
load1 = [val for val in load1 for _ in (0, 1, 2, 4)]
load2 = [val for val in load2 for _ in (0, 1, 2, 4)]
soc1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
soc2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
soc1 = [val for val in soc1 for _ in (0, 1, 2, 4)]
soc2 = [val for val in soc2 for _ in (0, 1, 2, 4)]


time = [0+i for i in range(len(load1))] 

#user = [maxrate,maxcapacity]
#demandprof = ( SOC begin, SOC waarmee we willen eindigen)
#count is een variabele om bij te houden bij welke laadbeurt we zitten, dit getal selecteerd de juiste tuple uit demandprof
#passfail, een lijst om bij te houden hoeveel procent er geladen is in die beurt afhankelijk van de overeenkomstige demandprof, als dit =1 dan is alles wat gevraagd is geladen kunnen worden. 
users = [

{"user":[5,70],"loadprof":load1,"soc":soc1,"demandprof": [(0.4,1),(0.6,0.9)],"passfail":[],"count":0},  
{"user":[4,60],"loadprof":load2,"soc":soc2,"demandprof": [(0.5,1),(0.1,0.9),(0.6,1),(0.4,1),(0.5,1)],"passfail":[],"count":0},
{"user":[6,60],"loadprof":load2,"soc":soc2,"demandprof": [(0.3,1),(0.1,0.9),(0.4,1),(0.4,1),(0.8,1)],"passfail":[],"count":0},
{"user":[4,70],"loadprof":load1,"soc":soc2,"demandprof": [(0.5,1),(0.1,1)],"passfail":[],"count":0}  


]


