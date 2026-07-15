# Prompt — Power BI après ETL (réservations + générique)

> Coller dans Claude Max / Claude Desktop / ChatGPT / Copilot.
> Prérequis : le DW réservations est déjà chargé dans `POC_ETL_IA`.
> Sur ce PC le livrable Power BI est déjà généré :
> `samples/powerbi/reservation/Reservation_Hotel_POC/Reservation_Hotel_POC.pbip`

---

## A. Version réservations (prête à coller)

```
Tu es un expert Power BI (modèle étoile + DAX + dashboard).

CONTEXTE
- SQL Server : NESNOUSSA\SQLEXPRESS
- Base : POC_ETL_IA
- DW déjà chargé :
  fact_reservation, dim_client, dim_chambre, dim_date
- Colonnes fait : reservation_key, reservation_id, client_key, chambre_key,
  date_key, nb_nuits, montant, montant_par_nuit
- Colonnes dims :
  dim_client(client_key, client_id, client_nom_clean, ville, pays)
  dim_chambre(chambre_key, chambre_id, type_chambre, capacite)
  dim_date(date_key, date_complete, annee, mois, jour)

OBJECTIF
Livrer exactement ce qu'il faut pour rejouer le même travail Power BI sur mon PC :
1) relations du modèle
2) mesures DAX (code prêt à coller)
3) disposition du dashboard Overview Réservations
4) SQL de contrôle des totaux

MESURES ATTENDUES
- CA Total = SUM(fact_reservation[montant])
- Nb Réservations = DISTINCTCOUNT(fact_reservation[reservation_id])
- Nb Nuits Total = SUM(fact_reservation[nb_nuits])
- CA Moyen / Réservation = DIVIDE([CA Total], [Nb Réservations])
- Montant Moyen / Nuit = AVERAGE(fact_reservation[montant_par_nuit])
- Nb Clients Distincts = DISTINCTCOUNT(fact_reservation[client_key])

DASHBOARD
- 4 cartes KPI en haut
- barres CA par ville
- colonnes CA par type_chambre
- courbe CA par date_complete
- table Top clients (nom, ville, CA, Nb réservations)

Si tu as MCP filesystem, ouvre / vérifie le projet déjà livré :
samples/powerbi/reservation/Reservation_Hotel_POC/Reservation_Hotel_POC.pbip
Sinon, donne les étapes exactes pour Power BI Desktop (Import SQL Server).
```

---

## B. Version générique (toute IA / tout projet)

Remplacez `{serveur} {base} {fait} {dimensions} {cles} {kpis} {axes}` puis collez.

```
Tu es un expert Power BI.
Serveur={serveur} Base={base}
Fait={fait} Dimensions={dimensions} Clés={cles}
KPI={kpis} Axes dashboard={axes}
Le DW est déjà chargé. Produis : relations, DAX, plan dashboard, SQL de contrôle.
N'invente aucune colonne. Mode Import. Français, étapes actionnables.
```
