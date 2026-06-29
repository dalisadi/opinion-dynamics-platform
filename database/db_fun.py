import sqlite3
from datetime import datetime

# Connect to the database
def connect_db():
    return sqlite3.connect('database/vns.db')

def create_db(cur):
    """creates database tables: 
    utilisateur(id_uti, pseudo, mdp, nom, prenom, mail, gender, dateNaissance, nationalite) 
    debats(id_debat, titre, description, id_uti, theme, date_creation, date_fin)
    argument(id_arg, id_debat, id_uti, court, texte, camps, change, like, date_creation)  
    campUti(id, id_debat, id_uti, camps, camps_debut)
    """
    cur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateur (
        id_uti INTEGER PRIMARY KEY AUTOINCREMENT,
        pseudo VARCHAR(255) NOT NULL UNIQUE, 
        mdp VARCHAR(255) NOT NULL,
        nom VARCHAR(255) NOT NULL,
        prenom VARCHAR(255) NOT NULL,
        mail VARCHAR(255) NOT NULL,
        gender VARCHAR(255) NOT NULL,
        dateNaissance DATE NOT NULL, 
        nationalite VARCHAR(255) NOT NULL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS debats (
        id_debat INTEGER PRIMARY KEY AUTOINCREMENT,
        titre VARCHAR(255) NOT NULL UNIQUE,
        description TEXT NOT NULL,
        id_uti INTEGER NOT NULL,
        theme VARCHAR(255) NOT NULL,
        date_creation DATETIME NOT NULL,
        date_fin DATETIME NOT NULL,
        FOREIGN KEY (id_uti) REFERENCES utilisateur(id_uti)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS argument (
        id_arg INTEGER PRIMARY KEY AUTOINCREMENT,
        id_debat INTEGER NOT NULL,
        id_uti INTEGER NOT NULL,
        court TEXT NOT NULL,
        texte TEXT NOT NULL,
        camps CHAR(1) CHECK(camps IN ('V', 'N', 'S')),
        change INTEGER DEFAULT 0,
        like INTEGER DEFAULT 0,
        dislike INTEGER DEFAULT 0,
        date_creation DATETIME NOT NULL,
        FOREIGN KEY (id_debat) REFERENCES debats(id_debat),
        FOREIGN KEY (id_uti) REFERENCES utilisateur(id_uti),
        UNIQUE (id_debat, court, texte, camps)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS campUti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_debat INTEGER NOT NULL,
        id_uti INTEGER NOT NULL,
        camp CHAR(1) CHECK(camp IN ('V', 'N', 'S')),
        camp_debut CHAR(1) CHECK(camp IN ('V', 'N', 'S')),
        FOREIGN KEY (id_debat) REFERENCES debats(id_debat),
        FOREIGN KEY (id_uti) REFERENCES utilisateur(id_uti)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id_arg INTEGER NOT NULL,
        id_uti INTEGER NOT NULL,
        date_like DATETIME NOT NULL,
        PRIMARY KEY (id_arg, id_uti),
        FOREIGN KEY (id_arg) REFERENCES argument(id_arg),
        FOREIGN KEY (id_uti) REFERENCES utilisateur(id_uti)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dislikes (
        id_arg INTEGER NOT NULL,
        id_uti INTEGER NOT NULL,
        date_dislike DATETIME NOT NULL,
        PRIMARY KEY (id_arg, id_uti),
        FOREIGN KEY (id_arg) REFERENCES argument(id_arg),
        FOREIGN KEY (id_uti) REFERENCES utilisateur(id_uti)
    )""")



def username_exists(pseudo):
    """Returns true if username is taken"""
    con = connect_db()
    if con is None:
        raise Exception("Impossible de se connecter à la base de données.")
    
    cur = con.cursor()
    cur.execute('SELECT * FROM utilisateur WHERE pseudo = ?', (pseudo,))
    result = cur.fetchone()
    con.close()
    return result is not None

def mail_exists(mail):
    """Returns true if email is connected to another account"""
    con = connect_db()
    if con is None:
        raise Exception("Impossible de se connecter à la base de données.")
    
    cur = con.cursor()
    cur.execute('SELECT * FROM utilisateur WHERE mail = ?', (mail,))
    result = cur.fetchone()
    con.close()
    return result is not None

def add_user(pseudo, mdp, nom, prenom, mail, gender, daten, nationalite):
    """Adds user to the database where daten's type is DATE"""
    if username_exists(pseudo) or mail_exists(mail):
        return False
    con = None
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute('''INSERT INTO utilisateur (pseudo, mdp, nom, prenom, mail, gender, dateNaissance, nationalite) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                    (pseudo, mdp, nom, prenom, mail, gender, daten, nationalite))
        con.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité (ex. contrainte UNIQUE) : {e}")
        return False
    except sqlite3.Error as e:
        print(f"Erreur d'insertion dans la base de données : {e}")
        return False
    finally:
        if con:
            con.close()

def add_debat(titre, description, id_uti, theme, date_creation, date_fin):
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO debats (titre, description, id_uti, theme, date_creation, date_fin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (titre, description, id_uti, theme, date_creation, date_fin))
        con.commit()
        debat_id = cur.lastrowid
        con.close()
        return debat_id
    except Exception as e:
        print(f"Erreur lors de l'ajout du débat: {e}")
        return None

def add_argument(id_debat, id_uti, court, texte, camps):
    """Adds argument to the database where camps is V N or S"""
    if camps not in ('V', 'N', 'S'):
        print("Invalid camp format.")
        return False
    if arg_uniq(id_debat, court, texte, camps):
        print("Cet argument a été déjà proposé.")
        return False
    try:
        con = connect_db()
        cur = con.cursor()
        date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO argument (id_debat, id_uti, court, texte, camps, date_creation) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_debat, id_uti, court, texte, camps, date_creation))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False


def add_or_modify_campUti(id_debat, id_uti, camp):
    """Adds or modifies the camp of the user for the given debate."""
    if camp not in ('V', 'N', 'S'):
        print("Invalid camp format.")
        return False
    
    con = None
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM campUti WHERE id_debat = ? AND id_uti = ?', (id_debat, id_uti))
        result = cur.fetchone()
        
        if result is not None:
            cur.execute("UPDATE campUti SET camp = ? WHERE id_uti = ? AND id_debat = ?", (camp, id_uti, id_debat))
        else:
            cur.execute("INSERT INTO campUti (id_debat, id_uti, camp, camp_debut) VALUES (?, ?, ?, ?)", (id_debat, id_uti, camp, camp))
        
        con.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if con is not None:
            con.close()

def change_avis(id_argx):
    """When an argument given changes someones mind (camps) increases the arguments column "change" by 1."""
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("UPDATE argument SET change = change + 1 WHERE id_arg = ?", (id_argx,))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False

def like(id_argx):
    """When an argument given is liked increases the arguments column "like" by 1."""
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("UPDATE argument SET like = like + 1 WHERE id_arg = ?", (id_argx,))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False

def arg_uniq(id_debat, court, texte, camps):
    """Returns true if (id_debat, court, texte, camps) are not unique"""
    con = connect_db()
    if con is None:
        raise Exception("Impossible de se connecter à la base de données.")
    
    cur = con.cursor()
    cur.execute('SELECT * FROM argument WHERE (id_debat, court, texte, camps) = (?,?,?,?)', (id_debat, court, texte, camps))
    result = cur.fetchone()
    con.close()
    return result is not None

def fetch_users():
    con = connect_db()
    if con is None:
        raise Exception("Impossible de se connecter à la base de données.")
    
    cur = con.cursor()
    cur.execute("SELECT * FROM utilisateur")
    rows = cur.fetchall()
    con.close()
    
    formatted_rows = []
    for row in rows:
        (user_id, pseudo, mdp, nom, prenom, mail, gender, date_db, nationalite) = row
        try:
            date_formatted = datetime.strptime(date_db, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            date_formatted = date_db
        formatted_rows.append((user_id, pseudo, mdp, nom, prenom, mail, gender, date_formatted, nationalite))
    return formatted_rows

def fetch_debat():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("SELECT id_debat, titre, description, date_creation FROM debats ORDER BY date_creation ASC")
        debates = cur.fetchall()
        con.close()
        return debates
    except Exception as e:
        print(f"Erreur lors de la récupération des débats: {e}")
        return []
    
if __name__ == '__main__':
    con = connect_db()
    cur = con.cursor()
    try:
        create_db(cur)
    except sqlite3.OperationalError:
        pass
    con.commit()
    con.close()