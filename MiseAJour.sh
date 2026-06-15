#!/bin/sh
############################################
#                                          #
# Memento mortuorum                        #
# (c) 2026+ Hubert Tournier                #
#                                          #
# Orchestration des différents traitements #
#                                          #
############################################

TelechargementFichiers.sh
if [ -f .nouveaux_fichiers ]
then
    cd data
    rm -f deces.sqlite
    ../MementoMortuorum.py deces-*.csv Deces_201*.csv deces_2020.csv Deces_202*
    if [ $? != 0 ]
    then
        ln ../deces.sqlite .
        exit 1
    fi
    sqlite3 deces.sqlite ".read ../stats.sql"

    cd ..
    GenererPageStatique.py
    mv stats.html public_html
    rm -f stats.txt

    rm -f deces.sqlite
    ln data/deces.sqlite .

    rm .nouveaux_fichiers
fi
exit 0
