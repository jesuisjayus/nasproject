import shutil, os

# lister tous les dossiers 

nb_routeurs = 8
ejemplo_dir = './Projet_GNS3/project-files/dynamips'

dossier = os.listdir(ejemplo_dir) 
fichiers = ['' for i in range(len(dossier))]


tab = [' _ ' for i in range(len(fichiers))]
var = 1

for i in range(1, len(fichiers)):
	chemin = ''
	if os.path.isdir( ejemplo_dir +'/'+ dossier[i-1] ):
		chemin = ejemplo_dir +'/'+ dossier[i-1] + '/configs' 
		f=os.listdir(chemin)[0] 
			
		if (f.split("_")[1]) == 'startup-config.cfg':
				fichiers[int((f.split("_")[0][1:]))] = chemin+'/'+f

print(fichiers)
for i in range(1,nb_routeurs+1):
	
	nom_fichier_nv = 'i' + str(i)+'_startup-config.cfg'
	
	for j in range(1,nb_routeurs+1):
		
		if nom_fichier_nv == fichiers[j].split("configs/")[1]:
			
			# Déplacer un fichier du répertoire rep1 vers rep2
			shutil.move('./A/i'+ str(i) +'_startup-config.cfg', fichiers[i])