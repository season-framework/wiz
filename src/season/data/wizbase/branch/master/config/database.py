from season import stdClass

config = stdClass()

config.mysql = stdClass()
config.mysql.host = '127.0.0.1'
config.mysql.user = 'dbuser'
config.mysql.password = 'dbpass'
config.mysql.database = 'dbname'
config.mysql.charset = 'utf8'