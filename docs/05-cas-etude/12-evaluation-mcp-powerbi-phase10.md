# Évaluation MCP + IA sur le modèle Power BI (Phase 10)

| Élément | Valeur |
| --- | --- |
| Date | 2026-07-06 |
| Prérequis | Phase 9 validée (modèle Power BI Superstore en étoile, 4 mesures DAX) |
| Outils | Power BI Desktop, Claude Desktop, serveur MCP `powerbi-modeling-mcp` |
| Statut | Test 1 réalisé et validé — audit du modèle en lecture seule |

## 1. Objectif

Évaluer si un assistant IA (Claude), connecté au modèle Power BI via le **Model Context
Protocol (MCP)**, peut **comprendre, documenter et challenger** un modèle sémantique
existant sans intervention manuelle — puis mesurer la valeur ajoutée par rapport à un
audit manuel classique.

## 2. Qu'est-ce que le MCP ?

Le **Model Context Protocol** est un protocole standard qui permet à un assistant IA de
dialoguer directement avec une application tierce via un serveur dédié, au lieu de se
limiter à du texte copié-collé. Ici, l'extension **Power BI Modeling MCP** expose le
modèle sémantique actuellement ouvert dans Power BI Desktop (tables, colonnes, relations,
mesures) à Claude, qui peut le lire et proposer des modifications.

```mermaid
flowchart LR
    user[Utilisateur] -->|pose une question| claude[Claude Desktop]
    claude <-->|MCP - lecture / écriture| mcp[Serveur MCP\npowerbi-modeling-mcp.exe]
    mcp <-->|pilote| pbi[Power BI Desktop\nmodèle ouvert]
```

## 3. Mise en place

### 3.1 Configuration Claude Desktop

Le serveur MCP est déclaré dans `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "powerbi-modeling-mcp": {
      "command": "C:\\Users\\<utilisateur>\\.vscode\\extensions\\analysis-services.powerbi-modeling-mcp-0.4.0-win32-x64\\server\\powerbi-modeling-mcp.exe",
      "args": ["--start"],
      "env": {}
    }
  }
}
```

### 3.2 Vérification de la connexion

Claude Desktop affiche le statut **« powerbi-modeling-mcp is running »**, confirmant que
le serveur MCP est actif et prêt à dialoguer avec l'instance ouverte de Power BI Desktop.

## 4. Scénario de test (Test 1 — audit du modèle)

**Question posée à Claude** : *« Peux-tu m'indiquer l'état du modèle sémantique
actuellement ouvert dans Power BI Desktop, vérifier si le schéma est bien en étoile, et
me signaler les points à améliorer ? »*

Aucune information sur le modèle n'a été fournie dans le prompt : Claude a tout récupéré
en direct via le serveur MCP.

## 5. Résultat obtenu

### 5.1 Tables détectées automatiquement

| Table | Type | Visible | Mode de stockage |
| --- | --- | --- | --- |
| `stg_fact_sales` | Table de faits | Oui | Import |
| `stg_dim_customer` | Dimension | Oui | Import |
| `stg_dim_product` | Dimension | Oui | Import |
| `LocalDateTable_...` (×2) | Calendrier auto-généré (masqué) | Non | Import |

Les deux tables de dates cachées sont créées automatiquement par la fonctionnalité
« Auto date/time » de Power BI (une pour `order_date`, une pour `ship_date`).

### 5.2 Relations détectées automatiquement

| De | Vers | Cardinalité | Active | Filtrage |
| --- | --- | --- | --- | --- |
| `stg_fact_sales[customer_id]` | `stg_dim_customer[customer_id]` | Plusieurs → un | Oui | Sens unique |
| `stg_fact_sales[product_id]` | `stg_dim_product[product_id]` | Plusieurs → un | Oui | Sens unique |
| `stg_fact_sales[order_date]` | `LocalDateTable` (order_date) | Plusieurs → un | Oui | Sens unique |
| `stg_fact_sales[ship_date]` | `LocalDateTable` (ship_date) | Plusieurs → un | Oui | Sens unique |

Toutes les relations sont en Plusieurs-vers-Un, filtrage à sens unique : pas de relation
many-to-many, pas de relation bidirectionnelle.

### 5.3 Mesures DAX détectées automatiquement

| Mesure | Table | Expression DAX |
| --- | --- | --- |
| Total Sales | `stg_fact_sales` | `SUM(stg_fact_sales[sales])` |
| Total Profit | `stg_fact_sales` | `SUM(stg_fact_sales[profit])` |
| Margin % | `stg_fact_sales` | `DIVIDE([Total Profit], [Total Sales], 0)` |
| # Orders | `stg_fact_sales` | `DISTINCTCOUNT(stg_fact_sales[order_id])` |

### 5.4 Vérification du schéma en étoile

**Conclusion de Claude** : structurellement correct — une seule table de faits entourée
de dimensions reliées en Plusieurs-vers-Un, sans flocon (snowflake) ni relation
many-to-many. C'est bien un schéma en étoile.

## 6. Points d'amélioration soulevés par l'IA

| # | Constat | Recommandation de Claude | Décision retenue |
| --- | --- | --- | --- |
| 1 | Double calendrier automatique (`Auto date/time`) : une table cachée par colonne date, au lieu d'une table `Dim_Date` unique | Créer une table `Dim_Date` unique, relation active sur `order_date`, relation inactive sur `ship_date` activée via `USERELATIONSHIP` dans les mesures qui en ont besoin | **Conservé tel quel pour le POC** — compromis jugé acceptable, `Dim_Date` reporté à une itération future |
| 2 | Nommage des tables avec le préfixe `stg_` (staging), au lieu de `Dim_Customer` / `Fact_Sales` | Renommer pour la lisibilité côté utilisateurs du rapport | Aucun impact fonctionnel : **pas de changement nécessaire** pour le POC |

## 7. Ce que ce test démontre

1. **Audit instantané** : Claude a restitué en quelques secondes un inventaire complet
   (tables, relations, mesures) qu'un audit manuel aurait nécessité d'explorer table par
   table dans la vue Modèle de Power BI.
2. **Raisonnement métier, pas seulement de la lecture** : l'IA n'a pas seulement listé les
   objets, elle a **validé une règle de modélisation** (schéma en étoile) et **proposé une
   amélioration argumentée** (Dim_Date, `USERELATIONSHIP`).
3. **La décision reste humaine** : les deux recommandations ont été examinées puis
   arbitrées consciemment (une acceptée comme compromis, une écartée car sans impact) —
   l'IA outille la décision, elle ne la remplace pas.
4. **Cas d'usage validé** : audit et documentation de modèle Power BI existant. Le test
   n'a pas encore couvert la **modification en écriture** du modèle par l'IA (ex. créer la
   table `Dim_Date` automatiquement via MCP), ce qui constitue une piste de test
   ultérieure.

## 8. Comparatif indicatif — audit manuel vs audit assisté par IA (MCP)

| Indicateur | Audit manuel (estimation) | Audit avec Claude + MCP (mesuré) |
| --- | --- | --- |
| Temps pour lister tables, relations, mesures | ~10-15 min (navigation manuelle dans la vue Modèle) | ~30 secondes (une question) |
| Détection du schéma en étoile | Manuelle, dépend de l'expérience de l'auditeur | Automatique et argumentée |
| Proposition de bonnes pratiques | Dépend de la présence d'un expert BI | Systématique (Dim_Date, conventions de nommage) |
| Risque d'erreur d'interprétation | Existant (oubli d'une relation, etc.) | Faible sur la restitution ; validation humaine requise sur les recommandations |

## 9. Limites observées

- Le test porte sur un modèle de taille réduite (1 fait, 2 dimensions, 4 mesures) : la
  restitution reste à valider sur un modèle plus large.
- Seule la capacité de **lecture / audit** du MCP a été testée à ce stade ; la capacité de
  **modification directe** du modèle par l'IA (écriture) n'a pas encore été évaluée sur ce
  POC.
- L'usage de MCP suppose une extension installée localement (Power BI Modeling MCP) et un
  Power BI Desktop ouvert avec le modèle chargé : ce n'est pas un mode d'audit à distance.

## 10. Prochaine étape possible

Tester une seconde fois le MCP sur une action en **écriture** (ex. demander à Claude de
créer la table `Dim_Date` et de configurer les relations actif/inactif directement dans
le modèle), afin de comparer le temps et la fiabilité par rapport à une manipulation
manuelle dans Power BI Desktop.
