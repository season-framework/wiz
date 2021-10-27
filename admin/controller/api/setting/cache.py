import season

class Controller(season.interfaces.wiz.admin.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def list(self, framework):
        res = dict()
        res['deploy_version'] = framework.cache.wiz_deploy_version
        res['prod'] = []
        res['dev'] = []
        res['etc'] = []

        if 'wiz' in framework.cache:
            if 'prod' in framework.cache.wiz:
                for key in framework.cache.wiz['prod']:
                    if key == "routes":
                        continue
                    item = framework.cache.wiz['prod'][key][0]
                    
                    obj = dict()
                    obj['version'] = item['version']
                    obj['version_name'] = item['version_name']
                    obj['namespace'] = item['namespace']
                    obj['id'] = item['id']
                    obj['key'] = key
                    obj['cachetime'] = item['cachetime']
                    res['prod'].append(obj)

            if 'dev' in framework.cache.wiz:
                for key in framework.cache.wiz['dev']:
                    if key == "routes":
                        continue
                    item = framework.cache.wiz['dev'][key][0]
                    obj = dict()
                    obj['version'] = item['version']
                    obj['version_name'] = item['version_name']
                    obj['namespace'] = item['namespace']
                    obj['id'] = item['id']
                    obj['key'] = key
                    obj['cachetime'] = item['cachetime']
                    res['dev'].append(obj)
        
        for key in framework.cache:
            if key in ['wiz', 'wiz_deploy_version']:
                continue
            obj = dict()
            obj['key'] = key
            obj['type'] = type(framework.cache[key])
            res['etc'].append(obj)

        self.status(200, res)