#!/usr/bin/env python3
"""
[RUN ONCE TO GENERATE token for .dropbox_token.json]
Créer une "app" dropbox pour récupérer et renseigner "APP_KEY et APP_SECRET" ci dessous,
via : https://www.dropbox.com/developers/apps/create?_tk=pilot_lp&_ad=ctabtn1&_camp=create
setup_dropbox.py — à lancer une seule fois sur le Pi.
Génère un refresh token permanent et le sauvegarde dans ~/.dropbox_token.json
"""

import json
import os
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY    = "PASTE APP KEY"
APP_SECRET = "PASTE APP SECRET"
TOKEN_FILE = os.path.expanduser("~/.dropbox_token.json")

def main():
    auth_flow = DropboxOAuth2FlowNoRedirect(
        APP_KEY,
        APP_SECRET,
        token_access_type="offline"
    )

    url = auth_flow.start()
    print("\n── Autorisation Dropbox ──────────────────────────")
    print(f"1. Ouvre ce lien dans ton navigateur :\n\n   {url}\n")
    print("2. Clique sur 'Autoriser'")
    print("3. Copie le code affiché et colle-le ici")
    print("──────────────────────────────────────────────────")
    code = input("\nCode d'autorisation : ").strip()

    try:
        result = auth_flow.finish(code)
        token_data = {
            "access_token":  result.access_token,
            "refresh_token": result.refresh_token,
            "app_key":       APP_KEY,
            "app_secret":    APP_SECRET,
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        os.chmod(TOKEN_FILE, 0o600)
        print(f"\n✓ Token sauvegardé dans {TOKEN_FILE}")
        print("Tu peux maintenant lancer writerdeck.py normalement.\n")
    except Exception as e:
        print(f"\n✗ Erreur : {e}\n")

if __name__ == "__main__":
    main()
