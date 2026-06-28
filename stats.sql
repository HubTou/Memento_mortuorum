#####################################################
#                                                   #
# Memento mortuorum                                 #
# (c) 2026+ Hubert Tournier                         #
#                                                   #
# Génération des données de la page de statistiques #
#                                                   #
#####################################################

.mode list
.separator '|'
.headers on
.output ../stats.txt

.print "@block:open"
.print "@name:dernier-deces"
.print "@title:Dernier décès enregistré"
.print "@subtitle:(les dernières données disponibles sont intégrées automatiquement à J+1 de leur sortie)"
SELECT MAX(date_deces) "Date"
FROM personnes
WHERE
    annee_deces != '0000'
    AND mois_deces != '00'
    AND jour_deces != '00';
.print

.print "@block:open"
.print "@name:personnes"
.print "@title:Entrées dans la table des personnes"
.print "@subtitle:(une fois la plupart des doublons retirés dans les données sources)"
SELECT
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes
FROM personnes;
.print

.print "@block:close"
.print "@name:oppositions"
.print "@title:dont personnes ayant fait opposition à l'exploitation de leurs données" 
SELECT 
    FORMAT('%,d', SUM(opposition = 1)) AS Total,
    FORMAT('%,d', SUM(opposition = 1 AND sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(opposition = 1 AND sexe = 2)) AS Femmes
FROM personnes;
.print

.print "@block:close"
.print "@name:annee-naissance"
.print "@title:Répartition par année de naissance"
.print "@subtitle:(année 0 = année non spécifiée ou invalide)"
SELECT
    annee_naissance "Année",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes
FROM personnes
GROUP BY annee_naissance
ORDER BY annee_naissance ASC;
.print

.print "@block:close"
.print "@name:annee-deces"
.print "@title:Répartition par année de décès"
.print "@subtitle:(année 0 = année non spécifiée ou invalide)"
SELECT
    annee_deces "Année",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes
FROM personnes
GROUP BY annee_deces
ORDER BY annee_deces ASC;
.print

.print "@block:close"
.print "@name:mois-naissance"
.print "@title:Répartition par mois de naissance"
.print "@subtitle:(mois ? = mois non spécifié ou invalide)"
SELECT
    CASE mois_naissance
        WHEN '0' THEN '?'
        WHEN '1' THEN 'Janvier'
        WHEN '2' THEN 'Février'
        WHEN '3' THEN 'Mars'
        WHEN '4' THEN 'Avril'
        WHEN '5' THEN 'Mai'
        WHEN '6' THEN 'Juin'
        WHEN '7' THEN 'Juillet'
        WHEN '8' THEN 'Août'
        WHEN '9' THEN 'Septembre'
        WHEN '10' THEN 'Octobre'
        WHEN '11' THEN 'Novembre'
        WHEN '12' THEN 'Décembre'
        ELSE '?'
    END AS "Mois",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes,
    COUNT(*) AS tri
FROM personnes
GROUP BY mois_naissance
ORDER BY tri DESC;
.print

.print "@block:close"
.print "@name:mois-deces"
.print "@title:Répartition par mois de décès"
.print "@subtitle:(mois ? = mois non spécifié ou invalide)"
SELECT
    CASE mois_deces
        WHEN '0' THEN '?'
        WHEN '1' THEN 'Janvier'
        WHEN '2' THEN 'Février'
        WHEN '3' THEN 'Mars'
        WHEN '4' THEN 'Avril'
        WHEN '5' THEN 'Mai'
        WHEN '6' THEN 'Juin'
        WHEN '7' THEN 'Juillet'
        WHEN '8' THEN 'Août'
        WHEN '9' THEN 'Septembre'
        WHEN '10' THEN 'Octobre'
        WHEN '11' THEN 'Novembre'
        WHEN '12' THEN 'Décembre'
        ELSE '?'
    END AS "Mois",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes,
    COUNT(*) AS tri
FROM personnes
GROUP BY mois_deces
ORDER BY tri DESC;
.print

.print "@block:close"
.print "@name:jour-naissance"
.print "@title:Répartition par jour de naissance"
.print "@subtitle:(jour 0 = jour non spécifié ou invalide)"
SELECT
    jour_naissance "Jour",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes,
    COUNT(*) AS tri
FROM personnes
GROUP BY jour_naissance
ORDER BY tri DESC;
.print

.print "@block:close"
.print "@name:jour-deces"
.print "@title:Répartition par jour de décès"
.print "@subtitle:(jour 0 = jour non spécifié ou invalide)"
SELECT
    jour_deces "Jour",
    FORMAT('%,d', COUNT(*)) AS Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes,
    COUNT(*) AS tri
FROM personnes
GROUP BY jour_deces
ORDER BY tri DESC;
.print

.print "@block:close"
.print "@name:cog"
.print "@title:Entrées dans la table des Codes Officiels Géographiques (COG)"
.print "@subtitle:(incluant les départements depuis 1943)"
SELECT FORMAT('%,d', COUNT(*)) "Nombre"
FROM cog;
.print

.print "@block:close"
.print "@name:types-cog"
.print "@title:Répartition par type de Code Officiel Géographique (COG)"
SELECT
    FORMAT('%,d', COUNT(*)) AS Nombre,
    CASE
        WHEN type = 'COM' THEN 'Commune'
        WHEN type = 'COMA' THEN 'Commune associée'
        WHEN type = 'COMD' THEN 'Commune déléguée'
        WHEN type = 'ARM' THEN 'Arrondissement municipal'
        WHEN type = 'DIS' THEN 'District'
        WHEN type = 'CIR' THEN 'Circonscription territoriale'
        WHEN type = 'CPT' THEN 'Code de La Passion-Clipperton'
        WHEN type = 'CDM' THEN 'Code du condominium de l''Île des Faisans'
        WHEN type = 'DEP' THEN 'Département'
        WHEN type = 'TOM' THEN 'Territoire d''Outre Mer'
        WHEN type = 'PAYS' THEN 'Pays'
        WHEN type LIKE 'PAYS:%' THEN 'Territoire rattaché à un pays: ' || SUBSTR(type, 6)
    END AS "Type",
    COUNT(*) AS tri
FROM cog
GROUP BY type
ORDER BY tri DESC;
.print

.print "@block:close"
.print "@name:communes-naissance"
.print "@title:Top 50 des communes de naissance"
.print "@subtitle:(nom vide = commune non spécifiée ou invalide)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    lieu_naissance "COG",
    commune_naissance "Commune",
    pays_naissance "Pays",
    COUNT(*) AS tri
FROM personnes
GROUP BY commune_naissance
ORDER BY tri DESC
LIMIT 50;
.print

.print "@block:close"
.print "@name:communes-deces"
.print "@title:Top 50 des communes de décès"
.print "@subtitle:(nom vide = commune non spécifiée ou invalide)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    lieu_deces "COG",
    commune_deces "Commune",
    pays_deces "Pays",
    COUNT(*) AS tri
FROM personnes
GROUP BY commune_deces
ORDER BY tri DESC
LIMIT 50;
.print

.print "@block:close"
.print "@name:pays-naissance"
.print "@title:Top 50 des pays de naissance"
.print "@subtitle:(nom vide = pays non spécifié ou invalide)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    CASE SUBSTR(lieu_naissance, 1, 2)
        WHEN '99' THEN lieu_naissance
        ELSE '< 99000'
    END AS "COG",   
    pays_naissance "Pays",
    COUNT(*) AS tri
FROM personnes
GROUP BY pays_naissance
ORDER BY tri DESC
LIMIT 50;
.print

.print "@block:close"
.print "@name:pays-deces"
.print "@title:Top 50 des pays de décès"
.print "@subtitle:(nom vide = pays non spécifié ou invalide)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    CASE SUBSTR(lieu_deces, 1, 2)
        WHEN '99' THEN lieu_deces
        ELSE '< 99000'
    END AS "COG",   
    pays_deces "Pays",
    COUNT(*) AS tri
FROM personnes
GROUP BY pays_deces
ORDER BY tri DESC
LIMIT 50;
.print

.print "@block:open"
.print "@name:noms"
.print "@title:Noms de familles"
SELECT FORMAT('%,d', COUNT(DISTINCT(nom))) "Nombre"
FROM personnes;
.print

.print "@block:close"
.print "@name:top-noms"
.print "@title:Top 500 des noms de familles"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    nom "Nom de famille",
    COUNT(*) AS tri
FROM personnes
GROUP BY nom
ORDER BY tri DESC
LIMIT 500;
.print

.print "@block:open"
.print "@name:prenoms"
.print "@title:Prénoms"
SELECT FORMAT('%,d', COUNT(*)) "Nombre"
FROM prenoms;
.print

.print "@block:close"
.print "@name:nombre-prenoms"
.print "@title:Prénoms par personne"
.print "@subtitle:(y compris des x DIT y et/ou des x ALIAS y)"
SELECT
    FORMAT('%,d', COUNT(*)) AS Nombre,
    max_ordre "Prénoms",
    COUNT(*) AS tri
FROM
    (
        SELECT
            id_personne,
            MAX(ordre) AS max_ordre
        FROM prenoms_personne
        GROUP BY id_personne
    )
GROUP BY max_ordre
ORDER BY tri DESC;
.print

#.print "@block:close"
#.print "@name:10-prenoms"
#.print "@title:Personnes avec plus de 9 prénoms"
#SELECT *
#FROM
#    (
#        SELECT
#            id_personne,
#            MAX(ordre) AS max_ordre
#        FROM prenoms_personne
#        GROUP BY id_personne
#    ) AS sr,
#   personnes p
#WHERE sr.max_ordre > 9
#AND sr.id_personne = p.id;
#.print

.print "@block:close"
.print "@name:top-prenoms"
.print "@title:Top 500 des prénoms"
.print "@subtitle:(quel que soit leur ordre)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    p.prenom "Prénom",
    COUNT(*) AS tri
FROM
    prenoms_personne pp,
    prenoms p
WHERE p.id = pp.id_prenom
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 500;
.print

.print "@block:close"
.print "@name:top-premiers-prenoms"
.print "@title:Top 500 des premiers prénoms"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    p.prenom "Prénom",
    COUNT(*) AS tri
FROM
    prenoms_personne pp,
    prenoms p
WHERE
    pp.ordre = 1
    AND p.id = pp.id_prenom
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 500;
.print

.print "@block:close"
.print "@name:prenoms-1890"
.print "@title:Top 100 des prénoms de 1890 à 1899"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1890 AND p.annee_naissance <= 1899
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1900"
.print "@title:Top 100 des prénoms de 1900 à 1909"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1900 AND p.annee_naissance <= 1909
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1910"
.print "@title:Top 100 des prénoms de 1910 à 1919"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1910 AND p.annee_naissance <= 1919
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1920"
.print "@title:Top 100 des prénoms de 1920 à 1929"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1920 AND p.annee_naissance <= 1929
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1930"
.print "@title:Top 100 des prénoms de 1930 à 1939"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1930 AND p.annee_naissance <= 1939
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1940"
.print "@title:Top 100 des prénoms de 1940 à 1949"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1940 AND p.annee_naissance <= 1949
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1950"
.print "@title:Top 100 des prénoms de 1950 à 1959"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1950 AND p.annee_naissance <= 1959
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1960"
.print "@title:Top 100 des prénoms de 1960 à 1969"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1960 AND p.annee_naissance <= 1969
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1970"
.print "@title:Top 100 des prénoms de 1970 à 1979"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1970 AND p.annee_naissance <= 1979
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1980"
.print "@title:Top 100 des prénoms de 1980 à 1989"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1980 AND p.annee_naissance <= 1989
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-1990"
.print "@title:Top 100 des prénoms de 1990 à 1999"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 1990 AND p.annee_naissance <= 1999
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-2000"
.print "@title:Top 100 des prénoms de 2000 à 2009"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 2000 AND p.annee_naissance <= 2009
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-2010"
.print "@title:Top 100 des prénoms de 2010 à 2019"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 2010 AND p.annee_naissance <= 2019
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:prenoms-2020"
.print "@title:Top 100 des prénoms de 2020 à 2029"
.print "@subtitle:(sur l'année de naissance et le premier prénom)"
SELECT
    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS "Rang",
    FORMAT('%,d', COUNT(*)) AS Nombre,
    pr.prenom "Prénom",
    COUNT(*) AS tri
FROM
    personnes p,
    prenoms_personne pp,
    prenoms pr
WHERE
    p.annee_naissance >= 2020 AND p.annee_naissance <= 2029
    AND p.id = pp.id_personne
    AND pp.ordre = 1
    AND pp.id_prenom = pr.id
GROUP BY pp.id_prenom
ORDER BY tri DESC
LIMIT 100;
.print

.print "@block:close"
.print "@name:centenaires"
.print "@title:Centenaires"
SELECT FORMAT('%,d', COUNT(*)) "Nombre"
FROM personnes
WHERE
    annee_naissance != '0000' AND mois_naissance != '00' AND jour_naissance != '00'
    AND (annee_deces - annee_naissance) - (
           CASE 
               WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance) 
               THEN 1 
               ELSE 0 
           END
        ) >= 100;
.print

.print "@block:close"
.print "@name:supercentenaires"
.print "@title:Supercentenaires"
.print "@subtitle:(un supercentenaire est une personne ayant atteint 110 ans)"
SELECT FORMAT('%,d', COUNT(*)) "Nombre"
FROM personnes
WHERE
    annee_naissance != '0000' AND mois_naissance != '00' AND jour_naissance != '00'
    AND (annee_deces - annee_naissance) - (
           CASE 
               WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance) 
               THEN 1 
               ELSE 0 
           END
        ) >= 110;
.print

.print "@block:close"
.print "@name:age-deces"
.print "@title:Âge au moment du décès"
.print "@subtitle:(les âges supérieurs au record mondial de 122 ans sont certainement des erreurs)"
SELECT
    (
        (annee_deces - annee_naissance) -
        (
            CASE
                WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance)
                    THEN 1
                    ELSE 0
            END
        )
    ) AS Age,
    FORMAT('%,d', COUNT(*)) Total,
    FORMAT('%,d', SUM(sexe = 1)) AS Hommes,
    FORMAT('%,d', SUM(sexe = 2)) AS Femmes
FROM personnes
WHERE
    annee_naissance != '0000' AND mois_naissance != '00' AND jour_naissance != '00'
    AND Age >= 0
GROUP BY Age
ORDER BY Age DESC;
.print

.print "@block:close"
.print "@name:esperance-vie"
.print "@title:Evolution de l'âge moyen au moment du décès"
.print "@subtitle:(la réalité de l'espérance de vie, en quelque sorte)"
SELECT 
    annee_deces AS "Année du décès",
    ROUND(
        AVG(
            CASE 
                WHEN sexe = 1 THEN 
                    (annee_deces - annee_naissance) - (
                        CASE
                            WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance)
                            THEN 1
                            ELSE 0
                        END
                    )
                ELSE NULL
            END
        ), 1
    ) AS "Âge Moyen Hommes",
    ROUND(
        AVG(
            CASE 
                WHEN sexe = 2 THEN 
                    (annee_deces - annee_naissance) - (
                        CASE
                            WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance)
                            THEN 1
                            ELSE 0
                        END
                    )
                ELSE NULL
            END
        ), 1
    ) AS "Âge Moyen Femmes"
FROM personnes
WHERE
    annee_naissance != '0000' AND mois_naissance != '00' AND jour_naissance != '00'
    AND annee_deces > 1970
GROUP BY annee_deces
ORDER BY annee_deces DESC;
.print

.print "@block:close"
.print "@name:age-moyen-deces"
.print "@title:Âge moyen au moment du décès"
.print "@subtitle:(sur l'ensemble des données de la base)"
SELECT ROUND(
           AVG(
               (annee_deces - annee_naissance) - (
                   CASE 
                      WHEN (mois_deces < mois_naissance) OR (mois_deces = mois_naissance AND jour_deces < jour_naissance) 
                      THEN 1 
                      ELSE 0 
                   END
               )
           ), 1
       ) AS "Age Moyen",
       CASE sexe
           WHEN '1' THEN 'Hommes'
           WHEN '2' THEN 'Femmes'
           ELSE '?'
       END AS "Sexe"
FROM personnes
WHERE annee_naissance != '0000' AND mois_naissance != '00' AND jour_naissance != '00'
GROUP BY Sexe;
.print

.print "@block:close"
.print "@name:erreurs"
.print "@title:Erreurs dans les données sources"
SELECT
    libelle AS Erreur,
    FORMAT('%,d', valeur) AS Nombre
FROM infos
WHERE
    valeur != 0
    AND cle LIKE 'erreur%';
.print

.exit 0
