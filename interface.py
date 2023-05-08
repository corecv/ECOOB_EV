import tkinter as tk

window = tk.Tk()
window.resizable(width=False, height=False)
window.geometry("500x500")

frame = tk.Frame()

user1 = tk.Label(master=frame,text="Vul hiernaast het aantal gebruikers van het type 1 in:")
ent_1 = tk.Entry(master=frame,width=10)
user2 = tk.Label(master=frame,text="Vul hiernaast het aantal gebruikers van het type 2 in:")
ent_2 = tk.Entry(master=frame,width=10)
user3 = tk.Label(master=frame,text="Vul hiernaast het aantal gebruikers van het type 3 in:")
ent_3 = tk.Entry(master=frame,width=10)
user4 = tk.Label(master=frame,text="Vul hiernaast het aantal gebruikers van het type 4 in:")
ent_4 = tk.Entry(master=frame,width=10)

frame.pack()
btn_calculate = tk.Button(master=window,text="Klik hier om de simulatie te starten!")
btn_calculate.pack()
user1.grid(row =0,column=0,pady=10)
ent_1.grid(row=0,column=1)
user2.grid(row =1,column=0,pady=10)
ent_2.grid(row=1,column=1)
user3.grid(row =2,column=0,pady=10)
ent_3.grid(row=2,column=1)
user4.grid(row =3,column=0,pady=10)
ent_4.grid(row=3,column=1)
window.mainloop()