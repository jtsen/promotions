"""
Promotion  Service
Paths:
------
GET /promotions - Returns a list all of the Promotions
GET /promotions/{id} - Returns the Promotion with a given id number
POST /promotions - creates a new Promotion record in the database
PUT /promotions/{id} - updates a Promotion record in the database
DELETE /promotions/{id} - deletes a Promotion record in the database
PUT /promotions/{id}/activate - activates a Promotion with a given id number
PUT /promotions/{id}/deactivate - deactivates a Promotion with a given id number
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Promotion, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")

######################################################################
# LIST ALL PROMOTIONS
######################################################################


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """ Returns all of the Promotions """
    app.logger.info("Request for promotion list")
    promotions = []
    promotion_type = request.args.get("promotion_type")
    active = request.args.get("active")
    title = request.args.get("title")
    end_date = request.args.get("end_date")

    if promotion_type:
        promotions = Promotion.find_by_promotiontype(promotion_type)
    elif active:
        promotions = Promotion.find_by_active(active)
    elif title:
        promotions = Promotion.find_by_title(title)
    elif end_date:
        promotions = Promotion.find_by_end_date(end_date)
    else:
        promotions = Promotion.all()

    results = [promotion.serialize() for promotion in promotions]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotions(promotion_id):
    """
    Retrieve a single Promotion
    This endpoint will return a Promotion based on it's id
    """
    app.logger.info("Request for promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PROMOTION
######################################################################


@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    Creates a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a promotion")
    check_content_type("application/json")
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()
    message = promotion.serialize()
    location_url = url_for(
        "get_promotions", promotion_id=promotion.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotions(promotion_id):
    """
    Update a Promotion
    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to update promotion with id: %s", promotion_id)
    check_content_type("application/json")
    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
    promotion.deserialize(request.get_json())
    promotion.id = promotion_id
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotions(promotion_id):
    """
    Delete a Promotion
    This endpoint will delete a Promotion based the id specified in the path
    """
    app.logger.info("Request to delete promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if promotion:
        promotion.delete()

    app.logger.info("Promotion with ID [%s] delete complete.", promotion_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# ACTIVATE AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
def activate_promotions(promotion_id):
    """
    Activate a Promotion
    This endpoint will activate a Promotion based on the id specified in the path
    """
    app.logger.info("Request to activate promotion with id: %s", promotion_id)

    check_content_type("application/json")

    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
    promotion.active = True
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
# DEACTIVATE AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
def deactivate_promotions(promotion_id):
    """
    Deactivate a Promotion
    This endpoint will deactivate a Promotion based on the id specified in the path
    """
    app.logger.info(
        "Request to deactivate promotion with id: %s", promotion_id)

    check_content_type("application/json")

    promotion = Promotion.find(promotion_id)
    if not promotion:
        raise NotFound(
            "Promotion with id '{}' was not found.".format(promotion_id))
    promotion.active = False
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return make_response(jsonify(promotion.serialize()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Promotion.init_db(app)


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if "Content-Type" in request.headers and request.headers["Content-Type"] == content_type:
        return
    app.logger.error(
        "Invalid Content-Type: [%s]", request.headers.get("Content-Type"))
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          "Content-Type must be {}".format(content_type))
