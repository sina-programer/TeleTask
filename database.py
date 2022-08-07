import configparser
import peewee as pw

config = configparser.ConfigParser()
config.read('config.ini')


db = pw.SqliteDatabase(config['Database']['path'])
db.connect()


class Base(pw.Model):

    @classmethod
    def get_fields(cls):
        return list(cls._meta.fields.keys())

    class Meta:
        database = db


class User(Base):
    telegram_id = pw.CharField(unique=True, null=True)
    username = pw.CharField(null=True)
    phone_number = pw.CharField()
    authenticated = pw.BooleanField()
    signup_date = pw.DateField()


class Gap(Base):
    telegram_id = pw.CharField(null=True)
    package_id = pw.IntegerField(null=True)
    title = pw.CharField()
    bio = pw.TextField(null=True)
    link = pw.CharField(null=True)
    create_date = pw.DateField()
    is_group = pw.BooleanField()


class Task(Base):
    type = pw.IntegerField()
    status = pw.CharField()
    create_time = pw.DateTimeField()
    done_time = pw.DateTimeField(null=True)


class Member(Base):
    user = pw.ForeignKeyField(User, backref='member')
    gap = pw.ForeignKeyField(Gap, backref='member')
    is_admin = pw.BooleanField()
    task = pw.ForeignKeyField(Task, backref='member')
    add_date = pw.DateField()
    expire_date = pw.DateField(null=True)

class Verify(Base):
    phone_number = pw.CharField()
    code = pw.CharField
    status = pw.CharField()
    task = pw.ForeignKeyField(Task)




TABLES = [User, Gap, Task, Member, Verify]

for table in TABLES:  # Create tables
    not db.table_exists(table.__name__) and db.create_tables([table])
