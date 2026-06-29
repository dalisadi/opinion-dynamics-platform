# Opinion Dynamics Platform

A collaborative web platform for structured online debates, allowing users to discuss controversial topics, share arguments, interact with other participants, and visualize how opinions evolve throughout a debate.

Developed as a university software engineering project using Flask and SQLite.

---

## Overview

Opinion Dynamics Platform aims to encourage respectful and structured discussions by organizing participants into three positions:

- 🟢 **V** – In Favor
- ⚪ **/** – Neutral
- 🔴 **S** – Against

Users can create debates, choose their position, publish arguments, react to other arguments, and observe how opinions change over time through interactive visualizations.

---

## Features

### User Management

- User registration
- Secure authentication
- User profile
- Profile editing

### Debate Management

- Create debates
- Browse debates by category
- Debate expiration date
- Debate themes

### Participation

- Choose a position (For / Neutral / Against)
- Publish arguments
- Like and dislike arguments
- Opinion change confirmation
- Comment visualization

### Statistics Dashboard

Once a debate ends, the application generates statistics including:

- Opinion distribution
- Number of arguments
- Most convincing arguments
- Most liked arguments
- Winning position
- Sankey diagram showing opinion evolution
- Top contributor

---

## Technologies

| Category | Technologies |
|-----------|--------------|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite |
| Templating | Jinja2 |
| Charts | Chart.js, Google Charts |
| Testing | PyTest |

---

## Project Structure

```text
opinion-dynamics-platform
│
├── app.py
├── README.md
├── Project_Report.pdf
|
├── screenshots/
|   ├── home_guest_1.png
|   ├── home_guest_2.png
|   ├── login.png
|   ├── register_1.png
|   ├── register_2.png
|   ├── create_debate_1.png
|   ├── create_debate_2.png
|   ├── scientific_category.png
|   ├── debate_page_1.png
|   ├── debate_page_2.png
|   ├── profile.png
|   └── statistique.png
│
├── tests/
│   └── test_app.py
│
├── database/
│   ├── db_fun.py
│   ├── db_args_test.py
│   ├── db_debats_test.py
│   ├── db_users_test.py
│   ├── db_test_finaux.py
│   └── vns.db
│
├── static/
│   ├── icons/
│   │   ├── hand-thumbs-up.svg
│   │   ├── hand-thumbs-down.svg
│   │   ├── heart.svg
│   │   └── heart-fill.svg
│   │
│   ├── images/
│   │   ├── img/
│   │   ├── academique.jpg
│   │   ├── culturel.jpg
│   │   ├── economique.jpg
│   │   ├── environnemental.jpg
│   │   ├── juridique.jpg
│   │   ├── mediatique.jpg
│   │   ├── politique.jpg
│   │   ├── scientifique.jpg
│   │   ├── societal.jpg
│   │   └── technologique.jpg
│   │
│   ├── road_rage/
│   │   ├── Road_Rage.otf
│   │   └── READ_ME.txt
│   │
│   ├── accueil.css
│   ├── choix_themes.css
│   ├── choixdebat.css
│   ├── commentaire.css
│   ├── connexion.css
│   ├── contact.css
│   ├── creerdebat.css
│   ├── debat.css
│   ├── home.css
│   ├── inscription.css
│   ├── profil.css
│   ├── stats.css
│   └── themes.css
│
└── templates/
    ├── accueil.html
    ├── home.html
    ├── connexion.html
    ├── inscription.html
    ├── profil.html
    ├── modifier_profil.html
    ├── contact.html
    ├── creerdebat.html
    ├── choix_themes.html
    ├── choixdebat.html
    ├── debat.html
    ├── commentaire.html
    ├── debat_closed.html
    ├── theme.html
    └── stats.js

---

## Installation

Clone the repository

```bash
git clone https://github.com/dalisadi/opinion-dynamics-platform.git
```

Go inside the project

```bash
cd opinion-dynamics-platform
```

Install dependencies

```bash
pip install flask pytest
```

Run the application

```bash
python app.py
```

---

## Testing

Run all tests

```bash
pytest
```

---

## Screenshots

### Home page (Guest)

![Home](screenshots/home_guest_1.png)
![Home](screenshots/home_guest_2.png)

---

### Login

![Login](screenshots/login.png)

---

### Registration

![Registration](screenshots/register_1.png)

![Registration](screenshots/register_2.png)

---

### Create a debate

![Create Debate](screenshots/create_debate_1.png)

![Create Debate](screenshots/create_debate_2.png)

---

### Debate page

![Debate](screenshots/debate_page_1.png)
![Debate](screenshots/debate_page_2.png)

---

### User profile

![Profile](screenshots/profile.png)

### Statistique

![Profile](screenshots/statistique.png)

---

## Authors

This project was developed by a team of **six undergraduate Computer Science students** as part of a Software Engineering project.

GitHub repository maintained by **Dalia SADI**.

---

## Academic Context

This project was carried out during the third year of the Bachelor's degree in Computer Science and focuses on:

- Full-stack web development
- Database design
- Human-computer interaction
- Collaborative software engineering
- Testing and validation
- Data visualization

---

## Future Improvements

- Email verification
- Password recovery
- Real-time notifications
- Search engine
- User moderation
- Recommendation system
- Responsive mobile version
- Docker deployment
- REST API
- AI-based argument recommendation

---

## License

This repository is shared for educational and portfolio purposes.
