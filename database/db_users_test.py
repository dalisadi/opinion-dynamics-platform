import sqlite3
from db_fun import connect_db, add_user, fetch_users


# Connexion à la base de données
con = connect_db()
if con is None:
    raise Exception("Impossible de se connecter à la base de données.")
cur = con.cursor()


# Ajout des utilisateurs de test 
add_user("Emma28", "password123", "Emma", "Burner", "emma.burner@gmail.com", "Femme", "08/04/2004", "FR")
add_user("pp", "şifre", "Poyraz", "Yüksekkaya", "pyuksekkaya@yahoo.com", "Homme", "05/10/2010", "TR")

# Affichage tous les utilisateurs présents dans la base de données
users = fetch_users()
for user in users:
    print(user)

# Fermeture de la connexion
con.close()