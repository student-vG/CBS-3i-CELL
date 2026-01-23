from flask import Blueprint, send_file, Response, abort
from utils.db import get_fs
from bson.objectid import ObjectId
import io

file_serving_bp = Blueprint('file_serving', __name__)

@file_serving_bp.route('/files/<file_id>')
def serve_file(file_id):
    fs = get_fs()
    try:
        if not ObjectId.is_valid(file_id):
            abort(404)
            
        file_obj = fs.get(ObjectId(file_id))
        
        # Determine content type based on filename extension (basic) or metadata
        filename = file_obj.filename
        content_type = 'application/octet-stream'
        
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.png'):
            content_type = 'image/png'
            
        return send_file(
            io.BytesIO(file_obj.read()),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        abort(404)
