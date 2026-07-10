# Prompt — ETL complet (source → staging → DW) réalisé par l'IA via MCP

> **À qui s'adresse ce prompt ?** À toute personne (par ex. l'encadrant) qui veut
> reproduire l'ETL **sans rien faire manuellement dans SSMS ni SSIS**. Il suffit
> de coller le prompt dans **Claude Desktop / Claude Max** connecté à SQL Server
> via un serveur **MCP `mssql`** autorisé en écriture. Claude crée les tables,
> les procédures, charge les données et vérifie — tout seul.
>
> Pré-requis (une fois) : serveur MCP configuré — voir
> `docs/05-cas-etude/13-demo-ia-mcp-sql-staging-dw.md` (§4) et
> `docs/05-cas-etude/14-etl-ssis-reservation.md`.

---

## A. Version « réservations d'hôtel » (exemple prêt à l'emploi)

```
Tu es un ingénieur Data (SQL Server). Tu es connecté à ma base via l'outil MCP
« mssql ». Utilise cet outil pour EXÉCUTER réellement le SQL (pas seulement l'afficher).

Base cible : POC_ETL_IA
Domaine : réservations d'hôtel

OBJECTIF : construire et exécuter un pipeline ETL complet source -> staging -> DW
en étoile, puis le vérifier.

ÉTAPES (dans l'ordre, via MCP) :
1) SOURCE/LANDING : crée une table raw_hotel_reservation (colonnes texte brutes :
   reservation_id, client_id, client_nom, client_ville, client_pays, chambre_id,
   type_chambre, capacite, date_arrivee, nb_nuits, montant) et insère 6 lignes
   d'exemple dont 1 doublon et des noms « sales » (espaces / casse).
2) STAGING : crée stg_hotel_reservation (typée + colonnes techniques batch_id,
   source_system, load_ts). Charge-la depuis raw en convertissant les types.
3) DW EN ÉTOILE :
   - dim_client, dim_chambre (clé de substitution IDENTITY, clé métier UNIQUE,
     attributs nettoyés ; pour dim_client : valid_from/valid_to/is_current + audit),
   - dim_date (date_key AAAAMMJJ, date_complete, annee, mois, jour),
   - fact_reservation (clé de substitution + FOREIGN KEY vers chaque dimension +
     mesures nb_nuits, montant + mesure dérivée montant_par_nuit).
4) CHARGEMENT DW : charge les dimensions depuis le staging (dédoublonnage par clé
   métier, nettoyage TRIM + casse), puis le fait en résolvant les clés de
   substitution par jointure (lookups).
5) VÉRIFICATION : compte les lignes par table, puis fais un SELECT du fait joint à
   ses dimensions pour prouver que les relations fonctionnent.

CONTRAINTES : SQL Server Express compatible ; rends le script idempotent (DROP/DELETE
avant recréation, dans le bon ordre à cause des clés étrangères) ; commente chaque
section ; après chaque exécution montre le SQL exécuté ET le résultat renvoyé par MCP.

RESTITUTION : récapitulatif (objets créés, lignes chargées, doublons éliminés,
relations créées) + 3 phrases expliquant staging vs DW, le rôle de la clé de
substitution, et l'apport des relations (schéma en étoile). Signale les points à
valider par un humain avant une vraie mise en production.
```

Résultat attendu : raw 6 → staging 6 → dim_client 4, dim_chambre 3, dim_date 5,
fact_reservation 5 (relié aux 3 dimensions).

> Script de référence équivalent (déjà validé) :
> `samples/sqlserver/reservation_etl_setup.sql` + `reservation_etl_procedures.sql`.

---

## B. Version GÉNÉRIQUE (tout type de projet)

Remplacez les variables `{...}` par votre domaine, puis collez dans Claude Max.

| Variable | Signification | Exemple |
| --- | --- | --- |
| `{base}` | Base cible | `POC_ETL_IA` |
| `{domaine}` | Sujet métier | facturation, RH, logistique… |
| `{entite_fait}` | Événement mesuré (fait) | facture, embauche, livraison |
| `{dimensions}` | Axes d'analyse | client, produit, date… |
| `{mesures}` | Indicateurs du fait | montant, quantité… |

```
Tu es un ingénieur Data (SQL Server), connecté à ma base via l'outil MCP « mssql ».
Utilise-le pour EXÉCUTER réellement le SQL.

Base cible : {base}
Domaine : {domaine}

OBJECTIF : construire et exécuter un pipeline ETL complet source -> staging -> DW
en étoile pour ce domaine, puis le vérifier.

ÉTAPES (via MCP, dans l'ordre) :
1) SOURCE : crée raw_{entite_fait} (colonnes brutes du domaine) et insère quelques
   lignes d'exemple, dont au moins un doublon et des valeurs texte à nettoyer.
2) STAGING : crée stg_{entite_fait} (typée + batch_id, source_system, load_ts) et
   charge-la depuis raw en convertissant les types.
3) DW EN ÉTOILE : une table de DIMENSION par axe de {dimensions} (clé de substitution
   IDENTITY, clé métier UNIQUE, attributs nettoyés), une dimension DATE si pertinent,
   et une table de FAITS fact_{entite_fait} avec clé de substitution, FOREIGN KEY vers
   chaque dimension et les mesures {mesures} + une mesure dérivée pertinente.
4) CHARGEMENT : dimensions depuis le staging (dédoublonnage + nettoyage), puis le fait
   avec résolution des clés de substitution par jointure.
5) VÉRIFICATION : lignes par table + SELECT du fait joint à ses dimensions.

CONTRAINTES : idempotent (ordre des clés étrangères respecté), commenté, compatible
Express. Ne touche QU'AUX tables de ce périmètre. Montre le SQL exécuté et le résultat.

RESTITUTION : récapitulatif + explication courte (staging vs DW, clé de substitution,
relations) + points à faire valider par un humain.
```

---

## C. Et pour SSIS ?

Un serveur MCP **ne peut pas créer** de package SSIS (`.dtsx`) : cette partie reste
faite dans Visual Studio (packages déjà fournis : `PKG_STG_RESERVATION`,
`PKG_DW_RESERVATION`). En revanche, l'IA peut **tout réaliser en SQL** via MCP, ce
qui produit exactement le même résultat dans les mêmes tables. Les deux approches
sont donc interchangeables pour la démonstration.
