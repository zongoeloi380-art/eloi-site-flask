from flask import Flask, render_template, request, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "ma_cle_secrete"


def creer_base():
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        email TEXT UNIQUE,
        motdepasse TEXT
    )
    """)

    connexion.commit()
    connexion.close()


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/inscription", methods=["GET", "POST"])
def inscription():

    if request.method == "POST":
        nom = request.form["nom"]
        email = request.form["email"]
        motdepasse = generate_password_hash(request.form["motdepasse"])

        connexion = sqlite3.connect("utilisateurs.db")
        curseur = connexion.cursor()

        try:
            curseur.execute(
                "INSERT INTO utilisateurs (nom, email, motdepasse) VALUES (?, ?, ?)",
                (nom, email, motdepasse)
            )

            connexion.commit()
            message = "Inscription réussie !"

        except:
            message = "Cet email existe déjà."

        connexion.close()

        return message

    return render_template("inscription.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():

    if request.method == "POST":

        email = request.form["email"]
        motdepasse = request.form["motdepasse"]

        connexion = sqlite3.connect("utilisateurs.db")
        curseur = connexion.cursor()

        curseur.execute(
            "SELECT * FROM utilisateurs WHERE email=?",
            (email,)
        )

        utilisateur = curseur.fetchone()

        connexion.close()


        if utilisateur and check_password_hash(utilisateur[3], motdepasse):

            session["id"] = utilisateur[0]
            session["nom"] = utilisateur[1]

            return render_template(
                "profil.html",
                nom=utilisateur[1]
            )

        else:
            return "Email ou mot de passe incorrect"


    return render_template("connexion.html")


@app.route("/profil")
def profil():

    if "nom" in session:
        return render_template(
            "profil.html",
            nom=session["nom"]
        )

    return "Vous devez être connecté."


@app.route("/modifier", methods=["GET", "POST"])
def modifier():

    if "id" not in session:
        return "Vous devez être connecté."

    if request.method == "POST":

        nouveau_nom = request.form["nom"]

        connexion = sqlite3.connect("utilisateurs.db")
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE utilisateurs SET nom=? WHERE id=?",
            (nouveau_nom, session["id"])
        )

        connexion.commit()
        connexion.close()

        session["nom"] = nouveau_nom

        return render_template(
            "profil.html",
            nom=nouveau_nom
        )

    return render_template("modifier.html")


@app.route("/deconnexion")
def deconnexion():

    session.clear()

    return render_template("index.html")


creer_base()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)