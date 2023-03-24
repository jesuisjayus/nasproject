import shutil, os

# lister tous les dossiers 
ejemplo_dir = './Projet_GNS3/project-files/dynamips'
dossier = os.listdir(ejemplo_dir) 
fichiers = ['' for i in range(15)]
print(fichiers)


for i in range(1, len(fichiers)):
	chemin = ejemplo_dir +'/'+ dossier[i-1] + '/configs' 
	tab = os.listdir(chemin)

	for f in tab:
		if (f.split("_")[1]) != 'private-config.cfg':
			fichiers[int((f.split("_")[0][1:]))] = chemin+'/'+f



print (fichiers)
for i in range(1,15):

	nom_fichier_nv = 'i' + str(i)+'_startup-config.cfg'

	# for j in range(1,15):

	# 	if  nom_fichier_nv == fichiers[j]: 

			# # Déplacer un fichier du répertoire rep1 vers rep2
	shutil.move('./A/i'+ str(i) +'_startup-config.cfg', fichiers[i])