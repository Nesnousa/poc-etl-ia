# Solution de secours - Importer le package SSIS dans Visual Studio

Si le fichier `.sln` / `.dtproj` genere ne s'ouvre pas dans Visual Studio, utilise cette methode **recommandee par Microsoft** : creer un projet vierge dans VS, puis importer le package.

## Pourquoi cette erreur arrive

L'erreur `serviceInstance` ou `Parameters missing` survient souvent quand un projet SSIS est cree manuellement (XML) au lieu d'etre cree par Visual Studio. L'extension SSIS attend un format de projet specifique.

## Methode fiable (5 minutes)

### Etape 1 - Creer un nouveau projet SSIS dans Visual Studio

1. Ouvrir Visual Studio
2. **File > New > Project**
3. Chercher **Integration Services Project**
4. Nom : `POC_ETL_IA_SSIS`
5. Emplacement : un dossier **court**, par exemple `C:\POC_ETL_IA_SSIS`
   - Eviter OneDrive et les chemins tres longs si possible
6. Cliquer **Create**

### Etape 2 - Supprimer le package par defaut

1. Dans Solution Explorer, supprimer `Package.dtsx` (le package vide cree par defaut)

### Etape 3 - Importer le package existant

1. Clic droit sur **SSIS Packages** (ou le dossier Packages)
2. **Add Existing Package...**
3. Choisir **File System**
4. Parcourir vers :

```
ssis\POC_ETL_IA_SSIS\PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER.dtsx
```

Chemin complet :

```
C:\Users\Nesrine\OneDrive - Ministere de l'Enseignement Superieur et de la Recherche Scientifique\Desktop\EY intership 3\ssis\POC_ETL_IA_SSIS\PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER.dtsx
```

### Etape 4 - Importer la connexion (si demande)

Si Visual Studio ne retrouve pas la connexion :

1. Double-cliquer sur **Connection Managers** en bas
2. **New OLE DB Connection**
3. Nom : `CM_POC_ETL_IA`
4. Serveur : ton instance SQL (`.`)
5. Base : `POC_ETL_IA`
6. Tester la connexion

Ou copier le fichier :

```
ssis\POC_ETL_IA_SSIS\CM_POC_ETL_IA.conmgr
```

dans le dossier du nouveau projet VS, puis **Add Existing Item**.

### Etape 5 - Verifier le package

1. Ouvrir `PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER.dtsx`
2. Verifier le Control Flow : 4 taches en chaine
3. Verifier le Data Flow : Source -> Derived Column -> Row Count -> Destination

### Etape 6 - Tester

Avant execution, dans SSMS :

```sql
USE POC_ETL_IA;
TRUNCATE TABLE stg_sales_customer;
DELETE FROM etl_run_log;
DELETE FROM etl_error_log;
```

Puis **F5** dans Visual Studio pour executer le package.

## Verifier l'extension SSIS

Si Visual Studio ne propose pas **Integration Services Project** :

1. **Extensions > Manage Extensions > Installed**
2. Verifier que **SQL Server Integration Services Projects** est **Enabled**
3. Redemarrer Visual Studio

Lien : https://marketplace.visualstudio.com/items?itemName=SSIS.MicrosoftDataToolsIntegrationServices

## Fichiers a utiliser

| Fichier | Role |
| --- | --- |
| `PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER.dtsx` | Package ETL principal |
| `CM_POC_ETL_IA.conmgr` | Connexion SQL Server |
| `docs/02-ssis/02-guide-creation-package-ssis.md` | Specification du package |

## Apres import reussi

Tu pourras comparer avec le prompt IA :

`docs/05-cas-etude/04-exemple-prompt-ia-ssis-cas-etude-01.md`
