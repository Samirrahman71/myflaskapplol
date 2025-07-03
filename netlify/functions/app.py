import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from app import app

def handler(event, context):
    return app(event, context)
