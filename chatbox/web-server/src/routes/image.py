
from flask import Blueprint, request, Response
from src.constants.http_status_codes import HTTP_500_INTERNAL_SERVER_ERROR

image = Blueprint("image", __name__, url_prefix="/web/api/v1/image")


@image.get("/<image_name>")
def get_image(image_name):
    try:
        image_filename = f"src/template/images/{image_name}"
        with open(image_filename, 'rb') as image_file:
            image_content = image_file.read()

        return Response(image_content, content_type='image/png')
    except Exception as e:
        return {"code": 500, "message": str(e)}, HTTP_500_INTERNAL_SERVER_ERROR
