# Mesures DAX — Cas Superstore (Phase 9)

Tables du modele (noms apres renommage suggere) :

- `Fact Sales` ← `stg_fact_sales`
- `Dim Customer` ← `stg_dim_customer`
- `Dim Product` ← `stg_dim_product`

Si vous n'avez pas renomme les tables, remplacer `Fact Sales` par `stg_fact_sales`, etc.

---

## Mesures principales (table Fact Sales)

### Total Sales

```dax
Total Sales =
SUM ( 'Fact Sales'[sales] )
```

### Total Profit

```dax
Total Profit =
SUM ( 'Fact Sales'[profit] )
```

### Total Quantity

```dax
Total Quantity =
SUM ( 'Fact Sales'[quantity] )
```

### Margin %

Marge globale = profit / ventes (pas moyenne des margin_pct ligne a ligne).

```dax
Margin % =
DIVIDE ( [Total Profit], [Total Sales], 0 )
```

Format : **Pourcentage**, 1 decimale.

### # Orders

```dax
# Orders =
DISTINCTCOUNT ( 'Fact Sales'[order_id] )
```

### Avg Discount

```dax
Avg Discount =
AVERAGE ( 'Fact Sales'[discount] )
```

Format : **Pourcentage**.

---

## Mesures analytiques (optionnel)

### Sales YTD

Necessite une colonne date sur le fait.

```dax
Sales YTD =
TOTALYTD ( [Total Sales], 'Fact Sales'[order_date] )
```

### Profit par client (exemple contexte filtre)

```dax
Profit Margin by Context =
DIVIDE ( [Total Profit], [Total Sales] )
```

---

## Points de vigilance DAX

| Sujet | Detail |
| --- | --- |
| Contexte de filtre | `Total Sales` en barres par `region` filtre via la relation Dim Customer |
| Margin % | Utiliser DIVIDE sur totaux, pas AVERAGE(margin_pct) |
| Dates | `order_date` sur le fait ; pas de Dim Date separee dans ce POC |
| Blank | Si relation cassee, les visuels par region/category seront vides |

---

## Validation rapide

Dans Power BI, carte **Total Sales** doit egaler :

```sql
SELECT SUM(sales) FROM stg_fact_sales WHERE batch_id = 1;
```

Carte **# Orders** doit egaler :

```sql
SELECT COUNT(DISTINCT order_id) FROM stg_fact_sales WHERE batch_id = 1;
```
