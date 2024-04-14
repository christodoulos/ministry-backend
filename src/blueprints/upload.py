from flask import Blueprint, request, Response, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
import json
import os
import uuid
from src.models.upload import FileUpload
from src.config import ALLOWED_EXTENSIONS
from bson import ObjectId

upload = Blueprint("upload", __name__)


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
        filename = f"{file_id}"
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], current_user)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_save_location = os.path.join(file_path, filename)
        file.save(file_save_location)

        file_upload = FileUpload(
            google_id=google_id,
            file_id=file_id,
            file_name=original_filename,
            file_type=ext,
            file_size=os.path.getsize(file_save_location),
            file_location=file_path,
        )
        file_upload.save()

        # return Response(json.dumps({"file_id": file_id}), status=200)
        return Response(json.dumps({"id": str(file_upload.id)}), status=200)

    return Response(json.dumps({"msg": "File not uploaded"}), status=400)


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


@upload.route("<docid>", methods=["GET"])
@jwt_required()
def uploaded_file(docid):
    file_upload = FileUpload.objects(id=ObjectId(docid)).first()
    if file_upload is None:
        return Response("File not found", status=404)

    original_filename = file_upload.file_name
    file_location = file_upload.file_location
    filename_uuid = file_upload.file_id

    return send_from_directory(
        file_location,
        filename_uuid,
        as_attachment=True,
        download_name=original_filename,
    )


# @upload.route("<filename_uuid>", methods=["PATCH"])
# def update_file(filename_uuid):
#     file = FileUpload.objects(file_id=filename_uuid).first()
#     if file is None:
#         return Response("File not found", status=404)

#     data = request.get_json()  # expect data["file_name"]
#     file.update(**data)

#     return Response(json.dumps(file.to_mongo().to_dict()), status=200)
