import peewee as pw

orm = wiz.model("portal/season/orm")
base = orm.base()

class Model(base):
    class Meta:
        db_table = 'user'

    id = pw.CharField(max_length=32, primary_key=True)
    email = pw.CharField(max_length=255)
    membership = pw.CharField(max_length=8)
    name = pw.CharField(max_length=192)
    mobile = pw.CharField(max_length=64)
    status = pw.CharField(max_length=8)
    onetimepass = pw.CharField(max_length=16)
    onetimepass_time = pw.DateTimeField()
    password = base.PasswordField()
    profile_image = pw.TextField()
    created = pw.DateTimeField()
    last_access = pw.DateTimeField()
