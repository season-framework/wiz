import os
import season
import peewee as pw
import bcrypt
import json
import datetime

def Model(namespace):
    class DBModel(pw.Model):
        class Meta:
            config = wiz.config("database").get(namespace)
            if config.type == 'mysql':
                opts = dict()
                for key in ['host', 'user', 'password', 'charset', 'port']:
                    if key in config:
                        opts[key] = config[key]
                database = pw.MySQLDatabase(config.database, **opts)
            else:
                sqlitedb = os.path.realpath(os.path.join(wiz.server.path.root, config.path))
                database = pw.SqliteDatabase(sqlitedb)

        class PasswordField(pw.TextField):
            def db_value(self, value):
                if value is None:
                    return value
                value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                return value

            def python_value(self, value):
                if value is None:
                    return None
                value = value.encode('utf-8')
                def check_password(password):
                    password = password.encode('utf-8')
                    return bcrypt.checkpw(password, value)
                return check_password

        class DateField(pw.DateField):
            def python_value(self, value):
                try:
                    return datetime.datetime.combine(value, datetime.datetime.min.time())
                except Exception as e:
                    pass
                return value

        class TextField(pw.TextField):
            field_type = 'LONGTEXT'

        class JSONArray(pw.TextField):
            field_type = 'LONGTEXT'

            def db_value(self, value):
                return json.dumps(value)

            def python_value(self, value):
                try:
                    if value is not None:
                        return json.loads(value)
                except Exception as e:
                    pass
                return []

        class JSONObject(pw.TextField):
            field_type = 'LONGTEXT'

            def db_value(self, value):
                return json.dumps(value)

            def python_value(self, value):
                try:
                    if value is not None:
                        return json.loads(value)
                except Exception as e:
                    pass
                return {}
    
    return DBModel