# IMPORTANT — Streamlit Community Cloud
# --------------------------------------
# runtime.txt est IGNORÉ par Streamlit Cloud.
# Vous DEVEZ choisir Python 3.12 dans l'interface :
#
# 1. https://share.streamlit.io → votre app poc-etl-ia
# 2. ⋮ (Settings) → Settings → Python version → 3.12
#    OU : supprimer l'app et la redéployer → Advanced settings → Python 3.12
# 3. Reboot / Redeploy
#
# Sans cette étape, Cloud utilise Python 3.14 et l'app plante (Segmentation fault)
# dès que vous changez de page.
