import json


def ecrireFichier(cheminVersDossier, num_routeur, num_as, num_routeur_as):
    chemin = cheminVersDossier+"/i"+str(num_routeur)+"_startup-config.cfg"
    file = open(chemin, "w")
    ecrireConfig(num_routeur, file, num_as, num_routeur_as)
    file.close()


def adressage(num_routeur_as, interface, num_as, nomRouteur):
    res = ""
    num_routeur1 = num_routeur_as
    address = ""
    protocole = ""
    vitesse= " negotiation auto"

    #determiner protocole
    if obj_python["AS"][num_as]["routage_protocol"] == "RIP":
        protocole = " ipv6 rip ripng enable"
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ipv6 ospf 1 area 0"

    # pour les routeurs de bordure
    for n in range(len(obj_python["connexion"]["connections"])):
        if nomRouteur == obj_python["connexion"]["connections"][n]["id1"] and interface == obj_python["connexion"]["connections"][n]["interface1"]:
            address = obj_python["connexion"]["connections"][n]["address"] + \
                str(num_routeur1)+"/64"
            return "interface "+interface+" \n"+" no ip address \n"+vitesse+"\n"+" ipv6 address "+address+" \n"+" ipv6 enable \n"+protocole

        elif nomRouteur == obj_python["connexion"]["connections"][n]["id2"] and interface == obj_python["connexion"]["connections"][n]["interface2"]:
            address = obj_python["connexion"]["connections"][n]["address"] + \
                str(num_routeur1)+"/64"
            return "interface "+interface+" \n"+" no ip address \n"+" duplex full\n"+" ipv6 address "+address+" \n"+" ipv6 enable \n"+protocole

    # pour le reste des routeurs
    for i in range(len(obj_python["AS"][num_as]["connections"])):
        if nomRouteur == obj_python["AS"][num_as]["connections"][i]["id1"] and interface == obj_python["AS"][num_as]["connections"][i]["interface1"]:
            num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id2"][1:])
            address = obj_python["AS"][num_as]["prefix"] + \
                str(lan[num_routeur1][num_routeur2])
            
            
            if  interface == "FastEthernet0/0":
                vitesse = " duplex full"

            if obj_python["AS"][num_as]["routage_protocol"] == "OSPF": 
                if obj_python["AS"][num_as]["connections"][i]["cout1"] != "default":
                    protocole = protocole + "\n ipv6 ospf cost "+ obj_python["AS"][num_as]["connections"][i]["cout1"]





            address = address+"::"+str(num_routeur1)+"/64"
            return "interface "+interface+" \n"+" no ip address \n"+vitesse+"\n ipv6 address "+address+" \n"+" ipv6 enable \n"+protocole

        elif nomRouteur == obj_python["AS"][num_as]["connections"][i]["id2"] and interface == obj_python["AS"][num_as]["connections"][i]["interface2"]:
            num_routeur2 = int(obj_python["AS"][num_as]["connections"][i]["id1"][1:])
            address = obj_python["AS"][num_as]["prefix"] + \
                str(lan[num_routeur1][num_routeur2])

            if  interface == "FastEthernet0/0":
                vitesse = " duplex full"

            if obj_python["AS"][num_as]["routage_protocol"] == "OSPF" :
                if obj_python["AS"][num_as]["connections"][i]["cout2"] != "default":
                    protocole = protocole + "\n ipv6 ospf cost "+ obj_python["AS"][num_as]["connections"][i]["cout2"]



            address = address+"::"+str(num_routeur1)+"/64"
            return "interface "+interface+" \n"+" no ip address \n"+vitesse+"\n ipv6 address "+address+" \n"+" ipv6 enable \n"+protocole

        else:
            res = "interface "+interface+"\n no ip address\n shutdown\n"+vitesse

    return res


# renvoie le string du loopback
def adressageLoopback(num_routeur_as, num_as):

    protocole = ""

    if obj_python["AS"][num_as]["routage_protocol"] == "RIP":
        protocole = " ipv6 rip ripng enable"
    if obj_python["AS"][num_as]["routage_protocol"] == "OSPF":
        protocole = " ipv6 ospf 1 area 0"

    return "interface Loopback0\n" + " no ip address\n" + " ipv6 address " + obj_python["AS"][num_as]["routeurs"][num_routeur_as]["address"] + "/64\n" + " ipv6 enable\n" + protocole

# renvoie le string pour chaque protocole


def ecrireProtocole(protocole, nomRouteur):
    if protocole == "RIP":
        return "ipv6 router rip ripng\n redistribute connected\n"
    if protocole == "OSPF":
        n = str(nomRouteur[1:])
        routeurID = n+"."+n+"."+n+"."+n
        return "ipv6 router ospf 1\n router-id "+routeurID+"\n"


# #ecrire bgp
def configBGP(num_routeur, num_as):
   

    AS = str(obj_python["AS"][num_as]["numeroAS"])
   
    res =   ("router bgp "+AS+"\n"
               + " bgp router-id "+str(num_routeur)+"."+str(num_routeur)+"."+str(num_routeur)+"."+str(num_routeur)+"\n"
               + " bgp log-neighbor-changes\n"
               + " no bgp default ipv4-unicast\n")

    for n in range(len(obj_python["connexion"]["connections"])):
        if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:]):
            num_voisin = int(obj_python["connexion"]["connections"][n]["id2"][1:])

            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]


            res = res + " neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" remote-as "+str(num_as_voisin)+"\n"


        if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:]):
            num_voisin = int(obj_python["connexion"]["connections"][n]["id1"][1:])

            for router in range(len(obj_python["connexion"]["routeurs"])):
                if num_voisin == int(obj_python["connexion"]["routeurs"][router]["id"][1:]):
                    num_as_voisin = obj_python["connexion"]["routeurs"][router]["as"]


            res = res + " neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" remote-as "+str(num_as_voisin)+"\n"


    for i in range(len(obj_python["AS"][num_as]["routeurs"])):
        adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:]

        if adresse != str(num_routeur):
            res= res + " neighbor 2001:ABCD:"+adresse+"::1 remote-as "+AS+"\n"+ " neighbor 2001:ABCD:"+adresse+"::1 update-source Loopback0\n"

    res = (res  + " !\n"
                + " address-family ipv4\n"
                + " exit-address-family\n"
                + " !\n"
                + " address-family ipv6\n")


    # filtre = False
    # for i in range(len(obj_python["connexion"]["routeurs"])):
    #     if num_routeur == int(obj_python["connexion"]["routeurs"][i]["id"][1:]) and obj_python["connexion"]["routeurs"][i]["filter_state"]!= "default":
    #         filtre = True



    for n in range(len(obj_python["connexion"]["connections"])):
        if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:]):

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                for j in range(i+1, len(obj_python["AS"][num_as]["routeurs"])):
                    adresse_i = int(obj_python["AS"][num_as]["routeurs"][i]["id"][1:])
                    adresse_j = int(obj_python["AS"][num_as]["routeurs"][j]["id"][1:])

                    if lan[adresse_i][adresse_j] != 0:
                        res = res + "  network " +obj_python["AS"][num_as]["prefix"] + str(lan[adresse_i][adresse_j]) + "::/64\n"
                        
            res = res + "  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" activate\n"
            
            res=res+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" route-map map_in_0 in\n"
            res=res+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" route-map map_out_0 out\n" 

            # if filtre : 
            #     # ajouter ligne map 
            #     res = res + "  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id2"])[1:]+" route-map map1 "


        if num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:]):

            for i in range(len(obj_python["AS"][num_as]["routeurs"])):
                for j in range(i+1, len(obj_python["AS"][num_as]["routeurs"])):
                    adresse_i = int(obj_python["AS"][num_as]["routeurs"][i]["id"][1:])
                    adresse_j = int(obj_python["AS"][num_as]["routeurs"][j]["id"][1:])

                   

                    if lan[adresse_i][adresse_j] != 0:
                        res = res + "  network " +obj_python["AS"][num_as]["prefix"] + str(lan[adresse_i][adresse_j]) + "::/64\n"


            res = res + "  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" activate\n"
            
            res=res+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" route-map map_in_0 in\n"
            res=res+"  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" route-map map_out_0 out\n" 
            # if filtre : 
            #     # ajouter ligne map 
            #     res = res + "  neighbor "+ obj_python["connexion"]["connections"][n]["address"]+ (obj_python["connexion"]["connections"][n]["id1"])[1:]+" route-map map1 "



    # for i in range(len(obj_python["connexion"]["routeurs"])):  

    #     if filtre and num_routeur == int(obj_python["connexion"]["routeurs"][i]["id"][1:]):
    #         res = res + obj_python["connexion"]["routeurs"][i]["filter_state"] + "\n"



    for i in range(len(obj_python["AS"][num_as]["routeurs"])):
        adresse = obj_python["AS"][num_as]["routeurs"][i]["id"][1:]

        if adresse != str(num_routeur):
            res = res + "  neighbor 2001:ABCD:"+adresse+"::1 activate\n"
            for n in range(len(obj_python["connexion"]["connections"])):
                if num_routeur == int(obj_python["connexion"]["connections"][n]["id1"][1:]) or num_routeur == int(obj_python["connexion"]["connections"][n]["id2"][1:]):
                    res = res + "  neighbor 2001:ABCD:"+adresse+"::1 send-community\n"


    res = res + " exit-address-family\n"

    return res

               




def ecrireMapEtACL(nomRouteur):
    res=""
    num_routeur = int(nomRouteur[1:])
    
    
    for i in range(len(obj_python["connexion"]["routeurs"])):  
        if num_routeur == int(obj_python["connexion"]["routeurs"][i]["id"][1:]) and obj_python["connexion"]["routeurs"][i]["filter_state"]!= "default":
            
            if num_routeur == int(obj_python["connexion"]["routeurs"][i]["id"][1:]):
                res = "route-map map1 deny 10\n match ipv6 address liste1\n!\nipv6 access-list liste1\n"

                if obj_python["connexion"]["routeurs"][i]["as"] ==1 :
                    nom_as = "AS2"
                else:
                    nom_as = "AS1"

                for j in range(len(obj_python["connexion"]["routeurs"][i]["acl"])):
                    
                    a = obj_python["connexion"]["routeurs"][i]["acl"][j][0]
                    b = obj_python["connexion"]["routeurs"][i]["acl"][j][1]

                    prefix = obj_python[nom_as]["prefix"]

                    res = res +" "+prefix + str(lan[a][b]) + "::/64 any\n"

    return res


def ecrireComm(num_as,nomRouteur):
    res=""
    num_as=num_as+1
    for i in range(len(obj_python["connexion"]["connections"])):  
        if nomRouteur == obj_python["connexion"]["connections"][i]["id1"] :
            if obj_python["connexion"]["connections"][i]["relation1"]=="peer":
                if obj_python["connexion"]["connections"][i]["relation2"]=="peer":
                    res=res+ "!\nip community-list standard "+str(num_as)+":30_out permit "+str(num_as)+":30\nip community-list standard "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":20\n set local-preference 200\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":30_out\n match community "+str(num_as)+":20_out\n!\nroute-map map_out_0 permit 100\n!\n"
                if obj_python["connexion"]["connections"][i]["relation2"]=="client":
                    res=res+"route-map map_in_0 permit 10\n set community "+str(num_as)+":10\n set local-preference 400\n!\nroute-map map_out_0 permit 100\n!\n"
                if obj_python["connexion"]["connections"][i]["relation2"]=="provider":
                    res=res+"ip community-list standard "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":30\n set local-preference 80\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":20_out\n!\nroute-map map_out_0 permit 100\n!\n"
            if obj_python["connexion"]["connections"][i]["relation1"]=="client":
                if obj_python["connexion"]["connections"][i]["relation2"]=="peer":
                    res=res+"ip community-list standart "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":30\n set local-preference 80\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":20_out_\n!\nroute-map map_out_0 permit 100\n!\n"
            if obj_python["connexion"]["connections"][i]["relation1"]=="provider":
                if obj_python["connexion"]["connections"][i]["relation2"]=="peer":
                    res=res+"route-map map_in_0 permit 10\n set community "+str(num_as)+":10\n set local-preference 400\n!\nroute-map map_out_0 permit 100\n!\n"
        if nomRouteur == obj_python["connexion"]["connections"][i]["id2"] :
                    if obj_python["connexion"]["connections"][i]["relation2"]=="peer":
                        if obj_python["connexion"]["connections"][i]["relation1"]=="peer":
                            res=res+ "!\nip community-list standard "+str(num_as)+":30_out permit "+str(num_as)+":30\nip community-list standard "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":20\n set local-preference 200\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":30_out\n match community "+str(num_as)+":20_out\n!\nroute-map map_out_0 permit 100\n!\n"
                        if obj_python["connexion"]["connections"][i]["relation1"]=="client":
                            res=res+"route-map map_in_0 permit 10\n set community "+str(num_as)+":10\n set local-preference 400\n!\nroute-map map_out_0 permit 100\n!\n"
                        if obj_python["connexion"]["connections"][i]["relation1"]=="provider":
                            res=res+"ip community-list standard "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":30\n set local-preference 80\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":20_out\n!\nroute-map map_out_0 permit 100\n!\n"
                    if obj_python["connexion"]["connections"][i]["relation2"]=="client":
                        if obj_python["connexion"]["connections"][i]["relation1"]=="peer":
                            res=res+"ip community-list standart "+str(num_as)+":20_out permit "+str(num_as)+":20\n!\nroute-map map_in_0 permit 10\n set community "+str(num_as)+":30\n set local-preference 80\n!\nroute-map map_out_0 deny 10\n match community "+str(num_as)+":20_out_\n!\nroute-map map_out_0 permit 100\n!\n"
                    if obj_python["connexion"]["connections"][i]["relation2"]=="provider":
                        if obj_python["connexion"]["connections"][i]["relation1"]=="peer":
                            res=res+"route-map map_in_0 permit 10\n set community "+str(num_as)+":10\n set local-preference 400\n!\nroute-map map_out_0 permit 100\n!\n"
    return res

# fct ecrit sur un fichier
def ecrireConfig(num_routeur, file, num_as, num_routeur_as):

    # AS = "AS"+str(num_as)

    # num_routeur = n

    # if num_routeur < 8:
    #     AS = "AS1"

    # else:
    #     AS = "AS2"
    #     num_routeur = num_routeur-7




    protocole = obj_python["AS"][num_as]["routage_protocol"]
    nomRouteur = obj_python["AS"][num_as]["routeurs"][num_routeur_as]["id"]

    file.write("!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec  \n! \nhostname "
               + nomRouteur + "\n"
               + ""
               + "!                                     \n"
               + "boot-start-marker                     \n"
               + "boot-end-marker                       \n"
               + "!                                     \n"
               + "no aaa new-model                      \n"
               + "no ip icmp rate-limit unreachable     \n"
               + "ip cef                                \n"
               + "!                                     \n"
               + "no ip domain lookup                   \n"
               + "ipv6 unicast-routing                  \n"
               + "ipv6 cef                              \n"
               + "!                                     \n"
               + "multilink bundle-name authen7ticated   \n"
               + "!                                     \n"
               + "ip tcp synwait-time 5                 \n"
               + "!                                     \n"
               + adressageLoopback(num_routeur_as, num_as)
               + "\n!\n"
               + adressage(num_routeur, "FastEthernet0/0", num_as, nomRouteur)
               + "\n!\n"
               + adressage(num_routeur,
                           "GigabitEthernet1/0", num_as, nomRouteur)
               + "\n!\n"
               + adressage(num_routeur,
                           "GigabitEthernet2/0", num_as, nomRouteur)
               + "\n!\n"
               + adressage(num_routeur,"GigabitEthernet3/0", num_as, nomRouteur)
               + "\n!\n"

               # bgp
			   + configBGP(num_routeur, num_as)
               + "!\n"
               + "ip forward-protocol nd\n"
               + "!\n"
               + "no ip http server\n"
               + "no ip http secure-server\n"
               + "!\n"
               + ecrireProtocole(protocole, nomRouteur)
               + "!\n"
            #    + ecrireMapEtACL(nomRouteur)
                +ecrireComm(num_as,nomRouteur)
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

    fileObject = open("./A/routeurs.json", "r")
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
            ecrireFichier("./A", num_routeur, a, i)

