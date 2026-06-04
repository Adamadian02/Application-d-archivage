import smtplib
import socket

print(f"Nom d'hôte détecté par socket : {socket.gethostname()}")
print(f"FQDN détecté par socket : {socket.getfqdn()}")

try:
    print("\n--- Test avec local_hostname='localhost' ---")
    # On utilise explicitement 'localhost' pour contourner le nom d'hôte machine invalide
    server = smtplib.SMTP('smtp.gmail.com', 587, local_hostname='localhost', timeout=15)
    server.set_debuglevel(1)
    server.starttls()
    print("Connexion TLS établie.")
    
    # Test du login (on enlève les espaces du mot de passe au cas où)
    user = 'cangu.ged@gmail.com'
    password = 'pedzxfpcgcudkyf' # sans espaces, 15 chars (à vérifier)
    
    print(f"Tentative de login pour {user} (MDP length: {len(password)})...")
    server.login(user, password)
    print("LOGIN RÉUSSI !")
    server.quit()
except Exception as e:
    print(f"\nERREUR : {e}")
