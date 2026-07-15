# Mesures DAX — Cas réservations d'hôtel

Créer ces mesures dans la table `fact_reservation` (ou une table `_Mesures`).

```dax
CA Total =
SUM ( fact_reservation[montant] )
```

```dax
Nb Réservations =
DISTINCTCOUNT ( fact_reservation[reservation_id] )
```

```dax
Nb Nuits Total =
SUM ( fact_reservation[nb_nuits] )
```

```dax
CA Moyen / Réservation =
DIVIDE ( [CA Total], [Nb Réservations] )
```

```dax
Montant Moyen / Nuit =
AVERAGE ( fact_reservation[montant_par_nuit] )
```

```dax
Nb Clients Distincts =
DISTINCTCOUNT ( fact_reservation[client_key] )
```

## Contrôle SQL

```sql
SELECT COUNT(*) AS nb, SUM(montant) AS ca, SUM(nb_nuits) AS nuits
FROM fact_reservation;
```
