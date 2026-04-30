# [Memento mortuorum](https://deces.famille.eu.org/)
Ce logiciel est composé :
* d'une dorsale en ligne de commande permettant de créer une base de données à partir des [Fichiers des personnes décédées depuis 1970](https://www.insee.fr/fr/information/4190491) distribués par l'[INSEE](https://www.insee.fr/fr/accueil)
* d'un frontal Web permettant d'effectuer des recherches dans cette base de données
  * Ce frontal est proposé en tant que [service en ligne](https://deces.famille.eu.org/), afin que chacun puisse l'exploiter librement sans pré-requis de connaissances ou d'infrastructures techniques
* de scripts permettant de générer des statistiques sur le contenu de la base de données.

### Implémentation technique
* La dorsale a été écrite en langage [Python](https://www.python.org/), pour importer les [fichiers CSV](https://fr.wikipedia.org/wiki/Comma-separated_values) sources, les nettoyer, et générer une base de données [SQLite](https://sqlite.org/)
* Le frontal a été généré en langage [PHP](https://www.php.net/) avec [Claude Sonnet 4.6](https://www.anthropic.com/claude/sonnet), afin de (re)tester le [vibe coding](https://fr.wikipedia.org/wiki/Vibe_coding) et finalisé manuellement
  * Le test a été tout à fait satisfaisant ! 
* Les scripts ont été écrits dans la [variante SQLite](https://www.tutorialspoint.com/sqlite/index.htm) du langage [SQL](https://fr.wikipedia.org/wiki/Structured_Query_Language)

Les lieux de naissance et de décès sont représentés à l'aide du [Code Officiel Géographique (COG)](https://www.insee.fr/fr/metadonnees/source/serie/s2084) de l'INSEE, qui est donc importé dans la base de données.

### Documentation de référence
Pour les fichiers des personnes décédées depuis 1970 :
* [Dessin d'enregistrement des fichiers de décès](https://www.insee.fr/fr/statistiques/fichier/4190491/dessin_fichier_deces.pdf)
* [Métadonnées des fichiers de décès](https://www.insee.fr/fr/statistiques/fichier/4190491/metadonnees_deces.zip)

Pour le Code Officiel Géographique :
* [dessin des fichiers au 1er janvier 2026](https://www.insee.fr/fr/information/8740222)
* [Liste de modalités des fichiers téléchargeables du COG](https://www.insee.fr/fr/information/8740218)
