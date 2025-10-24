import json
import os
from typing import Union

from flask import Blueprint, send_from_directory
from werkzeug.wrappers import Response

satic_root = "../../../"

# Serve react
react_public_dir: str = os.path.join(os.getcwd(), f"{satic_root}/dist/public/")
react_blueprint = Blueprint("react", __name__, static_folder=react_public_dir, url_prefix="/")

MISSING_STATIC_ROOT_ERR_MESSAGE = "Unable to resolve react root path"


@react_blueprint.route("/", defaults={"path": ""})
@react_blueprint.route("/<path:path>")
def serve_react_home(path: Union[os.PathLike, str]) -> Response:
    assert react_blueprint.static_folder, MISSING_STATIC_ROOT_ERR_MESSAGE
    return send_from_directory(react_blueprint.static_folder, "index.html")


@react_blueprint.route("/index.bundle.js")
def serve_js_bundle() -> Response:
    assert react_blueprint.static_folder, MISSING_STATIC_ROOT_ERR_MESSAGE
    return send_from_directory(react_blueprint.static_folder, "index.bundle.js")


@react_blueprint.route("/style.css")
def serve_css() -> Response:
    assert react_blueprint.static_folder, MISSING_STATIC_ROOT_ERR_MESSAGE
    return send_from_directory(react_blueprint.static_folder, "style.css")


# Server react static images
react_img_assets_dir: str = os.path.join(os.getcwd(), f"{satic_root}/dist/assets/img")
img_assets_blueprint = Blueprint("image_assets", __name__, static_folder=react_img_assets_dir, url_prefix="/assets")


@img_assets_blueprint.route("/assets/img/<path:filename>")
def serve_static_images(filename: Union[os.PathLike, str]) -> Response:
    assert img_assets_blueprint.static_folder, MISSING_STATIC_ROOT_ERR_MESSAGE
    return send_from_directory(img_assets_blueprint.static_folder, filename)


# Serve Api home page
api_blueprint = Blueprint("api", __name__, url_prefix="/api")


@api_blueprint.route("/")
def serve_api_home() -> Response:
    message = {"msg": "Start your development..."}
    return Response(json.dumps(message), status=200)
