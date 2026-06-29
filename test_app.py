import pytest
from app import app
from flask import url_for


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response= client.get('/')
    assert response.status_code==200 # vérifie que la page charge
    # verifie qu'il y a une animation dans le code HTML, en cherchant des classes spécifiques de l'animation CSS
    assert b"animate__animated animate__zoomIn" in response.data
    # vérifie que le titre de la page contient "V/S"
    assert b"Page de Connexion" in response.data

def test_connexion(client):
    response=client.get('/connexion.html')
    assert response.status_code==200
    assert b"Connexion" in response.data

# Test de la connexion avec des informations correctes
def test_connexion_post_valid(client):
    response = client.post('/connexion', data={'username': 'Emma28', 'password': 'password123'})
    assert response.status_code == 200
    assert b"V/S" in response.data  # Vérifie que la page d'accueil affiche bien le message de bienvenue

# Test de la connexion avec des informations incorrectes
def test_connexion_post_invalid(client):
    response = client.post('/connexion', data={'username': 'wrong_user', 'password': 'wrong_pass'})
    assert response.status_code == 200
    #print(response.data.decode()) Pour afficher la réponse brute dans la console
    # Vérifie que le message d'erreur est bien présent dans la réponse
    assert b"Nom d&#39;utilisateur ou mot de passe incorrect" in response.data   

def test_inscription(client):
    response = client.get('/inscription.html')
    assert response.status_code == 200
    assert b"Inscription" in response.data

# Test de l'inscription avec un pseudo déjà pris
def test_inscription_post_username_taken(client):
    response = client.post('/inscription.html', data={'pseudo': 'Emma28', 'password': 'password123','nom': 'Nom', 'prenom': 'Prenom', 'mail': 'email@example.com','gender': 'Femme', 'dateNaissance': '1990-01-01', 'nationalite': 'France'})
    assert response.status_code == 200
    assert "Ce nom d&#39;utilisateur existe déjà. Choisissez un autre pseudo.".encode('utf-8') in response.data #utf-8 pour les accents

# Test de l'inscription avec un email déjà pris
def test_inscription_post_email_taken(client):
    response = client.post('/inscription.html', data={'pseudo': 'username', 'password': 'password123','nom': 'Nom', 'prenom': 'Prenom', 'mail': 'emma.burner@gmail.com','gender': 'Femme', 'dateNaissance': '1990-01-01', 'nationalite': 'France'})
    assert response.status_code == 200
    assert "Cet adresse mail est déjà utilisée.".encode('utf-8') in response.data #utf-8 pour les accents

# Test de la redirection d'inscription vers la page d'accueil (succès)
def test_successful_registration_redirect(client):
    response = client.post('/inscription.html', data={
        'pseudo': 'new_username', 'password': 'new_password',
        'nom': 'Nom', 'prenom': 'Prenom', 'mail': 'new_email@example.com',
        'gender': 'M', 'dateNaissance': '01/01/1990', 'nationalite': 'Française'
    })
    assert response.status_code == 200
    assert b"Impossible d&#39;ajouter l&#39;utilisateur." not in response.data  # Vérifie qu'il n'y a pas d'erreur


def test_contact(client):
    response=client.get('/contact.html')
    assert response.status_code==200
    assert b"Contact" in response.data

def test_accueil(client):
    response=client.get('/accueil.html')
    assert response.status_code==200 
    assert b"V/S" in response.data

def test_commentaire(client):
    response=client.get('/commentaire.html')
    assert response.status_code==200

def test_creerdebat(client):
    with client.session_transaction() as sess:
        sess['username'] = 'Emma28'

    response = client.get('/creerdebat.html')
    assert response.status_code == 200

def test_debat_closed(client):
    response=client.get('/debat_closed.html')
    assert response.status_code==200

def test_debat(client):
    response=client.get('/debat.html')
    assert response.status_code==200

def test_modifier_profil(client):
    with client.session_transaction() as sess:
        sess['username'] = 'Emma28'
        sess['user_id'] = 1 

    response=client.get('/modifier_profil')
    assert response.status_code==200
    assert b"Modifier Profil" in response.data

def test_profil(client):
    with client.session_transaction() as sess:
        sess['username'] = 'Emma28'
        sess['user_id'] = 1 

    response=client.get('/profil')
    assert response.status_code==200

def test_theme(client):
    response=client.get('/theme/<theme_name>')
    assert response.status_code==200
