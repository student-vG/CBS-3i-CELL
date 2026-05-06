from pymongo import MongoClient
import gridfs
import os
from urllib.parse import quote_plus, unquote_plus, urlsplit, urlunsplit

# Get MONGO_URI from environment, or construct it from components
MONGO_URI = os.getenv('MONGO_URI', None)

# If MONGO_URI is present, normalize it by encoding username/password safely.
def normalize_mongo_uri(uri: str) -> str:
    parsed = urlsplit(uri)
    if not parsed.netloc or '@' not in parsed.netloc:
        return uri

    userinfo, hostinfo = parsed.netloc.rsplit('@', 1)
    if ':' not in userinfo:
        return uri

    user, password = userinfo.split(':', 1)
    user = quote_plus(unquote_plus(user))
    password = quote_plus(unquote_plus(password))
    normalized_netloc = f"{user}:{password}@{hostinfo}"
    return urlunsplit((parsed.scheme, normalized_netloc, parsed.path, parsed.query, parsed.fragment))

if MONGO_URI:
    MONGO_URI = normalize_mongo_uri(MONGO_URI)
else:
    mongo_user = os.getenv('MONGO_USER', 'placement_user')
    mongo_password = os.getenv('MONGO_PASSWORD', '')
    mongo_host = os.getenv('MONGO_HOST', 'localhost')
    mongo_port = os.getenv('MONGO_PORT', '27017')

    if mongo_password:
        encoded_password = quote_plus(mongo_password)
        MONGO_URI = f'mongodb+srv://{mongo_user}:{encoded_password}@{mongo_host}/?retryWrites=true&w=majority'
    else:
        MONGO_URI = f'mongodb://{mongo_host}:{mongo_port}'

DB_NAME = 'placement_system'

def get_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db

def get_fs():
    db = get_db()
    return gridfs.GridFS(db)

