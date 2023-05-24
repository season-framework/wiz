import os
import sys
import platform
import season
from texttable import Texttable
from argh import arg

fs = season.util.os.FileSystem(os.getcwd())

PATH_EXEC = sys.executable
PATH_EXEC_WIZ = os.path.join(os.path.dirname(PATH_EXEC), "wiz")
PATH_ROOT = fs.abspath()

EXEC_SCRIPT = f"""#!/bin/bash
source /root/.bashrc
cd {PATH_ROOT}
{PATH_EXEC_WIZ} run
"""

class ServiceCommand:
     
    def regist(self, serviceName=None):
        if fs.exists(os.path.join("public", "app.py")) == False:
            print("Invalid Project path: wiz structure not found in this folder.")
            return

        if serviceName is None or len(serviceName) == 0:
            print("wiz service regist [Service Name]")
            return
        
        serviceName = "wiz." + serviceName.lower()
        commandPath = f"/usr/local/bin/{serviceName}"
        servicePath = f"/etc/systemd/system/{serviceName}.service"
        
        fs.write(commandPath, EXEC_SCRIPT)
        os.system(f"chmod +x {commandPath}")
        print(f"`{commandPath}` created")

        SERVICE_SCRIPT = f"""[Unit]
Description={serviceName}
After=syslog.target network.target

[Service]
User=root
Environment="PATH=/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
ExecStart={commandPath}

[Install]
WantedBy=multi-user.target
        """

        fs.write(servicePath, SERVICE_SCRIPT)
        print(f"`{servicePath}` created")
        os.system("systemctl daemon-reload")
        os.system(f"systemctl enable {serviceName}")

    def install(self, *args, **kwargs):
        self.regist(*args, **kwargs)

    def unregist(self, serviceName=None):
        print(f"stop service `{serviceName}`...")
        self.stop(serviceName)

        serviceName = "wiz." + serviceName.lower()
        commandPath = f"/usr/local/bin/{serviceName}"
        servicePath = f"/etc/systemd/system/{serviceName}.service"

        print(f"unregist service `{serviceName}`...")
        os.system(f"systemctl disable {serviceName}")

        print(f"delete `{commandPath}`...")
        fs.remove(commandPath)
        print(f"delete `{servicePath}`...")
        fs.remove(servicePath)

        os.system("systemctl daemon-reload")

    def uninstall(self, *args, **kwargs):
        self.unregist(*args, **kwargs)
    
    def remove(self, *args, **kwargs):
        self.unregist(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.unregist(*args, **kwargs)

    def rm(self, *args, **kwargs):
        self.unregist(*args, **kwargs)

    def status(self, serviceName=None):
        serviceName = "wiz." + serviceName.lower()
        os.system(f"systemctl status {serviceName}")
    
    def start(self, serviceName=None):
        serviceName = "wiz." + serviceName.lower()
        os.system(f"systemctl start {serviceName}")
    
    def stop(self, serviceName=None):
        serviceName = "wiz." + serviceName.lower()
        os.system(f"systemctl stop {serviceName}")

    def restart(self, serviceName=None):
        serviceName = "wiz." + serviceName.lower()
        os.system(f"systemctl restart {serviceName}")

    def list(self):
        files = fs.files("/etc/systemd/system")
        services = [['service', 'systemd', 'binary']]
        for target in files:
            if target.startswith("wiz."):
                name = ".".join(target[4:].split(".")[:-1])
                path = f"/etc/systemd/{target}"
                binary = f"/usr/local/bin/wiz.{name}"
                services.append([name, path, binary])
        
        t = Texttable()
        t.add_rows(services)
        print(t.draw())
        
    def __call__(self, name, args):
        fn = getattr(self, name)
        fn(*args)
        
@arg('action', default=None, help="regist | status")
def service(action, *args):
    if platform.system() != 'Linux':
        print("Regist service function only support linux")
        return    
    cmd = ServiceCommand()
    cmd(action, args)