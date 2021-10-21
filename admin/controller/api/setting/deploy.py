import season
import datetime
import json
import urllib

class Controller(season.interfaces.wiz.admin.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def restore(self, framework):
        version_name = framework.request.query("version_name", True)
        version_message = framework.request.query("version_message", "")
        version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        rows = framework.request.query("data", True)
        rows = json.loads(rows)

        for row in rows:
            row['version'] = version
            row['version_name'] = version_name
            row['version_message'] = version_message
            del row['updated']
            self.wiz.upsert(row)

        self.wiz.flush()
        self.wiz.deploy_version(version)

        self.status(200, True)

    def backup(self, framework):
        version = framework.request.query("version", True)
        version_name = framework.request.query("version_name", True)
        version_name = urllib.parse.quote(version_name)

        rows = self.wiz.rows(version=version)
        framework.response.headers.load({'Content-Disposition': f'attachment;filename=backup-{version_name}.wiz'})
        framework.response.set_mimetype('application/json')
        framework.response.send(json.dumps(rows, default=self.json_default))

    def list(self, framework):
        deploy_version = self.wiz.deploy_version()
        rows = self.wiz.rows(groupby="version", orderby="`version` DESC", fields="version,version_message,created,updated,version_name,count(*) AS cnt")
        res = []
        for i in range(len(rows)):
            if rows[i]['cnt'] <= 1:
                continue
            rows[i]['deploy'] = False
            if rows[i]['version'] == deploy_version:
                rows[i]['deploy'] = True
            res.append(rows[i])
            
        self.status(200, res)

    def create(self, framework):
        version_name = framework.request.query("version_name", True)
        version_message = framework.request.query("version_message", "")
        version = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        rows = self.wiz.rows(version="master")
        for i in range(len(rows)):
            row = rows[i]
            row['version'] = version
            row['version_name'] = version_name
            row['version_message'] = version_message
            del row['updated']
            self.wiz.upsert(row)
            
        self.wiz.flush()
        self.wiz.deploy_version(version)
        self.status(200, True)

    def delete(self, framework):
        version = framework.request.query("version", True)
        if version == "master":
            self.status(200, True)
        self.wiz.delete(version=version)
        self.wiz.flush()
        self.status(200, True)

    def version(self, framework):
        version = framework.request.query("version", True)
        self.wiz.deploy_version(version)
        self.status(200, True)