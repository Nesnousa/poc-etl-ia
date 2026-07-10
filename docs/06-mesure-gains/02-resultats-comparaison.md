# Résultats de comparaison — POC IA ETL / Power BI

| Date de mise à jour | 2026-07-02 |
| --- | --- |
| Cas couvert en détail | Cas d'étude 1 — Clients / Ventes |
| Statut | Partiellement mesuré (SQL + SSIS réels ; Power BI à venir) |

## Grille principale

| ID | Cas d'étude | Artefact | Approche | Temps initial (min) | Temps correction (min) | Temps total (min) | Erreurs détectées | Réutilisable | Statut mesuré |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Client staging | Scripts SQL (setup + chargement) | Manuel | 40 | 5 | 45 | 0 | Oui | Réel |
| 2 | Client staging | Scripts SQL (setup + chargement) | IA assistée | 10 | 12 | 22 | 2 | Oui | Estimé |
| 3 | Client staging | Contrôles qualité SQL | Manuel | 25 | 5 | 30 | 0 | Oui | Réel |
| 4 | Client staging | Contrôles qualité SQL | IA assistée | 8 | 7 | 15 | 1 | Oui | Estimé |
| 5 | Client staging | Package SSIS source vers staging | Manuel | 75 | 15 | 90 | 2 | Oui | Estimé |
| 6 | Client staging | Package SSIS source vers staging | IA assistée | 20 | 95 | 115 | 8 | Partiel | **Réel** |
| 7 | Ventes | Mesure DAX | Manuel | 20 | 0 | 20 | 0 | Oui | À faire |
| 8 | Ventes | Mesure DAX | IA assistée | 5 | 6 | 11 | 1 | Oui | À faire |
| 9 | Client BI | Script Power Query | Manuel | 25 | 0 | 25 | 0 | Oui | À faire |
| 10 | Client BI | Script Power Query | IA assistée | 7 | 8 | 15 | 1 | Oui | À faire |

> **Note sur les temps SSIS manuel (ligne 5)** : estimé à partir du guide `docs/02-ssis/02-guide-creation-package-ssis.md`, en création directe dans Visual Studio (sans import de `.dtsx` généré).

> **Note sur les temps SSIS IA (ligne 6)** : mesure réelle de la session de travail (génération + dépannage connexion + métadonnées + validation d'exécution).

---

## Détail — Package SSIS (comparaison centrale du cas 1)

### Approche manuelle (référence)

| Élément | Évaluation |
| --- | --- |
| Méthode | Suivre le guide pas à pas dans Visual Studio |
| Points forts | Package compatible SSIS dès la création ; métadonnées validées par l'outil |
| Points faibles | Plus long à construire composant par composant |
| Corrections typiques | Connexion SQL (`localhost\SQLEXPRESS`), Trust Server Certificate |
| Résultat attendu | 4 lignes en staging, run log SUCCESS, contrôles qualité OK |

### Approche IA assistée (mesure réelle)

| Élément | Évaluation |
| --- | --- |
| Méthode | Génération via `ssis/generate_ssis_project.py` puis import dans le projet Visual Studio |
| Points forts | Structure rapide : Control Flow, Data Flow, variables, logging, gestion d'erreur |
| Points faibles | Format `.dtsx` incomplet ; nombreuses erreurs de validation SSIS |
| Package exécutable dès le premier essai | **Non** |

### Corrections nécessaires après génération IA

| # | Problème | Cause | Action corrective |
| --- | --- | --- | --- |
| 1 | Connexion échouée (`.`) | Instance SQL = SQLEXPRESS, pas l'instance par défaut | Serveur `localhost\SQLEXPRESS` |
| 2 | Erreur SSL / certificat | Le pilote OLE DB 19 impose le chiffrement | `Trust Server Certificate = True` |
| 3 | `SqlCommand` manquant | Métadonnées `.dtsx` incomplètes | Ajout des propriétés OLE DB Source/Destination |
| 4 | `CommandTimeout` manquant | Idem | Ajout dans le XML / le générateur |
| 5 | `FastLoadKeepIdentity` manquant | Idem (mode Fast Load en destination) | Ajout des propriétés Fast Load |
| 6 | Derived Column : 2 sorties requises | Sortie d'erreur absente | Ajout de la sortie d'erreur Derived Column |
| 7 | Sorties d'erreur OLE DB incomplètes | Métadonnées corrompues | Ajout de `ErrorCode` / `ErrorColumn` |
| 8 | Fichier Visual Studio différent du fichier corrigé | Visual Studio copie le `.dtsx` dans son propre projet | Réimport / correction du bon fichier |

### Résultat final (les deux approches)

| Contrôle | Manuel (attendu) | IA (observé après corrections) |
| --- | --- | --- |
| Lignes en staging | 4 | 4 |
| Run log | SUCCESS | SUCCESS (run_id = 2) |
| row_count_in / out | 4 / 4 | 4 / 4 |
| Doublon C001 détecté | Oui (2) | Oui (2) |
| null_customer_id | 0 | 0 |

---

## Synthèse cas d'étude 1 (SQL + SSIS)

| Indicateur | Manuel | IA assistée | Lecture |
| --- | --- | --- | --- |
| Temps total SQL staging | 45 min | 22 min (estimé) | Gain net sur SQL |
| Temps total SSIS | 90 min (estimé) | **115 min (réel)** | **Pas de gain** sur ce cas SSIS |
| Erreurs à la revue SSIS | ~2 | **8** | IA plus fragile sur le format technique SSIS |
| Réutilisabilité du livrable IA | — | Partielle (générateur utile, `.dtsx` non importable tel quel) | Validation humaine indispensable |
| Conformité au besoin métier | Oui | Oui (après corrections) | Résultat fonctionnel équivalent |

### Conclusions pour la soutenance

1. **L'IA accélère la conception** quand l'artefact est textuel et bien cadré (SQL, prompts, documentation).
2. **L'IA reste fragile** sur les formats propriétaires stricts (fichier `.dtsx` SSIS) sans validation dans Visual Studio.
3. **Le gain ne doit pas être supposé** : il doit être mesuré cas par cas.
4. **La supervision humaine** n'est pas optionnelle : connexion, métadonnées, tests d'exécution et contrôles qualité.
5. **Valeur du POC** : combiner génération IA, standards, checklist de validation et mesure des gains.

### Formulation recommandée (rapport / oral)

> « Sur le cas 1, l'assistance IA a réduit le temps de production SQL, mais le package SSIS généré automatiquement a nécessité plus de corrections que la création manuelle dans Visual Studio. Le résultat final est équivalent (4 lignes, SUCCESS, contrôles qualité OK), ce qui démontre l'intérêt de l'IA comme accélérateur de conception, pas comme substitut à la validation technique. »

---

## Enseignement confirmé sur le cas Superstore (7B)

Le cas Superstore (~10 000 lignes, 3 packages SSIS) a permis de consolider un enseignement clé : en déportant les transformations (nettoyage, dédoublonnage, filtres, rejets) dans le SQL de la source OLE DB plutôt que dans des composants graphiques SSIS (Derived Column, Conditional Split), les packages générés par IA sont devenus **robustes dès la première exécution dans Visual Studio**, sans les corrections répétées observées sur le cas d'étude 1.

## À compléter (prochaines sessions)

- [ ] Ajuster les temps SSIS manuel avec un chronomètre en cas de recréation du package from scratch
- [ ] Ajuster les temps SSIS IA avec le temps réel si noté
- [ ] Remplir les lignes Power Query (ID 9-10) et DAX (ID 7-8)
- [ ] Calculer le gain moyen global une fois tous les cas mesurés
