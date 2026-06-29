import sqlite3
from db_fun import connect_db, add_debat, fetch_debat

# Connecter à la base de données
con = connect_db()
if con is None:
    raise Exception("Impossible de se connecter à la base de données.")
cur = con.cursor()


add_debat("macron oui ou non ?", "description1", 1, "politique", "2025-02-18 00:00:00", "2025-02-19 00:00:00")
add_debat("ac", "description2", 2, "academique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("Oeuvre-Auteur", "Peut-on dissocier l'oeuvre de l'auteur ?", 2, "culturel", "2025-10-20 20:20:20", "2025-10-21 00:00:00")
add_debat("eco", "description3", 2, "economique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("env", "description4", 2, "environnemental", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("jur", "description 5", 2, "juridique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("media", "description 6", 2, "mediatique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("science", "description 7", 2, "scientifique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("socie", "description 8", 2, "societal", "2025-10-20 00:00:00", "2025-10-21 00:00:00")
add_debat("tech", "description9 ", 2, "technologique", "2025-10-20 00:00:00", "2025-10-21 00:00:00")


# Récupérer et afficher les débats
debates = fetch_debat()  
for debate in debates:
    print(debate)

# Fermer la connexion
con.close()