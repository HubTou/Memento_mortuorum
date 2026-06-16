#!/usr/local/bin/python3
####################################
#                                  #
# Memento mortuorum                #
# (c) 2026+ Hubert Tournier        #
#                                  #
# Génération du fichier stats.html #
#                                  #
####################################

DEBUT = "stats.html.debut"
DONNEES = "stats.txt"
FIN = "stats.html.fin"
RESULTAT = "stats.html"

with open(RESULTAT, "w") as fichier_sortie:
    with open(DEBUT, "r", encoding="utf-8") as fichier_entree:
        contenu = fichier_entree.read()
    fichier_sortie.write(contenu)

    with open(DONNEES, "r", encoding="utf-8") as fichier_entree:
        lignes = fichier_entree.readlines()

    in_block = False
    expecting = ""
    tri = False
    for ligne in lignes:
        ligne = ligne.strip()
        if in_block:
            if expecting == "":
                if ligne.startswith("@name:"):
                    name = ligne[6:]
                if ligne.startswith("@title:"):
                    expecting = "header"
                    fichier_sortie.write('    <div class="stat-block-titles">\n')
                    if name:
                        fichier_sortie.write(f'      <div class="stat-block-title"><a name="{name}">{ligne[7:]}</a></div>\n')
                        name = ""
                    else:
                        fichier_sortie.write(f'      <div class="stat-block-title">{ligne[7:]}</div>\n')
                    tri = False
            elif expecting == "header":
                if ligne.startswith("@subtitle:"):
                    fichier_sortie.write(f'      <div class="stat-block-subtitle">{ligne[10:]}</div>\n')
                else:
                    expecting = "data"
                    fichier_sortie.write('    </div>\n')
                    fichier_sortie.write('    <svg class="stat-block-chevron" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4,6 8,10 12,6"/></svg>\n')
                    fichier_sortie.write('  </button>\n')
                    fichier_sortie.write('  <div class="stat-block-body">\n')
                    fichier_sortie.write('    <div class="table-wrap"><table>\n')
                    fichier_sortie.write('      <thead><tr>\n')
                    for header in ligne.split("|"):
                        if header == "tri":
                            tri = True
                        else:
                            fichier_sortie.write(f'        <th>{header}</th>\n')
                    fichier_sortie.write('      </tr></thead>\n')
                    fichier_sortie.write('      <tbody>\n')
            elif expecting == "data":
                if ligne == "":
                    in_block = False
                    expecting = ""
                    fichier_sortie.write('      </tbody>\n')
                    fichier_sortie.write('    </table></div>\n')
                    fichier_sortie.write('  </div>\n')
                    fichier_sortie.write('</div>\n')
                    fichier_sortie.write('\n')
                else:
                    fichier_sortie.write('        <tr>\n')
                    if tri:
                        for column in ligne.split("|")[0:-1]:
                            fichier_sortie.write(f'          <td>{column}</td>\n')
                    else:
                        for column in ligne.split("|"):
                            fichier_sortie.write(f'          <td>{column}</td>\n')
                    fichier_sortie.write('        </tr>\n')
        else:
            if ligne == "@block:open":
                in_block = True
                fichier_sortie.write('<div class="stat-block open">\n')
                fichier_sortie.write('  <button class="stat-block-toggle" type="button">\n')
            elif ligne == "@block:close":
                in_block = True
                fichier_sortie.write('<div class="stat-block">\n')
                fichier_sortie.write('  <button class="stat-block-toggle" type="button">\n')

    with open(FIN, "r", encoding="utf-8") as fichier_entree:
        contenu = fichier_entree.read()
    fichier_sortie.write(contenu)
