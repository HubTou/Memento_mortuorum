#!/bin/sh
##################################################
#                                                #
# Memento mortuorum                              #
# (c) 2026+ Hubert Tournier                      #
#                                                #
# Téléchargement incrémental des données sources #
#                                                #
##################################################

DOWNLOADER=fetch # available on all FreeBSD systems
#DOWNLOADER=curl

URL_DECENNALE=https://www.insee.fr/fr/statistiques/fichier/4769950
URL_ANNUELLE=https://www.insee.fr/fr/statistiques/fichier/4190491
URL_OPPOSITIONS=https://www.data.gouv.fr/fr/datasets/r/7bcdfa57-dc50-43a8-beb6-6c76537e7057
URL_COG=https://www.insee.fr/fr/statistiques/fichier/8740222
INDICATEUR=../.nouveaux_fichiers

mkdir -p data/ZIP
mkdir -p data/COG
cd data

# Téléchargement des fichiers décennaux
ANNEE_COURANTE=`date "+%Y"`
DEBUT_DECENNIE=1970
FIN_DECENNIE=1979
while [ "${FIN_DECENNIE}" -lt "${ANNEE_COURANTE}" ]
do
    FICHIER=deces-${DEBUT_DECENNIE}-${FIN_DECENNIE}-csv.zip
    if [ ! -f ZIP/${FICHIER} ]
    then
        ${DOWNLOADER} ${URL_DECENNALE}/${FICHIER} -o ZIP
        if [ -f ZIP/${FICHIER} ]
        then
            unzip ZIP/${FICHIER}
            touch ${INDICATEUR}
        fi
    fi
    DEBUT_DECENNIE=`expr ${DEBUT_DECENNIE} + 10`
    FIN_DECENNIE=`expr ${FIN_DECENNIE} + 10`
done

# Téléchargement des fichiers annuels
ANNEE=`expr ${FIN_DECENNIE} - 9`
while [ "${ANNEE}" -lt "${ANNEE_COURANTE}" ]
do
    FICHIER=Deces_${ANNEE}.zip
    if [ ! -f ZIP/${FICHIER} ]
    then
        ${DOWNLOADER} ${URL_ANNUELLE}/${FICHIER} -o ZIP
        if [ -f ZIP/${FICHIER} ]
        then
            unzip ZIP/${FICHIER}
            touch ${INDICATEUR}
            ANNEE_PRECEDENTE=`expr ${ANNEE} - 1`
            rm -f Deces_${ANNEE_PRECEDENTE}_M*.csv
        fi
    fi
    ANNEE=`expr ${ANNEE} + 1`
done

# Téléchargement des fichiers mensuels
MOIS_COURANT=`date "+%m"`
MOIS="01"
while [ "${MOIS}" -lt "${MOIS_COURANT}" ]
do
    FICHIER=Deces_${ANNEE_COURANTE}_M${MOIS}.zip
    if [ ! -f ZIP/${FICHIER} ]
    then
        ${DOWNLOADER} ${URL_ANNUELLE}/${FICHIER} -o ZIP
        if [ -f ZIP/${FICHIER} ]
        then
            unzip ZIP/${FICHIER}
            touch ${INDICATEUR}
        fi
    fi
    MOIS_SUIVANT=`expr ${MOIS} + 1`
    MOIS=`printf "%02d" ${MOIS_SUIVANT}`
done

# Téléchargement systématique du fichier des oppositions
if [ -f oppositions.csv ]
then
    EMPREINTE1=`sha256 -q oppositions.csv`
else
    EMPREINTE1=""
fi
${DOWNLOADER} ${URL_OPPOSITIONS} -o oppositions.csv
EMPREINTE2=`sha256 -q oppositions.csv`
if [ "${EMPREINTE1}" != "${EMPREINTE2}" ]
then
    echo "Fichier des oppositions mis à jour"
    touch ${INDICATEUR}
fi

# Téléchargement du Code officiel géographique de l'année
FICHIER=cog_ensemble_${ANNEE_COURANTE}_csv.zip
if [ ! -f ZIP/${FICHIER} ]
then
    ${DOWNLOADER} ${URL_COG}/${FICHIER} -o ZIP
    if [ -f ZIP/${FICHIER} ]
    then
        unzip -d COG ZIP/${FICHIER}
        touch ${INDICATEUR}
    fi
fi

exit 0
