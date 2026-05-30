#!/usr/bin/env python3
"""
setup.py — Configuration interactive du writerdeck
À lancer une seule fois sur le Raspberry Pi.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 1. Connecte-toi à ton Raspberry Pi.
    Soit directement au clavier, soit via SSH
    depuis ton Mac/PC :
      ssh nomdutilisateur@nomduhote.local

 2. Télécharge ce fichier sur le Pi :
      wget https://raw.githubusercontent.com/Simaunux/writerdeck/main/setup.py

 3. Lance le script :
      python3 setup.py

 4. Réponds aux questions (clefs API, prénom,
    clavier, Dropbox...).

 5. Laisse le script tout configurer, puis
    reboot quand il te le propose :
      sudo reboot

 C'est tout ! Le Pi est prêt à l'emploi.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CE QUE LE SCRIPT FAIT AUTOMATIQUEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Crée les dossiers  ~/writerdeck, ~/documents,
    ~/journal, ~/scripts, ~/conversations...
  • Génère ~/.bashrc avec tes clefs API
  • Génère ~/.bash_profile avec le mapping TTY :
      tty1 = shell
      tty2 = journal
      tty3 = writerdeck (éditeur)
      tty4 = claude-chat
      tty5 = gpt-chat
  • Configure l'auto-login sur tty1–tty5
  • Configure le clavier Apple/Mac français
  • Installe les dépendances Python
  • Télécharge les scripts depuis GitHub
  • Configure Dropbox (optionnel)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 CLEFS API NÉCESSAIRES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Anthropic (Claude)  → console.anthropic.com
  • OpenAI (GPT)        → platform.openai.com
    (optionnel, uniquement si tu veux tty5)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import subprocess
import getpass
import json

# ── Couleurs ─────────────────────────────────────────────────────────────────

BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
RED    = "\033[31m"
RESET  = "\033[0m"

def titre(t):
    print(f"\n{BOLD}{CYAN}── {t} ──{RESET}")

def ok(msg):
    print(f"  {GREEN}✓{RESET}  {msg}")

def info(msg):
    print(f"  {DIM}  {msg}{RESET}")

def warn(msg):
    print(f"  {YELLOW}⚠{RESET}  {msg}")

def ask(question, default=None):
    if default:
        prompt = f"  {BOLD}{question}{RESET} {DIM}[{default}]{RESET} : "
    else:
        prompt = f"  {BOLD}{question}{RESET} : "
    while True:
        rep = input(prompt).strip()
        if rep:
            return rep
        if default is not None:
            return default

def ask_secret(question):
    return getpass.getpass(f"  {BOLD}{question}{RESET} : ")

def ask_yn(question, default="o"):
    opts = "O/n" if default == "o" else "o/N"
    rep = input(f"  {BOLD}{question}{RESET} {DIM}[{opts}]{RESET} : ").strip().lower()
    if not rep:
        return default == "o"
    return rep in ("o", "y", "oui", "yes")

def run(cmd, check=False):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def sudo_write(path, content):
    """Écrire un fichier avec sudo via tee."""
    proc = subprocess.run(
        f"sudo tee {path}",
        input=content, shell=True, capture_output=True, text=True
    )
    return proc.returncode == 0


# ── GitHub ────────────────────────────────────────────────────────────────────

GITHUB_RAW = "https://raw.githubusercontent.com/Simaunux/writerdeck/main"

SCRIPTS = [
    "writerdeck.py",
    "claude-chat.py",
    "gpt-chat.py",
    "journal.py",
    "setup_dropbox.py",
]

# ── Intro ─────────────────────────────────────────────────────────────────────

def intro():
    print(f"""
{BOLD}╔══════════════════════════════════════════╗
║        Setup du Writerdeck Pi            ║
╚══════════════════════════════════════════╝{RESET}

Ce script configure ton Raspberry Pi
comme writerdeck de A à Z :

  • Dossiers et structure de fichiers
  • .bashrc et .bash_profile
  • Auto-login sur tty1–tty5
  • Clavier Apple/MacBook français
  • Dépendances Python
  • Téléchargement des scripts depuis GitHub
  • Dropbox (optionnel)
""")
    input(f"  {DIM}Entrée pour commencer...{RESET} ")

# ── Étapes ───────────────────────────────────────────────────────────────────

def etape_infos():
    titre("1. Informations")

    user   = ask("Nom d'utilisateur Pi", default=getpass.getuser())
    prenom = ask("Ton prénom (pour le prompt)", default="Simon")

    print()
    info("Clef API Anthropic — console.anthropic.com")
    anthropic_key = ask_secret("Clef Anthropic (sk-ant-...)")
    if not anthropic_key.startswith("sk-"):
        warn("Clef invalide ou vide — à compléter dans ~/.bashrc")
        anthropic_key = "COLLE_TA_CLÉ_CLAUDE_ICI"

    print()
    info("Clef API OpenAI — platform.openai.com")
    openai_key = ask_secret("Clef OpenAI (sk-...)  [Entrée pour ignorer]")
    if not openai_key.startswith("sk-"):
        warn("Clef OpenAI non renseignée — à compléter dans ~/.bashrc si besoin")
        openai_key = "COLLE_TA_CLÉ_OPENAI_ICI"

    return {
        "user":          user,
        "prenom":        prenom,
        "anthropic_key": anthropic_key,
        "openai_key":    openai_key,
    }


def etape_clavier():
    titre("2. Clavier")
    info("Configure le layout Apple/MacBook français sur le Pi")
    return ask_yn("Configurer le clavier Mac français ?", default="o")


def etape_dropbox():
    titre("3. Dropbox")
    info("Synchronise ~/documents vers Dropbox à chaque sauvegarde dans writerdeck")
    if not ask_yn("Configurer Dropbox ?", default="n"):
        return None

    print()
    info("Créer une app Dropbox sur :")
    info("https://www.dropbox.com/developers/apps/create")
    info("(choisir : Scoped Access > Full Dropbox > donner un nom)")
    print()
    app_key    = ask("App Key Dropbox")
    app_secret = ask("App Secret Dropbox")
    return {"app_key": app_key, "app_secret": app_secret}

# ── Génération des contenus ───────────────────────────────────────────────────

def contenu_bashrc(cfg):
    openai_line = f'export OPENAI_API_KEY="{cfg["openai_key"]}"\n'

    return f"""# ~/.bashrc

case $- in
    *i*) ;;
      *) return;;
esac

HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s checkwinsize

# Couleurs
if [ -x /usr/bin/dircolors ]; then
    eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
fi

# Complétion bash
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# ── Langue ──────────────────────────────────────────────────────────────────
export LANG=fr_FR.UTF-8
export LC_ALL=fr_FR.UTF-8

# ── PATH ────────────────────────────────────────────────────────────────────
export PATH="$HOME/.local/bin:$PATH"

# ── Clefs API ───────────────────────────────────────────────────────────────
export ANTHROPIC_API_KEY="{cfg["anthropic_key"]}"
{openai_line}
# ── claude-chat / gpt-chat  tty1 integration ────────────────────────────────

# Exécuter la dernière commande envoyée depuis le chat
run() {{
    if [ -f ~/.lastcmd ]; then
        echo "── running ~/.lastcmd ──"
        bash ~/.lastcmd
        rm -f ~/.lastcmd.ts
        export __last_cmd_ts="0"
    else
        echo "pas de commande en attente"
    fi
}}

# Prévisualiser la commande avant de l'exécuter
grab() {{
    if [ -f ~/.lastcmd ]; then
        cat ~/.lastcmd
    else
        echo "pas de commande en attente"
    fi
}}

# Indicateur [cmd] dans le prompt quand une commande est prête
__cmd_check() {{
    if [ -f ~/.lastcmd.ts ]; then
        local ts=$(cat ~/.lastcmd.ts 2>/dev/null)
        local last=${{__last_cmd_ts:-0}}
        if [ "$ts" != "$last" ]; then
            echo -n " [cmd]"
            export __last_cmd_ts="$ts"
        fi
    fi
}}

PS1='Pi de {cfg["prenom"]}:'
"""


def contenu_bash_profile():
    return """# ~/.bash_profile

clear

if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

if [ "$(tty)" = "/dev/tty1" ] && [ -z "$SCRIPT_RUNNING" ]; then
    export SCRIPT_RUNNING=1
    exec script -q -f ~/.tty1.log
fi

case "$(tty)" in
    /dev/tty2)
        python3 ~/writerdeck/journal.py
        ;;
    /dev/tty3)
        python3 ~/writerdeck/writerdeck.py
        ;;
    /dev/tty4)
        python3 ~/writerdeck/claude-chat.py
        ;;
    /dev/tty5)
        python3 ~/writerdeck/gpt-chat.py
        ;;
esac
"""


def contenu_keymap_service():
    return """[Unit]
Description=Load custom keymap
After=console-setup.service

[Service]
Type=oneshot
ExecStart=/usr/bin/loadkeys /usr/share/keymaps/mac/mac-macbook-fr.kmap.gz

[Install]
WantedBy=multi-user.target
"""


def contenu_context_txt(prenom):
    return f"""Je m'appelle {prenom} et j'utilise un writerdeck — un Raspberry Pi configuré comme machine à écrire minimaliste.
Mon appareil a plusieurs TTY : tty1 shell, tty2 journal, tty3 writerdeck, tty4 claude-chat, tty5 gpt-chat.
Je préfère des réponses claires et sans trop de formatage markdown.
"""


def contenu_setup_dropbox(app_key, app_secret):
    return f'''#!/usr/bin/env python3
"""
setup_dropbox.py — à lancer une seule fois sur le Pi.
Génère un refresh token permanent et le sauvegarde dans ~/.dropbox_token.json
"""

import json
import os
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY    = "{app_key}"
APP_SECRET = "{app_secret}"
TOKEN_FILE = os.path.expanduser("~/.dropbox_token.json")

def main():
    auth_flow = DropboxOAuth2FlowNoRedirect(
        APP_KEY,
        APP_SECRET,
        token_access_type="offline"
    )

    url = auth_flow.start()
    print("\\n── Autorisation Dropbox ──────────────────────────")
    print(f"1. Ouvre ce lien dans ton navigateur :\\n\\n   {{url}}\\n")
    print("2. Clique sur \\'Autoriser\\'")
    print("3. Copie le code affiché et colle-le ici")
    print("──────────────────────────────────────────────────")
    code = input("\\nCode d\\'autorisation : ").strip()

    try:
        result = auth_flow.finish(code)
        token_data = {{
            "access_token":  result.access_token,
            "refresh_token": result.refresh_token,
            "app_key":       APP_KEY,
            "app_secret":    APP_SECRET,
        }}
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        os.chmod(TOKEN_FILE, 0o600)
        print(f"\\n✓ Token sauvegardé dans {{TOKEN_FILE}}")
        print("Tu peux maintenant lancer writerdeck.py normalement.\\n")
    except Exception as e:
        print(f"\\n✗ Erreur : {{e}}\\n")

if __name__ == "__main__":
    main()
'''

# ── Application ───────────────────────────────────────────────────────────────

def appliquer(cfg, clavier, dropbox_cfg):
    home = os.path.expanduser("~")

    # 1. Dossiers
    titre("Création des dossiers")
    dossiers = [
        "~/writerdeck",
        "~/documents",
        "~/journal",
        "~/scripts",
        "~/conversations/sessions",
        "~/conversations/gpt-sessions",
    ]
    for d in dossiers:
        path = os.path.expanduser(d)
        os.makedirs(path, exist_ok=True)
        ok(d)

    # 2. .bashrc
    titre("Fichiers de configuration")
    with open(os.path.join(home, ".bashrc"), "w") as f:
        f.write(contenu_bashrc(cfg))
    ok("~/.bashrc")

    # 3. .bash_profile
    with open(os.path.join(home, ".bash_profile"), "w") as f:
        f.write(contenu_bash_profile())
    ok("~/.bash_profile")

    # 4. context.txt
    ctx = os.path.join(home, "context.txt")
    if not os.path.exists(ctx):
        with open(ctx, "w") as f:
            f.write(contenu_context_txt(cfg["prenom"]))
        ok("~/context.txt")
    else:
        info("~/context.txt déjà présent — non modifié")

    # 5. setup_dropbox.py
    if dropbox_cfg:
        dbx_path = os.path.join(home, "writerdeck", "setup_dropbox.py")
        with open(dbx_path, "w") as f:
            f.write(contenu_setup_dropbox(
                dropbox_cfg["app_key"],
                dropbox_cfg["app_secret"]
            ))
        os.chmod(dbx_path, 0o700)
        ok("~/writerdeck/setup_dropbox.py")

    # 6. Messages de login
    titre("Nettoyage de l'écran de login")
    run("sudo truncate -s 0 /etc/issue")
    run("sudo rm -f /etc/issue.d/*")
    open(os.path.join(home, ".hushlogin"), "w").close()
    ok("Messages de login supprimés")

    # 7. Auto-login TTY 1–5
    titre("Auto-login TTY")
    for i in range(1, 6):
        tty = f"tty{i}"
        d   = f"/etc/systemd/system/getty@{tty}.service.d"
        conf = (
            "[Service]\n"
            "ExecStart=\n"
            f"ExecStart=-/sbin/agetty --autologin {cfg['user']} "
            "--skip-login --noclear --noissue --nohostname %I $TERM\n"
        )
        run(f"sudo mkdir -p {d}")
        if sudo_write(f"{d}/override.conf", conf):
            ok(f"Auto-login {tty}")
        else:
            warn(f"Auto-login {tty} — droits sudo manquants ?")

    run("sudo systemctl daemon-reload")

    # 8. Clavier Mac
    if clavier:
        titre("Clavier Apple/Mac français")
        svc = "/etc/systemd/system/keymap.service"
        if sudo_write(svc, contenu_keymap_service()):
            run("sudo systemctl enable keymap.service")
            ok("keymap.service activé")
            print()
            warn("Étape manuelle requise pour finir le clavier :")
            info("  sudo dpkg-reconfigure console-data")
            info("  → Sélectionner : liste complète > mac > macbook > fr")
        else:
            warn("Impossible d'écrire keymap.service — droits sudo ?")

    # 9. Dépendances Python
    titre("Dépendances Python")
    for pkg in ["anthropic", "openai", "dropbox"]:
        r = run(f"pip3 install {pkg} --break-system-packages")
        if r.returncode == 0:
            ok(f"{pkg}")
        else:
            warn(f"{pkg} — échec, à installer manuellement :")
            info(f"  pip3 install {pkg} --break-system-packages")


    # 10. Téléchargement des scripts depuis GitHub
    titre("Téléchargement des scripts")
    writerdeck_dir = os.path.join(home, "writerdeck")
    for script in SCRIPTS:
        dest = os.path.join(writerdeck_dir, script)
        url  = f"{GITHUB_RAW}/{script}"
        r = run(f"wget -q -O {dest} {url}")
        if r.returncode == 0:
            ok(script)
        else:
            warn(f"{script} — échec du téléchargement")
            info(f"  Copier manuellement depuis {url}")

def resume(cfg, clavier, dropbox_cfg):
    titre("Résumé")
    print(f"""
  Utilisateur   : {cfg["user"]}
  Prénom        : {cfg["prenom"]}
  TTY           : tty1 shell · tty2 journal · tty3 writerdeck
                  tty4 claude-chat · tty5 gpt-chat
  Clavier Mac   : {"✓" if clavier else "—"}
  Dropbox       : {"✓ (lancer ~/writerdeck/setup_dropbox.py)" if dropbox_cfg else "—"}

  Scripts téléchargés dans ~/writerdeck/ depuis GitHub
""")
    if dropbox_cfg:
        print(f"  {YELLOW}Dropbox — étape finale :{RESET}")
        print("    python3 ~/writerdeck/setup_dropbox.py")
        print()

    print(f"  {GREEN}Pour appliquer :{RESET}")
    print("    sudo reboot\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    intro()
    cfg         = etape_infos()
    clavier     = etape_clavier()
    dropbox_cfg = etape_dropbox()

    print()
    titre("Récapitulatif avant application")
    print(f"""
  Utilisateur   : {cfg["user"]}
  Prénom        : {cfg["prenom"]}
  Clavier Mac   : {"oui" if clavier else "non"}
  Dropbox       : {"oui" if dropbox_cfg else "non"}
""")

    if not ask_yn("Lancer la configuration ?", default="o"):
        warn("Annulé.")
        return

    appliquer(cfg, clavier, dropbox_cfg)
    resume(cfg, clavier, dropbox_cfg)

    if ask_yn("Rebooter maintenant ?", default="n"):
        run("sudo reboot")


if __name__ == "__main__":
    main()
