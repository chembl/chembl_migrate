__author__ = 'mnowotka'


from django.core.management.commands.sqlcustom import Command
from django.core.management.sql import sql_custom
from django.core.management.color import no_style
from django.db import connections
from django.db import transaction

#-----------------------------------------------------------------------------------------------------------------------

class Command(Command):
    def handle_app(self, app, **options):
        db = options.get('database')
        verbosity = int(options.get('verbosity'))
        conn = connections[db]
        cursor = conn.cursor()
        custom_sql = sql_custom(app, no_style(), conn)
        for sql in custom_sql:
            if verbosity >= 1:
                print "executing SQL: %s" % sql
            cursor.execute(sql)

#-----------------------------------------------------------------------------------------------------------------------