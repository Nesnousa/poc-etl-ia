"""
Application de démonstration du POC IA pour l'ETL et Power BI.
Lancement : streamlit run app/streamlit_demo.py
"""

from pathlib import Path

import streamlit as st

from superstore_qc import get_demo_diagnostic, get_guide, run_demo_qc, run_diagnostic, run_superstore_qc
from theme import (
    LOGO_PATH,
    badge,
    footer,
    hero,
    inject_global_css,
    render_sidebar_brand,
    render_topbar,
    section_title,
)

ROOT = Path(__file__).resolve().parents[1]

PROMPT_FILES = {
    "7B-1 — Setup SQL staging": ROOT / "prompts" / "prompt_sql_staging_setup.md",
    "7B-2 — Ingestion Python CSV": ROOT / "prompts" / "prompt_python_ingest.md",
    "7B-3/4 — Package SSIS dimension": ROOT / "prompts" / "prompt_ssis_dimension_package.md",
    "7B-4 — Package SSIS fait ventes": ROOT / "prompts" / "prompt_ssis_fact_package.md",
    "7B-5 — Contrôles qualité SQL": ROOT / "prompts" / "prompt_sql_quality_checks.md",
    "SSIS générique (repli)": ROOT / "prompts" / "prompt_ssis_template_generation.md",
    "Phase 9 — Modèle Power BI": ROOT / "prompts" / "prompt_powerbi_model.md",
    "Phase 9 — Mesure DAX": ROOT / "prompts" / "prompt_powerbi_dax.md",
    "Phase 9 — Power Query (M)": ROOT / "prompts" / "prompt_power_query.md",
}

TEMPLATE_FILES = {
    "Table de staging SQL": ROOT / "templates" / "sql" / "staging_table_template.sql",
    "Contrôles qualité": ROOT / "templates" / "quality" / "data_quality_checks_template.sql",
    "Cadre de journalisation (logging)": ROOT / "templates" / "logging" / "etl_logging_framework.sql",
    "Package SSIS": ROOT / "templates" / "ssis" / "source_to_staging_template.md",
    "Mesure DAX": ROOT / "templates" / "powerbi" / "dax_measure_template.md",
    "Power Query": ROOT / "templates" / "powerbi" / "power_query_template.m",
}

# Mode d'emploi de chaque template : outil, moment, variables et etapes concretes.
TEMPLATE_USAGE = {
    "Table de staging SQL": {
        "outil": "SSMS (SQL Server Management Studio)",
        "moment": "Tout au début, AVANT de créer le package SSIS.",
        "variables": "{schema}, {table_staging}, {colonne_cle}",
        "etapes": [
            "Ouvrir SSMS et se connecter à la base cible.",
            "Nouvelle requête, puis coller le template.",
            "Remplacer {schema}, {table_staging} et {colonne_cle} par votre contexte.",
            "Adapter la zone « colonnes métier » aux champs de votre source.",
            "Exécuter (F5) : la table de staging est créée, prête à être remplie par SSIS.",
        ],
    },
    "Cadre de journalisation (logging)": {
        "outil": "SSMS (SQL Server Management Studio)",
        "moment": "Une seule fois par base, avant les packages SSIS.",
        "variables": "Aucune — noms standard à conserver.",
        "etapes": [
            "Ouvrir SSMS sur la base cible.",
            "Coller le template dans une nouvelle requête.",
            "Exécuter : crée les tables etl_run_log / etl_error_log et les procédures usp_log_etl_run_start / usp_log_etl_run_end.",
            "Ces procédures seront ensuite appelées depuis les packages SSIS.",
        ],
    },
    "Package SSIS": {
        "outil": "Visual Studio / SSDT (le seul template réellement « dans SSIS »)",
        "moment": "Le chargement des données : source → table de staging.",
        "variables": "{nom_package}, {source}, {table_staging}, {source_system}",
        "etapes": [
            "Créer un package (.dtsx) dans Visual Studio / SSDT.",
            "Control Flow : ajouter un « Exécuter SQL » qui appelle usp_log_etl_run_start.",
            "Ajouter un Data Flow Task : Source → Derived Column (batch_id, source_system, load_ts) → Lookup (optionnel) → Destination OLE DB vers {table_staging}.",
            "Control Flow : « Exécuter SQL » de clôture qui appelle usp_log_etl_run_end.",
            "Ajouter un gestionnaire OnError qui écrit dans etl_error_log.",
            "Exécuter le package et vérifier le run dans etl_run_log (statut SUCCESS).",
        ],
    },
    "Contrôles qualité": {
        "outil": "SSMS (ou directement la page « Contrôles qualité Superstore » de cette app)",
        "moment": "APRÈS le chargement SSIS, pour valider les données.",
        "variables": "{table}, {cle}, {table_dim}, {cle_dim}, {colonne_num}, {min}, {max}",
        "etapes": [
            "Ouvrir SSMS une fois les tables de staging remplies.",
            "Coller le template et remplacer les variables par vos tables / colonnes.",
            "Garder les contrôles pertinents (volume, NULL, doublons, clés orphelines, bornes).",
            "Exécuter : chaque contrôle renvoie PASS ou FAIL avec la valeur observée.",
            "En cas de FAIL, corriger la source ou le package puis relancer.",
        ],
    },
    "Mesure DAX": {
        "outil": "Power BI Desktop",
        "moment": "Après import des tables et création des relations (modèle en étoile).",
        "variables": "{table_faits}, {colonne}, {table_dates}, {colonne_filtre}",
        "etapes": [
            "Ouvrir le modèle dans Power BI Desktop.",
            "Volet Données : clic droit sur la table de faits → Nouvelle mesure.",
            "Coller le patron adapté (total, filtre, ratio, cumul YTD).",
            "Remplacer {table_faits} et {colonne} par vos objets.",
            "Valider le résultat dans un visuel et documenter la mesure.",
        ],
    },
    "Power Query": {
        "outil": "Power BI Desktop (éditeur Power Query)",
        "moment": "Au moment d'importer les tables de staging dans Power BI.",
        "variables": "{serveur}, {base}, {schema}, {objet}",
        "etapes": [
            "Power BI Desktop → Transformer les données (ouvre Power Query).",
            "Nouvelle source vide → Éditeur avancé.",
            "Coller le code M et remplacer {serveur}, {base}, {schema}, {objet}.",
            "Adapter les colonnes sélectionnées, renommées et typées.",
            "Fermer et appliquer : la table est chargée dans le modèle.",
        ],
    },
}

# Etape POC -> template de base -> prompt IA -> livrable de reference (cas Superstore)
PIPELINE_STEPS = [
    {
        "etape": "7B-1 — Setup SQL",
        "template": "Table de staging SQL + Cadre de journalisation",
        "prompt": "7B-1 — Setup SQL staging",
        "reference": "samples/sqlserver/cas_etude_superstore_setup.sql",
    },
    {
        "etape": "7B-2 — Ingestion Python",
        "template": "— (script Python, pas de template SQL)",
        "prompt": "7B-2 — Ingestion Python CSV",
        "reference": "samples/python/ingest_superstore_to_sql.py",
    },
    {
        "etape": "7B-3 — Dimension client",
        "template": "Package SSIS",
        "prompt": "7B-3/4 — Package SSIS dimension",
        "reference": "ssis/superstore/generate_ssis_dim_customer.py",
    },
    {
        "etape": "7B-4 — Dimension produit",
        "template": "Package SSIS",
        "prompt": "7B-3/4 — Package SSIS dimension",
        "reference": "ssis/superstore/generate_ssis_dim_product.py",
    },
    {
        "etape": "7B-4 — Fait ventes",
        "template": "Package SSIS",
        "prompt": "7B-4 — Package SSIS fait ventes",
        "reference": "ssis/superstore/generate_ssis_fact_sales.py",
    },
    {
        "etape": "7B-5 — Contrôles qualité",
        "template": "Contrôles qualité",
        "prompt": "7B-5 — Contrôles qualité SQL",
        "reference": "samples/sqlserver/cas_etude_superstore_quality_checks.sql",
    },
    {
        "etape": "Phase 9 — Power BI",
        "template": "Mesure DAX + Power Query",
        "prompt": "Phase 9 — Modèle Power BI",
        "reference": "docs/05-cas-etude/11-guide-powerbi-superstore-phase9.md",
    },
]

TEMPLATE_TO_PROMPT = {
    "Table de staging SQL": "7B-1 — Setup SQL staging",
    "Contrôles qualité": "7B-5 — Contrôles qualité SQL",
    "Cadre de journalisation (logging)": "7B-1 — Setup SQL staging",
    "Package SSIS": "7B-3/4 — Package SSIS dimension",
    "Mesure DAX": "Phase 9 — Mesure DAX",
    "Power Query": "Phase 9 — Power Query (M)",
}

PHASES = [
    ("7B-1", "Setup SQL staging", "done"),
    ("7B-2", "Ingestion Python", "done"),
    ("7B-3", "Dimension client (SSIS)", "done"),
    ("7B-4", "Dimension produit + fait ventes (SSIS)", "done"),
    ("7B-5", "Contrôles qualité", "done"),
    ("Phase 9", "Modèle Power BI", "done"),
    ("Phase 10", "Évaluation MCP + IA", "progress"),
]

SUPERSTORE_QC_SQL = ROOT / "samples" / "sqlserver" / "cas_etude_superstore_quality_checks.sql"
DEFAULT_SERVER = r"NESNOUSSA\SQLEXPRESS"
DEFAULT_DATABASE = "POC_ETL_IA"

PAGES = [
    "Accueil",
    "Bibliothèque de templates",
    "Prompts IA",
    "Cas d'étude",
    "Contrôles qualité Superstore",
    "Phase 10 — MCP & IA",
    "MCP SQL — Staging & DW",
    "ETL — Source → Staging → DW",
    "Mesure des gains",
]

MCP_DOC = ROOT / "docs" / "05-cas-etude" / "12-evaluation-mcp-powerbi-phase10.md"

MCP_CONFIG_SNIPPET = """{
  "mcpServers": {
    "powerbi-modeling-mcp": {
      "command": "C:\\\\Users\\\\<utilisateur>\\\\.vscode\\\\extensions\\\\analysis-services.powerbi-modeling-mcp-0.4.0-win32-x64\\\\server\\\\powerbi-modeling-mcp.exe",
      "args": ["--start"],
      "env": {}
    }
  }
}"""

MCP_TABLES = [
    {"Table": "stg_fact_sales", "Type": "Table de faits", "Visible": "Oui", "Stockage": "Import"},
    {"Table": "stg_dim_customer", "Type": "Dimension", "Visible": "Oui", "Stockage": "Import"},
    {"Table": "stg_dim_product", "Type": "Dimension", "Visible": "Oui", "Stockage": "Import"},
    {"Table": "LocalDateTable_... (×2)", "Type": "Calendrier auto-généré", "Visible": "Non (masqué)", "Stockage": "Import"},
]

MCP_RELATIONS = [
    {"De": "stg_fact_sales[customer_id]", "Vers": "stg_dim_customer[customer_id]", "Cardinalité": "Plusieurs → un", "Active": "Oui", "Filtrage": "Sens unique"},
    {"De": "stg_fact_sales[product_id]", "Vers": "stg_dim_product[product_id]", "Cardinalité": "Plusieurs → un", "Active": "Oui", "Filtrage": "Sens unique"},
    {"De": "stg_fact_sales[order_date]", "Vers": "LocalDateTable (order_date)", "Cardinalité": "Plusieurs → un", "Active": "Oui", "Filtrage": "Sens unique"},
    {"De": "stg_fact_sales[ship_date]", "Vers": "LocalDateTable (ship_date)", "Cardinalité": "Plusieurs → un", "Active": "Oui", "Filtrage": "Sens unique"},
]

MCP_MEASURES = [
    {"Mesure": "Total Sales", "Expression DAX": "SUM(stg_fact_sales[sales])"},
    {"Mesure": "Total Profit", "Expression DAX": "SUM(stg_fact_sales[profit])"},
    {"Mesure": "Margin %", "Expression DAX": "DIVIDE([Total Profit], [Total Sales], 0)"},
    {"Mesure": "# Orders", "Expression DAX": "DISTINCTCOUNT(stg_fact_sales[order_id])"},
]

MCP_RECOMMENDATIONS = [
    {
        "Constat": "Double calendrier automatique (Auto date/time), une table cachée par colonne date",
        "Recommandation de l'IA": "Créer une table Dim_Date unique + USERELATIONSHIP pour ship_date",
        "Décision retenue": "Conservé tel quel pour le POC",
    },
    {
        "Constat": "Préfixe stg_ sur les noms de tables du modèle final",
        "Recommandation de l'IA": "Renommer en Dim_Customer / Fact_Sales pour la lisibilité",
        "Décision retenue": "Aucun impact fonctionnel — pas de changement",
    },
]

MCP_COMPARATIF = [
    {"Indicateur": "Lister tables, relations, mesures", "Audit manuel (estimation)": "10 à 15 min", "Avec Claude + MCP (mesuré)": "≈ 30 secondes"},
    {"Indicateur": "Détection du schéma en étoile", "Audit manuel (estimation)": "Manuelle, selon l'expérience", "Avec Claude + MCP (mesuré)": "Automatique et argumentée"},
    {"Indicateur": "Proposition de bonnes pratiques", "Audit manuel (estimation)": "Dépend d'un expert BI présent", "Avec Claude + MCP (mesuré)": "Systématique"},
]

# ---------------------------------------------------------------------------
# Page « MCP SQL — Staging & DW » : l'IA écrit dans SQL Server via MCP
# ---------------------------------------------------------------------------
MCP_SQL_DOC = ROOT / "docs" / "05-cas-etude" / "13-demo-ia-mcp-sql-staging-dw.md"
MCP_SQL_PROMPT = ROOT / "prompts" / "prompt_claude_mcp_staging_dw.md"
MCP_SQL_SCRIPT = ROOT / "samples" / "sqlserver" / "demo_ia_staging_dw.sql"

MCP_SQL_CONFIG_SNIPPET = """{
  "mcpServers": {
    "mssql": {
      "command": "npx",
      "args": ["-y", "mssql-mcp@latest"],
      "env": {
        "DB_SERVER": "NESNOUSSA\\\\SQLEXPRESS",
        "DB_DATABASE": "POC_ETL_IA",
        "DB_USER": "votre_login",
        "DB_PASSWORD": "votre_mot_de_passe",
        "DB_ENCRYPT": "false",
        "DB_TRUST_SERVER_CERTIFICATE": "true"
      }
    }
  }
}"""

MCP_SQL_COMPARE = [
    {"Aspect": "Rôle", "Table de staging": "Recevoir les données préparées", "Data Warehouse (DW)": "Servir l'analyse (Power BI, reporting)"},
    {"Aspect": "Clé", "Table de staging": "Clé métier (ex. client_id)", "Data Warehouse (DW)": "Clé de substitution (ex. client_key) + clé métier unique"},
    {"Aspect": "Données", "Table de staging": "Parfois brutes (doublons, casse)", "Data Warehouse (DW)": "Nettoyées et dédoublonnées"},
    {"Aspect": "Structure", "Table de staging": "Une table « à plat »", "Data Warehouse (DW)": "Schéma en étoile : dimensions + faits + relations"},
    {"Aspect": "Colonnes en plus", "Table de staging": "batch_id, source_system, load_ts", "Data Warehouse (DW)": "Historisation (valid_from, is_current) + audit (dw_load_ts)"},
]

MCP_SQL_RESULT = [
    {"Table": "stg_hotel_reservation_demo", "Type": "Staging", "Lignes": "5", "Détail": "dont 1 doublon"},
    {"Table": "dim_client_demo", "Type": "Dimension", "Lignes": "3", "Détail": "dédoublonné, noms nettoyés"},
    {"Table": "dim_chambre_demo", "Type": "Dimension", "Lignes": "3", "Détail": "une ligne par chambre"},
    {"Table": "dim_date_demo", "Type": "Dimension (date)", "Lignes": "4", "Détail": "dates d'arrivée distinctes"},
    {"Table": "fact_reservation_demo", "Type": "Faits", "Lignes": "4", "Détail": "relié aux 3 dimensions (clés étrangères)"},
]

# ---------------------------------------------------------------------------
# Page « ETL — Source → Staging → DW » : pipeline SSIS + SQL (réservations)
# ---------------------------------------------------------------------------
ETL_DOC = ROOT / "docs" / "05-cas-etude" / "14-etl-ssis-reservation.md"
ETL_SETUP_SQL = ROOT / "samples" / "sqlserver" / "reservation_etl_setup.sql"
ETL_PROCS_SQL = ROOT / "samples" / "sqlserver" / "reservation_etl_procedures.sql"
ETL_SSIS_GEN = ROOT / "ssis" / "reservation" / "generate_ssis_stg_reservation.py"
ETL_MCP_PROMPT = ROOT / "prompts" / "prompt_claude_mcp_etl_complet.md"

ETL_CONNECTOR = [
    {"Besoin": "Claude exécute du SQL (créer tables, lancer l'ETL)", "Connecteur ?": "Oui — MCP SQL Server (mssql)", "Statut": "✅ 100 % no-touch"},
    {"Besoin": "Claude génère un package SSIS (.dtsx)", "Connecteur ?": "Non", "Statut": "❌ Pas de MCP pour créer du SSIS"},
    {"Besoin": "Claude lit / migre un package SSIS existant", "Connecteur ?": "Oui (SSIS→ADF, SSIS→Databricks)", "Statut": "⚠️ Analyse / migration"},
]

ETL_RESULT = [
    {"Table": "raw_hotel_reservation", "Couche": "Source (brut)", "Lignes": "6", "Détail": "dont 1 doublon"},
    {"Table": "stg_hotel_reservation", "Couche": "Staging", "Lignes": "6", "Détail": "typé + traçabilité"},
    {"Table": "dim_client", "Couche": "DW — Dimension", "Lignes": "4", "Détail": "dédoublonné, noms nettoyés"},
    {"Table": "dim_chambre", "Couche": "DW — Dimension", "Lignes": "3", "Détail": "une ligne par chambre"},
    {"Table": "dim_date", "Couche": "DW — Dimension", "Lignes": "5", "Détail": "dates distinctes"},
    {"Table": "fact_reservation", "Couche": "DW — Faits", "Lignes": "5", "Détail": "relié aux 3 dimensions (FK)"},
]


def read_text(path: Path) -> str:
    if not path.exists():
        return (
            f"[Fichier manquant dans le déploiement : `{path.as_posix()}`]\n\n"
            "Ce contenu est disponible dans le dépôt local du POC."
        )
    return path.read_text(encoding="utf-8")


st.set_page_config(
    page_title="POC IA — ETL & Power BI | EY",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📊",
    layout="wide",
)

inject_global_css()

# ---------------------------------------------------------------------------
# Barre latérale : marque, navigation et suivi d'avancement
# ---------------------------------------------------------------------------
render_sidebar_brand("POC IA pour l'ETL et Power BI — Stage EY")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigation", PAGES, label_visibility="visible")

st.sidebar.markdown("---")
st.sidebar.markdown("**Avancement du programme**")
dot_colors = {"done": "#3DDC84", "progress": "#FFE600", "todo": "#5C5C68"}
for code, label, status in PHASES:
    dot = dot_colors[status]
    st.sidebar.markdown(
        f'<div class="ey-phase-item">'
        f'<div class="ey-phase-head"><span class="ey-phase-dot" '
        f'style="background:{dot};"></span><b>{code}</b></div>'
        f'<div class="ey-phase-label">{label}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.caption("Ministère de l'Enseignement Supérieur et de la Recherche Scientifique — Stage EY, 2026.")

# ---------------------------------------------------------------------------
# Bandeau supérieur
# ---------------------------------------------------------------------------
render_topbar(
    title="POC IA — Bibliothèque ETL & Power BI",
    subtitle="Démonstration interne : accélérer l'ETL et la BI avec l'IA, sous supervision humaine",
)

# ---------------------------------------------------------------------------
# Page : Accueil
# ---------------------------------------------------------------------------
if page == "Accueil":
    hero(
        eyebrow="Programme d'innovation — Stage EY",
        title="Une bibliothèque de composants ETL et BI accélérée par l'IA",
        description=(
            "Ce POC démontre comment l'intelligence artificielle peut accélérer la production "
            "de composants ETL (SQL, SSIS) et Power BI (Power Query, DAX), tout en conservant "
            "une validation humaine systématique à chaque étape. La démonstration s'appuie sur "
            "un cas d'étude réel : le jeu de données Superstore (environ 10 000 lignes)."
        ),
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Templates ETL / BI", str(len(TEMPLATE_FILES)))
    col2.metric("Prompts IA opérationnels", str(len(PROMPT_FILES)))
    col3.metric("Contrôles qualité Superstore", "12 / 12", delta="Tous PASS", delta_color="normal")
    col4.metric("Étapes du pipeline couvertes", str(len(PIPELINE_STEPS)))

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    with left:
        section_title("Architecture de la démonstration")
        st.markdown(
            """
            <div class="ey-card">
            <b>CSV Kaggle</b> → <b>Ingestion Python</b> → <code>raw_superstore</code> (SQL Server)
            → <b>Packages SSIS</b> (dimensions client / produit, fait ventes) → tables de
            <b>staging</b> → <b>contrôles qualité</b> automatisés → <b>modèle Power BI</b>
            (DAX, Power Query) → <b>évaluation MCP</b> avec un assistant IA.
            </div>
            """,
            unsafe_allow_html=True,
        )

        section_title("Comment utiliser cette application")
        st.markdown(
            """
            <div class="ey-card">

            L'application se lit de haut en bas dans la barre de navigation à gauche :

            - **Bibliothèque de templates** — squelettes réutilisables (SQL, SSIS, DAX, Power Query).
            - **Prompts IA** — instructions structurées à copier dans un assistant IA (Claude Max, Cursor, Copilot...).
            - **Cas d'étude** — cadrage fonctionnel et technique des scénarios traités par le POC.
            - **Contrôles qualité Superstore** — exécution en direct des 12 contrôles qualité du pipeline.
            - **Phase 10 — MCP & IA** — l'IA analyse un modèle Power BI en lecture, via le protocole MCP.
            - **MCP SQL — Staging & DW** — l'IA **écrit** dans SQL Server via MCP (crée et charge un modèle en étoile).
            - **ETL — Source → Staging → DW** — pipeline complet ; **Claude Max exécute tout l'ETL** à partir d'un prompt.
            - **Mesure des gains** — comparaison chiffrée entre approche manuelle et approche assistée par IA.

            </div>
            """,
            unsafe_allow_html=True,
        )

        section_title("Nouveau : l'IA fait le travail via Claude Max (MCP)")
        st.markdown(
            """
            <div class="ey-card" style="border-left:5px solid #FFE600;">
            Grâce au protocole <b>MCP</b>, l'encadrant n'a plus besoin de coder ni de cliquer :
            il colle un <b>prompt</b> dans <b>Claude Max</b> (connecté à SQL Server et Power BI),
            et l'IA réalise le travail à sa place, puis affiche les résultats.
            <br><br>
            <b>Encadrant → Claude Max → MCP → SQL Server / Power BI → résultat visible dans SSMS</b>
            <br><br>
            Deux pages le démontrent concrètement : <b>MCP SQL — Staging & DW</b> (l'IA crée le modèle)
            et <b>ETL — Source → Staging → DW</b> (l'IA exécute tout le pipeline). Le tout est
            <b>générique</b> : le même principe s'applique à n'importe quel projet.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        section_title("Feuille de route du POC")
        status_labels = {"done": "Terminé", "progress": "En cours", "todo": "À venir"}
        status_badges = {"done": "ey-badge-pass", "progress": "ey-badge-warn", "todo": "ey-badge-fail"}
        rows_html = ""
        for code, label, status in PHASES:
            css_class = status_badges[status]
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:8px 0;border-bottom:1px solid #EEEEF2;">'
                f'<span><b>{code}</b> — {label}</span>'
                f'<span class="ey-badge {css_class}">{status_labels[status]}</span>'
                f"</div>"
            )
        st.markdown(f'<div class="ey-card">{rows_html}</div>', unsafe_allow_html=True)

        section_title("Principe de validation humaine")
        st.markdown(
            """
            <div class="ey-card">
            L'IA <b>accélère la conception</b> (SQL, prompts, documentation, DAX), mais chaque
            livrable passe par une <b>validation humaine obligatoire</b> avant d'être considéré
            comme fiable :
            <ul>
                <li>Relecture du code généré</li>
                <li>Exécution réelle (SSMS, Visual Studio, Power BI)</li>
                <li>Contrôles qualité automatisés</li>
                <li>Comparaison avec le résultat attendu</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Page : Bibliothèque de templates
# ---------------------------------------------------------------------------
elif page == "Bibliothèque de templates":
    hero(
        eyebrow="Bibliothèque réutilisable",
        title="Templates ETL & Power BI",
        description=(
            "Les templates sont des squelettes réutilisables (SQL, SSIS, DAX, Power Query). "
            "Ils ne constituent pas un livrable fini : ils servent de point de départ, enrichis "
            "par l'IA à l'aide des prompts associés, puis validés par un humain."
        ),
    )

    section_title("Méthode d'utilisation d'un template")
    st.markdown(
        """
        <div class="ey-card">

        1. **Choisir un template** (squelette) dans la liste ci-dessous.
        2. **Copier le prompt IA associé** (page *Prompts IA* — voir le tableau du parcours ci-dessous).
        3. **Remplacer les `{variables}`** par le contexte réel du projet
           (ex. `source = vw_extract_superstore_customers`, `cible = stg_dim_customer`).
        4. **Coller le prompt dans Claude Max** (ou Cursor / un autre assistant IA) → l'IA génère le code,
           et avec MCP elle peut même l'**exécuter directement** sur la base.
        5. **Valider manuellement** (SSMS, Visual Studio, contrôles qualité) — étape obligatoire.

        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Parcours Superstore, étape par étape")
    st.dataframe(
        {
            "Étape": [s["etape"] for s in PIPELINE_STEPS],
            "Template de base": [s["template"] for s in PIPELINE_STEPS],
            "Prompt IA": [s["prompt"] for s in PIPELINE_STEPS],
            "Livrable de référence (validé)": [s["reference"] for s in PIPELINE_STEPS],
        },
        width="stretch",
        hide_index=True,
    )

    st.info(
        "Le livrable de **référence** est l'implémentation Superstore déjà validée dans le dépôt. "
        "Un nouveau projet repart du template et du prompt, puis doit suivre la même validation."
    )

    st.markdown("---")
    section_title("Explorer un template")
    selected_template = st.selectbox("Choisir un template", list(TEMPLATE_FILES.keys()))
    linked_prompt = TEMPLATE_TO_PROMPT.get(selected_template)
    if linked_prompt:
        st.caption(f"Prompt IA recommandé pour ce template : **{linked_prompt}** (page Prompts IA)")

    usage = TEMPLATE_USAGE.get(selected_template)
    if usage:
        st.markdown("**Où et comment l'utiliser**")
        u1, u2, u3 = st.columns(3)
        u1.markdown(
            f'<div class="ey-card" style="min-height:118px;"><b>Outil</b>'
            f'<p style="font-size:0.85rem;margin-top:6px;">{usage["outil"]}</p></div>',
            unsafe_allow_html=True,
        )
        u2.markdown(
            f'<div class="ey-card" style="min-height:118px;"><b>Quand</b>'
            f'<p style="font-size:0.85rem;margin-top:6px;">{usage["moment"]}</p></div>',
            unsafe_allow_html=True,
        )
        u3.markdown(
            f'<div class="ey-card" style="min-height:118px;"><b>Variables à remplacer</b>'
            f'<p style="font-size:0.85rem;margin-top:6px;"><code>{usage["variables"]}</code></p></div>',
            unsafe_allow_html=True,
        )
        steps_html = "".join(f"<li>{step}</li>" for step in usage["etapes"])
        st.markdown(
            f'<div class="ey-card"><b>Étapes</b><ol style="margin-top:8px;">{steps_html}</ol></div>',
            unsafe_allow_html=True,
        )

    st.markdown("**Code du template**")
    template_path = TEMPLATE_FILES[selected_template]
    lang = "sql" if template_path.suffix == ".sql" else ("markdown" if template_path.suffix == ".md" else "text")
    st.code(read_text(template_path), language=lang)

# ---------------------------------------------------------------------------
# Page : Prompts IA
# ---------------------------------------------------------------------------
elif page == "Prompts IA":
    hero(
        eyebrow="Cadre de validation IA",
        title="Prompts IA structurés",
        description=(
            "Un prompt est un ensemble d'instructions destinées à un assistant IA. Chaque prompt "
            "couvre une étape précise du pipeline Superstore et inclut des variables à remplacer, "
            "un objectif, des contraintes et le format de sortie attendu."
        ),
    )

    st.warning(
        "Ces prompts sont **opérationnels** : ils ont servi à produire les livrables réels du cas "
        "Superstore. Copier un prompt dans un assistant IA avec les bonnes variables donne un résultat "
        "cohérent avec l'étape visée — mais la sortie générée doit **toujours** être relue et validée "
        "manuellement avant mise en production (voir la page *Contrôles qualité Superstore*)."
    )

    selected_prompt = st.selectbox("Choisir un prompt", list(PROMPT_FILES.keys()))
    st.markdown(f'<div class="ey-card">{read_text(PROMPT_FILES[selected_prompt])}</div>', unsafe_allow_html=True)

    st.info(
        "Copier ce prompt dans Claude Max (ou Cursor / un autre assistant IA), remplacer les variables entre "
        "accolades `{ }`, puis valider manuellement le résultat dans SSMS / Visual Studio / Power BI. "
        "Avec un serveur MCP configuré, Claude Max peut aussi **exécuter** directement le résultat sur la base."
    )

# ---------------------------------------------------------------------------
# Page : Cas d'étude
# ---------------------------------------------------------------------------
elif page == "Cas d'étude":
    hero(
        eyebrow="Cadrage fonctionnel et technique",
        title="Cas d'étude du POC",
        description=(
            "Deux cas d'étude structurent la démonstration : un cas synthétique initial (4 clients) "
            "et le cas Superstore, basé sur un jeu de données réel d'environ 10 000 lignes."
        ),
    )

    tab1, tab2 = st.tabs(["Cas d'étude synthétique (référence)", "Cas Superstore (7B)"])
    with tab1:
        st.markdown(read_text(ROOT / "docs" / "05-cas-etude" / "01-cas-etude-etl-powerbi.md"))
    with tab2:
        st.markdown(read_text(ROOT / "docs" / "05-cas-etude" / "06-cas-etude-superstore-cadrage.md"))

# ---------------------------------------------------------------------------
# Page : Contrôles qualité Superstore
# ---------------------------------------------------------------------------
elif page == "Contrôles qualité Superstore":
    hero(
        eyebrow="Cas Superstore — Phase 7B-5",
        title="Contrôles qualité automatisés",
        description=(
            "Pipeline : CSV → ingestion Python → raw_superstore → packages SSIS "
            "(dimensions + fait) → staging → 12 contrôles qualité SQL."
        ),
    )

    section_title("Lancer les contrôles")
    col_s, col_d, col_mode = st.columns([2, 2, 2])
    server = col_s.text_input("Serveur SQL", value=DEFAULT_SERVER)
    database = col_d.text_input("Base de données", value=DEFAULT_DATABASE)
    qc_mode = col_mode.radio(
        "Mode",
        ["Données réelles", "Démonstration (simuler des erreurs)"],
        help="Le mode démonstration montre à quoi ressemble l'écran quand des contrôles échouent, sans modifier votre base.",
    )

    if st.button("Exécuter les contrôles qualité", type="primary"):
        with st.spinner("Exécution des contrôles en cours..."):
            if qc_mode == "Démonstration (simuler des erreurs)":
                qc_df, summary_df = run_demo_qc()
                error = None
            else:
                qc_df, summary_df, error = run_superstore_qc(server, database)

        if error:
            st.error(f"Connexion ou exécution impossible : {error}")
            st.info("Vérifier que SQL Server est démarré et que le pilote ODBC Driver 17 est installé.")
        elif qc_df.empty:
            st.warning("Aucun résultat retourné.")
        else:
            passed = int(summary_df["passed"].iloc[0]) if not summary_df.empty else 0
            failed = int(summary_df["failed"].iloc[0]) if not summary_df.empty else 0
            warnings = int(summary_df["warnings"].iloc[0]) if not summary_df.empty else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("PASS", passed)
            m2.metric("FAIL", failed)
            m3.metric("WARN", warnings)

            display_df = qc_df.copy()
            display_df["status"] = display_df["status"].apply(badge)
            display_df = display_df.rename(
                columns={
                    "check_id": "Identifiant",
                    "check_name": "Contrôle",
                    "observed_value": "Valeur observée",
                    "threshold": "Seuil attendu",
                    "status": "Statut",
                }
            )
            st.markdown(
                display_df.to_html(escape=False, index=False),
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            issues = qc_df[qc_df["status"].isin(["FAIL", "WARN"])]
            if issues.empty:
                st.success("Tous les contrôles bloquants sont PASS. Le pipeline Superstore est prêt pour Power BI (Phase 9).")
            else:
                st.error(f"{len(issues)} contrôle(s) en échec ou en alerte. Ouvrir le détail ci-dessous pour corriger.")

            section_title("Diagnostic et correction")
            st.caption("Cliquer sur un contrôle en échec pour voir où se situe le problème et comment le corriger.")

            for _, row in qc_df.iterrows():
                check_id = row["check_id"]
                status = row["status"]
                if status == "PASS":
                    continue

                guide = get_guide(check_id)
                if not guide:
                    continue

                icon = "❌" if status == "FAIL" else "⚠️"
                with st.expander(f"{icon} {check_id} — {row['check_name']}", expanded=True):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"**Étape du pipeline :** {guide.pipeline_step}")
                    c2.markdown(f"**Table / package concerné :** `{guide.table_or_package}`")
                    st.markdown(f"**Cause probable :** {guide.cause}")

                    st.markdown("**Lignes ou runs concernés :**")
                    if qc_mode == "Démonstration (simuler des erreurs)":
                        demo_df = get_demo_diagnostic(check_id)
                        if demo_df.empty:
                            st.info("Pas d'exemple de lignes pour ce contrôle en mode démonstration.")
                        else:
                            st.dataframe(demo_df, width="stretch", hide_index=True)
                            st.info("Données de démonstration — en mode réel, ces lignes proviennent de votre base SQL.")
                    else:
                        diag_df, diag_err = run_diagnostic(server, database, check_id)
                        if diag_err:
                            st.warning(f"Diagnostic SQL indisponible : {diag_err}")
                        elif diag_df.empty:
                            st.success("Aucune ligne problématique trouvée (le contrôle a peut-être été corrigé entre-temps).")
                        else:
                            st.dataframe(diag_df, width="stretch", hide_index=True)

                    st.markdown("**Comment corriger :**")
                    for i, step in enumerate(guide.fix_steps, start=1):
                        st.markdown(f"{i}. {step}")

                    if guide.reset_script:
                        st.code(guide.reset_script, language="text")

                    with st.popover("Voir le SQL de diagnostic"):
                        st.code(guide.diagnostic_sql.strip(), language="sql")

    st.markdown("---")
    with st.expander("Script SQL complet des contrôles qualité"):
        st.code(read_text(SUPERSTORE_QC_SQL), language="sql")

    st.markdown("**Documentation associée** : `docs/05-cas-etude/10-validation-superstore-7b5.md`")

# ---------------------------------------------------------------------------
# Page : Mesure des gains
# ---------------------------------------------------------------------------
elif page == "Phase 10 — MCP & IA":
    hero(
        eyebrow="Phase 10 — Innovation",
        title="Évaluation MCP + IA sur le modèle Power BI",
        description=(
            "Un assistant IA (Claude) peut-il comprendre, documenter et challenger un "
            "modèle Power BI existant sans intervention manuelle ? Cette page présente le "
            "test réalisé, ce que l'IA a détecté automatiquement, et la valeur ajoutée par "
            "rapport à un audit manuel classique."
        ),
    )

    section_title("Qu'est-ce que le MCP ?")
    st.markdown(
        """
        <div class="ey-card">
        Le <b>Model Context Protocol (MCP)</b> permet à un assistant IA de dialoguer
        <b>directement</b> avec une application tierce via un serveur dédié, au lieu de se
        limiter à du texte copié-collé. Ici, l'extension <b>Power BI Modeling MCP</b> expose
        le modèle sémantique ouvert dans Power BI Desktop (tables, relations, mesures) à
        Claude, qui peut le lire — et potentiellement le modifier.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Comment ça fonctionne")
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("👤", "Vous", "Posez une question en langage naturel dans Claude Desktop."),
        ("🤖", "Claude Desktop", "Interprète la question et interroge le modèle via MCP."),
        ("🔌", "Serveur MCP", "powerbi-modeling-mcp.exe fait le pont technique."),
        ("📊", "Power BI Desktop", "Modèle ouvert : tables, relations, mesures en direct."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], steps):
        col.markdown(
            f"""
            <div class="ey-card" style="text-align:center;min-height:150px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <b>{title}</b>
                <p style="font-size:0.82rem;color:#555;margin-top:6px;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("Scénario testé")
    st.markdown(
        """
        <div class="ey-card" style="border-left:5px solid #FFE600;">
        <i>« Peux-tu m'indiquer l'état du modèle sémantique actuellement ouvert dans
        Power BI Desktop, vérifier si le schéma est bien en étoile, et me signaler les
        points à améliorer ? »</i>
        <br><br>
        Aucune information sur le modèle n'a été fournie dans la question : Claude a tout
        récupéré en direct via le serveur MCP.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Ce que Claude a détecté automatiquement")
    t1, t2, t3 = st.tabs(["Tables", "Relations", "Mesures DAX"])
    with t1:
        st.dataframe(MCP_TABLES, width="stretch", hide_index=True)
    with t2:
        st.dataframe(MCP_RELATIONS, width="stretch", hide_index=True)
        st.caption("Toutes les relations sont Plusieurs → un, filtrage à sens unique : pas de many-to-many, pas de bidirectionnel.")
    with t3:
        st.dataframe(MCP_MEASURES, width="stretch", hide_index=True)

    st.success(
        "✅ **Vérification du schéma en étoile — validée par l'IA** : une seule table de "
        "faits entourée de dimensions reliées en Plusieurs-vers-Un, sans flocon (snowflake) "
        "ni relation many-to-many."
    )

    section_title("Recommandations de l'IA vs décision humaine")
    st.dataframe(MCP_RECOMMENDATIONS, width="stretch", hide_index=True)
    st.info(
        "Les deux recommandations ont été **examinées puis arbitrées consciemment** : "
        "l'IA outille la décision, elle ne la remplace pas."
    )

    section_title("Comparatif indicatif — audit manuel vs audit assisté par IA")
    st.dataframe(MCP_COMPARATIF, width="stretch", hide_index=True)

    section_title("Ce que ce test démontre")
    st.markdown(
        """
        <div class="ey-card">
        <ol>
            <li><b>Audit instantané</b> : un inventaire complet restitué en quelques secondes,
            là où l'exploration manuelle de la vue Modèle prend de 10 à 15 minutes.</li>
            <li><b>Raisonnement métier, pas seulement de la lecture</b> : l'IA a validé une
            règle de modélisation (schéma en étoile) et argumenté une recommandation.</li>
            <li><b>La décision reste humaine</b> : chaque recommandation a été examinée avant
            d'être acceptée ou écartée.</li>
            <li><b>Limite actuelle</b> : seule la capacité de <b>lecture</b> du MCP a été
            testée. La <b>modification en écriture</b> du modèle par l'IA reste à évaluer.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Configuration MCP utilisée (claude_desktop_config.json)"):
        st.code(MCP_CONFIG_SNIPPET, language="json")

    with st.expander("Documentation complète de la Phase 10"):
        st.markdown(read_text(MCP_DOC))

elif page == "MCP SQL — Staging & DW":
    hero(
        eyebrow="Extension MCP — Écriture",
        title="L'IA construit un modèle SQL complet (Staging → DW en étoile) via MCP",
        description=(
            "Après la Phase 10 (MCP en lecture sur Power BI), ce test va plus loin : "
            "connecté à SQL Server via un serveur MCP, un assistant IA (Claude) crée et "
            "charge lui-même un modèle complet — staging, dimensions, table de faits et "
            "relations — sans copier-coller manuel dans SSMS. L'exemple porte sur un "
            "domaine différent de Superstore (réservations d'hôtel) et le prompt est "
            "générique : il s'adapte à tout type de projet."
        ),
    )

    section_title("Staging vs Data Warehouse (DW)")
    st.dataframe(MCP_SQL_COMPARE, width="stretch", hide_index=True)
    st.caption(
        "La clé de substitution (surrogate key) du DW est stable et indépendante de la "
        "source ; les relations (clés étrangères) entre le fait et les dimensions forment "
        "le schéma en étoile, base de l'analyse et du modèle Power BI."
    )

    section_title("Comment ça fonctionne")
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("👤", "Vous", "Collez un prompt d'implémentation dans Claude Desktop."),
        ("🤖", "Claude Desktop", "Traduit la demande en instructions SQL (DDL + chargement)."),
        ("🔌", "Serveur MCP mssql", "Exécute réellement le SQL sur la base via l'outil MCP."),
        ("🗄️", "SQL Server", "Tables staging + DW créées et chargées en direct."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], steps):
        col.markdown(
            f"""
            <div class="ey-card" style="text-align:center;min-height:150px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <b>{title}</b>
                <p style="font-size:0.82rem;color:#555;margin-top:6px;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_title("Scénario testé")
    st.markdown(
        """
        <div class="ey-card" style="border-left:5px solid #FFE600;">
        <i>« Connecté à ma base SQL Server via l'outil MCP, construis un modèle en étoile
        complet : une table de staging, des dimensions (client, chambre, date) et une
        table de faits reliée aux dimensions par des clés étrangères. Insère des données
        d'exemple avec un doublon, charge les dimensions puis le fait, et vérifie. »</i>
        <br><br>
        Claude exécute directement le DDL, les relations et le chargement via le serveur
        MCP, puis renvoie le résultat pour validation. Le prompt est générique : on
        remplace le domaine par celui de son projet.
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Résultat attendu (exemple réservations d'hôtel)")
    st.dataframe(MCP_SQL_RESULT, width="stretch", hide_index=True)
    st.success(
        "✅ Modèle complet : 5 lignes en staging (dont 1 doublon) → 3 clients, 3 chambres, "
        "4 dates et 4 réservations dans la table de faits, reliées par des clés étrangères "
        "(schéma en étoile prêt pour Power BI)."
    )

    section_title("Ce que cette démo démontre")
    st.markdown(
        """
        <div class="ey-card">
        <ol>
            <li><b>L'IA peut agir, pas seulement conseiller</b> : via MCP, elle exécute
            réellement le DDL et le chargement sur la base.</li>
            <li><b>Le cadre reste maîtrisé</b> : périmètre limité aux tables de la démo,
            script de référence pour valider, points de revue humaine explicités.</li>
            <li><b>Continuité avec la Phase 10</b> : Power BI en lecture, SQL Server en
            écriture — même principe MCP, appliqué à deux couches du pipeline.</li>
            <li><b>Vigilance</b> : un accès en écriture à une base est sensible — à
            réserver à un environnement de test, avec un compte à privilèges limités.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Prompt à coller dans Claude (implémentation autonome)"):
        st.markdown(read_text(MCP_SQL_PROMPT))

    with st.expander("Configuration MCP SQL Server (claude_desktop_config.json)"):
        st.code(MCP_SQL_CONFIG_SNIPPET, language="json")

    with st.expander("Script SQL de référence (déjà validé)"):
        st.code(read_text(MCP_SQL_SCRIPT), language="sql")

    with st.expander("Documentation complète de la démo"):
        st.markdown(read_text(MCP_SQL_DOC))

elif page == "ETL — Source → Staging → DW":
    hero(
        eyebrow="ETL — Pipeline complet",
        title="Alimenter le staging depuis la source, puis le DW depuis le staging",
        description=(
            "Le pipeline ETL de bout en bout sur le cas réservations d'hôtel : la source "
            "brute alimente le staging, puis le staging alimente le Data Warehouse en "
            "étoile (dimensions + faits + relations). Deux chemins sont livrés : des "
            "packages SSIS (outil visuel) pour source → staging et staging → DW, et un "
            "ETL en procédures SQL que Claude Max exécute lui-même via MCP — l'encadrant "
            "n'a qu'à coller un prompt, sans rien coder ni cliquer."
        ),
    )

    section_title("Architecture du pipeline")
    st.markdown(
        """
        <div class="ey-card">
        <b>raw_hotel_reservation</b> (source / landing, brut)<br>
        &nbsp;&nbsp;⬇️ <i>Étape 1 : source → staging</i> — package SSIS <b>PKG_STG_RESERVATION</b>
        &nbsp;<i>ou</i>&nbsp; procédure <code>usp_load_stg_hotel_reservation</code><br>
        <b>stg_hotel_reservation</b> (staging typé + traçabilité)<br>
        &nbsp;&nbsp;⬇️ <i>Étape 2 : staging → DW</i> — package SSIS <b>PKG_DW_RESERVATION</b>
        &nbsp;<i>ou</i>&nbsp; procédures <code>usp_load_dim_*</code> puis <code>usp_load_fact_reservation</code><br>
        <b>dim_client · dim_chambre · dim_date</b> + <b>fact_reservation</b> (schéma en étoile, clés étrangères)
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Orchestration complète en une commande : EXEC usp_run_reservation_etl;")

    section_title("Pour l'encadrant : Claude Max fait tout (aucune manipulation)")
    st.markdown(
        """
        <div class="ey-card" style="border-left:5px solid #FFE600;">
        L'objectif du POC : l'encadrant n'a <b>rien à coder ni à cliquer</b>. Il colle
        un prompt dans <b>Claude Max</b> (connecté à SQL Server via MCP) et l'IA
        construit et exécute <b>tout le pipeline ETL</b> à sa place, puis affiche les
        résultats — visibles ensuite dans SSMS.
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("👤", "Encadrant", "Colle le prompt ETL dans Claude Max."),
        ("🤖", "Claude Max", "Traduit en SQL : tables, procédures, chargement, contrôles."),
        ("🔌", "Serveur MCP mssql", "Exécute réellement le SQL sur la base."),
        ("🗄️", "SSMS", "raw → staging → DW remplis, prêts pour Power BI."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], steps):
        col.markdown(
            f"""
            <div class="ey-card" style="text-align:center;min-height:150px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <b>{title}</b>
                <p style="font-size:0.82rem;color:#555;margin-top:6px;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.info(
        "Le prompt existe en **deux versions** : l'exemple **réservations d'hôtel** "
        "(prêt à l'emploi) et une version **générique** (variables à remplacer) "
        "réutilisable sur tout type de projet. Voir l'encadré « Prompt Claude Max » ci-dessous."
    )

    section_title("Peut-on tout faire avec Claude Max « sans rien toucher » ?")
    st.dataframe(ETL_CONNECTOR, width="stretch", hide_index=True)
    st.info(
        "À retenir : l'ETL en **procédures SQL** est entièrement exécutable par Claude via "
        "MCP (résultats visibles dans SSMS). En revanche, **aucun connecteur MCP ne crée de "
        "package SSIS** : le fichier .dtsx est généré par script (comme les packages "
        "Superstore) puis ouvert dans Visual Studio."
    )

    section_title("Les deux chemins livrés")
    c1, c2 = st.columns(2)
    c1.markdown(
        """
        <div class="ey-card" style="min-height:190px;border-left:5px solid #FFE600;">
        <b>Chemin A — Procédures SQL (via Claude/MCP)</b>
        <p style="font-size:0.86rem;color:#555;">
        Claude exécute <code>reservation_etl_setup.sql</code>,
        <code>reservation_etl_procedures.sql</code>, puis
        <code>EXEC usp_run_reservation_etl;</code>.<br>
        ➜ 100 % automatisable, aucun clic dans un outil.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c2.markdown(
        """
        <div class="ey-card" style="min-height:190px;">
        <b>Chemin B — Packages SSIS (Visual Studio)</b>
        <p style="font-size:0.86rem;color:#555;">
        Deux packages : <code>PKG_STG_RESERVATION</code> (source → staging) puis
        <code>PKG_DW_RESERVATION</code> (staging → DW). Clic droit → <i>Execute Package</i>.<br>
        ➜ Flux visuels + orchestration des dimensions et du fait.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    section_title("Résultat testé (base POC_ETL_IA)")
    st.dataframe(ETL_RESULT, width="stretch", hide_index=True)
    st.success(
        "✅ Pipeline validé : 6 lignes brutes (dont 1 doublon) → 6 en staging → 4 clients, "
        "3 chambres, 5 dates et 5 réservations dans la table de faits. Nettoyage "
        "automatique des noms (espaces et casse), doublon éliminé, "
        "montant par nuit calculé."
    )

    with st.expander("⭐ Prompt Claude Max — ETL complet (réservation + version générique)"):
        st.markdown(read_text(ETL_MCP_PROMPT))

    with st.expander("Chemin A — Script de setup (raw + staging + DW + données)"):
        st.code(read_text(ETL_SETUP_SQL), language="sql")

    with st.expander("Chemin A — Procédures ETL (staging + dimensions + fait + orchestration)"):
        st.code(read_text(ETL_PROCS_SQL), language="sql")

    with st.expander("Chemin B — Générateur du package SSIS (Python)"):
        st.code(read_text(ETL_SSIS_GEN), language="python")

    with st.expander("Documentation complète (architecture, connecteur, version générique)"):
        st.markdown(read_text(ETL_DOC))

elif page == "Mesure des gains":
    hero(
        eyebrow="Évaluation du POC",
        title="Comparaison manuel vs assistance IA",
        description=(
            "Cette page consolide les temps de production, le nombre de corrections et la "
            "réutilisabilité des livrables, pour chaque approche et chaque cas d'étude."
        ),
    )
    st.markdown(read_text(ROOT / "docs" / "06-mesure-gains" / "02-resultats-comparaison.md"))

    st.warning(
        "Les chiffres affichés proviennent des sessions de travail réelles ou d'estimations "
        "documentées. Ils doivent être complétés au fil des prochaines mesures."
    )

footer()
