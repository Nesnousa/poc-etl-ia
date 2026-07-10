# Exemples de mesures DAX pour le POC

## Total Sales

```DAX
Total Sales :=
SUM ( 'FactSales'[SalesAmount] )
```

## Sales YTD

```DAX
Sales YTD :=
TOTALYTD (
    [Total Sales],
    'DimDate'[Date]
)
```

## Sales Growth %

```DAX
Sales Growth % :=
VAR CurrentSales = [Total Sales]
VAR PreviousSales =
    CALCULATE (
        [Total Sales],
        DATEADD ( 'DimDate'[Date], -1, YEAR )
    )
RETURN
    DIVIDE ( CurrentSales - PreviousSales, PreviousSales )
```

## Points de vigilance

- verifier le role de la table date
- verifier le contexte de filtre
- tester les cas ou PreviousSales est nul
