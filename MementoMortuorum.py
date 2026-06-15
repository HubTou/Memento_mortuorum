#!/usr/local/bin/python3
####################################
#                                  #
# Memento mortuorum                #
# (c) 2026+ Hubert Tournier        #
#                                  #
# Génération de la base de données #
#                                  #
####################################

import csv
import datetime
from enum import Enum
import os
import pprint
import re
import sqlite3
import sys
import time
import unicodedata

BASE_DE_DONNEES = "deces.sqlite"
OPPOSITIONS = "oppositions.csv"
COMMUNES = "COG" + os.sep + "v_commune_depuis_1943.csv"
COMMUNES_OUTREMER = "COG" + os.sep + "v_commune_outremer_depuis_1943.csv"
PAYS = "COG" + os.sep + "v_pays_et_territoire_depuis_1943.csv"
TOM = "COG" + os.sep + "v_tom_depuis_1943.csv"
EXTENSIONS = "COG" + os.sep + "v_codes_extension_2026.csv"

class Severite(Enum):
    CRITIQUE = 8
    DONNEES_ERRONEES = 7
    ERREUR = 6
    DONNEES_INCONSISTANTES = 4
    AVERTISSEMENT = 4
    DONNEES_MANQUANTES = 3
    INFORMATION_IMPORTANTE = 2
    INFORMATION = 1
    DEBOGAGE = 0

class Couleur:
    VIOLET = "\033[0;35m"
    ROUGE = "\033[0;31m"
    ORANGE = "\033[1;31m"
    JAUNE = "\033[0;33m"
    VERT = "\033[0;32m"
    BLEU_CIEL = "\033[0;36m"
    BLANC_SUR_FOND_BLEU = "\033[44m\033[1;37m"
    NORMAL = "\033[0m"

infos = {
    "erreur.nomprenom.format_incorrect": 0,
    "erreur.sexe.valeur_inconnue": 0, 
    "erreur.datenaiss.vide": 0,
    "erreur.datenaiss.taille_incorrecte": 0,
    "erreur.datenaiss.avant_1840": 0,
    "erreur.datenaiss.dans_le_futur": 0,
    "erreur.datenaiss.mois_incorrect": 0,
    "erreur.datenaiss.jour_incorrect": 0,
    "erreur.datenaiss.non_numerique": 0,
    "erreur.datenaiss.date_impossible": 0,
    "erreur.lieunaiss.vide": 0,
    "erreur.lieunaiss.commune_inconnue": 0,
    "erreur.lieunaiss.pays_inconnu": 0,
    "erreur.lieunaiss.code_inconnu": 0,
    "erreur.lieunaiss.code_inconsistant_avec_commune": 0,
    "erreur.lieunaiss.format_incorrect": 0,
    "erreur.lieunaiss.code_inconnu_a_date": 0,
    "erreur.commnaiss.commune_mal_orthographiee": 0,
    "erreur.paysnaiss.pays_mal_orthographie": 0,
    "erreur.datedeces.vide": 0,
    "erreur.datedeces.taille_incorrecte": 0,
    "erreur.datedeces.avant_naissance": 0,
    "erreur.datedeces.dans_le_futur": 0,
    "erreur.datedeces.mois_incorrect": 0,
    "erreur.datedeces.jour_incorrect": 0,
    "erreur.datedeces.non_numerique": 0,
    "erreur.datedeces.age_trop_grand": 0,
    "erreur.lieudeces.vide": 0,
    "erreur.lieudeces.commune_inconnue": 0,
    "erreur.lieudeces.pays_inconnu": 0,
    "erreur.lieudeces.format_incorrect": 0,
    "erreur.actedeces.non_numerique": 0,
    "erreur.opposition.utilisation_multiple": 0,
    "erreur.doublons.complets": 0,
    "info.opposition.lignes": 0,
    "info.opposition.lignes_inutilisees": 0,
    "info.opposition.lignes_reutilisees": 0,
}

####################################################################################################
def Log(criticite, message):
    """ """
    prefixe = ""
    suffixe = Couleur.NORMAL
    match criticite:
        case Severite.CRITIQUE: prefixe = Couleur.VIOLET
        case Severite.DONNEES_ERRONEES: prefixe = Couleur.ROUGE
        case Severite.ERREUR: prefixe = Couleur.ROUGE
        case Severite.DONNEES_INCONSISTANTES: prefixe = Couleur.ORANGE
        case Severite.AVERTISSEMENT: prefixe = Couleur.ORANGE
        case Severite.DONNEES_MANQUANTES: prefixe = Couleur.JAUNE
        case Severite.INFORMATION_IMPORTANTE: prefixe = Couleur.BLANC_SUR_FOND_BLEU
        case Severite.INFORMATION: prefixe = Couleur.VERT
        case Severite.DEBOGAGE: prefixe = Couleur.BLEU_CIEL
    print(f"{prefixe}{message}{suffixe}")

####################################################################################################
def InitialiserBaseDeDonnees():
    """ Crée les tables de la base de données """
    Log(Severite.INFORMATION_IMPORTANTE, "===== Création des tables de la base de données =====")
    t1 = time.perf_counter()

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    curseur.execute("""
CREATE TABLE 'cog'
(
    'code' TEXT,
    'type' TEXT,
    'nom_maj' TEXT,
    'nom_riche' TEXT,
    'libelle' TEXT,
    'date_debut' INTEGER,
    'date_fin' INTEGER,
    PRIMARY KEY ('code', 'date_debut', 'date_fin')
)""")

    curseur.execute("""
CREATE TABLE 'personnes'
(
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'nom' TEXT,
    'prenoms' TEXT,
    'sexe' INTEGER,
    'annee_naissance' INTEGER,
    'mois_naissance' INTEGER,
    'jour_naissance' INTEGER,
    'date_naissance' INTEGER,
    'lieu_naissance' TEXT,
    'commune_naissance' TEXT,
    'pays_naissance' TEXT,
    'annee_deces' INTEGER,
    'mois_deces' INTEGER,
    'jour_deces' INTEGER,
    'date_deces' INTEGER,
    'lieu_deces' TEXT,
    'commune_deces' TEXT,
    'pays_deces' TEXT,
    'acte_deces' TEXT,
    'opposition' INTEGER
)""")

    curseur.execute("""
CREATE TABLE 'prenoms'
(
    'id' INTEGER PRIMARY KEY AUTOINCREMENT,
    'prenom' TEXT
)""")

    curseur.execute("""
CREATE TABLE 'prenoms_personne'
(
    'id_personne' INTEGER,
    'id_prenom' INTEGER,
    'ordre' INTEGER
)""")

    curseur.execute("""
CREATE TABLE 'infos'
(
    'cle' TEXT,
    'libelle' TEXT,
    'valeur' TEXT
)""")

    base.commit()
    curseur.close()
    base.close()

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

####################################################################################################
def InclureArticleDansNom(tncc, ncc, nccenr):
    """ Réintroduit les articles dans les noms (exemple "LE MANS" plutôt que "MANS") """
    nom_maj = ""
    nom_riche = ""

    if tncc in ["0", "1"]:
        nom_maj = ncc
        nom_riche = nccenr
    elif tncc == "2":
        nom_maj = "LE " + ncc
        nom_riche = "Le " + nccenr
    elif tncc == "3":
        nom_maj = "LA " + ncc
        nom_riche = "La " + nccenr
    elif tncc == "4":
        nom_maj = "LES " + ncc
        nom_riche = "Les " + nccenr
    elif tncc == "5":
        nom_maj = "L'" + ncc
        nom_riche = "L'" + nccenr
    elif tncc == "6":
        nom_maj = "AUX " + ncc
        nom_riche = "Aux " + nccenr
    elif tncc == "7":
        nom_maj = "LAS " + ncc
        nom_riche = "Las " + nccenr
    elif tncc == "8":
        nom_maj = "LOS " + ncc
        nom_riche = "Los " + nccenr

    return nom_maj, nom_riche

####################################################################################################
def InsererCommunes():
    """ Insertion des communes du Code Officiel Géographique (COG) de l'INSEE """
    if not os.path.isfile(COMMUNES):
        Log(Severite.CRITIQUE, f"{COMMUNES}: fichier non trouvé")
        sys.exit(1)
    else:
        base = sqlite3.connect(BASE_DE_DONNEES)
        curseur = base.cursor()

        with open(COMMUNES, newline="") as fichier:
            champs = ["TYPECOM","COM","TNCC","NCC","NCCENR","LIBELLE","DATE_DEBUT","DATE_FIN"]
            data = csv.DictReader(fichier, delimiter=",", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                nom_maj, nom_riche = InclureArticleDansNom(ligne['TNCC'], ligne['NCC'], ligne['NCCENR'])

                date_debut = ligne['DATE_DEBUT'].replace("-", "")
                if date_debut == "19430101":
                    date_debut = "00000000"

                date_fin = ligne['DATE_FIN'].replace("-", "")
                if date_fin == "":
                    date_fin = "99999999"

                curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?, ?)", (ligne['COM'], ligne['TYPECOM'], nom_maj, nom_riche, ligne['LIBELLE'], int(date_debut), int(date_fin)))

            # communes fusionnées ou supprimées avant 1943 ou omises dans le COG
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('01220', 'COM', 'LOMPNES', 'Lompnes', 'Lompnes', '00000000', '19420731')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('01459', 'COM', 'HAUTEVILLE', 'Hauteville', 'Hauteville', '00000000', '19420731')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('54454', 'COM', 'REMENAUVILLE', 'Remenauville', 'Remenauville', '00000000', '19621221')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('54448', 'COM', 'REGNIEVILLE', 'Regniéville', 'Regniéville', '00000000', '19621221')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('66131', 'COM', 'PALALDA', 'Palalda', 'Palalda', '00000000', '19420930')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('66235', 'COM', 'AMELIE-LES-BAINS', 'Amélie-les-Bains', 'Amélie-les-Bains', '00000000', '19420930')")
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('78025', 'COM', 'ARTHIEUL', 'Arthieul', 'Arthieul', '00000000', '19671220')")

            base.commit()

        curseur.close()
        base.close()

####################################################################################################
def InsererCommunesOutremer():
    """ Insertion des communes d'outremer du Code Officiel Géographique (COG) de l'INSEE """
    if not os.path.isfile(COMMUNES_OUTREMER):
        Log(Severite.CRITIQUE, f"{COMMUNES_OUTREMER}: fichier non trouvé")
        sys.exit(1)
    else:
        base = sqlite3.connect(BASE_DE_DONNEES)
        curseur = base.cursor()

        with open(COMMUNES_OUTREMER, newline="") as fichier:
            champs = ["NATURE_ZONAGE", "COM_COMER", "TNCC", "NCC", "NCCENR", "LIBELLE", "DATE_DEBUT", "DATE_FIN"]
            data = csv.DictReader(fichier, delimiter=",", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                nom_maj, nom_riche = InclureArticleDansNom(ligne['TNCC'], ligne['NCC'], ligne['NCCENR'])

                date_debut = ligne['DATE_DEBUT'].replace("-", "")
                if date_debut == "19430101":
                    date_debut = "00000000"

                date_fin = ligne['DATE_FIN'].replace("-", "")
                if date_fin == "":
                    date_fin = "99999999"

                curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?, ?)", (ligne['COM_COMER'], ligne['NATURE_ZONAGE'], nom_maj, nom_riche, ligne['LIBELLE'], int(date_debut), int(date_fin)))

            base.commit()

        curseur.close()
        base.close()

####################################################################################################
def InsererDepartements():
    """ Insertion des départements """
    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    # départements utilisés dans les fichiers de décès mais omis dans le COG
    # NB: la redivision de l'Algérie Française en 17 départements en 1957/1958 ne semble pas utilisée
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('91', 'DEP', 'ALGERIE FRANCAISE DEPARTEMENT D''ALGER', 'Algérie Française Département d''Alger', 'de l''Algérie Française Département d''Alger', '00000000', '19620705')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('92', 'DEP', 'ALGERIE FRANCAISE DEPARTEMENT D''ORAN', 'Algérie Française Département d''Oran', 'de l''Algérie Française Département d''Oran', '00000000', '19620705')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('93', 'DEP', 'ALGERIE FRANCAISE DEPARTEMENT DE CONSTANTINE', 'Algérie Française Département de Constantine', 'de l''Algérie Française Département de Constantine', '00000000', '19620705')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('94', 'DEP', 'ALGERIE FRANCAISE SUD DE L''ALGERIE', 'Algérie Française Sud de l''Algérie', 'de l''Algérie Française Sud de l''Algérie', '00000000', '19620705')")

    # départements parce que pourquoi pas !
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('01', 'DEP', 'AIN', 'Ain', 'de l''Ain', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('02', 'DEP', 'AISNE', 'Aisne', 'de l''Aisne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('03', 'DEP', 'ALLIER', 'Allier', 'de l''Allier', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('04', 'DEP', 'ALPES DE HAUTE PROVENCE', 'Alpes de Haute Provence', 'des Alpes de Haute Provence', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('05', 'DEP', 'HAUTES ALPES', 'Hautes Alpes', 'des Hautes Alpes', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('06', 'DEP', 'ALPES MARITIMES', 'Alpes Maritimes', 'des Alpes Maritimes', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('07', 'DEP', 'ARDECHE', 'Ardèche', 'de l''Ardèche', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('08', 'DEP', 'ARDENNES', 'Ardennes', 'des Ardennes', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('09', 'DEP', 'ARIEGE', 'Ariège', 'de l''Ariège', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('10', 'DEP', 'AUBE', 'Aube', 'de l''Aube', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('11', 'DEP', 'AUDE', 'Aude', 'de l''Aude', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('12', 'DEP', 'AVEYRON', 'Aveyron', 'de l''Aveyron', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('13', 'DEP', 'BOUCHES DU RHONE', 'Bouches du Rhône', 'des Bouches du Rhône', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('14', 'DEP', 'CALVADOS', 'Calvados', 'du Calvados', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('15', 'DEP', 'CANTAL', 'Cantal', 'du Cantal', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('16', 'DEP', 'CHARENTE', 'Charente', 'de la Charente', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('17', 'DEP', 'CHARENTE MARITIME', 'de la Charente Maritime', 'Charente Maritime', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('18', 'DEP', 'CHER', 'Cher', 'du Cher', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('19', 'DEP', 'CORREZE', 'Corrèze', 'de la Corrèze', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('20', 'DEP', 'CORSE', 'Corse', 'Corse', '00000000', '19753112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('2A', 'DEP', 'CORSE DU SUD', 'Corse du Sud', 'de la Corse du Sud', '19760101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('2B', 'DEP', 'HAUTE CORSE', 'Haute Corse', 'de la Haute Corse', '19760101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('21', 'DEP', 'COTE D''OR', 'Côte d''Or', 'de la Côte d''Or', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('22', 'DEP', 'COTES D''ARMOR', 'Côtes d''Armor', 'des Côtes d''Armor', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('23', 'DEP', 'CREUSE', 'Creuse', 'de la Creuse', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('24', 'DEP', 'DORDOGNE', 'Dordogne', 'de la Dordogne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('25', 'DEP', 'DOUBS', 'Doubs', 'du Doubs', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('26', 'DEP', 'DROME', 'Drôme', 'de la Drôme', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('27', 'DEP', 'EURE', 'Eure', 'de l''Eure', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('28', 'DEP', 'EURE ET LOIR', 'Eure et Loir', 'de l''Eure et Loir', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('29', 'DEP', 'FINISTERE', 'Finistère', 'du Finistère', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('30', 'DEP', 'GARD', 'Gard', 'du Gard', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('31', 'DEP', 'HAUTE GARONNE', 'Haute Garonne', 'de la Haute Garonne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('32', 'DEP', 'GERS', 'Gers', 'du Gers', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('33', 'DEP', 'GIRONDE', 'Gironde', 'de la Gironde', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('34', 'DEP', 'HERAULT', 'Hérault', 'de l''Hérault', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('35', 'DEP', 'ILLE ET VILAINE', 'Ille et Vilaine', 'de l''Ille et Vilaine', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('36', 'DEP', 'INDRE', 'Indre', 'de l''Indre', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('37', 'DEP', 'INDRE ET LOIRE', 'Indre et Loire', 'de l''Indre et Loire', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('38', 'DEP', 'ISERE', 'Isère', 'de l''Isère', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('39', 'DEP', 'JURA', 'Jura', 'du Jura', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('40', 'DEP', 'LANDES', 'Landes', 'des Landes', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('41', 'DEP', 'LOIR ET CHER', 'Loir et Cher', 'du Loir et Cher', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('42', 'DEP', 'LOIRE', 'Loire', 'de la Loire', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('43', 'DEP', 'HAUTE LOIRE', 'Haute Loire', 'de la Haute Loire', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('44', 'DEP', 'LOIRE ATLANTIQUE', 'Loire Atlantique', 'de la Loire Atlantique', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('45', 'DEP', 'LOIRET', 'Loiret', 'du Loiret', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('46', 'DEP', 'LOT', 'Lot', 'du Lot', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('47', 'DEP', 'LOT ET GARONNE', 'Lot et Garonne', 'du Lot et Garonne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('48', 'DEP', 'LOZERE', 'Lozère', 'de la Lozère', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('49', 'DEP', 'MAINE ET LOIRE', 'Maine et Loire', 'du Maine et Loire', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('50', 'DEP', 'MANCHE', 'Manche', 'de la Manche', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('51', 'DEP', 'MARNE', 'Marne', 'de la Marne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('52', 'DEP', 'HAUTE MARNE', 'Haute Marne', 'de la Haute Marne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('53', 'DEP', 'MAYENNE', 'Mayenne', 'de la Mayenne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('54', 'DEP', 'MEURTHE ET MOSELLE', 'Meurthe et Moselle', 'de la Meurthe et Moselle', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('55', 'DEP', 'MEUSE', 'Meuse', 'de la Meuse', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('56', 'DEP', 'MORBIHAN', 'Morbihan', 'du Morbihan', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('57', 'DEP', 'MOSELLE', 'Moselle', 'de la Moselle', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('58', 'DEP', 'NIEVRE', 'Nièvre', 'de la Nièvre', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('59', 'DEP', 'NORD', 'Nord', 'du Nord', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('60', 'DEP', 'OISE', 'Oise', 'de l''Oise', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('61', 'DEP', 'ORNE', 'Orne', 'de l''Orne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('62', 'DEP', 'PAS DE CALAIS', 'Pas de Calais', 'du Pas de Calais', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('63', 'DEP', 'PUY DE DOME', 'Puy de Dôme', 'du Puy de Dôme', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('64', 'DEP', 'PYRENEES ATLANTIQUES', 'Pyrénées Atlantiques', 'des Pyrénées Atlantiques', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('65', 'DEP', 'HAUTES PYRENEES', 'Hautes Pyrénées', 'des Hautes Pyrénées', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('66', 'DEP', 'PYRENEES ORIENTALES', 'Pyrénées Orientales', 'des Pyrénées Orientales', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('67', 'DEP', 'BAS RHIN', 'Bas Rhin', 'du Bas Rhin', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('68', 'DEP', 'HAUT RHIN', 'Haut Rhin', 'du Haut Rhin', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('69', 'DEP', 'RHONE', 'Rhône', 'du Rhône', '00000000', '20143112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('69D', 'DEP', 'RHONE', 'Rhône', 'du Rhône', '20150101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('69M', 'DEP', 'METROPOLE DE LYON', 'Métropole de Lyon', 'de la Métropole de Lyon', '20150101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('70', 'DEP', 'HAUTE SAONE', 'Haute Saône', 'de la Haute Saône', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('71', 'DEP', 'SAONE ET LOIRE', 'Saône et Loire', 'de la Saône et Loire', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('72', 'DEP', 'SARTHE', 'Sarthe', 'de la Sarthe', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('73', 'DEP', 'SAVOIE', 'Savoie', 'de la Savoie', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('74', 'DEP', 'HAUTE SAVOIE', 'Haute Savoie', 'de la Haute Savoie', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('75', 'DEP', 'SEINE', 'Seine', 'de la Seine', '00000000', '19673112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('75', 'DEP', 'PARIS', 'Paris', 'de Paris', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('76', 'DEP', 'SEINE MARITIME', 'Seine Maritime', 'de la Seine Maritime', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('77', 'DEP', 'SEINE ET MARNE', 'Seine et Marne', 'de la Seine et Marne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('78', 'DEP', 'SEINE ET OISE', 'Seine et Oise', 'de la Seine et Oise', '00000000', '19673112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('78', 'DEP', 'YVELINES', 'Yvelines', 'des Yvelines', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('79', 'DEP', 'DEUX SEVRES', 'Deux Sèvres', 'des Deux Sèvres', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('80', 'DEP', 'SOMME', 'Somme', 'de la Somme', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('81', 'DEP', 'TARN', 'Tarn', 'du Tarn', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('82', 'DEP', 'TARN ET GARONNE', 'Tarn et Garonne', 'du Tarn et Garonne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('83', 'DEP', 'VAR', 'Var', 'du Var', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('84', 'DEP', 'VAUCLUSE', 'Vaucluse', 'du Vaucluse', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('85', 'DEP', 'VENDEE', 'Vendée', 'de la Vendée', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('86', 'DEP', 'VIENNE', 'Vienne', 'de la Vienne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('87', 'DEP', 'HAUTE VIENNE', 'Haute Vienne', 'de la Haute Vienne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('88', 'DEP', 'VOSGES', 'Vosges', 'des Vosges', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('89', 'DEP', 'YONNE', 'Yonne', 'de l''Yonne', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('90', 'DEP', 'TERRITOIRE DE BELFORT', 'Territoire de Belfort', 'du Territoire de Belfort', '00000000', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('91', 'DEP', 'ESSONNE', 'Essonne', 'de l''Essonne', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('92', 'DEP', 'HAUTS DE SEINE', 'Hauts de Seine', 'des Hauts de Seine', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('93', 'DEP', 'SEINE SAINT DENIS', 'Seine Saint Denis', 'de la Seine Saint Denis', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('94', 'DEP', 'VAL DE MARNE', 'Val de Marne', 'du Val de Marne', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('95', 'DEP', 'VAL D''OISE', 'Val d''Oise', 'du Val d''Oise', '19680101', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('971', 'DEP', 'GUADELOUPE', 'Guadeloupe', 'de la Guadeloupe', '19460319', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('972', 'DEP', 'MARTINIQUE', 'Martinique', 'de la Martinique', '19460319', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('973', 'DEP', 'GUYANE', 'Guyane', 'de la Guyane', '19460319', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('974', 'DEP', 'REUNION', 'Réunion', 'de la Réunion', '19460319', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('975', 'DEP', 'GUADELOUPE', 'Guadeloupe', 'de la Guadeloupe', '19460319', '19743112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('976', 'DEP', 'MARTINIQUE', 'Martinique', 'de la Martinique', '19460319', '19743112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('976', 'DEP', 'MAYOTTE', 'Mayotte', 'de Mayotte', '20090320', '99999999')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('977', 'DEP', 'GUYANE', 'Guyane', 'de la Guyane', '19460319', '19743112')")
    curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('978', 'DEP', 'REUNION', 'Réunion', 'de la Réunion', '19460319', '19743112')")

    base.commit()

    curseur.close()
    base.close()


####################################################################################################
def InsererPays():
    """ Insertion des pays et territoires du Code Officiel Géographique (COG) de l'INSEE """
    if not os.path.isfile(PAYS):
        Log(Severite.CRITIQUE, f"{PAYS}: fichier non trouvé")
        sys.exit(1)
    else:
        base = sqlite3.connect(BASE_DE_DONNEES)
        curseur = base.cursor()

        with open(PAYS, newline="") as fichier:
            champs = ["COG", "CRPAY", "LIBCOG", "LIBENR", "DATE_DEBUT", "DATE_FIN"]
            data = csv.DictReader(fichier, delimiter=",", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                # Conversion en majuscules non accentuées du nom du pays
                nom_maj = ligne['LIBCOG'].upper()
                nom_normalise = unicodedata.normalize('NFKD', nom_maj)
                nom_maj = "".join([c for c in nom_normalise if not unicodedata.combining(c)])

                pays = "PAYS"
                if ligne['CRPAY']:
                    pays += ":" + ligne['CRPAY']

                date_debut = ligne['DATE_DEBUT'].replace("-", "")
                if date_debut == "19430101":
                    date_debut = "00000000"

                date_fin = ligne['DATE_FIN'].replace("-", "")
                if date_fin == "":
                    date_fin = "99999999"

                curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?, ?)", (ligne['COG'], pays, nom_maj, ligne['LIBCOG'], ligne['LIBENR'], int(date_debut), int(date_fin)))

            # pays utilisés dans les fichiers de décès mais omis dans le COG
            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES ('99901', 'PAYS', 'EAUX INTERNATIONALES', 'Eaux internationales', 'Eaux internationales', '00000000', '99999999')")

            base.commit()

        curseur.close()
        base.close()

####################################################################################################
def InsererTerritoiresOutremer():
    """ Insertion des territoires d'outremer du Code Officiel Géographique (COG) de l'INSEE """
    if not os.path.isfile(TOM):
        Log(Severite.CRITIQUE, f"{TOM}: fichier non trouvé")
        sys.exit(1)
    else:
        base = sqlite3.connect(BASE_DE_DONNEES)
        curseur = base.cursor()

        with open(TOM, newline="") as fichier:
            champs = ["COMER", "TNCC", "NCC", "NCCENR", "LIBELLE", "DATE_DEBUT", "DATE_FIN"]
            data = csv.DictReader(fichier, delimiter=",", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                nom_maj, nom_riche = InclureArticleDansNom(ligne['TNCC'], ligne['NCC'], ligne['NCCENR'])

                date_debut = ligne['DATE_DEBUT'].replace("-", "")
                if date_debut == "19430101":
                    date_debut = "00000000"

                date_fin = ligne['DATE_FIN'].replace("-", "")
                if date_fin == "":
                    date_fin = "99999999"

                curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?, ?)", (ligne['COMER'], "TOM", nom_maj, nom_riche, ligne['LIBELLE'], int(date_debut), int(date_fin)))

            base.commit()

        curseur.close()
        base.close()

####################################################################################################
def ChargerCOG():
    """ Charge en mémoire la table des Codes Officiel Geographiques (COG) de l'INSEE """
    cog = {}

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    curseur.execute("SELECT * from cog")
    lignes = curseur.fetchall()
    for ligne in lignes:
        code = ligne[0]
        type_code = ligne[1]
        nom_maj = ligne[2]
        nom_riche = ligne[3]
        libelle = ligne[4]
        date_debut = ligne[5]
        date_fin = ligne[6]

        if code not in cog:
            cog[code] = []

        cog[code].append({"debut": date_debut, "fin": date_fin, "type": type_code, "nom_maj": nom_maj, "nom_riche": nom_riche, "libelle": libelle})

    curseur.close()
    base.close()

    return cog

####################################################################################################
def InsererExtensions(cog):
    """ Insertion des extensions du Code Officiel Géographique (COG) de l'INSEE """
    if not os.path.isfile(EXTENSIONS):
        Log(Severite.CRITIQUE, f"{EXTENSIONS}: fichier non trouvé")
        sys.exit(1)
    else:
        base = sqlite3.connect(BASE_DE_DONNEES)
        curseur = base.cursor()

        with open(EXTENSIONS, newline="") as fichier:
            champs = ["CODE_EXT", "CODE_GEO", "LIBGEO"]
            data = csv.DictReader(fichier, delimiter=",", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                if ligne['CODE_GEO'] not in cog:
                    Log(Severite.DONNEES_INCONSISTANTES, f"{EXTENSIONS}|{no_ligne}|CODE_GEO|COG inconnu|{ligne['CODE_GEO']}|")
                else:
                    for code in cog[ligne['CODE_GEO']]:
                        try:
                            curseur.execute("INSERT INTO cog (code, type, nom_maj, nom_riche, libelle, date_debut, date_fin) VALUES (?, ?, ?, ?, ?, ?, ?)", (ligne['CODE_EXT'], code['type'], code['nom_maj'], code['nom_riche'], code['libelle'], code['debut'], code['fin']))
                        except sqlite3.IntegrityError:
                            Log(Severite.DONNEES_INCONSISTANTES, f"{EXTENSIONS}|{no_ligne}|CODE_EXT|COG déjà présent|{ligne['CODE_EXT']}|ignoré")

            base.commit()

        curseur.close()
        base.close()

####################################################################################################
def InsererCOG():
    """ Insertion des données du Code Officiel Géographique (COG) de l'INSEE """
    Log(Severite.INFORMATION_IMPORTANTE, "===== Insertion des données du Code Officiel Géographique (COG) de l'INSEE =====")
    t1 = time.perf_counter()

    InsererCommunes()
    InsererCommunesOutremer()
    InsererDepartements()
    InsererPays()
    InsererTerritoiresOutremer()

    cog = ChargerCOG()
    InsererExtensions(cog)

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

####################################################################################################
def ChargerFichierDesOppositions():
    """ Charge en mémoire le fichier des oppositions """
    oppositions = {}
    if not os.path.isfile(OPPOSITIONS):
        Log(Severite.CRITIQUE, f"{OPPOSITIONS}: fichier non trouvé")
        sys.exit(1)
    else:
        with open(OPPOSITIONS, newline="") as fichier:
            champs = ["Date de décès", "Code du lieu de décès", "Numéro d'acte de décès"]
            data = csv.DictReader(fichier, delimiter=";", fieldnames=champs)
            no_ligne = 0
            for ligne in data:
                no_ligne += 1
                if no_ligne == 1:
                    continue

                if ligne["Date de décès"] not in oppositions:
                    oppositions[ligne["Date de décès"]] = {}
                if ligne["Code du lieu de décès"] not in oppositions[ligne["Date de décès"]]:
                    oppositions[ligne["Date de décès"]][ligne["Code du lieu de décès"]] = {}
                if ligne["Numéro d'acte de décès"] not in oppositions[ligne["Date de décès"]][ligne["Code du lieu de décès"]]:
                    acte_deces = re.sub(r"^0*", "", ligne["Numéro d'acte de décès"])
                    oppositions[ligne["Date de décès"]][ligne["Code du lieu de décès"]][acte_deces] = 0 # nombre d'occurrences rencontrées
            infos["info.opposition.lignes"] = no_ligne - 1

    return oppositions

####################################################################################################
def ChargerPrenoms():
    """ Charge en mémoire la table des prénoms """
    prenoms = {}

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    curseur.execute("SELECT * from prenoms")
    lignes = curseur.fetchall()
    for ligne in lignes:
        id_prenom = ligne[0]
        prenom = ligne[1]

        if prenom not in prenoms:
            prenoms[prenom] = id_prenom

    curseur.close()
    base.close()

    return prenoms

####################################################################################################
def TrouverNomCommuneEtPays(cog, code, date_evenement):
    """ Recherche le nom d'une commune ou d'un pays dans le Code Officiel Geographique (COG) de l'INSEE à partir d'un code et d'une date """
    commune = ""
    pays = ""
    trouve = False
    evenement = int(date_evenement)

    if code in cog:
        for ligne in cog[code]:
            # au cas où la date d'événement ne correspondrait à aucune entrée
            # mais où il y aurait des résultats pour d'autres périodes
            # on note quand même le dernier résultat
            if code.startswith("99"):
                pays = ligne["nom_maj"]
            else:
                pays = "FRANCE"
                commune = ligne["nom_maj"]

            if evenement >= ligne["debut"] and evenement <= ligne["fin"]:
                trouve = True
                break
    elif code == "99990":
        pass
    elif code.endswith("990"): # commune inconnue
        # on fait une recherche du département
        for ligne in cog[code[0:2]]:
            pays = "FRANCE"
            nom_maj = ligne['libelle'].upper()
            nom_normalise = unicodedata.normalize('NFKD', nom_maj)
            nom_maj = "".join([c for c in nom_normalise if not unicodedata.combining(c)])
            commune = "COMMUNE " + nom_maj

            if evenement >= ligne["debut"] and evenement <= ligne["fin"]:
                trouve = True
                break

    return commune, pays, trouve

####################################################################################################
def InsererFichierDeDeces(nom_fichier, oppositions, cog, table_prenoms):
    """ Insertion des données de décès d'un fichier """
    Log(Severite.INFORMATION_IMPORTANTE, f"===== Traitement de '{nom_fichier}' =====")
    t1 = time.perf_counter()

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    curseur.execute("SELECT seq FROM sqlite_sequence WHERE name = 'personnes'")
    ligne = curseur.fetchone()
    if ligne:
        prochain_id_personne = ligne[0] + 1
    else:
        prochain_id_personne = 1

    curseur.execute("SELECT seq FROM sqlite_sequence WHERE name = 'prenoms'")
    ligne = curseur.fetchone()
    if ligne:
        prochain_id_prenom = ligne[0] + 1
    else:
        prochain_id_prenom = 1

    annee_du_fichier = re.sub(r'[^0-9]', '', nom_fichier)[0:4]
    annee_actuelle = datetime.datetime.now().date().year
    mois_actuel = datetime.datetime.now().date().month
    jour_actuel = datetime.datetime.now().date().day
    with open(nom_fichier, newline="") as fichier:
        champs = ['nomprenom', 'sexe', 'datenaiss', 'lieunaiss', 'commnaiss', 'paysnaiss', 'datedeces', 'lieudeces', 'actedeces']
        data = csv.DictReader(fichier, delimiter=";", fieldnames=champs)
        no_ligne = 0
        for ligne in data:
            no_ligne += 1
            if no_ligne == 1:
                continue

            nom = ""
            prenoms = ""
            annee_naissance = ""
            mois_naissance = ""
            jour_naissance = ""
            lieu_naissance = ""
            commune_naissance = ""
            pays_naissance = ""
            annee_deces = ""
            mois_deces = ""
            jour_deces = ""
            lieu_deces = ""
            commune_deces = ""
            pays_deces = ""
            acte_deces = ""
            opposition = ""

            # nom et prénoms
            # NB: on va traiter les doublons après...
            match = re.match(r"([^\*]*)\*([^/]*)/", ligne['nomprenom'])
            if match:
                nom = match.group(1)
                prenoms = match.group(2)
            else:
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|nomprenom|Pas de la forme 'NOM*PRENOMS/'|{ligne['nomprenom']}|{nom}*{prenoms}/")
                infos["erreur.nomprenom.format_incorrect"] += 1
                if "*" in ligne['nomprenom']:
                    nom = ligne['nomprenom'].split("*")[0]
                    if len(ligne['nomprenom']) < 68:
                        prenoms = ligne['nomprenom'].split("*")[1]
                    else:
                        prenoms = ligne['nomprenom'].split("*")[1] + "..."
                elif "/" in ligne['nomprenom']:
                    prenoms = ligne['nomprenom'].split("/")[0]
                else:
                    nom = ligne['nomprenom'] + "..."

            # sexe
            # NB: on ne vérifie pas la compatibilité avec le prénom principal, notamment parce que l'état cibil se trompe parfois sur le sexe !
            if ligne['sexe'] not in ["1", "2"]:
                sexe = "?"
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|sexe|Code inconnu|{ligne['sexe']}|{sexe}")
                infos["erreur.sexe.valeur_inconnue"] += 1

            # date de naissance
            if ligne['datenaiss'] == "":
                annee_naissance = "0000"
                mois_naissance = "00"
                jour_naissance = "00"
                #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|datenaiss|Vide|{ligne['datenaiss']}|00000000")
                infos["erreur.datenaiss.vide"] += 1
            elif ligne['datenaiss'].isdigit():
                date_corrigee = ligne['datenaiss']
                if len(date_corrigee) != 8:
                    if len(date_corrigee) < 4:
                        date_corrigee = "00000000"
                    elif len(date_corrigee) < 6:
                        date_corrigee = date_corrigee[0:4] + "0000"
                    elif len(date_corrigee) < 8:
                        date_corrigee = date_corrigee[0:6] + "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|Taille incorrecte|{ligne['datenaiss']}|{date_corrigee}")
                    infos["erreur.datenaiss.taille_incorrecte"] += 1
                    
                annee_naissance = date_corrigee[0:4]
                if annee_naissance != "0000" and int(annee_naissance) < 1840:
                    annee_naissance = "0000"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datenaiss|Année < 1840|{ligne['datenaiss']}|0000mmjj")
                    infos["erreur.datenaiss.avant_1840"] += 1
                elif annee_naissance != "0000" and int(annee_naissance) > int(annee_du_fichier):
                    annee_naissance = "0000"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|Année > {annee_du_fichier} (année du fichier)|{ligne['datenaiss']}|0000mmjj")
                    infos["erreur.datenaiss.dans_le_futur"] += 1
                mois_naissance = date_corrigee[4:6]
                if mois_naissance != "00" and int(mois_naissance) > 12:
                    mois_naissance = "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|Mois > 12|{ligne['datenaiss']}|aaaa00jj")
                    infos["erreur.datenaiss.mois_incorrect"] += 1
                jour_naissance = date_corrigee[6:]
                if jour_naissance != "00" and int(jour_naissance) > 31:
                    jour_naissance = "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|Jour > 31|{ligne['datenaiss']}|aaaamm00")
                    infos["erreur.datenaiss.jour_incorrect"] += 1
            else:
                annee_naissance = "0000"
                mois_naissance = "00"
                jour_naissance = "00"
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|Pas de la forme 'AAAAMMJJ'|{ligne['datenaiss']}|00000000")
                infos["erreur.datenaiss.non_numerique"] += 1

            # date de naissance potentiellement approximative (pour les comparaisons de dates)
            if annee_naissance == "0000":
                date_naissance = "0001"
            else:
                date_naissance = annee_naissance
            if mois_naissance == "00":
                date_naissance += "01"
            else:
                date_naissance += mois_naissance
            if jour_naissance == "00":
                date_naissance += "01"
            else:
                date_naissance += jour_naissance

            # recherche de fates impossibles (ex: 19000229, xxxx0631)
            try:
                _ = datetime.date.fromisoformat(date_naissance)
            except:
                jour_naissance = "00"
                date_naissance = date_naissance[0:6] + "01"
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datenaiss|date impossible|{ligne['datenaiss']}|{annee_naissance}{mois_naissance}{jour_naissance}")
                infos["erreur.datenaiss.date_impossible"] += 1

            # code INSEE du lieu de naissance (avec gestion de quelques cas particuliers)
            if ligne['lieunaiss'] == "":
                lieu_naissance = "00000"
                #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Vide|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.vide"] += 1
            elif ligne['lieunaiss'] == "00000":
                lieu_naissance = ligne['lieunaiss']
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code '{lieu_naissance}'|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.commune_inconnue"] += 1
            elif ligne['lieunaiss'] == "99990":
                lieu_naissance = ligne['lieunaiss']
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code '{lieu_naissance}'|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.pays_inconnu"] += 1
            elif ligne['lieunaiss'] == "99":
                lieu_naissance = "99990" # apparemment utilisé pour désigner un pays inconnu
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Pays inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.pays_inconnu"] += 1
            elif ligne['lieunaiss'][2:] == "990": # apparemment utilisé pour désigner une commune française inconnue
                lieu_naissance = ligne['lieunaiss']
                ligne['commnaiss'] = ""
                ligne['paysnaiss'] = "FRANCE"
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Commune inconnue 1/3|{ligne['lieunaiss']}|{lieu_naissance}")
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Commune inconnue 2/3|commnaiss:{ligne['commnaiss']}|")
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Commune inconnue 3/3|paynaiss:{ligne['paysnaiss']}|FRANCE")
                infos["erreur.lieunaiss.commune_inconnue"] += 1
            elif ligne['lieunaiss'] in ["91", "91352", "92", "92352", "93", "93352", "94", "94352"]: # Algérie Française
                lieu_naissance = ligne['lieunaiss'][0:2]
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Algérie française 1/2|{ligne['lieunaiss']}|{lieu_naissance}")
                commnaiss_origine = ligne['commnaiss']
                ligne['commnaiss'] = re.sub(" ALGERIE$", "", ligne['commnaiss'])
                if ligne['commnaiss'].startswith("DEPARTEMENT") or ligne['commnaiss'] == "SUD DE L'ALGERIE":
                    ligne['commnaiss'] = ""
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Algérie française 2/2|commnaiss:{commnaiss_origine}|{ligne['commnaiss']}")
                infos["erreur.lieunaiss.commune_inconnue"] += 1
            elif ligne['lieunaiss'] == "123" and ligne['commnaiss'] == "EREVAN":
                lieu_naissance = "99123" # URSS
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "99146" and ligne['paysnaiss'] == "ANCIENNE ARMENIE": 
                lieu_naissance = "99123" # URSS
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "95025" and ligne['commnaiss'] == "ARTHIEUL":
                lieu_naissance = "78025" # Arthieul (erreur de code apparemment)
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "95065" and ligne['commnaiss'] == "BLAMECOURT":
                lieu_naissance = "78065" # Blamécourt (erreur de code apparemment)
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "99147" and ligne['commnaiss'] == "PAPEETE": 
                lieu_naissance = "98601" # Îles du Vent
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "99150" and ligne['commnaiss'] == "ESSAOUAIRA": 
                lieu_naissance = "95332" # Mogador (ancien nom d'Essaouira)
                ligne['paysnaiss'] = "MAROC"
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|paysnaiss|Libellé pays|{ligne['paysnaiss']}|MAROC")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "20000" and ligne['commnaiss'] == "CASABLANCA":
                lieu_naissance = "95101" # Casablanca
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "98308" and ligne['commnaiss'] == "BRAZZAVILLE":
                lieu_naissance = "98302" # Moyen-Congo
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconnu"] += 1
            elif ligne['lieunaiss'] == "984" and ligne['commnaiss'] == "ADDIS ABEBA":
                lieu_naissance = "99315" # Éthiopie
                Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code incompatible avec commune|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconsistant_avec_commune"] += 1
            elif ligne['lieunaiss'] == "984" and ligne['commnaiss'] == "PORT-LYAUTEY": 
                lieu_naissance = "95661" # Port-Lyautey
                Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code incompatible avec commune|{ligne['lieunaiss']}|{lieu_naissance}")
                infos["erreur.lieunaiss.code_inconsistant_avec_commune"] += 1
            else:
                match = re.match(r"^([0-9][0-9AB][0-9DM][0-9][0-9])$", ligne['lieunaiss'])
                if match:
                    lieu_naissance = match.group(1)
                else:
                    lieu_naissance = "00000"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Pas de la forme 'XXXXX'|{ligne['lieunaiss']}|{lieu_naissance}")
                    infos["erreur.lieunaiss.format_incorrect"] += 1

            # commune et pays de naissance (orthographe variable redressée)
            if lieu_naissance in ["00000", "99990"]:
                commune_naissance = ligne['commnaiss']
                pays_naissance = ligne['paysnaiss']
            else:
                commune_naissance, pays_naissance, trouve = TrouverNomCommuneEtPays(cog, lieu_naissance, date_naissance)
                if lieu_naissance.startswith("99"):
                    commune_naissance = ligne['commnaiss'] # seul moyen de l'obtenir, le code désignant un pays
                    if not trouve:
                        if pays_naissance == "":
                            if ligne['paysnaiss'] != "":
                                pays_naissance = ligne['paysnaiss']
                                Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu à cette date|{ligne['lieunaiss']}@datenaiss:{date_naissance}|{lieu_naissance}")
                                infos["erreur.lieunaiss.code_inconnu_a_date"] += 1
                else:
                    if not trouve:
                        if commune_naissance == "":
                            if ligne['commnaiss'] != "":
                                commune_naissance = ligne['commnaiss']
                                Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieunaiss|Code inconnu à cette date|{ligne['lieunaiss']}@datenaiss:{date_naissance}|{lieu_naissance}")
                                infos["erreur.lieunaiss.code_inconnu_a_date"] += 1
                if commune_naissance != ligne['commnaiss']:
                    #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|commnaiss|Valeur modifiée|{ligne['commnaiss']}|{commune_naissance}")
                    infos["erreur.commnaiss.commune_mal_orthographiee"] += 1
                if pays_naissance != ligne['paysnaiss'] and pays_naissance != "FRANCE":
                    #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|paysnaiss|Valeur modifiée|{ligne['paysnaiss']}|{pays_naissance}")
                    infos["erreur.paysnaiss.pays_mal_orthographie"] += 1

            # date de décès
            if ligne['datedeces'] == "":
                annee_deces = annee_du_fichier
                mois_deces = "00"
                jour_deces = "00"
                #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|datedeces|Vide|{ligne['datedeces']}|{annee_deces}0000")
                infos["erreur.datedeces.vide"] += 1
            elif ligne['datedeces'].isdigit():
                date_corrigee = ligne['datedeces']
                if len(date_corrigee) != 8:
                    if len(date_corrigee) < 4:
                        date_corrigee = "00000000"
                    elif len(date_corrigee) < 6:
                        date_corrigee = date_corrigee[0:4] + "0000"
                    elif len(date_corrigee) < 8:
                        date_corrigee = date_corrigee[0:6] + "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datedeces|Taille incorrecte|{ligne['datedeces']}|{date_corrigee}")
                    infos["erreur.datedeces.taille_incorrecte"] += 1
                    
                annee_deces = date_corrigee[0:4]
                if annee_deces != "0000" and annee_naissance != "0000" and int(annee_deces) < int(annee_naissance):
                    annee_deces = "0000"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datedeces|Date < année de naissance|{ligne['datedeces']}//datenaiss:{date_naissance}|0000mmjj")
                    infos["erreur.datedeces.avant_naissance"] += 1
                elif annee_deces != "0000" and int(annee_deces) > annee_actuelle:
                    annee_deces = "0000"
                    mois_deces = "00"
                    jour_deces = "00"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datedeces|Date future|{ligne['datedeces']}|00000000")
                    infos["erreur.datedeces.dans_le_futur"] += 1
                mois_deces = date_corrigee[4:6]
                if mois_deces != "00" and int(mois_deces) > 12:
                    mois_deces = "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datedeces|Mois > 12|{ligne['datedeces']}|aaaa00jj")
                    infos["erreur.datedeces.mois_incorrect"] += 1
                elif int(annee_deces) == annee_actuelle and mois_deces != "00" and int(mois_deces) > mois_actuel:
                    annee_deces = "0000"
                    mois_deces = "00"
                    jour_deces = "00"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datedeces|Date future|{ligne['datedeces']}|00000000")
                    infos["erreur.datedeces.dans_le_futur"] += 1
                jour_deces = date_corrigee[6:]
                if jour_deces != "00" and int(jour_deces) > 31:
                    jour_deces = "00"
                    Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datedeces|Jour > 31|{ligne['datedeces']}|aaaamm00")
                    infos["erreur.datedeces.jour_incorrect"] += 1
                elif int(annee_deces) == annee_actuelle and int(mois_deces) == mois_actuel and jour_deces != "00" and int(jour_deces) > jour_actuel:
                    annee_deces = "0000"
                    mois_deces = "00"
                    jour_deces = "00"
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datedeces|Date future|{ligne['datedeces']}|00000000")
                    infos["erreur.datedeces.dans_le_futur"] += 1
            else:
                annee_deces = "0000"
                mois_deces = "00"
                jour_deces = "00"
                Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|datedeces|Pas de la forme 'AAAAMMJJ'|{ligne['datedeces']}|00000000")
                infos["erreur.datedeces.non_numerique"] += 1

            # date de décès potentiellement approximative (pour les comparaisons de dates)
            if annee_deces == "0000":
                date_deces = "9999"
            else:
                date_deces = annee_deces
            if mois_deces == "00":
                date_deces += "12"
            else:
                date_deces += mois_deces
            if jour_deces == "00":
                if mois_deces in ["00", "01", "03", "05", "07", "08", "10", "12"]:
                    date_deces += "31"
                elif mois_deces in ["04", "06", "09", "11"]:
                    date_deces += "30"
                else:
                    date_deces += "28" # on ne s'embête pas avec les années bisextiles...
            else:
                date_deces += jour_deces

            if date_naissance != "00010101" and date_deces != "99991231":
                delta = datetime.date.fromisoformat(date_deces) - datetime.date.fromisoformat(date_naissance)
                age = delta.days / 365
                if age >= 123 and age < 250:
                    Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|datedeces|Âge > 122 ans|{age:.0f}|")
                    infos["erreur.datedeces.age_trop_grand"] += 1

            # code INSEE du lieu de décès
            if ligne['lieudeces'] == "":
                lieu_deces = "00000"
                #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Vide|{ligne['lieudeces']}|{lieu_deces}")
                infos["erreur.lieudeces.vide"] += 1
            elif ligne['lieudeces'] == "00000":
                lieu_deces = ligne['lieudeces']
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Code '{lieu_deces}'|{ligne['lieudeces']}|{lieu_deces}")
                infos["erreur.lieudeces.commune_inconnue"] += 1
            elif ligne['lieudeces'] == "99990":
                lieu_deces = ligne['lieudeces']
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Code '{lieu_deces}'|{ligne['lieudeces']}|{lieu_deces}")
                infos["erreur.lieudeces.pays_inconnu"] += 1
            elif ligne['lieudeces'] == "99":
                lieu_deces = "99990"
                #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Code inconnu|{ligne['lieudeces']}|{lieu_deces}")
                infos["erreur.lieudeces.pays_inconnu"] += 1
            else:
                match = re.match(r"^([0-9][0-9AB][0-9DM][0-9][0-9])$", ligne['lieudeces'])
                if match:
                    lieu_deces = match.group(1)
                else:
                    if ligne['lieudeces'] == "-   -": # Cas particulier
                        lieu_deces = "99990" # Inconnu
                        Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieudeces|Code inconnu|{ligne['lieudeces']}|{lieu_deces}")
                        infos["erreur.lieudeces.format_incorrect"] += 1
                    elif ligne['lieudeces'] == "20": # Cas particulier
                        lieu_deces = "20990" # Commune de Corse inconnue
                        Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Code inconnu|{ligne['lieudeces']}|{lieu_deces}")
                        infos["erreur.lieudeces.commune_inconnue"] += 1
                    elif ligne['lieudeces'] == "38": # Cas particulier
                        lieu_deces = "38990" # Commune de l'Isère inconnue
                        Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|lieudeces|Code inconnu|{ligne['lieudeces']}|{lieu_deces}")
                        infos["erreur.lieudeces.commune_inconnue"] += 1
                    else:
                        lieu_deces = "99990"
                        Log(Severite.DONNEES_ERRONEES, f"{nom_fichier}|{no_ligne}|lieudeces|Pas de la forme 'XXXXX'|{ligne['lieudeces']}|{lieu_deces}")
                        infos["erreur.lieudeces.format_incorrect"] += 1

            # commune et pays de décès
            commune_deces, pays_deces, trouve = TrouverNomCommuneEtPays(cog, lieu_deces, date_deces)

            # acte de décès
            # TODO: vérifier si utilisé pour plusieurs personnes ?
            acte_deces = re.sub(r"^0*", "", ligne['actedeces'])
            if not acte_deces.isdigit():
                #Log(Severite.DONNEES_MANQUANTES, f"{nom_fichier}|{no_ligne}|actedeces|Contient des caractères non numériques|{ligne['actedeces']}|{acte_deces}")
                infos["erreur.actedeces.non_numerique"] += 1

            # opposition ?
            try:
                nb_oppositions = oppositions[annee_deces + mois_deces + jour_deces][lieu_deces][acte_deces]
                opposition = "1"
                oppositions[annee_deces + mois_deces + jour_deces][lieu_deces][acte_deces] += 1
                if nb_oppositions >= 1:
                    #Log(Severite.DONNEES_INCONSISTANTES, f"{nom_fichier}|{no_ligne}|actedeces|Réutilisé {nb_oppositions + 1} fois|{annee_deces + mois_deces + jour_deces}/{ligne['lieudeces']}/{acte_deces}|")
                    infos["erreur.opposition.utilisation_multiple"] += 1
            except KeyError:
                opposition = "0"
            
            curseur.execute("INSERT INTO personnes (nom, prenoms, sexe, annee_naissance, mois_naissance, jour_naissance, date_naissance, lieu_naissance, commune_naissance, pays_naissance, annee_deces, mois_deces, jour_deces, date_deces, lieu_deces, commune_deces, pays_deces, acte_deces, opposition) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (nom, prenoms, ligne['sexe'], annee_naissance, mois_naissance, jour_naissance, date_naissance, lieu_naissance, commune_naissance, pays_naissance, annee_deces, mois_deces, jour_deces, date_deces, lieu_deces, commune_deces, pays_deces, acte_deces, opposition))

            # prénoms
            ordre = 1
            for prenom in prenoms.split():
                if prenom in table_prenoms:
                    curseur.execute("INSERT INTO prenoms_personne (id_personne, id_prenom, ordre) VALUES (?, ?, ?)", (prochain_id_personne, table_prenoms[prenom], ordre))
                else:
                    # nouveau prénom
                    curseur.execute("INSERT INTO prenoms (prenom) VALUES (?)", (prenom,)) # la virgule après prenom indique un tuple. C'est nécessaire !
                    table_prenoms[prenom] = prochain_id_prenom

                    curseur.execute("INSERT INTO prenoms_personne (id_personne, id_prenom, ordre) VALUES (?, ?, ?)", (prochain_id_personne, prochain_id_prenom, ordre))

                    prochain_id_prenom += 1

                ordre += 1

            prochain_id_personne += 1

    base.commit()

    curseur.close()
    base.close()

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

    return table_prenoms, oppositions

####################################################################################################
def VerifierOppositions(oppositions):
    """ Vérifie les anomalies dans l'utilisation des oppositions """
    for date_deces, value1 in oppositions.items():
        for lieu_deces, value2 in value1.items():
            for acte_deces, nb_occurrences in value2.items():
                if nb_occurrences == 0:
                    Log(Severite.INFORMATION, f"oppositions.csv|?|{date_deces}|{lieu_deces}|{acte_deces}|Non utilisée|")
                    infos["info.opposition.lignes_inutilisees"] += 1
                elif nb_occurrences > 1:
                    #Log(Severite.INFORMATION, f"oppositions.csv|?|{date_deces}|{lieu_deces}|{acte_deces}|Réutilisée|{nb_occurrences}")
                    infos["info.opposition.lignes_reutilisees"] += 1

####################################################################################################
def PurgerDoublons():
    """ Purge les doublons de la base de données """
    Log(Severite.INFORMATION_IMPORTANTE, "===== Suppression des doublons =====")
    t1 = time.perf_counter()

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    # Doublons complets (tous les champs identiques sauf l'id)
    # comptage :
    curseur.execute("""
WITH doublons AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY 
                nom, prenoms, sexe, 
                annee_naissance, mois_naissance, jour_naissance, date_naissance, lieu_naissance, commune_naissance, pays_naissance,
                annee_deces, mois_deces, jour_deces, date_deces, lieu_deces, commune_deces, pays_deces, acte_deces,
                opposition
            ORDER BY id
        ) AS rang
    FROM personnes
)
SELECT count(*)
FROM doublons 
WHERE rang > 1
""")
    ligne = curseur.fetchone()
    if ligne:
        infos["erreur.doublons.complets"] = ligne[0]

    # suppression :
    curseur.execute("""
DELETE FROM personnes
WHERE id IN (
    SELECT id 
    FROM (
        SELECT id, 
               ROW_NUMBER() OVER (
                   PARTITION BY 
                       nom, prenoms, sexe, 
                       annee_naissance, mois_naissance, jour_naissance, date_naissance, lieu_naissance, commune_naissance, pays_naissance,
                       annee_deces, mois_deces, jour_deces, date_deces, lieu_deces, commune_deces, pays_deces, acte_deces,
                       opposition
                   ORDER BY id
               ) AS rang 
        FROM personnes
    ) 
    WHERE rang > 1
)
""")

    base.commit()

    curseur.close()
    base.close()

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

####################################################################################################
def InsererInfos():
    """ Insère les informations de comptage dans la base de données """
    Log(Severite.INFORMATION_IMPORTANTE, "===== Insertion des informations de comptage =====")
    t1 = time.perf_counter()

    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.nomprenom.format_incorrect', 'Champ nomprenom avec format incorrect', infos["erreur.nomprenom.format_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.sexe.valeur_inconnue', 'Champ sexe avec valeur inconnue', infos["erreur.sexe.valeur_inconnue"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.vide', 'Champ datenaiss vide', infos["erreur.datenaiss.vide"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.taille_incorrecte', 'Champ datenaiss de taille incorrecte', infos["erreur.datenaiss.taille_incorrecte"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.avant_1840', 'Champ datenaiss avec valeur < 1840', infos["erreur.datenaiss.avant_1840"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.dans_le_futur', 'Champ datenaiss avec valeur dans le futur', infos["erreur.datenaiss.dans_le_futur"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.mois_incorrect', 'Champ datenaiss avec mois > 12', infos["erreur.datenaiss.mois_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.jour_incorrect', 'Champ datenaiss avec jour > 31', infos["erreur.datenaiss.jour_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.non_numerique', 'Champ datenaiss avec valeur non numérique', infos["erreur.datenaiss.non_numerique"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datenaiss.date_impossible', 'Champ datenaiss avec date impossible', infos["erreur.datenaiss.date_impossible"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.vide', 'Champ lieunaiss vide', infos["erreur.lieunaiss.vide"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.commune_inconnue', 'Champ lieunaiss indiquant une commune inconnue', infos["erreur.lieunaiss.commune_inconnue"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.pays_inconnu', 'Champ lieunaiss indiquant un pays inconnu', infos["erreur.lieunaiss.pays_inconnu"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.code_inconnu', 'Champ lieunaiss avec code inconnu', infos["erreur.lieunaiss.code_inconnu"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.code_inconsistant_avec_commune', 'Champ lieunaiss ne correspondant pas à la commune', infos["erreur.lieunaiss.code_inconsistant_avec_commune"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.format_incorrect', 'Champ lieunaiss avec format incorrect', infos["erreur.lieunaiss.format_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieunaiss.code_inconnu_a_date', 'Champ lieunaiss utilisant un code inexistant à cette date', infos["erreur.lieunaiss.code_inconnu_a_date"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.commnaiss.commune_mal_orthographiee', 'Champ commnaiss mal orthographié', infos["erreur.commnaiss.commune_mal_orthographiee"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.paysnaiss.pays_mal_orthographie', 'Champ paysnaiss mal orthographié', infos["erreur.paysnaiss.pays_mal_orthographie"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.vide', 'Champ datedeces vide', infos["erreur.datedeces.vide"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.taille_incorrecte', 'Champ datedeces de taille incorrecte', infos["erreur.datedeces.taille_incorrecte"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.avant_naissance', 'Champ datedeces avant datenaiss', infos["erreur.datedeces.avant_naissance"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.dans_le_futur', 'Champ datedeces avec valeur dans le futur', infos["erreur.datedeces.dans_le_futur"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.mois_incorrect', 'Champ datedeces avec mois > 12', infos["erreur.datedeces.mois_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.jour_incorrect', 'Champ datedeces avec jour > 31', infos["erreur.datedeces.jour_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.non_numerique', 'Champ datedeces avec valeur non numérique', infos["erreur.datedeces.non_numerique"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.datedeces.age_trop_grand', 'Champ datedeces avec âge > 122 ans', infos["erreur.datedeces.age_trop_grand"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieudeces.vide', 'Champ lieudeces vide', infos["erreur.lieudeces.vide"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieudeces.commune_inconnue', 'Champ lieudeces indiquant une commune inconnue', infos["erreur.lieudeces.commune_inconnue"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieudeces.pays_inconnu', 'Champ lieudeces indiquant un pays inconnu', infos["erreur.lieudeces.pays_inconnu"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.lieudeces.format_incorrect', 'Champ lieudeces avec format incorrect', infos["erreur.lieudeces.format_incorrect"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.actedeces.non_numerique', 'Champ actedeces avec valeur non numérique', infos["erreur.actedeces.non_numerique"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.opposition.utilisation_multiple', 'Opposition utilisée plusieurs fois', infos["erreur.opposition.utilisation_multiple"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('erreur.doublons.complets', 'Doublons complets', infos["erreur.doublons.complets"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('info.opposition.lignes', 'Oppositions : nombre de lignes', infos["info.opposition.lignes"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('info.opposition.lignes_inutilisees', 'Oppositions : nombre de lignes inutilisées', infos["info.opposition.lignes_inutilisees"]))
    curseur.execute("INSERT INTO infos (cle, libelle, valeur) VALUES (?, ?, ?)", ('info.opposition.lignes_reutilisees', 'Oppositions : nombre de lignes réutilisées', infos["info.opposition.lignes_reutilisees"]))

    base.commit()

    curseur.close()
    base.close()

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

####################################################################################################
def CreerIndexes():
    """ Crée les indexes de la base de données """
    base = sqlite3.connect(BASE_DE_DONNEES)
    curseur = base.cursor()

    Log(Severite.INFORMATION_IMPORTANTE, "===== Création de l'index sur cog:code =====")
    t1 = time.perf_counter()
    curseur.execute("CREATE INDEX index_codes ON cog(code)")
    base.commit()
    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

    Log(Severite.INFORMATION_IMPORTANTE, "===== Création de l'index sur personnes:nom =====")
    t1 = time.perf_counter()
    curseur.execute("CREATE INDEX index_noms ON personnes(nom)")
    base.commit()
    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

    Log(Severite.INFORMATION_IMPORTANTE, "===== Création de l'index sur prenoms:prenom =====")
    t1 = time.perf_counter()
    curseur.execute("CREATE INDEX index_prenoms ON prenoms(prenom)")
    base.commit()
    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

    Log(Severite.INFORMATION_IMPORTANTE, "===== Création de l'index sur prenoms_personne:id_personne =====")
    t1 = time.perf_counter()
    curseur.execute("CREATE INDEX index_id_personnes ON prenoms_personne(id_personne)")
    base.commit()
    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Exécuté en {t2 - t1:.3f} secondes")

    curseur.close()
    base.close()

####################################################################################################
def main():
    """ Fonction principale """
    t1 = time.perf_counter()

    if not os.path.exists(BASE_DE_DONNEES):
        InitialiserBaseDeDonnees()
        InsererCOG()
    elif not os.path.isfile(BASE_DE_DONNEES):
        Log(Severite.CRITIQUE, f"{BASE_DE_DONNEES}: pas un fichier")
        sys.exit(1)

    oppositions = ChargerFichierDesOppositions()
    cog = ChargerCOG()
    prenoms = ChargerPrenoms()

    for parametre in sys.argv[1:]:
        if parametre.endswith(".csv"):
            prenoms, oppositions = InsererFichierDeDeces(parametre, oppositions, cog, prenoms)

    VerifierOppositions(oppositions)

    PurgerDoublons()

    InsererInfos()

    CreerIndexes()

    t2 = time.perf_counter()
    Log(Severite.INFORMATION, f"Globalement exécuté en {t2 - t1:.3f} secondes")

    pprint.pprint(infos)

    sys.exit(0)

####################################################################################################
main()
