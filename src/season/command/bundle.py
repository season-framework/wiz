import season
import os
from argh import arg

@arg('--project', default='main', help='project name')
def bundle(project="main"):
    """
    Bundle project for deployment
    
    Usage:
        wiz bundle                     - Bundle default project (main)
        wiz bundle --project=<name>    - Bundle specific project
    
    Creates a deployable bundle in the 'bundle' directory containing:
        - project/<project>/bundle
        - config
        - public
        - plugin
    """
    fs = season.util.fs(os.getcwd())
    
    if fs.exists(os.path.join("public", "app.py")) == False:
        print("Invalid Project path: wiz structure not found in this folder.")
        return
    
    BUNDLE_PATH = os.path.join("project", project, "bundle")
    if fs.isdir(BUNDLE_PATH) == False:
        print(f"Project '{project}' not exists or not built.")
        print("")
        print("Usage:")
        print("  wiz bundle                     - Bundle default project (main)")
        print("  wiz bundle --project=<name>    - Bundle specific project")
        print("")
        print("Note: Make sure to build the project first with 'wiz project build'")
        return

    try:
        print(f"Bundling project '{project}'...")
        fs.remove("bundle")
        fs.makedirs("bundle")
        fs.makedirs("bundle/project/main/bundle")
        fs.makedirs("bundle/config")
        fs.makedirs("bundle/public")
        fs.makedirs("bundle/plugin")

        fs.copy(BUNDLE_PATH, "bundle/project/main/bundle")
        fs.copy("config", "bundle/config")
        fs.copy("public", "bundle/public")
        fs.copy("plugin", "bundle/plugin")
        
        print(f"Project '{project}' bundled successfully to 'bundle' directory.")
    except Exception as e:
        print(f"Bundle failed: {e}")
