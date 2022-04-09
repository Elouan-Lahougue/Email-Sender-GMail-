# coding:utf-8

# Importation des modules

import smtplib, re, webbrowser, os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.scrolledtext as tks
from tkinter import filedialog
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# Classes

class AppWin(tk.Tk):
    def __init__(self, label, x, y, version, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        xScreen, yScreen = int(self.winfo_screenwidth()), int(self.winfo_screenheight())
        
        self.label = label
        self.version = version
        self.x, self.y = x, y
        self.xPos, self.yPos = (xScreen - self.x) // 2, (yScreen - self.y) // 2
        self.geometry("{}x{}+{}+{}".format(self.x, self.y, self.xPos, self.yPos))
        self.title(f"{title} v{version[0]}.{version[1]}.{version[2]}{label}")
        self.minsize(self.x, self.y)

class TLWin(tk.Toplevel):
    def __init__(self, label, x, y, version, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        xScreen, yScreen = int(self.winfo_screenwidth()), int(self.winfo_screenheight())
        
        self.label = label
        self.version = version
        self.x, self.y = x, y
        self.xPos, self.yPos = (xScreen - self.x) // 2, (yScreen - self.y) // 2
        self.geometry("{}x{}+{}+{}".format(self.x, self.y, self.xPos, self.yPos))
        self.title(f"{title} {version[0]}.{version[1]}.{version[2]}{label}")
        # self.iconbitmap("Logo.ico")
        self.resizable(width=False, height=False)
        self.grab_set()

class XEntry(tk.Entry):
    def __init__(self, name, row, email, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        
        self.name, self.email, self.row = name, email, row
        
        if row >= 0: self.grid(row=row, column=1)
        self.insert(0, self.name)
        
        self.bind("<FocusIn>", self.focusin)
        self.bind("<Key>", self.writein)
        self.bind("<FocusOut>", self.focusout)
        self.bind("<KeyRelease>", self.correctemail)
    
    def correctemail(self, _):
        if self.email in (0, 1) and re.match(r"^([\w\.-]+)@gmail.com$", self.get()): self.config(fg="blue")
        elif self.email in (1, 2) and re.match(r"^([\w\.-]+)@([\w\.-]+).(\.[\w\.]+)$", self.get()): self.config(fg="green")
        elif self.get() == self.name: self.config(fg="grey")
        else: self.config(fg="black")

    def focusin(self, _):
        if self.get() == self.name: self.icursor(0)
    
    def writein(self, _):
        if self.get() == self.name: self.delete(0, "end")
        self.correctemail(None)

    def focusout(self, _=None):
        if self.get() == "": self.config(fg='grey'), self.insert(0, self.name)

class EButton(ttk.Button):
    def __init__(self, row, *args, **kwargs):
        ttk.Button.__init__(self, text="@", width=14, *args, **kwargs)
        
        self.grid(row=row, column=2, padx=(2, 0))
        
        self["command"] = lambda: emaildir(row)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(text="Email Directory")

    def on_leave(self, enter):
        self.configure(text="@")

class DelButton(ttk.Button):
    def __init__(self, column, *args, **kwargs):
        ttk.Button.__init__(self, text="Delete selected e-mail", width=22, *args, **kwargs)
        a, b = 0, 14
        if column == 1: a, b = b, a
        self.grid(row=2, column=column, padx=(a, b))

# Fonction permettant d'envoyer un e-mail.

def sendemail(frm, to, pw, sbj, msg):
    msg_ = MIMEMultipart()
    msg_["From"] = frm
    msg_["To"] = to
    msg_["Subject"] = sbj
    msg_.attach(MIMEText(msg, "plain"))
    
    for f in enclosed:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f,"rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg_.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(frm, pw)

    txt = msg_.as_string()
    server.sendmail(frm, to, txt)
    server.quit()


# Fonction activant la fenêtre de validation

def validation():

    def emailsending():
        try:
            sendemail(fromentry.get(), toentry.get(), pwentry.get(), subentry.get(), msgentry.get(1.0, "end"))
            tk.messagebox.showinfo("Success", "Your e-mail was sent successfully.")
        except smtplib.SMTPAuthenticationError:
            errorsendingmsg = """The sending failed.


The error can be due to several causes :

    • The password doesn't match with the email - In this case, check your password on your Google account.
    
    • You aren't connected to your Google account on your Internet browser - In this case, try to connect to it.
    
    • Your account hasn't activated the authorisation to use it from thied-party softwares - In this case, look at the indications in the menu heading : Help -> Set up your Google Account
"""
            tk.messagebox.showerror("Sending failed", errorsendingmsg)

    # Fonction fermant la page de validation

    def cancel():
        validwin.destroy()

    email_re = r"^([\w\.-]+)@([\w\.-]+).(\.[\w\.]+)$"
    if fromentry.get() == "From" or toentry.get() == "To" or subentry.get() == "Subject" or msgentry.get(1.0, "end-1c") == "":
        empties = 0
        if fromentry.get() == "From": empties += 1
        if toentry.get() == "To": empties += 1
        if subentry.get() == "Subject": empties += 1
        if msgentry.get(1.0, "end-1c") == "": empties += 1
        if empties == 1: tk.messagebox.showerror("Empty entry", "One entry is empty.")
        else: tk.messagebox.showerror("Empty entries", "Several entries are empty.")
    elif not re.match(email_re, fromentry.get()): tk.messagebox.showerror("Non-compliant email adress", "Your email adress isn't compliant.")
    elif not re.match(email_re, toentry.get()): tk.messagebox.showerror("Non-compliant email adress", "The receiving email adress isn't compliant.")
    else:
        # Création de l'interface graphique
        validwin = TLWin(" - Validation", 380, 90, version)

        # Création du body
        globaltlframe = tk.Frame(validwin, width=validwin.x-10, height=validwin.y-10)
        globaltlframe.pack(padx=6, pady=6)

        pwlabel = tk.Label(globaltlframe, text="Enter your Google/Gmail password to validate the sending.")
        pwentry = XEntry("Password", -1, -1, globaltlframe, bg="white", width=25, fg="grey", show="•")
        pwlabel.pack()
        pwentry.pack(pady=4)

        btnframe = tk.Frame(globaltlframe)
        btnframe.pack()

        finalsend = ttk.Button(btnframe, text="Send", width=10, command=emailsending)
        cancel = ttk.Button(btnframe, text="Cancel", width=10, command=cancel)
        finalsend.grid(row=0, column=0)
        cancel.grid(row=0, column=1)

# Fonction lançant l'email directory

def emaildir(target):
    
    def selectemail(tgt):
        global fromentry, toentry
        try:
            with open(f"data/{tgt}emails.txt", "r") as f:
                globals()[f"{tgt}entry"].delete(0, "end"), globals()[f"{tgt}entry"].config(fg='black'), globals()[f"{tgt}entry"].insert(0, f.readlines()[emaildirlb.curselection()[0]][:-1])
            edirectorywin.destroy()
        except IndexError: pass
    
    def lselectemail(_): selectemail(tgt)
    
    tgt = "from" if target == 0 else "to"
    
    edirectorywin = TLWin(" - E-mail Directory", 360, 252, version)
    
    globalemaildirframe = tk.Frame(edirectorywin, width=edirectorywin.x-10, height=edirectorywin.y-10)
    globalemaildirframe.pack(padx=6, pady=(6, 0))
    
    labelemaildir = tk.Label(globalemaildirframe, text="Select an e-mail")
    labelemaildir.pack()
    
    emaildirframe = tk.Frame(globalemaildirframe)
    emaildirframe.pack(pady=3)

    emaildirsb = tk.Scrollbar(emaildirframe)
    emaildirsb.pack(side="right", fill="y")

    emaildirlb = tk.Listbox(emaildirframe, yscrollcommand=emaildirsb.set, width=45, height=11)
    emaildirlb.pack(side="right", fill="both")

    emaildirsb.config(command=emaildirlb.yview)
    
    with open(f"data/{tgt}emails.txt", "r") as f:
        data = f.readlines()
        for i in range(len(data)):
            if data[i][:-1] != "": emaildirlb.insert("end", data[i][:-1])
    
    emaildirbtnframe = tk.Frame(globalemaildirframe)
    emaildirbtnframe.pack(pady=5)
    
    cancelbtned = ttk.Button(emaildirbtnframe, text="Cancel", command=lambda: edirectorywin.destroy())
    cancelbtned.grid(row=0, column=0, padx=(0, 5))
    
    selectbtned = ttk.Button(emaildirbtnframe, text="Select", command=lambda: selectemail(tgt))
    selectbtned.grid(row=0, column=1, padx=(5, 0))
    
    emaildirlb.bind("<Double-Button-1>", lselectemail)


# Fonction lançant l'email manager

def emailmgr():
    
    def addtoemails(tgt):
        colors = ("blue") if tgt == "from" else ("green", "blue")

        if addemailentry["fg"] in colors:
            newemail = addemailentry.get()
            
            with open(f"data/{tgt}emails.txt", "a") as f:
                f.write(newemail+"\n")

            with open(f"data/{tgt}emails.txt", "r") as f:
                data = f.readlines()
                for i in range(len(data)): data[i] = data[i][:-1]
                data = sorted(data)
                if data[0] == "": del data[0]

            with open(f"data/{tgt}emails.txt", "w") as f:
                f.writelines("\n".join(data)+"\n")

            fromemailslb.insert(data.index(newemail), newemail) if tgt == "from" else toemailslb.insert(data.index(newemail), newemail)
    
    def delfromemails(tgt):
        data = []
        try:
            with open(f"data/{tgt}emails.txt", "r") as f:
                data = f.readlines()
                for i in range(len(data)): data[i] = data[i][:-1]
                selection = fromemailslb.curselection()[0] if tgt == "from" else toemailslb.curselection()[0]
                del data[selection]
                data = sorted(data)
            if len(data) != 0:
                if data[0] == "": del data[0]
            with open(f"data/{tgt}emails.txt", "w") as f:
                f.writelines("\n".join(data)+"\n")
                fromemailslb.delete(selection) if tgt == "from" else toemailslb.delete(selection)
        except IndexError: pass
    
    # Création de l'interface graphique
    emanagerwin = TLWin(" - E-mail Manager", 392, 276, version)

    # Création du body
    globalmgrframe = tk.Frame(emanagerwin, width=emanagerwin.x-10, height=emanagerwin.y-10)
    globalmgrframe.pack(padx=6, pady=6)

    addemaillabel = tk.Label(globalmgrframe, text="Add an e-mail")
    addemailentry = XEntry("E-mail", -1, 1, globalmgrframe, fg="grey", width=40)
    addemaillabel.pack()
    addemailentry.pack(pady=(3, 5))

    addingframe = tk.Frame(globalmgrframe)
    addingframe.pack(pady=4)

    addtoemailsbtn = ttk.Button(addingframe, text="Add to your e-mails", width=22, command=lambda: addtoemails("from"))
    addtodirectorybtn = ttk.Button(addingframe, text="Add to your directory", width=22, command=lambda: addtoemails("to"))
    addtoemailsbtn.grid(row=0, column=0, padx=(0, 14))
    addtodirectorybtn.grid(row=0, column=1, padx=(14, 0))

    fromemailsframe = tk.Frame(addingframe)
    toemailsframe = tk.Frame(addingframe)
    fromemailsframe.grid(row=1, column=0, padx=(0, 14), pady=3)
    toemailsframe.grid(row=1, column=1, padx=(14, 0), pady=3)

    fromemailssb = tk.Scrollbar(fromemailsframe)
    fromemailssb.pack(side="right", fill="y")

    fromemailslb = tk.Listbox(fromemailsframe, yscrollcommand=fromemailssb.set, width=20, height=9)
    fromemailslb.pack(side="right", fill="both")

    fromemailssb.config(command=fromemailslb.yview)

    toemailssb = tk.Scrollbar(toemailsframe)
    toemailssb.pack(side="right", fill="y")

    toemailslb = tk.Listbox(toemailsframe, yscrollcommand=toemailssb.set, width=20, height=9)
    toemailslb.pack(side="right", fill="both")

    toemailssb.config(command=toemailslb.yview)
    
    with open("data/fromemails.txt", "r") as f:
        data = f.readlines()
        for i in range(len(data)):
            if data[i][:-1] != "": fromemailslb.insert("end", data[i][:-1])
    
    with open("data/toemails.txt", "r") as f:
        data = f.readlines()
        for i in range(len(data)):
            if data[i][:-1] != "": toemailslb.insert("end", data[i][:-1])
    
    fromdel = DelButton(0, addingframe, command=lambda: delfromemails("from"))
    todel = DelButton(1, addingframe, command=lambda: delfromemails("to"))
    

# Fonction effaçant tout

def clearall():
    fromentry.delete(0, "end"), fromentry.config(fg='grey'), fromentry.insert(0, fromentry.name), fromentry.icursor(0)
    toentry.delete(0, "end"), toentry.config(fg='grey'), toentry.insert(0, toentry.name), toentry.icursor(0)
    subentry.delete(0, "end"), subentry.config(fg='grey'), subentry.insert(0, subentry.name), subentry.icursor(0)
    msgentry.delete(1.0, "end")
    for element in range(len(enclosed)): deleteenclosed(0)

# Fonction pour ouvrir un fichier

def uploadenclosed():
    filename = filedialog.askopenfilename()
    if filename != "": enclosedlb.insert("end", filename), enclosed.append(filename)

def deleteenclosed(selection=True):
    if selection:
        try: selection = enclosedlb.curselection()[0]
        except IndexError: pass
    try:
        del enclosed[selection]
        enclosedlb.delete(selection)
    except IndexError: pass

def darktheme(_):
    txtcolor="white"
    print("a")

# Fermer la fenêtre

def close():
    App.destroy()

# Update

def update(_=None):
    size = 20 + 10*(App.winfo_width() - App.x)//67
    if size > 92: size = 92
    enclosedlb["width"] = size


# Informations sur le logiciel

title = "GmailXandR"
version = (1, 0, 0)
dev = "Elouan Lahougue"
url = "https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4NC8fkpRb8vwtzL9Ss5ycOasKqKDc7SAtqULeHdqe21fTNRIvPKOR2Fvunpr5h8ZHrTF1VjcQ0W9kAhrCHsr1Nwex74hQ"
txtcolor = "black"
enclosed = []


# Création de l'interface graphique et de son menu

App = AppWin("", 572, 386, version)
enclosedwidth = 20 + App.winfo_width() - App.x

mainmenu = tk.Menu(App)

file = tk.Menu(mainmenu, tearoff=0)
file.add_command(label="Clear all", command=clearall)
mainmenu.add_cascade(label="File", menu=file)

tools = tk.Menu(mainmenu, tearoff=0)
tools.add_command(label="E-mail adress manager", command=emailmgr)
mainmenu.add_cascade(label="Tools", menu=tools)


# Création du body

def fromenter(_): toentry.focus_set()
def toenter(_): subentry.focus_set()
def subenter(_): msgentry.focus_set()

def openurl(): webbrowser.open_new_tab(url)

# Widgets du body

globalmainframe = tk.Frame(App, width=App.x-10, height=App.y-10)
globalmainframe.pack(padx=6, pady=(6, 0))

topwin = tk.Frame(globalmainframe)
topwin.pack(padx=5)

fromtosub = tk.Frame(topwin)
fromtosub.grid(row=0, column=0, padx=(0, 4))

fromlabel = tk.Label(fromtosub, text="          @", fg=txtcolor)
fromentry = XEntry("From", 0, 0, fromtosub, bg="white", width=40, fg="grey")
emailbutton1 = EButton(0, fromtosub)
fromlabel.grid(row=0, column=0)

tolabel = tk.Label(fromtosub, text="          @", fg=txtcolor)
toentry = XEntry("To", 1, 2, fromtosub, bg="white", width=40, fg="grey")
emailbutton2 = EButton(1, fromtosub)
tolabel.grid(row=1, column=0)

sublabel = tk.Label(fromtosub, text="Subject")
subentry = XEntry("Subject", 2, -1, fromtosub, bg="white", width=40, fg="grey")
sublabel.grid(row=2, column=0, pady=2)

addanddelete = tk.Frame(fromtosub)
addanddelete.grid(row=2, column=2, padx=(2, 0))

plusbutton = ttk.Button(addanddelete, text="+", width=6, cursor="plus", command=uploadenclosed)
plusbutton.pack(side="left", padx=(0, 1))

moinsbutton = ttk.Button(addanddelete, text="-", width=6, command=deleteenclosed)
moinsbutton.pack(side="right", padx=(1, 0))

enclosedframe = tk.LabelFrame(topwin, text="Enclosed", width=160, height=76)
enclosedframe.grid(row=0, column=1, padx=(4, 0))

enclosedsb = tk.Scrollbar(enclosedframe)
enclosedsb.pack(side="right", fill="y")

enclosedlb = tk.Listbox(enclosedframe, yscrollcommand=enclosedsb.set, width=20, height=3)
enclosedlb.pack(side="right", fill="both", padx=(4, 0), pady=(0, 5))

enclosedsb.config(command=enclosedlb.yview)

bottombuttons = tk.Frame(globalmainframe)
bottombuttons.pack(side="bottom", pady=(1, 7))

msgentry = tks.ScrolledText(globalmainframe, bg="white", width=300, height=60)
msgentry.pack(pady=5)

closebutton = ttk.Button(bottombuttons, text="Close", command=close)
closebutton.pack(side="left")

sendbutton = ttk.Button(bottombuttons, text="Send", command=validation)
sendbutton.pack(side="right")


# Creation des bindings

fromentry.bind("<Return>", fromenter)
toentry.bind("<Return>", toenter)
subentry.bind("<Return>", subenter)
fromlabel.bind("<Button-1>", darktheme)
App.bind("<Configure>", update)

fromentry.focus_set()
App.config(menu=mainmenu), App.mainloop()
