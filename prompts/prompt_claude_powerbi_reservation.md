# Prompt — Power BI après ETL (réservations + générique)

> **Pour l'encadrant :** coller le prompt **A** dans Claude Max / Claude Desktop /
> ChatGPT / Copilot / Gemini. L'IA vous guide pour construire sur **votre PC** :
> modèle en étoile → mesures DAX → **dashboard visible dans Power BI Desktop**.
>
> Prérequis : le DW est déjà chargé (prompt ETL exécuté, tables visibles dans SSMS).
>
> Option avancée : si le MCP **Power BI Modeling** est configuré et un `.pbix` est
> ouvert, demandez à Claude d'appliquer relations + mesures directement dans le modèle.

---

## A. Version « réservations d'hôtel » — prête à coller

```
Tu es un expert Power BI Desktop (modélisation en étoile, DAX, dashboards).

CONTEXTE — mon Data Warehouse est DÉJÀ chargé dans SQL Server :
- Serveur : .\SQLEXPRESS   (ou localhost\SQLEXPRESS / NOM_PC\SQLEXPRESS)
- Base    : POC_ETL_IA
- Tables DW (ne pas utiliser raw_* ni stg_*) :
  • fact_reservation (reservation_key, reservation_id, client_key, chambre_key,
    date_key, nb_nuits, montant, montant_par_nuit)
  • dim_client (client_key, client_id, client_nom_clean, ville, pays)
  • dim_chambre (chambre_key, chambre_id, type_chambre, capacite)
  • dim_date (date_key, date_complete, annee, mois, jour)

OBJECTIF
Je dois voir sur MON PC, dans Power BI Desktop, un dashboard opérationnel.
Tu dois me livrer un guide EXÉCUTABLE pas à pas (clics exacts) + le code DAX
copier-coller, pour obtenir :
1) modèle en étoile avec 3 relations
2) 6 mesures DAX
3) une page « Overview Réservations » avec visuels
4) une requête SQL de contrôle des totaux

═══════════════════════════════════════
ÉTAPE 1 — Créer le fichier et importer le DW
═══════════════════════════════════════
1. Ouvrir Power BI Desktop → Fichier → Enregistrer sous → Reservation_Hotel_POC.pbix
2. Accueil → Obtenir des données → SQL Server
3. Serveur : .\SQLEXPRESS | Base : POC_ETL_IA | Mode : Importer
4. Cocher UNIQUEMENT : fact_reservation, dim_client, dim_chambre, dim_date
5. Charger
6. Si message « chiffrement » → OK → Se connecter (authentification Windows)

═══════════════════════════════════════
ÉTAPE 2 — Relations (vue Modèle)
═══════════════════════════════════════
Créer (si non auto-détectées) :
• fact_reservation[client_key]  → dim_client[client_key]    (*:1)
• fact_reservation[chambre_key] → dim_chambre[chambre_key]  (*:1)
• fact_reservation[date_key]    → dim_date[date_key]        (*:1)
Direction du filtre : Unique (dimension → fait)

═══════════════════════════════════════
ÉTAPE 3 — Mesures DAX (à coller dans fact_reservation)
═══════════════════════════════════════
CA Total = SUM ( fact_reservation[montant] )

Nb Réservations = DISTINCTCOUNT ( fact_reservation[reservation_id] )

Nb Nuits Total = SUM ( fact_reservation[nb_nuits] )

CA Moyen / Réservation = DIVIDE ( [CA Total], [Nb Réservations] )

Montant Moyen / Nuit = AVERAGE ( fact_reservation[montant_par_nuit] )

Nb Clients Distincts = DISTINCTCOUNT ( fact_reservation[client_key] )

Format : CA en devise (€), compteurs en entier.

═══════════════════════════════════════
ÉTAPE 4 — Dashboard page « Overview Réservations »
═══════════════════════════════════════
Vue Rapport → nouvelle page renommée Overview Réservations.

Disposition :
1. Ligne 1 — 4 CARTES (visuel Carte) :
   [CA Total] | [Nb Réservations] | [Nb Nuits Total] | [CA Moyen / Réservation]
2. Ligne 2 :
   • Barres groupées : Axe = dim_client[ville] ; Valeurs = [CA Total]
   • Colonnes groupées : Axe = dim_chambre[type_chambre] ; Valeurs = [CA Total]
3. Ligne 3 :
   • Courbe : Axe = dim_date[date_complete] ; Valeurs = [CA Total]
   • Table : dim_client[client_nom_clean], dim_client[ville], [CA Total], [Nb Réservations]
4. Trancheurs (optionnel) : dim_client[pays], dim_chambre[type_chambre], dim_date[annee]

═══════════════════════════════════════
ÉTAPE 5 — Contrôle
═══════════════════════════════════════
Dans SSMS :
  SELECT COUNT(*) AS nb, SUM(montant) AS ca, SUM(nb_nuits) AS nuits
  FROM fact_reservation;
Les KPI Power BI doivent correspondre.

RESTITUTION ATTENDUE DE TA PART
1. Les étapes ci-dessus reformulées clairement pour mon PC
2. Le DAX exact dans des blocs séparés
3. Un checklist « à l'ouverture de Power BI je vois : modèle / mesures / page Overview »
4. Ce que je dois valider avant une présentation EY
```

**Résultat attendu chez l'encadrant :** page Overview avec KPI + graphiques + table, données du DW réservations.

---

## B. Version GÉNÉRIQUE — tout projet / toute IA

Remplacez les variables `{...}`, puis collez dans Claude Max, ChatGPT, Copilot, Gemini, etc.

| Variable | Signification | Exemple réservations |
| --- | --- | --- |
| `{serveur}` | Instance SQL Server | `.\SQLEXPRESS` |
| `{base}` | Base DW | `POC_ETL_IA` |
| `{fait}` | Table de faits | `fact_reservation` |
| `{dimensions}` | Dimensions | `dim_client, dim_chambre, dim_date` |
| `{cles}` | Relations fait → dim | `client_key, chambre_key, date_key` |
| `{mesures_colonnes}` | Colonnes numériques | `montant, nb_nuits` |
| `{kpis}` | Indicateurs | `CA, volume, ticket moyen` |
| `{axes}` | Axes du dashboard | `ville, type_chambre, date` |
| `{nom_page}` | Nom de la page rapport | `Overview` |

```
Tu es un expert Power BI Desktop (étoile + DAX + dashboard).

CONTEXTE
- Serveur SQL : {serveur}
- Base : {base}
- Le Data Warehouse est DÉJÀ chargé (ETL terminé).
- Table de faits : {fait}
- Dimensions : {dimensions}
- Clés de relation (fait → dim) : {cles}
- Colonnes numériques du fait : {mesures_colonnes}
- KPI souhaités : {kpis}
- Axes d'analyse du dashboard : {axes}
- Nom de page : {nom_page}

OBJECTIF
Produis un guide EXÉCUTABLE pour que je construise sur mon PC, dans Power BI Desktop :
1) Import des tables DW uniquement (pas raw/stg) — mode Import
2) Relations du modèle en étoile (*:1, filtre unique dim → fait)
3) Mesures DAX prêtes à coller pour {kpis} (formule complète + format)
4) Layout exact de la page {nom_page} sur les axes {axes}
   (cartes KPI + 2 graphiques + 1 courbe ou table)
5) Requête SQL de contrôle croisé des totaux

CONTRAINTES
- N'invente aucune colonne absente du schéma
- Étapes numérotées, clics Power BI Desktop, français clair
- Code DAX dans des blocs séparés
- Signale ce que l'humain doit valider avant production

RESTITUTION
Checklist finale : « À l'ouverture de Power BI je dois voir modèle / mesures / page {nom_page} ».
```

---

## C. Message pour la démonstration EY

| Étape | Qui | Résultat |
| --- | --- | --- |
| 1. Prompt ETL | Encadrant → Claude Max + MCP SQL | Tables DW dans SSMS |
| 2. Prompt Power BI (A ou B) | Encadrant → n'importe quelle IA | Guide + DAX + plan dashboard |
| 3. Power BI Desktop | Encadrant suit 5–10 min | **Dashboard visible sur son PC** |

Principe du POC : **l'IA produit le livrable Power BI ; l'humain valide dans Power BI Desktop.**

---

## D. Fichiers de référence dans le dépôt

| Fichier | Rôle |
| --- | --- |
| `prompts/prompt_claude_powerbi_reservation.md` | Ce prompt (A + B) |
| `samples/powerbi/reservation/reservation_dax_measures.md` | Mesures DAX prêtes |
| `docs/05-cas-etude/15-powerbi-reservation.md` | Cadrage cas réservations (si présent) |
