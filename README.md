# writerdeck
Raspberry Pi writing device and assistant inspired by shmimel work : https://github.com/shmimel/bee-write-back
Developped to be used as a personnal journal, text editor but also as personnal assistant with solution for using cheap api solution to use claude and open ai the light way.

# Set up

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
