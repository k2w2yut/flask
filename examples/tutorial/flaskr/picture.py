from werkzeug.exceptions import abort
from flask.cli import with_appcontext
from flask import (
    Blueprint, flash, g, current_app,redirect, render_template, request, url_for
)
from flask_boto3 import Boto3
import os,uuid
from werkzeug.utils import secure_filename
from config import *

boto_flask = Boto3()
bp = Blueprint('picture', __name__)


def encode_filename(filename):
    extension = os.path.splitext(filename)[1]
    uuid_name = uuid.uuid5(uuid.NAMESPACE_OID,secure_filename(filename))
    uuid_time = uuid.uuid1().time_low
    return uuid_name, str(uuid_name) + str(uuid_time) +  extension


def upload_to_s3(file):
    s3 = boto_flask.clients['s3']
    bucket_name = BUCKET_NAME
    uuid_name,encoded_filename = encode_filename(file.filename)
    try:
        extra_args = {"ContentType": file.content_type}
        s3.upload_fileobj(
            file.stream._file,
            bucket_name,
            encoded_filename,
            ExtraArgs=extra_args
        )
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Error: ", e)
        return e

    # s3_bucket_url = 'http://{}.s3.ap-southeast-1.amazonaws.com/'.format(bucket_name)
    # return "{}{}".format(s3_bucket_url, encoded_filename)
    return encoded_filename

def getS3URL(encoded_filename):
    s3 = boto_flask.clients['s3']
    signed_url = s3.generate_presigned_url(
                    ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': encoded_filename
            }
        )
    return signed_url

def init_boto(app):
    boto_flask = Boto3(app)
