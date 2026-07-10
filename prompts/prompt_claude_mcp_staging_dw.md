# Prompt — Implémentation autonome d'un STAGING + DW complet par l'IA (via MCP SQL Server)

> **À qui s'adresse ce prompt ?** À toute personne qui teste la démo avec Claude
> (Claude Desktop / Claude Max) **connecté à SQL Server via un serveur MCP**
> autorisé en écriture (DDL). Une fois collé, Claude crée et charge les tables
> **lui-même**, sans copier-coller manuel dans SSMS.
>
> **Générique :** remplacez les variables `{...}` par VOTRE domaine (RH, santé,
> logistique, e-commerce, etc.). L'exemple de référence livré porte sur des
> réservations d'hôtel, mais la structure convient à tout projet.
>
> Pré-requis : voir `docs/05-cas-etude/13-demo-ia-mcp-sql-staging-dw.md`
> (installation du serveur MCP + configuration `claude_desktop_config.json`).

---

## Variables à personnaliser

| Variable | Signification | Exemple (hôtel) |
| --- | --- | --- |
| `{base}` | Base de données cible | `POC_ETL_IA` |
| `{domaine}` | Sujet métier | réservations d'hôtel |
| `{entite_fait}` | Événement mesuré (table de faits) | réservation |
| `{dimensions}` | Axes d'analyse (tables de dimension) | client, chambre, date |
| `{mesures}` | Indicateurs numériques du fait | nb_nuits, montant |

---

## Prompt à copier dans Claude

```
Tu es un ingénieur Data (SQL Server). Tu es connecté à ma base SQL Server
via l'outil MCP « mssql ». Utilise cet outil pour EXÉCUTER réellement le SQL
sur ma base (pas seulement l'afficher).

Base cible : {base}   (si elle n'existe pas, demande-moi avant de créer)
Domaine : {domaine}

OBJECTIF
Construire une démonstration COMPLÈTE « staging -> data warehouse » en schéma
en étoile, puis la charger et la vérifier :

1) UNE table de STAGING « stg_{entite_fait} »
   - Colonnes techniques : batch_id INT NOT NULL, source_system NVARCHAR(100) NOT NULL,
     load_ts DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME().
   - Colonnes métier : les clés naturelles et attributs du domaine, plus les
     mesures {mesures}. Les données peuvent contenir des doublons / du texte à nettoyer.

2) Un DATA WAREHOUSE en étoile :
   - Une table de DIMENSION par axe de {dimensions}, chacune avec :
       * une clé de substitution (surrogate key) INT IDENTITY(1,1), clé primaire,
       * la clé métier en contrainte UNIQUE,
       * les attributs (nettoyés si nécessaire),
       * pour la dimension principale : historisation (valid_from, valid_to, is_current)
         et audit (source_system, dw_load_ts).
   - Une table de DIMENSION DATE (date_key AAAAMMJJ, date_complete, annee, mois, jour).
   - Une table de FAITS « fact_{entite_fait} » avec :
       * une clé de substitution (PK),
       * une CLÉ ÉTRANGÈRE (FOREIGN KEY) vers CHAQUE dimension (relations en étoile),
       * les mesures {mesures} + une mesure dérivée pertinente.

ÉTAPES À EXÉCUTER (dans l'ordre, via l'outil MCP)
a) Rends le script idempotent : supprime d'abord le fait, puis les dimensions
   (à cause des clés étrangères), puis le staging (IF OBJECT_ID ... DROP TABLE).
b) Crée le staging, les dimensions, la dimension date, puis le fait avec ses
   FOREIGN KEY vers les dimensions. Ajoute les index utiles.
c) Insère des données d'exemple en staging (au moins un doublon et des valeurs
   textuelles « sales » pour illustrer le nettoyage).
d) Charge les dimensions depuis le staging (dédoublonnage par clé métier,
   nettoyage TRIM + casse). Charge la dimension date depuis les dates distinctes.
e) Charge le fait en résolvant les clés de substitution par jointure sur les
   dimensions (lookups).
f) Vérifie : nombre de lignes par table, puis un SELECT du fait joint à ses
   dimensions (pour prouver que les relations fonctionnent).

CONTRAINTES
- SQL Server compatible (Express OK). Commente brièvement chaque section.
- Ne touche QU'AUX tables de cette démo (préfixe/suffixe _demo conseillé).
- Après chaque exécution, montre-moi le SQL exécuté ET le résultat renvoyé
  par l'outil MCP.

RESTITUTION FINALE
- Récapitulatif : objets créés, lignes chargées, doublons éliminés, relations créées.
- Explique en 3 phrases : staging vs DW, le rôle de la clé de substitution, et
  ce qu'apportent les relations (schéma en étoile) pour l'analyse.
- Signale tout point à valider par un humain avant une mise en production réelle.
```

---

## Exemple de référence livré (déjà validé)

Un script complet équivalent, sur le domaine **réservations d'hôtel**, est
disponible ici : `samples/sqlserver/demo_ia_staging_dw.sql`.

Résultat attendu :

| Table | Type | Lignes |
| --- | --- | --- |
| `stg_hotel_reservation_demo` | Staging | 5 (dont 1 doublon) |
| `dim_client_demo` | Dimension | 3 |
| `dim_chambre_demo` | Dimension | 3 |
| `dim_date_demo` | Dimension (date) | 4 |
| `fact_reservation_demo` | Faits | 4 (relié aux 3 dimensions) |

> L'utilisateur peut ainsi : (1) laisser Claude implémenter via MCP pour SON
> domaine, puis (2) comparer la démarche avec ce script de référence pour valider.
