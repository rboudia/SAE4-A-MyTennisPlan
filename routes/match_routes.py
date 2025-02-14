from flask import Blueprint, jsonify
from Client2Mongo import Client2Mongo as Mongo


matchs_bp = Blueprint('matchs', __name__)

# Ouverture de la connexion à la bd
bd = Mongo("MyTennisPlan")


# Méthode qui permet d'afficher les matchs d'un tournoi et qui prend en paramètre le nom du tournoi souhaité
@matchs_bp.route('/tournoi/<string:nom_tournoi>', methods=['GET'])
def affiche_matchs_tournoi(nom_tournoi: str):

    # Récupération de la collection matchs de la bd
    collection = bd.get_collection("matchs")

    # Requête qui permet de vérifier si au moins un match existe pour le nom de tournoi donné
    match = collection.find_one({"nomTournoi": nom_tournoi})

    if not match:
        return f"Aucun match n'est en cours pour le tournoi : {nom_tournoi}", 404
    else:

        # Création d'une liste pour stocker les documents de la requête find
        matchs_tournoi = []

        # Ajout des documents dans la liste
        for match in collection.find({"nomTournoi": nom_tournoi}):
            matchs_tournoi.append(match)

        return jsonify(matchs_tournoi), 200
