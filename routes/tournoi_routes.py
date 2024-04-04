from flask import Blueprint, jsonify, request
from Client2Mongo import Client2Mongo as Mongo
from Tournoi import Tournoi
from routes.equipement_routes import affiche_nb_equip, modif_statut_en_fonction_tournoi
from routes.match_routes import suppresion_matchs_tournois, modif_nom_tournoi
from id.createur_id import creation_id
import random

tournois_bp = Blueprint('tournois', __name__)

# Ouverture de la connexion à la bd
bd = Mongo("rayan")


# Méthode qui permet l'insertion d'un tournoi dans la bd
@tournois_bp.route('/', methods=['POST'])
def insertion_tournoi():

    # Récupération des données envoyées via le formulaire
    tournoi = request.json

    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Décomposition de la requête pour gérer l'insertion du tournoi
    nom, date, format, age_min, age_max, niveau = (tournoi.get(attribut) for attribut in ["nom", "date", "format",
                                                                                          "ageMin", "ageMax", "niveau"])

    # Creation d'un tournoi pour vérifier si les entrées sont bonnes
    t = Tournoi(nom, date, format, ((age_min, age_max), niveau))

    dernier_id = creation_id("tournois")

    # Création d'un document qui correspond aux champs de la collection tournois
    tournoi = {"_id": str(dernier_id), "nom": nom, "date": {"debut": date, "fin": date}, "format": format,
               "Categorie": {"age": str(age_min) + "-" + str(age_max), "niveau": niveau}, "status": "Prévu"}

    # Insertion du tournoi dans la collection tournois de la bd
    collection.insert_one(tournoi)

    return "Tournoi inséré avec succès", 201


"""
Méthode qui permet de modifier soit le nom du tournoi, soit le format ou bien le statut et qui prend en paramètre
l'id du tournoi à modifier, le nom du champ à modifier , l'ancienne valeur de ce champ, et la nouvelle valeur
"""


@tournois_bp.route('/modif/<string:id_tournoi>/<string:nom_champ>/<string:ancienne_valeur>/<string:nouvelle_valeur>',
                   methods=['PATCH'])
def modif_tournoi(id_tournoi: str, nom_champ: str, ancienne_valeur: str, nouvelle_valeur: str):
    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection.find_one({"_id": id_tournoi})

    if not tournoi:
        return f"Aucun tournoi n'a été trouvé avec cet id : {id_tournoi}", 456
    else:
        # Requête qui permet de vérifier si le nom du champ donné en paramètre existe
        tournoi = collection.find_one({"_id": id_tournoi, nom_champ: ancienne_valeur})

        if not tournoi:
            return f"Aucun valeur a été trouvé pour le champ {nom_champ}", 487
        else:
            # Filtre qui permet de permet de cibler le tournoi à modifier
            filtre = {"_id": id_tournoi}

            # Variable qui permet de modifier le champ spécifié et de lui attribué la nouvelle valeur
            new_valeur_tournoi = {"$set": {nom_champ: nouvelle_valeur}}

            # Mise à jour de la collection tournoi pour modifier le champ du tournoi voulu
            collection.update_one(filtre, new_valeur_tournoi)

            if nom_champ == "nom":
                modif_nom_tournoi(ancienne_valeur, nouvelle_valeur)

            return "Modif avec succès", 200


# Méthode qui permet d'afficher tous les tournois contenu dans la bd
@tournois_bp.route('/', methods=['GET'])
def affiche_tournois():
    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Création d'une liste pour stocker les documents de la requête find
    tournois = []

    # Ajout des documents dans la liste
    for tournoi in collection.find():
        tournois.append(tournoi)
    return jsonify(tournois), 200


# Méthode qui permet d'afficher un tournoi et qui prend en paramètre l'id du tournoi voulue
@tournois_bp.route('/<string:id_tournoi>', methods=['GET'])
def affiche_tournoi(id_tournoi: str):
    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection.find_one({"_id": id_tournoi})

    if not tournoi:
        return f"Aucun tournoi n'a été trouvé avec cet id : {id_tournoi}", 404
    else:
        return jsonify(tournoi), 200


# Méthode qui permet de supprimer un tournoi et qui prend en paramètre l'id du tournoi qu'on souhaite supprimer
@tournois_bp.route('/<string:id_tournoi>', methods=['DELETE'])
def suppresion_tournoi(id_tournoi: str):
    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection.find_one({"_id": id_tournoi})

    if tournoi is None:
        return f"Aucun tournoi n'a été trouvé avec cet id : {id_tournoi}", 404
    else:

        # Suppression dans la collection tournois
        collection.delete_one({"_id": id_tournoi})

        # Suppression des matchs du tournoi dans la collection matchs
        suppresion_matchs_tournois(tournoi.get("nom"))

        # Modification de la disponibilité des équipements dans la collection équipements
        modif_statut_en_fonction_tournoi(id_tournoi)

        return "Suppression du tournoi effectuée avec succès", 200


"""
Méthode qui permet d'inscrire un joueur à un tournoi et qui prend en paramètre l'id du joueur à ajouté et l'id du
tournoi dans lequel on ajoute le joueur
"""


@tournois_bp.route('/ajout_joueurs/<string:id_tournoi>/<string:id_joueur>', methods=['PATCH'])
def ajout_joueur(id_tournoi: str, id_joueur: str):
    # Récupération des collections joueurs et tournois de la bd
    collection_joueur, collection_tournoi = (bd.get_collection(collection) for collection in ["joueurs", "tournois"])

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection_tournoi.find_one({"_id": id_tournoi})

    # Requête qui permet de vérifier si le joueur existe
    joueur = collection_joueur.find_one({"_id": id_joueur})

    if not tournoi:
        return "Le tournoi n'existe pas", 404
    elif not joueur:
        return "Le joueur n'existe pas", 404

    else:

        # Récupération de la liste des joueurs qui sont déjà inscrit au tournoi
        joueurs_inscrits = tournoi.get("Joueurs", [])

        if len(joueurs_inscrits) >= 8:
            return "Nombre maximal de joueurs atteint pour ce tournoi", 456

        # Vérification de la présence du joueur dans listes des inscrits
        id_joueur_present = any(joueur.get("_id") == id_joueur for joueur in joueurs_inscrits)

        if id_joueur_present:
            return "Le joueur est déja inscrit à ce tournoi.", 458
        else:

            # Récupération du niveau requis pour s'incrire au tournoi et du niveau du joueur à inscrire
            niveau_tournoi, niveau_joueur = (item.get("Categorie", {}).get("niveau") for item in [tournoi, joueur])

            # Récupération du de l'age requis pour s'incrire au tournoi
            age_tournoi = str(tournoi.get("Categorie", {}).get("age"))
            age_min, age_max = age_tournoi.split("-")

            # Récupération de l'âge du joueur
            age_joueur = int(joueur.get("Categorie", {}).get("age"))

            if niveau_joueur == niveau_tournoi and int(age_min) <= age_joueur <= int(age_max):

                # Récupération du nom et du prénom du joueur
                nom, prenom = (joueur.get(attribut) for attribut in ["nom", "prenom"])

                # Inscription du joueur en l'ajoutant à la liste des inscrits
                joueurs_inscrits.append({"_id": id_joueur, "nom": nom, "prenom": prenom})

                # Filtre qui permet de permet de cibler le tournoi à modifier
                filtre = {"_id": id_tournoi}

                # Variable qui permet de modifier la liste des joueurs inscrits au tournoi
                nouvelles_valeurs = {"$set": {"Joueurs": joueurs_inscrits}}

                # Mise à jour de la collection tournoi pour modifier le champ du tournoi voulu
                collection_tournoi.update_one(filtre, nouvelles_valeurs)

                return "Le joueur a bien été inscrit", 200
            else:
                return "Le joueur ne correspond pas aux critères d'âge ou de niveau du tournoi", 450

# Méthode qui permet de savoir le nombre d'inscrits d'un tournoi
@tournois_bp.route('/nb_inscrit/<string:id_tournoi>', methods=['GET'])
def affiche_nb_inscrit(id_tournoi: str):
    # Récupération de la collection tournois de la bd
    collection = bd.get_collection("tournois")

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection.find_one({"_id": id_tournoi})

    if not tournoi:
        return "Le tournoi n'existe pas"
    else:

        # Récupération de la liste des joueurs inscrits
        joueurs_inscrits = tournoi.get("Joueurs", [])

        # Récupération des nombres d'inscrits
        nb_inscrits = len(joueurs_inscrits)

        return str(nb_inscrits)


@tournois_bp.route('/creer_match/<string:id_tournoi>', methods=['PATCH'])
def creation_match_tournois(id_tournoi: str):
    # Récupération des collections tournois, matchs et joueurs de la bd
    collection_tournoi, collection_match, collection_equipement = (bd.get_collection(collection) for collection in
                                                                   ["tournois", "matchs", "equipements"])

    # Requête qui permet de vérifier si le tournoi existe
    tournoi = collection_tournoi.find_one({"_id": id_tournoi})

    if not tournoi:
        return "Le tournoi n'existe pas", 404
    # Récupération du nombre de joueurs inscrits au tournoi
    nb_inscrit = int(affiche_nb_inscrit(id_tournoi))

    # Récupération du nombre de balles, de tables et raquettes contenu dans la collection équipements
    nb_balle, nb_table, nb_raquette = [int(affiche_nb_equip(equip)) for equip in ["balle", "table", "raquette"]]

    if nb_inscrit < 4:
        return "Pas assez de joueurs pour créer des matchs", 451
    elif nb_inscrit > 8:
        return "Trop de joueurs pour créer des matchs", 452
    elif nb_inscrit % 2 != 0:
        return "Le nombre de participant doit être pair pour pouvoir créer les matchs", 439
    elif nb_table < 2:
        return "Le nombre de table est insufisant pour pouvoir créer les matchs", 459
    elif nb_balle < 2:
        return "Le nombre de balle est insufisant pour pouvoir créer les matchs", 469
    elif nb_raquette < 4:
        return "Le nombre de raquette est insufisant pour pouvoir créer les matchs", 489
    else:

        """
        Création de conditions pour mettre à jour la disponibilitée des balles, des tables et des raquettes 
        utilisées dans le tournoi
        """
        cond_balle, cond_table, cond_raquette = [{"type": type, "statut": "Disponible"} for type in
                                                 ["balle", "table", "raquette"]]

        result_balle, result_table, result_raquette = [collection_equipement.find(cond).limit(limite) for cond, limite
                                                       in zip([cond_balle, cond_table, cond_raquette], [2, 2, 4])]

        for doc in result_balle:
            collection_equipement.update_one({"_id": doc["_id"]},
                                             {"$set": {"statut": "Occupé", "idTournoi": id_tournoi}})

        liste = list(result_table)

        for doc in liste:
            collection_equipement.update_one({"_id": doc["_id"]},
                                             {"$set": {"statut": "Occupé", "idTournoi": id_tournoi}})

        for doc in result_raquette:
            collection_equipement.update_one({"_id": doc["_id"]},
                                             {"$set": {"statut": "Occupé", "idTournoi": id_tournoi}})

        joueurs_actuels = tournoi.get("Joueurs", [])
        random.shuffle(joueurs_actuels)

        paires_matchs = []
        for i in range(0, len(joueurs_actuels), 2):
            if i + 1 < len(joueurs_actuels):
                paires_matchs.append((joueurs_actuels[i], joueurs_actuels[i + 1]))

        a = 0

        for paire in paires_matchs:
            joueur_1 = paire[0]
            joueur_2 = paire[1]

            dernier_id = creation_id("matchs")

            doc = {"_id": str(dernier_id), "nomTournoi": tournoi.get("nom"), "phase": "Phase de poule",
                   "format": "Simple", "joueurs": [joueur_1, joueur_2], "scores": "0-0",
                   "idTable": liste[a].get("_id"), "statut": "Prévu"}
            collection_match.insert_one(doc)
            a += 1

            if a == 2:
                a = 0

        return "Les matchs ont été crée", 200
