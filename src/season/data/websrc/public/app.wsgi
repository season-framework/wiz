import os
import sys
PATH_PUBLIC = os.path.dirname(__file__)
sys.path.insert(0, PATH_PUBLIC)
from app import app as application