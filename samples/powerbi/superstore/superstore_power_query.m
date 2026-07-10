// =============================================================================
// Power Query (M) — Cas Superstore Phase 9
// Usage : dans Power BI Desktop → Transform data → requete → Advanced Editor
// Remplacer Server et Database si besoin.
// =============================================================================

// -----------------------------------------------------------------------------
// Requete 1 : stg_fact_sales  (renommer la requete : Fact Sales)
// -----------------------------------------------------------------------------
let
    Source = Sql.Database("NESNOUSSA\SQLEXPRESS", "POC_ETL_IA"),
    dbo_stg_fact_sales = Source{[Schema="dbo", Item="stg_fact_sales"]}[Data],
    FilterBatch = Table.SelectRows(dbo_stg_fact_sales, each [batch_id] = 1),
    RemoveTech = Table.RemoveColumns(FilterBatch, {"batch_id", "source_system", "load_ts"}),
    Typed = Table.TransformColumnTypes(
        RemoveTech,
        {
            {"order_date", type date},
            {"ship_date", type date},
            {"sales", type number},
            {"profit", type number},
            {"discount", type number},
            {"margin_pct", type number},
            {"quantity", Int64.Type}
        }
    )
in
    Typed

// -----------------------------------------------------------------------------
// Requete 2 : stg_dim_customer  (renommer : Dim Customer)
// -----------------------------------------------------------------------------
let
    Source = Sql.Database("NESNOUSSA\SQLEXPRESS", "POC_ETL_IA"),
    dbo_stg_dim_customer = Source{[Schema="dbo", Item="stg_dim_customer"]}[Data],
    FilterBatch = Table.SelectRows(dbo_stg_dim_customer, each [batch_id] = 1),
    RemoveTech = Table.RemoveColumns(
        FilterBatch,
        {"batch_id", "source_system", "load_ts", "is_active"}
    )
in
    RemoveTech

// -----------------------------------------------------------------------------
// Requete 3 : stg_dim_product  (renommer : Dim Product)
// -----------------------------------------------------------------------------
let
    Source = Sql.Database("NESNOUSSA\SQLEXPRESS", "POC_ETL_IA"),
    dbo_stg_dim_product = Source{[Schema="dbo", Item="stg_dim_product"]}[Data],
    FilterBatch = Table.SelectRows(dbo_stg_dim_product, each [batch_id] = 1),
    RemoveTech = Table.RemoveColumns(FilterBatch, {"batch_id", "source_system", "load_ts"})
in
    RemoveTech
