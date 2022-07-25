import configparser
import peewee as pw

config = configparser.ConfigParser()
config.read('config.ini')


db = pw.SqliteDatabase(config['Database']['path'])
db.connect()


class Gap(pw.Model):
    code = pw.CharField(unique=True)  # the unique code to detect different queries
    username = pw.CharField()
    phone_number = pw.CharField()
    task_type = pw.IntegerField()
    title = pw.CharField()
    bio = pw.TextField()
    id = pw.CharField()  # final created id of gap
    link = pw.CharField()
    status = pw.CharField()
    datetime = pw.DateTimeField()  # created time

    class Meta:
        database = db



TABLES = [Gap]

for table in TABLES:  # Create tables
    not db.table_exists(table.__name__) and db.create_tables([table])