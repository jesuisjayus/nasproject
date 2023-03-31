
import json

def ecrireFichier(cheminVersDossier, num_routeur, num_as, num_routeur_as):
    chemin = cheminVersDossier+"/i"+str(num_routeur)+"_startup-config.cfg"
    file = open(chemin, "w")
    ecrireConfig(num_routeur, file, num_as, num_routeur_as)
    file.close()



def ecrireProtocole(protocole, nomRouteur): 
    if protocole == "OSPF":
        n = str(nomRouteur[1:])
        routeurID = n+"."+n+"."+n+"."+n
        return "router ospf 123\n router-id "+routeurID+"\n"

    return ""


def adressage(num_routeur_as, interface, num_as, nomRouteur):

    res = ""
    num_routeur1 = num_routeur_as
    address = ""
    protocole = ""
    vitesse= " negotiation auto"


    #determiner protocole 
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ip ospf 123 area 0\n mpls ip"



    # pour les routeurs de bordure
    for n in range(len(obj_python["connexion"]["connections"])):
        if nomRouteur == obj_python["connexion"]["connections"][n]["id1"] and interface == obj_python["connexion"]["connections"][n]["interface1"]: 
            address = obj_python["connexion"]["connections"][n]["address"] + \
                str(num_routeur1)+" 255.255.255.0"
            return " \n"+vitesse+"\n"+" ip address "+address

        elif nomRouteur == obj_python["connexion"]["connections"][n]["id2"] and interface == obj_python["connexion"]["connections"][n]["interface2"]: 
            address = obj_python["connexion"]["connections"][n]["address"] + \
               str(num_routeur1)+" 255.255.255.0"
            return " \n"+vitesse+"\n"+" ip address "+address




    # pour le reste des routeurs
    if(len(obj_python["AS"][num_as]["connections"])>0):
        for i in range(len(obj_python["AS"][num_as]["connections"])):
 
            if nomRouteur == obj_python["AS"][num_as]["connections"][i]["id1"] and interface == obj_python["AS"][num_as]["connections"][i]["interface1"]:

                num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id2"][1:])
                address = obj_python["AS"][num_as]["prefix"] +"." +\
                    str(lan[num_routeur1][num_routeur2])
                
                if  interface == "FastEthernet0/0":
                    vitesse = " duplex full"

                address = address+"."+str(num_routeur1)+" 255.255.255.0"
                return " \n"+" ip address "+address+"\n"+protocole+"\n"+vitesse

            elif nomRouteur == obj_python["AS"][num_as]["connections"][i]["id2"] and interface == obj_python["AS"][num_as]["connections"][i]["interface2"]:
 
                num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id1"][1:])
                address = obj_python["AS"][num_as]["prefix"] +"." + \
                    str(lan[num_routeur1][num_routeur2])

                if  interface == "FastEthernet0/0":
                    vitesse = " duplex full"

                address = address+"."+str(num_routeur1)+" 255.255.255.0"
                return  " \n"+" ip address "+address+"\n"+protocole+"\n"+vitesse

        return  "\n no ip address\n shutdown\n"+vitesse

    else: 
        if  interface == "FastEthernet0/0":
            vitesse = " duplex full"

        return  "\n no ip address\n shutdown\n"+vitesse
       

    return res




def adressageLoopback(num_routeur_as, num_as):

    protocole = "" 
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ip ospf 123 area 0"
        return "interface Loopback0\n" + " ip address " + obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"] + " 255.255.255.255\n"  + protocole

    return "interface Loopback0\n" + " ip address " + obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"] + " 255.255.255.255" 




#ecrire bgp
def configBGP(num_routeur, num_as, typeRouteur, num_routeur_as):


    if(typeRouteur=="bordure"):

        relation1 = ""
        relation2 = ""
        num_as_voisin=""
        strAddressFam = "" 
        loopbackProvider=""
        adresse=""
        AS = str(obj_python["AS"][num_as]["numeroAS"])
       
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
                    res = res + " neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" remote-as "+str(num_as_voisin)+"\n"
                    strAddressFam=strAddressFam + "  neighbor "+obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+ " activate\n"





            if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:]):
                num_voisin = int(obj_python["connexion"]["connections"][n]["id1"][1:])
                relation2 = obj_python["connexion"]["connections"][n]["relation2"]

                for router in range(len(obj_python["connexion"]["routeurs"])):
                    if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                        num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]

                if relation2 == "client":
                    res = res + " neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" remote-as "+str(num_as_voisin)+"\n"
                    strAddressFam = strAddressFam + "  neighbor "+obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+ " activate\n"
            

        #Router PE 
        if obj_python["AS"][num_as]["nomClient"]=="":

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:] 

                if ((adresse != str(num_routeur))and(obj_python["AS"][num_as]["routeurs"][i]["type"]=="bordure")):
                    res= res + " neighbor 10.0.0."+adresse+" remote-as "+AS+"\n"+ " neighbor 10.0.0."+adresse+" update-source Loopback0\n"

            res = (res  + " !\n"
                        + " address-family vpnv4\n" )
         

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:]

                if (adresse != str(num_routeur) and (obj_python["AS"][num_as]["routeurs"][i]["type"]=="bordure")):
                    res = res + "  neighbor 10.0.0."+adresse+" activate\n  neighbor 10.0.0."+adresse+" send-community both\n"

            vrf = configVRF(num_routeur)
            res = res + " exit-address-family\n !\n"+vrf

        if obj_python["AS"][num_as]["nomClient"]!="":
            res= res + " !\n address-family ipv4\n  network "+ obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"]+" mask 255.255.255.255\n" + strAddressFam+" exit-address-family\n"


        return res

    return ""           


#faire fontion ecrire vrf
# !!!! rajouter vrf forwarding sur interfaces


def configVRF (num_routeur):
    res=""
    tmp=""
    num_as_voisin=0
    num_voisin=0

    client = False
    nbclient=0
    count = 0


    for n in range(len(obj_python["connexion"]["connections"])):
        if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:])and obj_python["connexion"]["connections"][n]["relation2"]=="client":
            nbclient = nbclient+1

        if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:])and obj_python["connexion"]["connections"][n]["relation1"]=="client":
            nbclient = nbclient+1


    for n in range(len(obj_python["connexion"]["connections"])):
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

        if client :
            tmp = tmp+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:] + " remote-as "+str(num_as_voisin)+"\n"
            tmp = tmp+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:] +" activate\n"

            num = 0;
            for i in range( len(obj_python["AS"])):
                if num_as_voisin == obj_python["AS"][i]["numeroAS"]:
                    num = i

           
            if count < nbclient:
                res = res+" address-family ipv4 vrf "+str(obj_python["AS"][num]["nomClient"])+"\n"+ tmp + " exit-address-family\n !\n"
            else:
                res = res+" address-family ipv4 vrf "+str(obj_python["AS"][num]["nomClient"])+"\n"+ tmp + " exit-address-family\n!\n"

    return res

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

                    return " ip vrf forwarding "+str(obj_python["AS"][num]["nomClient"])


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


def declareClient(num_routeur):
    res="!"
    numClient=0
    num_as_client=0
    premiereLigne=True
    numClientPrecedent =0
    numeroClient = ""

    for i in range(len(obj_python["relations"])): 
        if num_routeur ==  obj_python["relations"][i]["idPE"]: 
            numClient = int(obj_python["relations"][i]["client"][1:])
            if numClient != numClientPrecedent :
                premiereLigne=True

            for router in range(len(obj_python["connexion"]["routeurs"])):
                if numClient == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_client = obj_python["connexion"]["routeurs"][router]["as"]

            for j in range(len(obj_python["AS"])):
                if num_as_client==obj_python["AS"][j]["numeroAS"]:
                    numeroClient = obj_python["AS"][j]["numClientVPN"]

            if premiereLigne: 
                res =res+ "\n!\nip vrf "+ obj_python["relations"][i]["nomClient"]+"\n"
                premiereLigne=False
                res = res+" rd "+str(num_as_client)+":123"+"\n route-target export "+str(num_as_client)+":"+numeroClient

            
            res=res+"\n route-target import "+str(obj_python["relations"][i]["asImport"])+":"+str(obj_python["relations"][i]["numImport"])
            numClientPrecedent = numClient

    return res



def ecrireConfig(num_routeur, file, num_as, num_routeur_as): 

    protocole = obj_python["AS"][num_as]["routage_protocol"]
    nomRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["id"]
    typeRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["type"]

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
               + adressage(num_routeur,
                           "GigabitEthernet1/0", num_as, nomRouteur)
            
               + "\n!\ninterface GigabitEthernet2/0"
               +forwardingClient(num_routeur, "GigabitEthernet2/0")
               + adressage(num_routeur,
                           "GigabitEthernet2/0", num_as, nomRouteur)
               
               + "\n!\ninterface GigabitEthernet3/0"
               +forwardingClient(num_routeur, "GigabitEthernet3/0")
               + adressage(num_routeur,"GigabitEthernet3/0", num_as, nomRouteur)
               
               + "\n!\ninterface GigabitEthernet4/0"
               +forwardingClient(num_routeur, "GigabitEthernet4/0")
               + adressage(num_routeur,"GigabitEthernet4/0", num_as, nomRouteur)
                

               + "\n!\n"

               # bgp
               + configBGP(num_routeur, num_as, typeRouteur, num_routeur_as)
               + ecrireProtocole(protocole, nomRouteur)
               + "!\n"
               + "ip forward-protocol nd\n"
               + "!\n"
               + "no ip http server\n"
               + "no ip http secure-server\n"
               + "!\n"
             
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





if __name__ == "__main__":

    fileObject = open("config.json", "r")
    jsonContent = fileObject.read()
    obj_python = json.loads(jsonContent)

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


    for a in range(len(obj_python["AS"])):
        for i in range(len(obj_python["AS"][a]["routeurs"])):

            num_routeur = int(obj_python["AS"][a]["routeurs"][i]["id"][1:])
            ecrireFichier("./configs", num_routeur, a, i)
