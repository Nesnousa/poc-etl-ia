# Déployer l'application Streamlit en ligne (lien à envoyer par e-mail)

Objectif : obtenir une **URL publique** (ex. `https://poc-etl-ia.streamlit.app`) que votre
encadrant ouvre dans son navigateur, **sans rien installer**.

> Rappel : les pages « explications, prompts, templates, schémas, résultats » fonctionnent
> partout. La page **Contrôles qualité – Données réelles** et les démos **MCP / Claude Max**
> restent **locales** (elles ont besoin de votre SQL Server et du Claude de l'utilisateur).
> En ligne, l'encadrant voit tout le contenu et peut utiliser le mode **Démonstration**.

---

## Étape 1 — Créer un compte (gratuit)

1. Compte GitHub : https://github.com/join
2. Compte Streamlit Community Cloud : https://share.streamlit.io (se connecter avec GitHub)

## Étape 2 — Mettre le projet sur GitHub

Option simple (interface web) :
1. Sur GitHub, cliquer **New repository** → nom : `poc-etl-ia` → **Private** → **Create**.
2. Sur la page du dépôt vide, cliquer **uploading an existing file**.
3. Glisser-déposer **au minimum** ces éléments :
   - le dossier `app/` (avec `streamlit_demo.py`, `theme.py`, `superstore_qc.py`, `assets/`)
   - `requirements.txt`
   - `packages.txt`
   - (optionnel) `docs/`, `prompts/`, `samples/` pour le contexte
4. **Commit changes**.

> Astuce : évitez d'envoyer des fichiers lourds/inutiles (bases, `.dtsx`, captures).
> Le minimum pour que l'app tourne = `app/` + `requirements.txt` + `packages.txt`.

## Étape 3 — Déployer

1. Aller sur https://share.streamlit.io → **Create app** → **Deploy a public app from GitHub**.
2. Renseigner :
   - **Repository** : `votre-compte/poc-etl-ia`
   - **Branch** : `main`
   - **Main file path** : `app/streamlit_demo.py`
3. Cliquer **Deploy**. Attendre 2–4 min (installation des dépendances).
4. Vous obtenez une **URL** → c'est celle à envoyer par e-mail.

## Étape 4 — Partager

- Pour un dépôt **Private**, l'app peut rester privée : dans **Settings → Sharing**,
  ajoutez l'e-mail de votre encadrant, OU passez l'app en **public** pour un simple lien.
- Copier l'URL et la coller dans l'e-mail (modèle fourni séparément).

---

## Dépannage rapide

| Symptôme | Cause probable | Solution |
|---|---|---|
| Build échoue sur `pyodbc` | driver ODBC manquant | `packages.txt` (déjà fourni) contient `unixodbc-dev` |
| `ModuleNotFoundError: theme` | mauvais chemin | **Main file path** doit être `app/streamlit_demo.py` |
| Logo EY absent | dossier non envoyé | vérifier que `app/assets/ey_logo.png` est bien sur GitHub |
| Page « Données réelles » en erreur | pas de SQL Server en ligne (normal) | utiliser le mode **Démonstration** |
