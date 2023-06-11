
import json

def ecrireFichier(cheminVersDossier, num_routeur, num_as, num_routeur_as, liensExt):
    chemin = cheminVersDossier+"/i"+str(num_routeur)+"_startup-config.cfg"
    file = open(chemin, "w")
    ecrireConfig(num_routeur, file, num_as, num_routeur_as, liensExt)
    file.close()


def ecrireConfig(num_routeur, file, num_as, num_routeur_as, liensExt): 

    protocole = obj_python["AS"][num_as]["routage_protocol"]
    nomRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["id"]
    typeRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["type"]
    utilRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["utilisation"]

    file.write("!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec  \n! \nhostname "
               + nomRouteur + "\n" 
               + "!                                     \n"
               + "boot-start-marker                     \n"
               + "boot-end-marker                       \n"
               + "!                                     \n"
               + "no aaa new-model                      \n"
               + "no ip icmp rate-limit unreachable     \n"
               + "ip cef                                \n"
               + "!                                     \n"
               + declareClient(nomRouteur)
               +"\n!\n"
               + "no ip domain lookup                   \n"
               + "no ipv6 cef                           \n" 
               + "!                                     \n"
               + "multilink bundle-name authenticated   \n"
               + "!                                     \n"
               + "ip tcp synwait-time 5                 \n"
               + "!                                     \n"

               + adressageLoopback(num_routeur_as, num_as)

               + "\n!\ninterface FastEthernet0/0" 
               + forwardingClient(num_routeur, "FastEthernet0/0")
               + adressage(num_routeur, "FastEthernet0/0", num_as, nomRouteur)

               + "\n!\ninterface GigabitEthernet1/0"
               +forwardingClient(num_routeur, "GigabitEthernet1/0")
               + adressage(num_routeur, "GigabitEthernet1/0", num_as, nomRouteur)
            
               + "\n!\ninterface GigabitEthernet2/0"
               +forwardingClient(num_routeur, "GigabitEthernet2/0")
               + adressage(num_routeur, "GigabitEthernet2/0", num_as, nomRouteur)
               
               + "\n!\ninterface GigabitEthernet3/0"
               +forwardingClient(num_routeur, "GigabitEthernet3/0")
               + adressage(num_routeur,"GigabitEthernet3/0", num_as, nomRouteur)
               
               + "\n!\ninterface GigabitEthernet4/0"
               +forwardingClient(num_routeur, "GigabitEthernet4/0")
               + adressage(num_routeur,"GigabitEthernet4/0", num_as, nomRouteur)
                

               + "\n!\n"

               # bgp
               + configBGP(num_routeur, num_as, typeRouteur, num_routeur_as, utilRouteur, liensExt)
               + ecrireProtocole(protocole, nomRouteur)
               + "!\n"
               + "ip forward-protocol nd\n"
               + "!\n"
               + setIPCommunity(num_routeur)
               + "!\n"
               + "no ip http server\n"
               + "no ip http secure-server\n"
               + "!\n"
               + ecrireRouteMap(num_routeur)
             
            #    + "!\n"
            #    + ecrireMapEtACL(nomRouteur)
            #     +ecrireComm(num_as,nomRouteur)
               +"!\n"
               + "control-plane\n"
               + "!\n"
               + "line con 0\n"
               + " exec-timeout 0 0\n"
               + " privilege level 15\n"
               + " logging synchronous\n"
               + " stopbits 1\n"
               + "line aux 0\n"
               + " exec-timeout 0 0\n"
               + " privilege level 15\n"
               + " logging synchronous\n"
               + " stopbits 1\n"
               + "line vty 0 4\n"
               + " login\n"
               + "!\n"
               + "!\n"
               + "end\n"

               )


def declareClient(num_routeur): # voir commentaire
    res="!"
    numClient=0
    num_as_client=0
    premiereLigne=True 
    numeroClient = ""
    nomClient = ""
    nomClientPrecedent = ""

    for i in range(len(obj_python["connexion"]["relations"])): 
        if num_routeur ==  obj_python["connexion"]["relations"][i]["idPE"]: 
            numClient = int(obj_python["connexion"]["relations"][i]["client"][1:])
            nomClient = obj_python["connexion"]["relations"][i]["nomClient"]

            if nomClient != nomClientPrecedent :
                premiereLigne=True

            for router in range(len(obj_python["connexion"]["routeurs"])):
                if numClient == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_client = obj_python["connexion"]["routeurs"][router]["as"]
                    numeroClient = obj_python["connexion"]["routeurs"][router]["numClient"]
                    for k in range(len(obj_python["connexion"]["routeurs"][router]["dest"])):
                        if num_routeur == obj_python["connexion"]["routeurs"][router]["dest"][k]:
                            numeroClient = obj_python["connexion"]["routeurs"][router]["rd"]                          

            if premiereLigne: 
                res =res+ "\n!\nip vrf "+ obj_python["connexion"]["relations"][i]["nomClient"]+"\n" #est ce que on peut pas mettre direct nomClient ?
                premiereLigne=False
                res = res+" rd "+str(num_as_client)+":123"+"\n route-target export "+str(num_as_client)+":"+numeroClient

            
            res=res+"\n route-target import "+str(obj_python["connexion"]["relations"][i]["asImport"])+":"+str(obj_python["connexion"]["relations"][i]["numImport"])
           

            nomClientPrecedent = nomClient

    return res


def adressageLoopback(num_routeur_as, num_as): # est ce que on peut pas mettre ospf numAS pour adapter à chaque as ?

    protocole = "" 
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ip ospf 123 area 0"
        return "interface Loopback0\n" + " ip address " + obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"] + " 255.255.255.255\n"  + protocole

    return "interface Loopback0\n" + " ip address " + obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"] + " 255.255.255.255" 


def forwardingClient(num_routeur, interface):
    num_as_voisin = 0
    num_voisin = 0

    for n in range(len(obj_python["connexion"]["connections"])):
        tmp="" 
        if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:])and obj_python["connexion"]["connections"][n]["relation2"]=="client"and interface==obj_python["connexion"]["connections"][n]["interface1"]:
            num_voisin = int(obj_python["connexion"]["connections"][n]["id2"][1:])
            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

                    num = 0;
                    for i in range( len(obj_python["AS"])):
                        if num_as_voisin == obj_python["AS"][i]["numeroAS"]:
                            num = i

                    return "\n ip vrf forwarding "+str(obj_python["AS"][num]["nomClient"])


        if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:])and obj_python["connexion"]["connections"][n]["relation1"]=="client" and interface==obj_python["connexion"]["connections"][n]["interface2"]:
            num_voisin = int(obj_python["connexion"]["connections"][n]["id1"][1:])
            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

                    num = 0;
                    for i in range( len(obj_python["AS"])):
                        if num_as_voisin == obj_python["AS"][i]["numeroAS"]:
                            num = i

                    return "\n ip vrf forwarding "+str(obj_python["AS"][num]["nomClient"])

    return ""


def adressage(num_routeur_as, interface, num_as, nomRouteur):

    res = ""
    num_routeur1 = num_routeur_as 
    protocole = ""
    vitesse= " negotiation auto"
    if  interface == "FastEthernet0/0":
        vitesse = " duplex full"

    address = obj_python["AS"][num_as]["prefix"]+"."

    #determiner protocole 
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ip ospf 123 area 0\n mpls ip"


    # pour les routeurs de bordure
    for n in range(len(obj_python["connexion"]["connections"])):
        if nomRouteur == obj_python["connexion"]["connections"][n]["id1"] and interface == obj_python["connexion"]["connections"][n]["interface1"]: 
            num_routeur2 = int(obj_python["connexion"]["connections"][n]["id2"][1:])
            address = address+str(liensExt[num_routeur1][num_routeur2])+ "."+\
                str(num_routeur1)+" 255.255.255.0"
            return " \n"+vitesse+"\n"+" ip address "+address

        elif nomRouteur == obj_python["connexion"]["connections"][n]["id2"] and interface == obj_python["connexion"]["connections"][n]["interface2"]: 
            num_routeur2 = int(obj_python["connexion"]["connections"][n]["id1"][1:])
            address = address+str(liensExt[num_routeur1][num_routeur2]) + "."+\
               str(num_routeur1)+" 255.255.255.0"
            return " \n"+vitesse+"\n"+" ip address "+address


    # pour le reste des routeurs
    address = obj_python["AS"][num_as]["prefix"]+"."
    if(len(obj_python["AS"][num_as]["connections"])>0):
        for i in range(len(obj_python["AS"][num_as]["connections"])):
            if nomRouteur == obj_python["AS"][num_as]["connections"][i]["id1"] and interface == obj_python["AS"][num_as]["connections"][i]["interface1"]:
                num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id2"][1:])
                address = address + str(lan[num_routeur1][num_routeur2])+"."+str(num_routeur1)+" 255.255.255.0"
                return " \n"+" ip address "+address+"\n"+protocole+"\n"+vitesse

            elif nomRouteur == obj_python["AS"][num_as]["connections"][i]["id2"] and interface == obj_python["AS"][num_as]["connections"][i]["interface2"]:
                num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id1"][1:])
                address = address +str(lan[num_routeur1][num_routeur2])+"."+str(num_routeur1)+" 255.255.255.0"
                return  " \n"+" ip address "+address+"\n"+protocole+"\n"+vitesse

        return  "\n no ip address\n shutdown\n"+vitesse

    else: 

        return  "\n no ip address\n shutdown\n"+vitesse
       

    return res


#ecrire bgp
def configBGP(num_routeur, num_as, typeRouteur, num_routeur_as, utilRouteur, liensExt):


    if(typeRouteur=="bordure" ):

        relation1 = ""
        relation2 = ""
        num_as_voisin=""
        strAddressFam = "" 
        loopbackProvider=""
        adresse=""
        set_map=""
        AS = str(obj_python["AS"][num_as]["numeroAS"])

        nombre_clients = 0
       
        res =   ("router bgp "+AS+"\n"
                   + " bgp router-id "+str(num_routeur)+"."+str(num_routeur)+"."+str(num_routeur)+"."+str(num_routeur)+"\n"
                   + " bgp log-neighbor-changes\n" )
      
        for n in range(len(obj_python["connexion"]["connections"])):
            if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:]):
                num_voisin = int(obj_python["connexion"]["connections"][n]["id2"][1:])
                relation1 = obj_python["connexion"]["connections"][n]["relation1"]

                for router in range(len(obj_python["connexion"]["routeurs"])):
                    if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                        num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

                if relation1 == "client":
                    adresse = obj_python["connexion"]["prefix"] + "." +str(liensExt[num_routeur][num_voisin])+"."
                    res = res + " neighbor "+ adresse + str(num_voisin) + " remote-as "+str(num_as_voisin)+"\n"
                    strAddressFam=strAddressFam + "  neighbor "+ adresse + str(num_voisin) + " activate\n"


                if relation1 == "provider":
                    nombre_clients = nombre_clients + 1

        
            if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:]):
                num_voisin = int(obj_python["connexion"]["connections"][n]["id1"][1:])
                relation2 = obj_python["connexion"]["connections"][n]["relation2"]

                for router in range(len(obj_python["connexion"]["routeurs"])):
                    if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                        num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

                if relation2 == "client":
                    adresse = obj_python["connexion"]["prefix"] + "." + str(liensExt[num_routeur][num_voisin])+"."
                    res = res + " neighbor "+ adresse + str(num_voisin) +" remote-as "+str(num_as_voisin)+"\n"
                    strAddressFam = strAddressFam + "  neighbor "+ adresse + str(num_voisin) + " activate\n"

                if relation2 == "provider":
                    nombre_clients = nombre_clients + 1

        #Router Provider 
        if nombre_clients>0 and utilRouteur== "default":

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:] 

                if ((adresse != str(num_routeur))and(obj_python["AS"][num_as]["routeurs"][i]["type"]=="bordure") and (obj_python["AS"][num_as]["routeurs"][i]["utilisation"] == "default")):
                    res= res + " neighbor 10.0.0."+adresse+" remote-as "+AS+"\n"+ " neighbor 10.0.0."+adresse+" update-source Loopback0\n"

            res = (res  + " !\n"
                        + " address-family vpnv4\n" )
         

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:]

                if (adresse != str(num_routeur) and (obj_python["AS"][num_as]["routeurs"][i]["type"]=="bordure")  and (obj_python["AS"][num_as]["routeurs"][i]["utilisation"] == "default")):
                    res = res + "  neighbor 10.0.0."+adresse+" activate\n  neighbor 10.0.0."+adresse+" send-community both\n"

            set_map = setMap(num_routeur, liensExt)
            
            if set_map != "":
                res = res + " "+set_map

            vrf = configVRF(num_routeur, nombre_clients,utilRouteur)
            res = res + " exit-address-family\n !\n"+vrf


        if nombre_clients > 0 and utilRouteur== "backup":   
            
            for j in range(len(obj_python["AS"][num_as]["routeurs"][num_routeur_as]["destination"])):
                adresse = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["destination"][j][1:] 
                res= res + " neighbor 10.0.0."+adresse+" remote-as "+AS+"\n"+ " neighbor 10.0.0."+adresse+" update-source Loopback0\n"
                res = res + setMap(num_routeur, liensExt)

            res = (res  + " !\n"
                + " address-family vpnv4\n" )

            for j in range(len(obj_python["AS"][num_as]["routeurs"][num_routeur_as]["destination"])):
                adresse = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["destination"][j][1:] 
                res = res + "  neighbor 10.0.0."+adresse+" activate\n  neighbor 10.0.0."+adresse+" send-community both\n"
           
            vrf = configVRF(num_routeur, nombre_clients, utilRouteur)
            res = res + " exit-address-family\n !\n"+vrf

        # Pour le client
        if obj_python["AS"][num_as]["nomClient"]!="":
            set_map= setMap(num_routeur, liensExt)
            res= res + " !\n address-family ipv4\n  network "+ obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"]+" mask 255.255.255.255\n" + strAddressFam
            if set_map != "":          
                res = res+"  "+ set_map
            
            res = res +" exit-address-family\n" 

        return res

    return "" 


def ecrireProtocole(protocole, nomRouteur): 
    if protocole == "OSPF":
        n = str(nomRouteur[1:])
        routeurID = n+"."+n+"."+n+"."+n
        return "router ospf 123\n router-id "+routeurID+"\n"

    return ""


def setIPCommunity(num_routeur) :

    nom = ""
    action = ""
    standard = ""
    community = ""
    res = ""

    for i in range(len(obj_python["filtre"])):
        for j in range(len(obj_python["filtre"][i]["routeurs"])):
            if num_routeur == int(obj_python["filtre"][i]["routeurs"][j][1:]) :
                for k in range(len(obj_python["filtre"][i]["configurations"])):
                    if obj_python["filtre"][i]["configurations"][k]["type"] == "community-list":
                        standard = obj_python["filtre"][i]["configurations"][k]["entrées"]["standard"]
                        if standard == "true":
                            nom = obj_python["filtre"][i]["configurations"][k]["nom"]
                            action = obj_python["filtre"][i]["configurations"][k]["entrées"]["action"]                           
                            community = obj_python["filtre"][i]["configurations"][k]["entrées"]["community"]
                            
                            res = res + "ip community-list standard "+ nom +" "+ action +" "+ community +"\n"
    return res


def ecrireRouteMap(num_routeur):

    nom = ""
    sequence = ""
    action = ""
    match_community = ""
    setLocalPref = ""
    setCommunity = ""
    res = ""

    for i in range(len(obj_python["filtre"])):
        for j in range(len(obj_python["filtre"][i]["routeurs"])):
            if num_routeur == int(obj_python["filtre"][i]["routeurs"][j][1:]) :
                for k in range(len(obj_python["filtre"][i]["configurations"])):
                    if obj_python["filtre"][i]["configurations"][k]["type"] == "route-map":
                        nom = obj_python["filtre"][i]["configurations"][k]["nom"]
                        for conf in range(len(obj_python["filtre"][i]["configurations"][k]["entrées"])):
                            sequence = obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["sequence"]
                            action = obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["action"]
                            
                            res = res + "route-map "+ nom + " " + action + " " + sequence

                            if obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["match"] != "":
                                match_community = obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["match"]["community"]
                                if match_community !="":
                                    res = res + "\n match community " + match_community

                            if obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["set"] != "":
                                setLocalPref = obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["set"]["local-preference"]
                                setCommunity = obj_python["filtre"][i]["configurations"][k]["entrées"][conf]["set"]["community"]
                                if setLocalPref != "":
                                    res = res + "\n set local-preference "+setLocalPref
                                if setCommunity != "":
                                    res = res + "\n set community " + setCommunity 
                            res = res + "\n!\n"                    
                            
    return res


def setMap(num_routeur, liensExt):
    res=""
    nom = ""
    dest = 0
    lien = 0
    sortie = ""

    for i in range(len(obj_python["filtre"])):
        for j in range(len(obj_python["filtre"][i]["routeurs"])):
            if num_routeur == int(obj_python["filtre"][i]["routeurs"][j][1:]) :
                for k in range(len(obj_python["filtre"][i]["configurations"])):
                    if obj_python["filtre"][i]["configurations"][k]["type"] == "send-community":
                        dest = int(obj_python["filtre"][i]["configurations"][k]["dest"][1:])
                        prefixe = obj_python["filtre"][i]["configurations"][k]["prefixe"]
                        numLan = liensExt[num_routeur][dest]
                        
                        res = res + "neighbor "+prefixe+str(numLan)+"."+str(dest)+ " send-community\n "
                    
                    if obj_python["filtre"][i]["configurations"][k]["type"] == "route-map":
                        nom = obj_python["filtre"][i]["configurations"][k]["nom"]
                        dest = int(obj_python["filtre"][i]["configurations"][k]["dest"][1:])
                        sortie = obj_python["filtre"][i]["configurations"][k]["sortie"]
                        lien = int(obj_python["filtre"][i]["configurations"][k]["lien"][1:])
                        prefixe = obj_python["filtre"][i]["configurations"][k]["prefixe"]
                        numLan = liensExt[dest][lien]

                        res = res + " neighbor "+ prefixe + str(numLan) +"." +str(dest)+ " route-map " +nom+" "+sortie+"\n"
    return res


def configVRF (num_routeur, nbclient, utilRouteur):
    res=""
    tmp=""
    nomClient = ""
    num_as_voisin=0
    num_voisin=0

    client = False 
    count = 0


    for n in range(len(obj_python["connexion"]["connections"])):
        address = obj_python["connexion"]["prefix"]
        tmp=""
        client=False

        if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:])and obj_python["connexion"]["connections"][n]["relation2"]=="client":
            client = True
            count = count+1
            num_voisin = int(obj_python["connexion"]["connections"][n]["id2"][1:])
            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]


        if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:])and obj_python["connexion"]["connections"][n]["relation1"]=="client":
            client = True
            count = count+1
            num_voisin = int(obj_python["connexion"]["connections"][n]["id1"][1:])
            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

        lan = str(liensExt[num_routeur][num_voisin])
        address = address +"." + lan +"."+ str(num_voisin)

        if client :
            tmp = tmp+"  neighbor "+ address  + " remote-as "+str(num_as_voisin)+"\n"
            tmp = tmp+"  neighbor "+ address  + " activate\n"

            num = 0;
            for i in range( len(obj_python["AS"])):
                if num_as_voisin == obj_python["AS"][i]["numeroAS"]:
                    num = i
      
            if count < nbclient:
                nomClient = obj_python["AS"][num]["nomClient"]

                res = res+" address-family ipv4 vrf "+str(obj_python["AS"][num]["nomClient"])+"\n"+ tmp 

                # ne marche que dans ce cas particulier
                if utilRouteur == "backup":
                    res = res + " " + setMap(num_routeur, liensExt) 

                res = res + " exit-address-family\n !\n"
            else:
                res = res+" address-family ipv4 vrf "+str(obj_python["AS"][num]["nomClient"])+"\n"+ tmp 
                # ne marche que dans ce cas particulier
                if utilRouteur == "backup":
                    res = res + " " + setMap(num_routeur, liensExt) 

                res = res + " exit-address-family\n!\n"

    return res


if __name__ == "__main__":

    fileObject = open("config.json", "r")
    jsonContent = fileObject.read()
    obj_python = json.loads(jsonContent)

    lenTabConnexion = len(obj_python["connexion"]["connections"]) 
    
    length=0
    for  i in range(len(obj_python["AS"])):
        length = length + len(obj_python["AS"][i]["routeurs"])
    length = length+1
    
    
    lan = [[0 for i in range(length)] for i in range(length)]
    x = 1

    for a in range(len(obj_python["AS"])):
        for i in range(length):
            for j in range(i+1,length): 
                for k in range(len(obj_python["AS"][a]["connections"])):
                    if i == int(obj_python["AS"][a]["connections"][k]["id1"][1:]) and j == int(obj_python["AS"][a]["connections"][k]["id2"][1:]):
                        lan[i][j] = x
                        lan[j][i] = x
                        x = x+1

                    if j == int(obj_python["AS"][a]["connections"][k]["id1"][1:]) and i == int(obj_python["AS"][a]["connections"][k]["id2"][1:]):
                        lan[i][j] = x
                        lan[j][i] = x
                        x = x+1

    liensExt = [[0 for i in range(length)] for i in range(length)]
    x=4
 
    for i in range(length):
        for j in range(i+1,length): 
            for k in range(lenTabConnexion):
                if i == int(obj_python["connexion"]["connections"][k]["id1"][1:]) and j == int(obj_python["connexion"]["connections"][k]["id2"][1:]):
                    liensExt[i][j] = x
                    liensExt[j][i] = x
                    x = x+1

                if j == int(obj_python["connexion"]["connections"][k]["id1"][1:]) and i == int(obj_python["connexion"]["connections"][k]["id2"][1:]):
                    liensExt[i][j] = x
                    liensExt[j][i] = x
                    x = x+1
 
    for a in range(len(obj_python["AS"])):
        for i in range(len(obj_python["AS"][a]["routeurs"])):
            num_routeur = int(obj_python["AS"][a]["routeurs"][i]["id"][1:])
            ecrireFichier("./configs générées", num_routeur, a, i, liensExt)
            
            
