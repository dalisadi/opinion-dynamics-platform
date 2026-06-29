from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime, timedelta
from database.db_fun import add_user, username_exists, mail_exists, add_argument, add_debat, add_or_modify_campUti, change_avis
from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32) 

def connect_db():
    return sqlite3.connect('database/vns.db')

@app.template_filter('datetimeformat')
def datetimeformat(value):
    if value is None:
        return "Date non disponible"  # Ou une autre valeur par défaut
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/connexion.html')
def connexion():
    return render_template('connexion.html', is_logged_in='username' in session)

@app.route('/connexion', methods=['POST'])
def accueil():
	# Récupérer le pseudo et le mot de passe depuis le formulaire
    username = request.form.get("username")
    password = request.form.get("password")
    con = connect_db()
    cur = con.cursor()

    # Vérifier si l'utilisateur existe
    cur.execute("SELECT id_uti, mdp FROM utilisateur WHERE pseudo = ?", (username,))
    user = cur.fetchone()  # Récupérer le mot de passe stocké

    con.close()  # Fermer la connexion à la BD

    # Vérifier si l'utilisateur existe dans la "base de données"
    if user and user[1] == password:
        session["user_id"] = user[0]  # Stocker l'ID dans la session
        session["username"] = username
        return render_template('accueil.html', username=username)
    else:
        return render_template('connexion.html', error="Nom d'utilisateur ou mot de passe incorrect")

@app.route('/contact.html')
def contact():
     return render_template('contact.html', is_logged_in='username' in session)

@app.route('/accueil.html')
def acc():
     return render_template('accueil.html', is_logged_in='username' in session)

@app.route('/inscription.html', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        pseudo = request.form.get("pseudo")
        mdp = request.form.get("password")
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        mail = request.form.get("mail")
        gender = request.form.get("gender")
        daten = request.form.get("dateNaissance")  # Expected format: DD/MM/YYYY
        nationalite = request.form.get("nationalite")

        # Validation des champs obligatoires
        if not pseudo or not mdp or not nom or not prenom or not mail or not gender or not daten or not nationalite:
            return render_template('inscription.html', error="Tous les champs doivent être remplis.")

        # Vérification du format de la date
        try:
            birth_date = datetime.strptime(daten, "%Y-%m-%d")
        except ValueError:
            return render_template('inscription.html', error="Format de date invalide! Utilisez le sélecteur de date.")

        # Vérification de l'existence du pseudo et de l'email
        if username_exists(pseudo):
            return render_template('inscription.html', error="Ce nom d'utilisateur existe déjà. Choisissez un autre pseudo.")
        if mail_exists(mail):
            return render_template('inscription.html', error="Cet adresse mail est déjà utilisée.")

        # Vérification du mot de passe au min 6 caracteres
        if len(mdp) < 6:
            return render_template('inscription.html', error="Le mot de passe doit comporter au moins 6 caractères.")
   
        try:
            success = add_user(pseudo, mdp, nom, prenom, mail, gender, birth_date, nationalite)
            if success:
                return render_template('connexion.html')  
            else:
                return render_template('inscription.html', error="Impossible d'ajouter l'utilisateur.")
    
        except sqlite3.Error as e:
            return render_template('inscription.html', error=f"Erreur de base de données: {e}")

    return render_template('inscription.html', is_logged_in='username' in session)  # Affichage de la page d'inscription

@app.route('/theme/<theme_name>')
def theme_page(theme_name):
    con = connect_db()
    cur = con.cursor()

    cur.execute("SELECT id_debat, titre, description, date_creation FROM debats WHERE theme = ?", (theme_name,))

    
    debates_raw = cur.fetchall()
    con.close()

    # Formater les dates
    debates = [(id_debat, titre, description, datetime.strptime(date_creation, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y à %H:%M:%S"))
               for id_debat, titre, description, date_creation in debates_raw]

    return render_template('theme.html', theme_name=theme_name, debates=debates, is_logged_in='username' in session)

@app.route('/choixdebat.html')
def choixdebat():

    debat_id = request.args.get("debat_id")
    ancien_choix = request.args.get("ancien_choix")
    if not debat_id:
        return "Error: No debate selected."

    con = connect_db()
    cur = con.cursor()

    cur.execute("SELECT titre, description FROM debats WHERE id_debat = ?", (debat_id,))
    debate = cur.fetchone()

    cur.execute("SELECT date_fin FROM debats WHERE id_debat = ?", (debat_id,))
    data = cur.fetchone()
    if not data or not debate:
        con.close()
        return "Erreur: Débat introuvable."

    date_fin = data[0]
    date_fin = datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    time_left = (date_fin - now).total_seconds()

    if time_left <= 0:
        con.close()
        return redirect(url_for('debat_closed', debat_id=debat_id))

    #Vérifier si l'utilisateur est connecté
    if 'username' in session and not ancien_choix:  # ancien_choix indique un changement d'avis
        cur.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
        id_uti = cur.fetchone()
        if id_uti:
            id_uti = id_uti[0]
            # Vérifier si l'utilisateur a déjà un camp pour ce débat
            cur.execute("SELECT camp FROM campUti WHERE id_debat = ? AND id_uti = ?", (debat_id, id_uti))
            result = cur.fetchone()
            if result:
                con.close()
                # Rediriger directement vers debat.html avec le camp actuel
                return redirect(url_for('debat', debat_id=debat_id, choix=result[0]))

    con.close()
    
    # Si pas de camp ou changement d'avis, afficher la page de choix
    return render_template('choixdebat.html', debate=debate, debat_id=debat_id, time_left=time_left, 
                           is_logged_in='username' in session, ancien_choix=ancien_choix)

@app.route('/confirmer_changement')
def confirmer_changement():

    debat_id = request.args.get("debat_id")
    id_arg = request.args.get("id_arg")
    
    if not debat_id or not id_arg:
        return "Erreur : Débat ou argument non spécifié."
    
    if 'username' not in session:
        return redirect(url_for('connexion'))
    
    con = connect_db()
    cur = con.cursor()
    
    # Récupérer id_uti
    cur.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
    id_uti = cur.fetchone()
    if not id_uti:
        con.close()
        return "Utilisateur non trouvé", 404
    id_uti = id_uti[0]
    session['user_id'] = id_uti

    # Récupérer l'ancien camp
    cur.execute("SELECT camp FROM campUti WHERE id_debat = ? AND id_uti = ?", (debat_id, id_uti))
    result = cur.fetchone()
    ancien_choix = result[0] if result else None
    
    
    # Mettre à jour la table campUti  selon le choix
    try:
        if not add_or_modify_campUti(debat_id, id_uti, ancien_choix):
            return redirect(url_for('commentaire', arg_id=id_arg, error="Erreur lors du changement"))
        # Incrémenter le change de l’argument
        success = change_avis(id_arg)
        if not success:
            con.close()
            return redirect(url_for('commentaire', arg_id=id_arg, error="Erreur lors de la mise à jour de l’argument"))
        
        # Supprimer choix de la session
        if 'choix' in session:
            del session['choix']
    except Exception as e:
        con.close()
        return redirect(url_for('commentaire', arg_id=id_arg, error="Erreur lors du changement"))
    
    con.close()
    
    # Rediriger vers choixdebat.html avec l'ancien camp
    return redirect(url_for('choixdebat', debat_id=debat_id, ancien_choix=ancien_choix))


@app.route('/debat.html')
def debat():
    
    debat_id = request.args.get("debat_id")
    choix = request.args.get("choix")
    
    if not debat_id:
        return "Erreur: Aucun débat sélectionné."
    
    con = connect_db()
    cur = con.cursor()

    # Si l'utilisateur est connecté et a fait un choix
    if 'username' in session and choix in ['V', 'S', 'N']:
        cur.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
        id_uti = cur.fetchone()
        if id_uti:
            id_uti = id_uti[0]
            session['user_id'] = id_uti  # Mettre à jour session['user_id']
            add_or_modify_campUti(debat_id, id_uti, choix)
        session['choix'] = choix
    elif 'username' in session:
        # Récupérer le camp actuel si pas de nouveau choix
        cur.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
        id_uti = cur.fetchone()
        if id_uti:
            id_uti = id_uti[0]
            session['user_id'] = id_uti
            cur.execute("SELECT camp FROM campUti WHERE id_debat = ? AND id_uti = ?", (debat_id, id_uti))
            result = cur.fetchone()
            session['choix'] = result[0] if result else None

    cur.execute("SELECT titre, description, date_fin FROM debats WHERE id_debat = ?", (debat_id,))
    data = cur.fetchone()

    cur.execute("SELECT theme FROM debats WHERE id_debat = ?", (debat_id,))
    theme = cur.fetchone()

    theme_name = theme[0]

    if not data:
        con.close()
        return "Erreur: Débat introuvable."

    titre, description, date_fin = data

    date_fin = datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    time_left = (date_fin - now).total_seconds()
   
    debate = (titre, description)

    # Récupérer les arguments triés par camp (S, V, N) et date de création
    cur.execute("""
        SELECT a.id_arg,u.pseudo, a.court, a.texte, a.camps, a.date_creation, a.like, a.dislike
        FROM argument a
        JOIN utilisateur u ON a.id_uti = u.id_uti
        WHERE a.id_debat = ?
        ORDER BY 
            CASE camps 
                WHEN 'S' THEN 1 
                WHEN 'V' THEN 2 
                WHEN 'N' THEN 3 
            END, 
            date_creation ASC
    """, (debat_id,))
    args = cur.fetchall()

    # Pour désactiver les boutons on utilise : 
    # liked_args et disliked_args pour récupérer les arguments likés et dislikés par l’utilisateur connecté
    liked_args = []
    disliked_args = []
    if 'username' in session:
        cur.execute("SELECT id_arg FROM likes WHERE id_uti = (SELECT id_uti FROM utilisateur WHERE pseudo = ?)", (session['username'],))
        liked_args = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT id_arg FROM dislikes WHERE id_uti = (SELECT id_uti FROM utilisateur WHERE pseudo = ?)", (session['username'],))
        disliked_args = [row[0] for row in cur.fetchall()]

    con.close()

    return render_template('debat.html', debate=debate, args=args, time_left=int(time_left), theme_name=theme_name,
                           debat_id=debat_id, choix=choix or session.get('choix'), is_logged_in='username' in session, liked_args=liked_args, disliked_args=disliked_args)

@app.route('/commentaire.html')
def commentaire():

    arg_id = request.args.get("arg_id")
    if not arg_id:
        return "Erreur: Argument non spécifié."

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
    SELECT a.id_debat, u.pseudo, a.court, a.texte, a.camps, a.like, a.date_creation
    FROM argument a
    JOIN utilisateur u ON a.id_uti = u.id_uti
    WHERE a.id_arg = ?
    """, (arg_id,))
    
    result = cur.fetchone()

    con.close()
    if not result:
        return "Argument introuvable."
    
    debat_id, auteur, titre, desc, camps, like, date = result  
    
    choix =request.args.get("choix") or session.get("choix")
    
    return render_template('commentaire.html', 
        auteur=auteur, 
        titre=titre, 
        desc=desc, 
        camps=camps, 
        like=like,
        date=date,
        debat_id=debat_id,  
        choix=choix,
        arg_id=arg_id 
    )

@app.route('/creerdebat.html', methods=['GET', 'POST'])
def creerdebat():
    if "username" not in session:
        return redirect(url_for("connexion"))

    if request.method == 'POST':
        titre = request.form.get('title')
        description = request.form.get('description')
        theme = request.form.get('theme')
        id_uti = session["user_id"]
        date_fin = request.form['date_fin']
        heure_fin = request.form['heure_fin'] + ":00"
        date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Combiner date et heure
        try:
            datetime_str = f"{date_fin} {heure_fin}"  # ex. "2025-04-03 15:30:00"
            date_fin = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            if date_fin <= datetime.now():
                return render_template('creerdebat.html', error="La date et heure de fin doivent être dans le futur.", is_logged_in=True)
        except ValueError:
            return render_template('creerdebat.html', 
                                 error="Format invalide. Utilisez aaaa-mm-jj pour la date et hh:mm:ss pour l'heure (ex. 2025-04-03 et 15:30:00).", 
                                 is_logged_in=True)
        
        try:
            add_debat(titre, description, id_uti, theme, date_creation, date_fin)
            flash("Votre débat a été ajouté avec succès !", "success")
            return redirect(url_for('theme_page', theme_name=theme))
        except Exception as e:
            return render_template('creerdebat.html', error=f"Erreur lors de la création du débat: {e}")

    return render_template('creerdebat.html', is_logged_in='username' in session)

@app.route('/debat_closed.html')
def debat_closed():
    debat_id = request.args.get("debat_id")
    if not debat_id:
        return "Erreur: Aucun débat sélectionné."

    con = connect_db()
    cur = con.cursor()
    
    # Infos du débat
    cur.execute("SELECT titre, description FROM debats WHERE id_debat = ?", (debat_id,))
    debate = cur.fetchone()

    # CAMPS DU DEBUT
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp_debut = 'V' AND id_debat = ?", (debat_id,))
    debut_V = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp_debut = 'S' AND id_debat = ?", (debat_id,))
    debut_S = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp_debut = 'N' AND id_debat = ?", (debat_id,))
    debut_N = cur.fetchone()[0]

    # CAMPS A LA FIN
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp = 'V' AND id_debat = ?", (debat_id,))
    fin_V = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp = 'S' AND id_debat = ?", (debat_id,))
    fin_S = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campUti WHERE camp = 'N' AND id_debat = ?", (debat_id,))
    fin_N = cur.fetchone()[0]

    # NB TOTAL DE VOTES
    cur.execute("SELECT COUNT(distinct id_arg) FROM argument where camps = 'V' AND id_debat = ?", (debat_id,))
    nb_V = cur.fetchone()[0]
    cur.execute("SELECT COUNT(distinct id_arg) FROM argument where camps = 'S' AND id_debat = ?", (debat_id,))
    nb_S = cur.fetchone()[0]
    cur.execute("SELECT COUNT(distinct id_arg) FROM argument where camps = 'N' AND id_debat = ?", (debat_id,))
    nb_N = cur.fetchone()[0]
    nb_total = nb_N+nb_S+nb_V

    #ON RECUP LES FLUX
    cur.execute("""
        SELECT camp_debut, camp, COUNT(*) as count
        FROM campUti
        WHERE id_debat = ?
        GROUP BY camp_debut, camp
    """, (debat_id,))
    flows = cur.fetchall()

    # Nombre de personnes ayant changé d'avis
    cur.execute("""
        SELECT COUNT(*) 
        FROM campUti 
        WHERE id_debat = ? 
        AND camp_debut != camp
    """, (debat_id,))
    nb_change = cur.fetchone()[0]

    #TOP 3 des arguments les plus likés
    cur.execute("""
        SELECT a.court, a.texte, a.like, a.camps, u.pseudo
        FROM argument a
        JOIN utilisateur u ON a.id_uti = u.id_uti
        WHERE a.id_debat = ?
        ORDER BY a.like DESC
        LIMIT 3
    """, (debat_id,))
    top_arguments_like = cur.fetchall()

    # TOP 3 des arguments les plus convaincants
    cur.execute("""
        SELECT a.court, a.texte, a.change, a.camps, u.pseudo
        FROM argument a
        JOIN utilisateur u ON a.id_uti = u.id_uti
        WHERE a.id_debat = ?
        ORDER BY a.change DESC
        LIMIT 3
    """, (debat_id,))
    top_3_convaincants = cur.fetchall()

    # Camp qui a le plus convaincu (le plus de migrations vers lui)
    cur.execute("""
        SELECT camp, COUNT(*) 
        FROM campUti 
        WHERE camp_debut != camp AND id_debat = ?
        GROUP BY camp
    """, (debat_id,))
    results = cur.fetchall()

    # On met tous les scores dans un dict avec 0 par défaut
    camp_scores = {'V': 0, 'S': 0, 'N': 0}
    for camp, count in results:
        camp_scores[camp] = count

    # On trie pour avoir l’ordre du podium
    sorted_camps = sorted(camp_scores.items(), key=lambda x: x[1], reverse=True)
    podium_order = ''.join([camp for camp, _ in sorted_camps])

    camp_gagnant = podium_order[0]

    #RECUP l'utilisateur qui a le plus contribué à la victoire du debat
    #c-a-d celui dont les arguments ont convaincus le plus de personnes 
    cur.execute("""
        SELECT 
            u.pseudo,
            SUM(a.change) as total_change,
            a.camps
        FROM argument a
        JOIN utilisateur u ON a.id_uti = u.id_uti
        WHERE a.id_debat = ?
        AND a.camps = ?
        GROUP BY u.id_uti, u.pseudo, a.camps
        ORDER BY total_change DESC
        LIMIT 1
    """, (debat_id, camp_gagnant))
    top_contributeur = cur.fetchone()

    # Vérifier si on a un résultat et le formater
    top_contributeur_data = None
    if top_contributeur:
        top_contributeur_data = {
            'pseudo': top_contributeur[0],
            'total_change': top_contributeur[1],
            'camp': top_contributeur[2]
        }

    con.close()

    if not debate:
        return "Erreur: Débat introuvable."

    # Préparer les données pour les charts
    chart_data = {
        'debut': {
            'labels': ['Pour', 'Contre', 'Neutre'],
            'values': [debut_V, debut_S, debut_N]
        },
        'fin': {
            'labels': ['Pour', 'Contre', 'Neutre'],
            'values': [fin_V, fin_S, fin_N]
        },
        'total' : {
            'labels' : ['Pour', 'Contre', 'Neutre'],
            'values' : [nb_V, nb_S, nb_N]
        }
    }

    # Ajouter les flux à chart_data
    chart_data['flows'] = [{'source': row[0], 'target': row[1], 'value': row[2]} for row in flows]

    #on recupère les données des top3
    top_3_args_like = [
        {
            'court': row[0],
            'texte': row[1],
            'like': row[2],
            'camp': row[3],
            'pseudo': row[4]
        }
        for row in top_arguments_like
    ]

    top_3_convaincants = [
        {'court': row[0], 'texte': row[1], 'change': row[2], 'camps': row[3], 'pseudo': row[4]}
        for row in top_3_convaincants
    ]

    print("au début,\n"),
    print("nb de POUR : ",debut_V)
    print("nb de CONTRE : ",debut_S)
    print("nb de NEUTRE : ",debut_N)

    print("A la fin,\n"),
    print("nb de POUR : ",fin_V)
    print("nb de CONTRE : ",fin_S)
    print("nb de NEUTRE : ",fin_N)

    print("Au total,\n"),
    print("nb d'argument(s) POUR : ",nb_V)
    print("nb d'argument(s) CONTRE : ",nb_S)
    print("nb d'argument(s) NEUTRE : ",nb_N)
    print("soit ",nb_total," argument(s) en tout.\n")

    return render_template('debat_closed.html', 
                         debate=debate,
                         chart_data=chart_data,
                         debut_V=debut_V,
                         debut_S=debut_S,
                         debut_N=debut_N,
                         fin_V=fin_V,
                         fin_S=fin_S,
                         fin_N=fin_N,
                         nb_V=nb_V,
                         nb_S=nb_S,
                         nb_N=nb_N,
                         nb_total=nb_total,
                         nb_change=nb_change,
                         top_3_args_like=top_3_args_like,
                         top_3_convaincants=top_3_convaincants,
                         podium_order=podium_order,
                         camp_scores=camp_scores,
                         top_contributeur_data=top_contributeur_data,
                         debat_id=debat_id, is_logged_in='username' in session)

@app.route('/logout')
def logout():
    session.pop("username", None)  # Remove user from session
    return redirect(url_for("home"))  # Redirect to homepage

@app.route('/profil')
def profil():
    if "username" not in session:
        return redirect(url_for("connexion"))

    user_id = session["user_id"]
    
    con = connect_db()
    cur = con.cursor()

    # Récupérer les infos de l'utilisateur
    cur.execute("""
        SELECT pseudo, nom, prenom, mail, gender, dateNaissance, nationalite 
        FROM utilisateur 
        WHERE id_uti = ?
    """, (user_id,))
    user = cur.fetchone()

    # Récupérer et formater les débats créés par l'utilisateur
    cur.execute("""
        SELECT id_debat, titre, description, date_creation 
        FROM debats 
        WHERE id_uti = ?
    """, (user_id,))
    debates_raw = cur.fetchall()
    debates = [(id_debat, titre, description, datetime.strptime(date_creation, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y à %H:%M:%S"))
               for id_debat, titre, description, date_creation in debates_raw]

    con.close()

    if not user:
        return "Erreur : Utilisateur introuvable."


    pseudo, nom, prenom, mail, gender, date_naissance, nationalite = user

    try:
        formatted_date = datetime.strptime(date_naissance, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        # Si la date n'est pas au format attendu, on la laisse telle quelle
        formatted_date = date_naissance

    return render_template('profil.html', 
                          pseudo=pseudo, nom=nom, prenom=prenom, mail=mail, 
                          gender=gender, date_naissance=formatted_date, nationalite=nationalite,
                          debates=debates)

@app.route('/modifier_profil', methods=['GET', 'POST'])
def modifier_profil():
    if "username" not in session:
        return redirect(url_for("connexion"))

    user_id = session["user_id"]

    if request.method == 'POST':
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        mail = request.form.get("mail")
        gender = request.form.get("gender")
        date_naissance = request.form.get("dateNaissance")
        nationalite = request.form.get("nationalite")

        if not all([nom, prenom, mail, gender, date_naissance, nationalite]):
            return render_template('modifier_profil.html', error="Tous les champs doivent être remplis.")

        try:
            datetime.strptime(date_naissance, "%Y-%m-%d") 
        except ValueError:
            return render_template('modifier_profil.html', error="Format de date invalide! Utilisez JJ/MM/AAAA.")

        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            UPDATE utilisateur 
            SET nom = ?, prenom = ?, mail = ?, gender = ?, dateNaissance = ?, nationalite = ?
            WHERE id_uti = ?
        """, (nom, prenom, mail, gender, date_naissance, nationalite, user_id))
        con.commit()
        con.close()

        return redirect(url_for('profil'))

    con = connect_db()
    cur = con.cursor()
    cur.execute("""
        SELECT nom, prenom, mail, gender, dateNaissance, nationalite 
        FROM utilisateur 
        WHERE id_uti = ?
    """, (user_id,))
    user = cur.fetchone()
    con.close()

    nom, prenom, mail, gender, date_naissance, nationalite = user

    return render_template('modifier_profil.html', 
                          nom=nom, 
                          prenom=prenom, 
                          mail=mail, 
                          gender=gender, 
                          date_naissance=date_naissance, 
                          nationalite=nationalite)

@app.route('/add_argument', methods=['POST'])
def ajouter_argument():
    if "username" not in session:
        return redirect(url_for("connexion"))

    user_id = session["user_id"]
    debat_id = request.form.get("debat_id")
    choix = request.form.get("choix")
    texte = request.form.get("texte")
    court = request.form.get("court")

    if not all([debat_id, choix, texte, court]):
        flash("Tous les champs doivent être remplis.", "error")
        return redirect(url_for('debat', debat_id=debat_id, choix=choix))

    try:
        add_argument(debat_id, user_id, court, texte, choix)
        flash("Votre argument a été ajouté avec succès !", "success")
        return redirect(url_for('debat', debat_id=debat_id, choix=choix))
    except sqlite3.Error as e:
        flash(f"Erreur lors de l'ajout de l'argument : {e}", "error")
        return redirect(url_for('debat', debat_id=debat_id, choix=choix))



@app.route('/liker_argument/<int:arg_id>', methods=['POST'])
def liker_argument(arg_id):

    if 'username' not in session:
        return redirect(url_for('connexion'))
    
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
    id_uti = cursor.fetchone()
    if not id_uti:
        db.close()
        return "Utilisateur non trouvé", 404
    id_uti = id_uti[0]
    
    cursor.execute("SELECT id_debat FROM argument WHERE id_arg = ?", (arg_id,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return "Argument non trouvé", 404
    debat_id = result[0]
    
    cursor.execute("SELECT COUNT(*) FROM likes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
    already_liked = cursor.fetchone()[0] > 0
    
    if not already_liked:
        try:
            cursor.execute("SELECT COUNT(*) FROM dislikes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
            already_disliked = cursor.fetchone()[0] > 0

            now = datetime.now()

            if already_disliked:
                cursor.execute("DELETE FROM dislikes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
                cursor.execute("UPDATE argument SET dislike = dislike - 1 WHERE id_arg = ?", (arg_id,))

            cursor.execute("""
                INSERT INTO likes (id_arg, id_uti, date_like)
                VALUES (?, ?, ?)
            """, (arg_id, id_uti, now))
            cursor.execute("UPDATE argument SET like = like + 1 WHERE id_arg = ?", (arg_id,))
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l’ajout du like : {e}")
            db.close()
            return redirect(url_for('debat', debat_id=debat_id, choix=session.get('choix'), error="Erreur lors du like"))
    
    db.close()
    return redirect(url_for('debat', debat_id=debat_id, choix=session.get('choix')))


@app.route('/disliker_argument/<int:arg_id>', methods=['POST'])
def disliker_argument(arg_id):

    if 'username' not in session:
        return redirect(url_for('connexion'))
    
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT id_uti FROM utilisateur WHERE pseudo = ?", (session['username'],))
    id_uti = cursor.fetchone()
    if not id_uti:
        db.close()
        return "Utilisateur non trouvé", 404
    id_uti = id_uti[0]
    
    cursor.execute("SELECT id_debat FROM argument WHERE id_arg = ?", (arg_id,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return "Argument non trouvé", 404
    debat_id = result[0]
    
    cursor.execute("SELECT COUNT(*) FROM dislikes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
    already_disliked = cursor.fetchone()[0] > 0
    
    if not already_disliked:
        try:
            cursor.execute("SELECT COUNT(*) FROM likes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
            already_liked = cursor.fetchone()[0] > 0

            now = datetime.now()

            if already_liked:
                cursor.execute("DELETE FROM likes WHERE id_arg = ? AND id_uti = ?", (arg_id, id_uti))
                cursor.execute("UPDATE argument SET like = like - 1 WHERE id_arg = ?", (arg_id,))

            cursor.execute("""
                INSERT INTO dislikes (id_arg, id_uti, date_dislike)
                VALUES (?, ?, ?)
            """, (arg_id, id_uti, now))
            cursor.execute("UPDATE argument SET dislike = dislike + 1 WHERE id_arg = ?", (arg_id,))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l’ajout du dislike : {e}")
            db.close()
            return redirect(url_for('debat', debat_id=debat_id, choix=session.get('choix'), error="Erreur lors du dislike"))
    
    db.close()
    return redirect(url_for('debat', debat_id=debat_id, choix=session.get('choix')))


if __name__ == '__main__':
    app.run(debug=True)