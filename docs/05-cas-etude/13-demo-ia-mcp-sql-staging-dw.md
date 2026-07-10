# Démo IA + MCP SQL Server — Staging & Data Warehouse complet (schéma en étoile)

| Élément | Valeur |
| --- | --- |
| Objectif | Montrer que l'IA peut créer et charger un modèle SQL complet (staging + DW en étoile) **elle-même**, via MCP, pour n'importe quel domaine |
| Outils | SQL Server (Express OK), Claude Desktop / Claude Max, un serveur MCP SQL Server autorisé en écriture (DDL) |
| Livrables | `samples/sqlserver/demo_ia_staging_dw.sql` (exemple complet de référence), `prompts/prompt_claude_mcp_staging_dw.md` (prompt générique) |
| Domaine d'exemple | Réservations d'hôtel (volontairement différent du cas Superstore) |
| Statut | Prêt à tester |

## 1. Objectif

Prolonger la Phase 10 (MCP en **lecture** sur Power BI) par un test en **écriture** :
un assistant IA connecté à SQL Server via MCP crée un **modèle en étoile complet**
— une table de **staging**, plusieurs **dimensions**, une table de **faits** et les
**relations** (clés étrangères) — puis le charge et le vérifie, de façon autonome.
L'humain valide le résultat.

Le domaine d'exemple (réservations d'hôtel) est **différent du cas Superstore** :
c'est volontaire, pour montrer que la démarche s'applique à **tout type de projet**.
Le prompt fourni est générique (variables `{...}`) et s'adapte à n'importe quel domaine.

## 2. Rappel : staging vs DW

| | Table de STAGING | Data Warehouse (DW) |
| --- | --- | --- |
| Rôle | Recevoir les données préparées | Servir l'analyse (Power BI, reporting) |
| Clé | Clé métier (ex. `client_id`) | Clé de substitution (`client_key`) + clé métier unique |
| Données | Parfois brutes (doublons, casse) | Nettoyées et dédoublonnées |
| Structure | Une table « à plat » | Schéma en étoile : dimensions + faits + relations |
| Colonnes en plus | `batch_id`, `source_system`, `load_ts` | Historisation (`valid_from`, `is_current`) + audit (`dw_load_ts`) |

La **clé de substitution** (surrogate key) est stable et indépendante de la source.
Les **relations** (clés étrangères entre le fait et les dimensions) forment le
**schéma en étoile**, base de l'analyse et du modèle Power BI.

## 3. Modèle en étoile de l'exemple

```mermaid
flowchart TB
    stg[stg_hotel_reservation_demo\n(staging)] --> dc[dim_client_demo]
    stg --> dch[dim_chambre_demo]
    stg --> dd[dim_date_demo]
    stg --> f[fact_reservation_demo]
    dc --- f
    dch --- f
    dd --- f
```

- `dim_client_demo`, `dim_chambre_demo`, `dim_date_demo` : dimensions (axes d'analyse).
- `fact_reservation_demo` : table de faits (mesures + clés étrangères vers les dimensions).

## 4. Mise en place du serveur MCP SQL Server

> Il n'existe pas de serveur MCP SQL Server « officiel » unique : plusieurs
> implémentations open source existent. L'exemple ci-dessous utilise un serveur
> communautaire lançable via `npx`, en **mode écriture** (nécessaire pour créer
> des tables). Vérifier la réputation du paquet avant usage en entreprise.

### 4.1 Configuration `claude_desktop_config.json`

Windows : `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mssql": {
      "command": "npx",
      "args": ["-y", "mssql-mcp@latest"],
      "env": {
        "DB_SERVER": "NESNOUSSA\\SQLEXPRESS",
        "DB_DATABASE": "POC_ETL_IA",
        "DB_USER": "votre_login",
        "DB_PASSWORD": "votre_mot_de_passe",
        "DB_ENCRYPT": "false",
        "DB_TRUST_SERVER_CERTIFICATE": "true"
      }
    }
  }
}
```

Notes :
- Pour une **authentification Windows** ou une autre implémentation, adapter les
  variables selon la documentation du serveur MCP choisi.
- Certains serveurs sont **en lecture seule par défaut** : activer explicitement
  le mode écriture / DDL pour que l'IA puisse créer des tables.
- Après modification du fichier, **quitter complètement puis relancer** Claude Desktop.

### 4.2 Vérifier la connexion

Dans Claude : « Peux-tu lister les tables de la base POC_ETL_IA via l'outil mssql ? »
Si Claude renvoie la liste, le pont MCP fonctionne.

## 5. Scénario de démonstration

1. Ouvrir Claude Desktop (serveur MCP `mssql` actif).
2. Coller le prompt de `prompts/prompt_claude_mcp_staging_dw.md`, en remplaçant les
   variables `{...}` par votre domaine (ou en gardant l'exemple hôtel).
3. Claude exécute, via MCP : création du staging, des dimensions, du fait et des
   relations, insertion d'exemples, chargement, puis vérification.
4. Comparer la démarche avec le script de référence
   `samples/sqlserver/demo_ia_staging_dw.sql`.

### Résultat attendu (exemple hôtel)

| Table | Type | Lignes |
| --- | --- | --- |
| `stg_hotel_reservation_demo` | Staging | 5 (dont 1 doublon) |
| `dim_client_demo` | Dimension | 3 |
| `dim_chambre_demo` | Dimension | 3 |
| `dim_date_demo` | Dimension (date) | 4 |
| `fact_reservation_demo` | Faits | 4 (relié aux 3 dimensions) |

## 6. Ce que cette démo prouve

1. **L'IA peut agir, pas seulement conseiller** : via MCP, elle exécute réellement
   le DDL, les relations et le chargement sur la base.
2. **Un modèle complet, pas une table isolée** : dimensions + faits + relations =
   un vrai schéma en étoile, directement exploitable dans Power BI.
3. **Générique** : le même prompt s'adapte à tout domaine (RH, santé, logistique…).
4. **Le cadre reste maîtrisé** : périmètre limité aux tables `_demo`, script de
   référence pour valider, points de revue humaine explicités.

## 7. Limites et vigilance

- Donner à une IA un accès **en écriture** à une base est sensible : à réserver à
  un environnement de test, avec un compte à privilèges limités.
- Toujours **relire et rejouer** le SQL généré ; ne pas exécuter en production sans
  validation humaine.
- Le nettoyage de texte illustré (casse/espaces) est volontairement simple ; un cas
  réel demande des règles de qualité plus complètes.

## 8. Étape suivante possible

- Brancher **Power BI** sur ce DW (les relations existent déjà) pour retrouver le
  même type de modèle qu'en Phase 9 sur Superstore.
- Faire générer par l'IA les **contrôles qualité** associés (cf. template QC), puis
  les exécuter via le même serveur MCP.
