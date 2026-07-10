// =====================================================================
// TEMPLATE GÉNÉRIQUE — Requête Power Query (M)
// ---------------------------------------------------------------------
// Objectif : charger et préparer une table depuis SQL Server (ou autre
// source) vers Power BI, de façon réutilisable sur n'importe quel projet.
//
// Comment l'utiliser :
//   1. Remplacer les variables { } par votre contexte.
//   2. Adapter la liste des colonnes sélectionnées et renommées.
//   3. Ajouter/retirer des étapes selon le besoin (filtres, types...).
//
// Variables à remplacer :
//   {serveur}   -> nom du serveur SQL, ex. NESNOUSSA\SQLEXPRESS
//   {base}      -> base de données, ex. POC_ETL_IA
//   {schema}    -> schéma, ex. dbo
//   {objet}     -> table ou vue source, ex. stg_dim_customer
// =====================================================================
let
    // 1. Connexion à la source
    Source = Sql.Database("{serveur}", "{base}"),
    Table_source = Source{[Schema = "{schema}", Item = "{objet}"]}[Data],

    // 2. Sélection des colonnes utiles (à adapter)
    ColonnesChoisies = Table.SelectColumns(
        Table_source,
        {"cle_metier", "attribut_1", "attribut_2"}
    ),

    // 3. Renommage lisible pour l'utilisateur métier (à adapter)
    ColonnesRenommees = Table.RenameColumns(
        ColonnesChoisies,
        {
            {"cle_metier", "Identifiant"},
            {"attribut_1", "Libellé"},
            {"attribut_2", "Catégorie"}
        }
    ),

    // 4. Typage explicite des colonnes (à adapter)
    TypesDefinis = Table.TransformColumnTypes(
        ColonnesRenommees,
        {
            {"Identifiant", type text},
            {"Libellé", type text},
            {"Catégorie", type text}
        }
    ),

    // 5. Suppression des lignes vides sur la clé
    LignesValides = Table.SelectRows(
        TypesDefinis,
        each [Identifiant] <> null and [Identifiant] <> ""
    )
in
    LignesValides
