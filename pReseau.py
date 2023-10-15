from tkinter import *
from tkinter import ttk
import ipaddress, re

#--------------------------------------- FONCTIONS ----------------------------------------
#CHANGER LA COULEUR DE FOND DE TOUS LES WIDGETS
def changeBackgroundColor(widget, couleur):
    if (type(widget).__name__ not in DONT_CHANGE_COLOR_WIDGET):widget.configure(bg=couleur)
    for child in widget.winfo_children():
        changeBackgroundColor(child, couleur)

# CHANGER D'UNE FRAME À L'AUTRE
def switchPage(nowFrame, nextFrame):
    nowFrame.pack_forget()
    nextFrame.pack()
    changeBackgroundColor(nextFrame, BACKGROUND_COLOR)

#AFFICHER/CACHER LE RÉSULTAT DE LA PREMIÈRE FONCTIONNALITÉ
def showResults(fields, wantToMask):
    if (wantToMask):
        for field in fields:
            fieldInfos = int(field.place_info()['x'])
            if fieldInfos < 10000 : field.place_configure(x=fieldInfos + 10000)
    else:
        for field in fields:
            fieldInfos = int(field.place_info()['x'])
            if fieldInfos >= 10000 : field.place_configure(x=fieldInfos - 10000)

#BLOQUER/DÉBLOQUER LE CHAMP DU MASQUE
def enableMasque(decoupe, txtMasque):
    if(decoupe.get()):
        txtMasque.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX)
    else: 
        txtMasque.delete("1.0", END)
        txtMasque.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

#EFFACER LES CHAMPS
def resetFields(fields, txtFieldsToBlock):
    for field in fields:
        #Si il s'agit d'une Textbox
        if (type(field).__name__ == "Text"):
           (Text) (field.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX))
           (Text) (field.delete("1.0", END))

        #Si il s'agit d'un Label
        if (type(field).__name__ == "Label"):
            (Label) (field.config(text=""))

        #Si il s'agit d'un Checkbutton
        if (type(field).__name__ == "BooleanVar"):
            (Checkbutton) (field.set(False))
    
    #Bloquer tous les fields présents dans la liste
    for field in txtFieldsToBlock:
        (Text) (field.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX))

#VÉRIFIER SI UNE ADRESSE IP EST CORRECTE
def checkAdresseIPValidity(adresseIP):
    regexIP= "^(?!127)(?:[1-9]|[01]?[0-9][0-9]|2[0-2][0-3])(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$"
    if(re.match(regexIP, adresseIP)):
        return True
    return False

#VÉRIFIER SI UN MASQUE EST CORRECTE
def checkMasqueValidity(masque):
    regexMasque= '^((255.){3}(0|128|192|224|240|248|252|254|255))|((255.){2}(0|128|192|224|240|248|252|254|255).0)|((255.)(0|128|192|224|240|248|252|254|255).0.0)|(0|128|192|224|240 248|252|254|255).0.0.0$'
    if(re.match(regexMasque, masque)):
        return True
    return False

def getMaskandClasse(adresse):
    #Récupérer la valeur du première octet de l'adresse IP
    premierOctet = int(adresse.split(".")[0])
    
    #Récupérer le masque et la classe
    if 1 <= premierOctet <= 126:     
        classe, masque = "Classe A", "255.0.0.0" 
    elif 128 <= premierOctet <= 191: 
        classe, masque = "Classe B", "255.255.0.0"
    elif 192 <= premierOctet <= 223: 
        classe, masque = "Classe C", "255.255.255.0"

    return masque, classe

#RÉCUPÉRER LES SOUS RÉSEAUX D'UN RÉSEAU
def getSousReseaux(adresseIP, masque):
    try:
        #Convertir l'adresse IP et le masque de sous-réseau en objets IPv4Network
        subnet = ipaddress.IPv4Network(f"{adresseIP}/{masque}", strict=False)

        #Adresse de sous-réseau
        subnet_address = subnet.network_address
        return subnet_address
    except ipaddress.AddressValueError as e:
        return f"Erreur : {e}"

#CHANGER LE LABEL DE LA FONCTIONNALITÉ 3
def changeLblTF():
    if(isNbSousReseau.get() == 1): lblNbRorHTF.config(text="Nombre de SR     :")
    else: lblNbRorHTF.config(text="Nombre d'hôtes   :")

def getBitAdresse(adresse, masque):
    #Convertir l'adresse IP et le masque de réseau en objets IPv4Network
    reseau = ipaddress.IPv4Network(adresse + '/' + masque, strict=False)
    
    #Récupérer le nombre de bits de notre masque de départ
    nbBits = reseau.prefixlen

    return nbBits

#DONNER LE NOMBRE DE SOUS-RÉSEAUX
def giveNbSousReseau(srVoulus, adresse, masque):
    #Variables
    nbSRs = 0
    n = 0
    nbBits = getBitAdresse(adresse, masque)
    
    #Boucle pour avoir le n et le nombre de SRs
    while(nbSRs < srVoulus):
        n += 1
        nbSRs = pow(2, n) - 1
        
        if((n + nbBits) >= 30):
            return nbSRs, n 
    
    return nbSRs, n

#RÉCUPÉRER LE NOMBRE D'HÔTES
def giveNbIPs(hotesVoulus, adresse, masque):
    #Variables
    nbHotes = 0
    n = 0
    nbBits = getBitAdresse(adresse, masque)
    
    #Boucle pour avoir le n et le nombre de SRs
    while(nbHotes < hotesVoulus):
        n += 1
        nbHotes = pow(2, n) - 2
        
        if((n + nbBits) >= 30):
            return nbHotes, n 
    
    return nbHotes, n

#CHANGER LE MASQUE DE RÉSEAU EN MASQUE DE SOUS-RÉSEAU
def changeMask(ip, masque, n):
    #Récupérer le nombre de bit du réseau
    nbBits = getBitAdresse(ip, masque)

    #Récupérer le nombre de bits total
    nbBits = nbBits + n

    if(nbBits <= 32):
        #Transformer le nombre de bits en masque
        masque_binaire = '1' * nbBits + '0' * (32 - nbBits)
        octets = [int(masque_binaire[i:i+8], 2) for i in range(0, 32, 8)]
        masque = '.'.join(map(str, octets))
    else:
        masque = "Error"

    #Retourner le masque
    return masque, nbBits

#CHANGER LE MASQUE DE RÉSEAU EN MASQUE DE SOUS-RÉSEAU
def changeMaskHote(ip, masque, n):
    #Récupérer le nombre de bit du réseau
    nbBits = getBitAdresse(ip, masque)

    #Récupérer le nombre de bits rajoutés
    nbBitsAdded = 32 - nbBits - n

    #Récupérer le nombre de bits total
    nbBits = 32 - n

    if(nbBits <= 32):
        #Transformer le nombre de bits en masque
        masque_binaire = '1' * nbBits + '0' * (32 - nbBits)
        octets = [int(masque_binaire[i:i+8], 2) for i in range(0, 32, 8)]
        masque = '.'.join(map(str, octets))
    else:
        masque = "Error"

    #Retourner le masque
    return masque, nbBits, nbBitsAdded

def getPas(masque):
    #Convertir le masque en binaire
    masqueBinaire = ''.join(format(int(octet), '08b') for octet in masque.split('.'))
    
    #Trouver l'index du bit le plus à droite ayant la valeur '1'
    indiceBit = masqueBinaire.rfind('1')

    #Donner le numéro de l'octet
    octet = int(indiceBit/8) + 1

    #Calculer la position du bit dans l'octet
    positionDansOctet = 7 - (indiceBit % 8)
    
    #Trouver la valeur du bit dans l'octet
    valeurOctet = 2 ** positionDansOctet

    print(octet, valeurOctet)

    #Retourner le pas
    return octet, valeurOctet

#DONNER TOUS LES DÉTAILS DES SRS
def giveDetails(adresseReaseau, masqueR, masqueSR, nbSRsTotal, nbSRsVoulus, nbBits, octet, valeurOctet, nbBitsAdded):
    #Afficher les titres
    print("SRs    -   Adresse Reseau")

    #Transformer l'adresse réseau (str) en Objet
    reseau = ipaddress.IPv4Network(adresseReaseau + '/' + masqueR, strict=False)

    #Récupérer la liste des sous-réseaux
    sousReseaux = list(reseau.subnets(new_prefix= nbBits))

    if(isNbSousReseau.get() == 2):
        nbSRsTotal = pow(2, nbBitsAdded) - 1

    #Déclarer la liste des données
    listeData = []

    for i in range(nbSRsTotal):
        numeroSR = i + 1
        adresseSR = ipaddress.IPv4Network(f"{sousReseaux[i]}", strict=False)
        adresseBroadCastSR = adresseSR.broadcast_address
        hostFirst = adresseSR.network_address + 1
        hostLast = adresseSR.broadcast_address - 1
        pas = f"{valeurOctet} sur {octet} ème octet" 
        nbMachines = 2 ** (32 - nbBits) - 2

        #Ajouter les données à la liste
        listeData.append([numeroSR, adresseSR, adresseBroadCastSR, hostFirst, hostLast, pas, nbMachines])
        tvListeReseauxTF.insert(parent='', index='end', values=listeData[-1])

        #Afficher les résultats
        #print(numeroSR, adresseSR, adresseBroadCastSR, hostFirst, hostLast, pas, nbMachines)

#VÉRIFIER (FONCTIONNALITÉ 1)
def checkValidityFF():
    #Déclaration & Initialisation des variables
    adresseIP = txtAdresseIPFF.get("1.0", "end-1c")

    #Vérifier que l'adresse IP encoder par l'utilisateur est juste
    if not(checkAdresseIPValidity(adresseIP)):
        lblValidityFF.config(text="IP INVALIDE !")
        showResults(fieldsToMask, True)
    else:

        masque, classe = getMaskandClasse(adresseIP)

        #Si l'utilisateur encode un masque
        if(isDecoupeFF.get()):

            #Récupérer le masque 
            masqueSR = txtMasqueFF.get('1.0', 'end-1c')
            masqueUsed = masqueSR

        else:
            masqueUsed = masque

        txtMasqueFF.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX)
        txtMasqueFF.delete("1.0", END)
        txtMasqueFF.insert(END, masqueUsed)

        #Remettre la textbox en disabled si l'utilisateur n'a pas coché "Découpe"
        if not(isDecoupeFF.get()):txtMasqueFF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

        #Afficher les résultats si l'adresse IP et le masque sont corrects
        if(checkAdresseIPValidity(adresseIP) and checkMasqueValidity(masqueUsed)):
            
            #Reset les fields
            #resetFields(fields, txtFieldsToBlock)
            showResults(fieldsToMask, True)

            if not(isDecoupeFF.get()):
                #Ajouter l'adresse Réseau
                reseau = ipaddress.IPv4Network(f"{adresseIP}/{masque}", strict=False).network_address
                lblAdresseReseauResultFF.config(text=reseau)

                #Ajouter l'adresse Broadcast
                broadcast =  ipaddress.IPv4Network(f"{adresseIP}/{masqueUsed}", strict=False).broadcast_address
                lblAdresseBroadCastResultFF.config(text=broadcast)

                #Afficher les résultats
                showResults(fieldsNoDecoupeFF, False)
                print(fieldsNoDecoupeFF)
            else:
                #Ajouter l'adresse de sous-réseaux
                sousReseaux = getSousReseaux(adresseIP, masqueUsed)
                lblAdresseSousReseauResultFF.config(text=sousReseaux)

                #Afficher les résultats
                showResults(fieldsDecoupeFF, False)
            
            lblValidityFF.config(text="")
        else:
            lblValidityFF.config(text="MASQUE INVALIDE !")
            showResults(fieldsToMask, True)

#VÉRIFIER (FONCTIONNALITÉ 2)
def checkValiditySF():
    #Déclaration & Initialisation des variables
    adresseIP = txtAdresseIPSF.get("1.0", "end-1c")
    adresseReseau = txtAdresseReseauSF.get("1.0", "end-1c")

    #Vérifier que l'adresse IP encoder par l'utilisateur est juste
    if not(checkAdresseIPValidity(adresseIP)):
        lblValiditySF.config(text="IP INVALIDE !", fg="red")
        showResults(fieldsToMask, True)
    else:
        if(checkAdresseIPValidity(adresseReseau)):
            masque, classe = getMaskandClasse(adresseIP)
            
            #Afficher le masque à l'utilisateur
            txtMasqueSF.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX)
            txtMasqueSF.delete("1.0", END)
            txtMasqueSF.insert(END, masque)
            txtMasqueSF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

            #Convertir l'adresse IP de départ en un objet IPv4Address
            try:
                #Convertissez les entrées en objets ipaddress.IPv4Address et ipaddress.IPv4Network
                ip = ipaddress.IPv4Address(adresseIP)
                network = ipaddress.IPv4Network(f"{adresseReseau}/{masque}", strict=False)

                if(adresseReseau == str(network).split("/")[0]):

                    #Vérifiez si l'adresse IP appartient à l'adresse réseau
                    if ip in network: 
                        lblValiditySF.config(text="L'ip appartient au réseau", fg="black")
                    else: 
                        lblValiditySF.config(text="L'ip n'appartient pas au réseau", fg="black")

                else: lblValiditySF.config(text="ADRESSE RESEAU INVALIDE !", fg="red")
            except ValueError as e: lblValiditySF.config(text=e, fg="red")
        
        else:
            lblValiditySF.config(text="ADRESSE RESEAU INVALIDE !", fg="red")

#VÉRIFIER (FONCTIONNALITÉ 3)
def checkValidityTF():
    #Déclaration & Initialisation des variables
    adresseIP = txtAdresseIPTF.get("1.0", "end-1c")
    
    #Vider les résultats
    tvListeReseauxTF.delete(*tvListeReseauxTF.get_children())

    if (txtNbRorHTF.get("1.0", "end-1c").isnumeric() and int(txtNbRorHTF.get("1.0", "end-1c")) > 0):
        nbSRorHote = int(txtNbRorHTF.get("1.0", "end-1c"))

        #Vérifier que l'adresse IP encoder par l'utilisateur est juste
        if not(checkAdresseIPValidity(adresseIP)):
            lblValidityTF.config(text="ADRESSE RESEAU INVALIDE !", fg="red")
        else:
            #Récupérer le masque et la classe
            masque, classe = getMaskandClasse(adresseIP)

            #Convertissez les entrées en objets ipaddress.IPv4Address et ipaddress.IPv4Network
            ip = ipaddress.IPv4Address(adresseIP)
            network = ipaddress.IPv4Network(f"{adresseIP}/{masque}", strict=False)

            if(str(ip) == str(network).split("/")[0]):
                #Reset le message d'erreur
                lblValidityTF.config(text="", fg="red")
                
                #Si c'est la découpe avec le nombre de sous-réseaux
                if(isNbSousReseau.get() == 1):
                    #Récupérer le nombre de SRs possible, ainsi que le n
                    nbSRsTotal, n = giveNbSousReseau(nbSRorHote, adresseIP, masque)

                    #Si l'utilisateur envoie une valeur trop grande
                    if (nbSRsTotal >= nbSRorHote):
                        #Récupérer le masque de SR
                        masqueSR, nbBits = changeMask(adresseIP, masque, n)

                        if not(masqueSR == "Error"):
                            #Récupérer le pas
                            octet, valeurOctet = getPas(masqueSR)

                            #Récupérer les détails des sous-réseaux
                            giveDetails(adresseIP, masque, masqueSR, nbSRsTotal, nbSRorHote, nbBits, octet, valeurOctet, 0)

                            #Afficher le masque à l'utilisateur
                            txtMasqueTF.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX)
                            txtMasqueTF.delete("1.0", END)
                            txtMasqueTF.insert(END, masque)
                            txtMasqueTF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)
                        else:
                            lblValidityTF.config(text=f"MASQUE INVALIDE ! (MAX : {nbSRsTotal})", fg="red")  
                    else:
                        lblValidityTF.config(text=f"NOMBRE DE SR TROP GRAND ! (MAX : {nbSRsTotal})", fg="red")  

                #Si c'est la découpe avec le nombre d'hôte
                else:
                    #Récupérer le nombre d'IPs possible, ainsi que le n
                    nbHotesTotal, n = giveNbIPs(nbSRorHote, adresseIP, masque)

                    #Si l'utilisateur envoie une valeur trop grande
                    if (nbHotesTotal >= nbSRorHote):
                        #Récupérer le masque de SR
                        masqueSR, nbBits, nbBitsAdded = changeMaskHote(adresseIP, masque, n)

                        if not(masqueSR == "Error"):
                            #Récupérer le pas
                            octet, valeurOctet = getPas(masqueSR)

                            #Récupérer les détails des sous-réseaux
                            giveDetails(adresseIP, masque, masqueSR, nbHotesTotal, nbSRorHote, nbBits, octet, valeurOctet, nbBitsAdded)

                            #Afficher le masque à l'utilisateur
                            txtMasqueTF.configure(state="normal", bg=ENEABLED_BG_COLOR_TEXTBOX)
                            txtMasqueTF.delete("1.0", END)
                            txtMasqueTF.insert(END, masque)
                            txtMasqueTF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)
                        else:
                            lblValidityTF.config(text=f"MASQUE INVALIDE ! (MAX : {nbSRsTotal})", fg="red") 
                    else:
                        lblValidityTF.config(text=f"NOMBRE D'HÔTE TROP GRAND ! (MAX : {nbHotesTotal})", fg="red") 
            else:
                lblValidityTF.config(text=f"ADRESSE RESEAU INVALIDE", fg="red")
    else:
        lblValidityTF.config(text=f"VALEUR D'HÔTE OU DE SOUS-RÉSEAU INVALIDE !", fg="red") 

#--------------------------------------- FONCTIONS ----------------------------------------


#--------------------------------------- CONSTANTES ---------------------------------------
DISABLED_BG_COLOR_TEXTBOX = "light gray"
ENEABLED_BG_COLOR_TEXTBOX = "white"
BACKGROUND_COLOR = "#009790"

FONT_POLICE = "Courier New"
FONT_COLOR = "#009790"
FONT_SIZE_TITLE = 50
FONT_SIZE_SUBTITLE = 35
FONT_SIZE_TEXT = 12
DONT_CHANGE_COLOR_WIDGET = ['Text', 'Scrollbar', 'Treeview', 'Button']
#--------------------------------------- CONSTANTES ---------------------------------------

#------------------------------------------ ROOT ------------------------------------------
#Gérer la fenêtre principal
root = Tk()
root.geometry("1320x820")
root.update()
root.title("Projet Réseaux")
root.configure(bg=BACKGROUND_COLOR)

#Récupération de certaines informations utiles
rootWidth = root.winfo_width()
rootHeight = root.winfo_height()
root.resizable(False, False)
#------------------------------------------ ROOT ------------------------------------------

#---------------------------------------- CONNEXION ---------------------------------------

#-----------------------------------------CONNEXION ---------------------------------------

#------------------------------------------ MENU ------------------------------------------
#Création du Menu
menuFrame =Frame(root, bg=BACKGROUND_COLOR)

#Création du label du Menu
lblMenu = Label(menuFrame, text="Menu", font=(FONT_POLICE, FONT_SIZE_TITLE))

#Création des différents boutons du Menu
btnOne = Button(menuFrame, text="Informations Réseaux", font=(FONT_POLICE, FONT_SIZE_TEXT), height=2, fg=FONT_COLOR, command=lambda: switchPage(menuFrame, firstFonctionnalityFrame))
btnTwo = Button(menuFrame, text="Vérification IP", font=(FONT_POLICE, FONT_SIZE_TEXT), height=2, fg=FONT_COLOR, command=lambda: switchPage(menuFrame, secondFonctionnalityFrame))
btnThree = Button(menuFrame, text="Informations Découpe", font=(FONT_POLICE, FONT_SIZE_TEXT), height=2, fg=FONT_COLOR, command=lambda: switchPage(menuFrame, thirdFonctionnalityFrame))
btnQuit = Button(menuFrame, text="Quitter", font=(FONT_POLICE, FONT_SIZE_TEXT), height=2, fg=FONT_COLOR, command=quit)

#Liste de boutons
widgets = [lblMenu, btnOne, btnTwo, btnThree, btnQuit]
for widget in widgets:
    widget.pack(pady=40, padx=400, fill="x", expand=True)

#Configuration de la menuFrame
menuFrame.pack()
menuFrame.pack_propagate(False)
menuFrame.configure(width=rootWidth, height=rootHeight)

#Changer la couleur de fond de tous les éléments présents dans mon applications
changeBackgroundColor(root, BACKGROUND_COLOR)
#------------------------------------------ MENU ------------------------------------------


#-------------------------------- PREMIERE FONCTIONNALITE ---------------------------------
#CRÉATION DE LA FRAME
firstFonctionnalityFrame =Frame(root, bg=BACKGROUND_COLOR)

#VARIABLES
isDecoupeFF = BooleanVar(value=False)

#TITRE
lblMenuFF = Label(firstFonctionnalityFrame, text="Informations Réseaux", font=(FONT_POLICE, FONT_SIZE_SUBTITLE))
lblMenuFF.place(x=rootWidth/3, y=30)

#INPUTS
lblAdresseIPFF = Label(firstFonctionnalityFrame, text="Adresse IP          :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseIPFF.place(x=200, y=200)
txtAdresseIPFF = Text(firstFonctionnalityFrame)
txtAdresseIPFF.place(x=340, y=200, width=rootWidth/3, height=20)

lblMasqueFF = Label(firstFonctionnalityFrame, text="Masque              :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblMasqueFF.place(x=200, y=275)
txtMasqueFF = Text(firstFonctionnalityFrame)
txtMasqueFF.place(x=340, y=275, width=rootWidth/3, height=20)
txtMasqueFF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

lblDecoupeFF = Label(firstFonctionnalityFrame, text="Découpe             :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblDecoupeFF.place(x=200, y=350)

chkDecoupeFF = Checkbutton(firstFonctionnalityFrame, variable=isDecoupeFF, command=lambda : enableMasque(isDecoupeFF, txtMasqueFF))
chkDecoupeFF.place(x=340, y=350)

lblValidityFF = Label(firstFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT), fg='red')
lblValidityFF.place(x=rootWidth/3, y=400, width=rootWidth/3)

#RÉSULTATS
lblAdresseReseauFF = Label(firstFonctionnalityFrame, text="Adresse Réseau        :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseReseauFF.place(x=200, y=450)
lblAdresseReseauResultFF = Label(firstFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseReseauResultFF.place(x=rootWidth/3, y=450)

lblAdresseBroadCastFF = Label(firstFonctionnalityFrame, text="Adresse Broadcast    :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseBroadCastFF.place(x=200, y=525)
lblAdresseBroadCastResultFF = Label(firstFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseBroadCastResultFF.place(x=rootWidth/3, y=525)

lblAdresseSousReseauFF = Label(firstFonctionnalityFrame, text="Sous-réseau              :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseSousReseauFF.place(x=200, y=600 )
lblAdresseSousReseauResultFF = Label(firstFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseSousReseauResultFF.place(x=rootWidth/3, y=600)

#CHAMPS À RESET
fieldsFF = [lblAdresseReseauResultFF, lblAdresseBroadCastResultFF, lblValidityFF, txtAdresseIPFF, isDecoupeFF, lblAdresseSousReseauResultFF, txtMasqueFF]
fieldsNoDecoupeFF = [lblAdresseReseauResultFF, lblAdresseBroadCastResultFF, lblAdresseReseauFF, lblAdresseBroadCastFF]
fieldsDecoupeFF = [lblAdresseSousReseauResultFF, lblAdresseSousReseauFF]
txtFieldsToBlockFF = [txtMasqueFF]

#CHAMP À MASQUER
fieldsToMask = [lblAdresseReseauResultFF, lblAdresseBroadCastResultFF, lblAdresseSousReseauResultFF, lblAdresseReseauFF, lblAdresseBroadCastFF, lblAdresseSousReseauFF]

#MASQUER LES RÉSULTATS AU DÉMARRAGE DE L'APPLICATION
showResults(fieldsToMask, True)

#BOUTONS RETOUR & VALIDER
btnBackFF = Button(firstFonctionnalityFrame, text="Back", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda: [switchPage(firstFonctionnalityFrame, menuFrame), resetFields(fieldsFF, txtFieldsToBlockFF), showResults(fieldsToMask, True)])
btnBackFF.place(x = 30, y=rootHeight - 50)

btnValiderFF = Button(firstFonctionnalityFrame, text="Valider", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda : checkValidityFF())
btnValiderFF.place(x=rootWidth/3, y=650, width=rootWidth/3)

#CONFIGURATION DE LA FRAME
firstFonctionnalityFrame.pack_propagate(False)
firstFonctionnalityFrame.configure(width=rootWidth, height=rootHeight)
#-------------------------------- PREMIERE FONCTIONNALITE ---------------------------------


#-------------------------------- DEUXIEME FONCTIONNALITE ---------------------------------
#CRÉATION DE LA FRAME
secondFonctionnalityFrame =Frame(root, bg=BACKGROUND_COLOR)

#TITRE
lblMenuSF = Label(secondFonctionnalityFrame, text="Vérification Réseaux", font=(FONT_POLICE, FONT_SIZE_SUBTITLE))
lblMenuSF.place(x=rootWidth/3, y=30, width=rootWidth/3)

#INPUTS
lblAdresseIPSF = Label(secondFonctionnalityFrame, text="Adresse IP            :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseIPSF.place(x=200, y=200)
txtAdresseIPSF = Text(secondFonctionnalityFrame)
txtAdresseIPSF.place(x=340, y=200, width=rootWidth/3, height=20)

lblAdresseReseauSF = Label(secondFonctionnalityFrame, text="Adresse Réseau :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseReseauSF.place(x=200, y=275)
txtAdresseReseauSF = Text(secondFonctionnalityFrame)
txtAdresseReseauSF.place(x=340, y=275, width=rootWidth/3, height=20)

lblMasqueSF = Label(secondFonctionnalityFrame, text="Masque              :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblMasqueSF.place(x=200, y=350)
txtMasqueSF = Text(secondFonctionnalityFrame)
txtMasqueSF.place(x=340, y=350, width=rootWidth/3, height=20)
txtMasqueSF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

lblValiditySF = Label(secondFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT), fg='red')
lblValiditySF.place(x=rootWidth/3, y=425, width=rootWidth/3)

#BOUTONS RETOUR & VALIDER
btnBackSF = Button(secondFonctionnalityFrame, text="Back", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda: switchPage(secondFonctionnalityFrame, menuFrame))
btnBackSF.place(x = 30, y=rootHeight - 50)

btnValiderSF = Button(secondFonctionnalityFrame, text="Valider", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda: [checkValiditySF()])
btnValiderSF.place(x=rootWidth/3, y=650, width=rootWidth/3)

#CONFIGURATION DE LA FRAME
secondFonctionnalityFrame.pack_propagate(False)
secondFonctionnalityFrame.configure(width=rootWidth, height=rootHeight)
#-------------------------------- DEUXIEME FONCTIONNALITE ---------------------------------

#-------------------------------- TROISIEME FONCTIONNALITE --------------------------------
#CRÉATION DE LA FRAME
thirdFonctionnalityFrame =Frame(root, bg=BACKGROUND_COLOR)

#VARIABLES
isNbSousReseau = IntVar(value=1)

#TITRE
lblMenuTF = Label(thirdFonctionnalityFrame, text="Découpe Réseaux", font=(FONT_POLICE, FONT_SIZE_SUBTITLE))
lblMenuTF.place(x=rootWidth/3, y=30, width=rootWidth/3)

#INPUTS
lblAdresseIPTF = Label(thirdFonctionnalityFrame, text="Adresse IP            :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblAdresseIPTF.place(x=200, y=200)
txtAdresseIPTF = Text(thirdFonctionnalityFrame)
txtAdresseIPTF.insert(END, "50.0.0.0")
txtAdresseIPTF.place(x=340, y=200, width=rootWidth/3, height=20)

lblNbRorHTF = Label(thirdFonctionnalityFrame, text="Nombre de SR     :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblNbRorHTF.place(x=200, y=275)
txtNbRorHTF = Text(thirdFonctionnalityFrame)
txtNbRorHTF.insert(END, 15)
txtNbRorHTF.place(x=340, y=275, width=rootWidth/3, height=20)

lblSRTF = Label(thirdFonctionnalityFrame, text="Nb. SR", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblSRTF.place(x=750, y=275)
chkSRTF = Radiobutton(thirdFonctionnalityFrame, variable=isNbSousReseau, value=1, command= lambda: changeLblTF())
chkSRTF.place(x=825, y=275)

lblHoteTF = Label(thirdFonctionnalityFrame, text="Nb. Hôte", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblHoteTF.place(x=950, y=275)
chkHoteTF = Radiobutton(thirdFonctionnalityFrame, variable=isNbSousReseau, value=2, command= lambda: changeLblTF())
chkHoteTF.place(x=875, y=275)

lblMasqueTF = Label(thirdFonctionnalityFrame, text="Masque                 :", font=(FONT_POLICE, FONT_SIZE_TEXT))
lblMasqueTF.place(x=200, y=350)
txtMasqueTF = Text(thirdFonctionnalityFrame)
txtMasqueTF.place(x=340, y=350, width=rootWidth/3, height=20)
txtMasqueTF.configure(state="disabled", bg=DISABLED_BG_COLOR_TEXTBOX)

lblValidityTF = Label(thirdFonctionnalityFrame, text="", font=(FONT_POLICE, FONT_SIZE_TEXT), fg='red')
lblValidityTF.place(x=rootWidth/3, y=400)

#RÉSULTATS
listeHead = ['Nb.', 'Adresse SR', 'Adresse BC', '1er IP', 'Dern. IP', 'Pas', 'Nb. Hotes']

tvListeReseauxTF = ttk.Treeview(thirdFonctionnalityFrame, columns=listeHead)
tvListeReseauxTF.column('#0', stretch=NO, width=0)
for col in listeHead:
    tvListeReseauxTF.heading(col, text=col)
    tvListeReseauxTF.column(col, width='100', anchor='center')

#Création d'une scrollbar
vsb = ttk.Scrollbar(thirdFonctionnalityFrame, orient="vertical", command=tvListeReseauxTF.yview)
vsb.place(x=900, y=450, height=150)
tvListeReseauxTF.configure(yscrollcommand=vsb.set)

tvListeReseauxTF.place(x=100, y=450, width=800, height=150)

#BOUTONS RETOUR & VALIDER
btnBackTF = Button(thirdFonctionnalityFrame, text="Back", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda: switchPage(thirdFonctionnalityFrame, menuFrame))
btnBackTF.place(x = 30, y=rootHeight - 50)

btnValiderTF = Button(thirdFonctionnalityFrame, text="Valider", font=(FONT_POLICE, FONT_SIZE_TEXT), fg=FONT_COLOR, command=lambda: [checkValidityTF()])
btnValiderTF.place(x=rootWidth/3, y=650, width=rootWidth/3)

#CONFIGURATION DE LA FRAME
thirdFonctionnalityFrame.pack_propagate(False)
thirdFonctionnalityFrame.configure(width=rootWidth, height=rootHeight)
#-------------------------------- TROISIEME FONCTIONNALITE --------------------------------

#Run
root.mainloop()