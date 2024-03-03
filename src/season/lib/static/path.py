import os

class Path:
    def __init__(self, root):
        if root is None: root = os.getcwd()
        self.root = root
        self.config = os.path.join(root, "config")
        self.public = os.path.join(root, "public")
        self.ide = os.path.join(root, "ide")
        self.project = os.path.join(root, "project")
