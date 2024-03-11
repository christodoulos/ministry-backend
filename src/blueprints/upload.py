import json
from flask import Blueprint, jsonify, request, Response, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models.upload import FileUpload
import os
import uuid

upload = Blueprint("upload", __name__)


ALLOWED_EXTENSIONS = {"png", "jpg", "pdf", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload.route("", methods=["POST"])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    file = request.files["file"]
    google_id = current_user
    if file and allowed_file(file.filename):
        original_filename = file.filename
        file_id = str(uuid.uuid4())
        ext = original_filename.rsplit(".", 1)[1].lower()
        filename = f"{file_id}.{ext}"
        file_location = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        # save the file
        file.save(file_location)

        file_upload = FileUpload(
            google_id=google_id,
            file_id=file_id,
            file_name=original_filename,
            file_type=ext,
            file_size=os.path.getsize(file_location),
            file_location=file_location,
            file_url=f"{current_app.config['UPLOAD_FOLDER']}/uploads/{filename}",
        )
        file_upload.save()

        return Response("File uploaded", status=200)

    return Response("File not uploaded", status=400)


@upload.route("/getfiles", methods=["GET"])
@jwt_required()
def get_file():
    current_user = get_jwt_identity()
    files = FileUpload.objects(google_id=current_user).exclude("id")
    return Response(
        json.dumps([file.to_mongo().to_dict() for file in files]),
        mimetype="application/json",
        status=200,
    )
