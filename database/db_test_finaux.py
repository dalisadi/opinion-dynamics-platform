import random
from datetime import datetime
from db_fun import connect_db, add_debat, add_user, add_argument, add_or_modify_campUti, like, change_avis

# Crée un débat
titre = "DEBAT final"
description = "Débat final pour tester les fonctions"
theme = "mediatique"
date_creation = "2025-04-22 15:21:00"
date_fin = "2025-04-22 16:00:00"
id_createur = 1  # Créateur du débat (tu peux changer selon tes données)

# Crée le débat
id_debat = add_debat(titre, description, id_createur, theme, date_creation, date_fin)

# Génère 50 utilisateurs avec des camps initiaux aléatoires
camp_options = ['V', 'S', 'N']
user_ids = []

for i in range(50):
    pseudo = f"utilisateur{i}"
    mdp = "password123"
    nom = f"Nom{i}"
    prenom = f"Prenom{i}"
    mail = f"{pseudo}@gmail.com"
    gender = "Femme" if i % 2 == 0 else "Homme"
    date_naissance = "2000-01-01"
    nationalite = "FR"

    if add_user(pseudo, mdp, nom, prenom, mail, gender, date_naissance, nationalite):
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (pseudo,))
        id_uti = cur.fetchone()[0]
        user_ids.append(id_uti)
        con.close()

        # Choix du camp initial
        camp = random.choice(camp_options)
        add_or_modify_campUti(id_debat, id_uti, camp)

        # Ajout d'un argument
        court = f"Argument court {i}"
        texte = f"Voici mon argument numéro {i}, je suis {pseudo}."
        add_argument(id_debat, id_uti, court, texte, camp)

# Récupération de tous les arguments pour les likes et les changements d’avis
con = connect_db()
cur = con.cursor()
cur.execute("SELECT id_arg, id_uti FROM argument WHERE id_debat = ?", (id_debat,))
arguments = cur.fetchall()
con.close()

# Chaque utilisateur va liker 3 arguments aléatoires (différents des siens)
for id_uti in user_ids:
    possible_args = [arg for arg in arguments if arg[1] != id_uti]
    liked_args = random.sample(possible_args, min(3, len(possible_args)))
    for arg_id, _ in liked_args:
        like(arg_id)

# 10 utilisateurs changent d’avis aléatoirement
changed_users = random.sample(user_ids, 10)
for id_uti in changed_users:
    # On récupère son camp actuel
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT camp FROM campUti WHERE id_uti = ? AND id_debat = ?", (id_uti, id_debat))
    current_camp = cur.fetchone()[0]
    con.close()

    # On choisit un camp différent
    new_camp = random.choice([c for c in camp_options if c != current_camp])
    add_or_modify_campUti(id_debat, id_uti, new_camp)

    # On met à jour l'argument qui l’a convaincu (choix aléatoire pour le test)
    possible_args = [arg for arg in arguments if arg[1] != id_uti]
    if possible_args:
        convincing_arg = random.choice(possible_args)
        change_avis(convincing_arg[0])

print("Débat, utilisateurs, camps, arguments, likes et changements d’avis créés avec succès.")
