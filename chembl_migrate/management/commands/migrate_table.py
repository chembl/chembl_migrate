__author__ = 'mnowotka'

from django.core.management.base import BaseCommand
from django.apps import apps
from optparse import make_option
from django.db.utils import DatabaseError
from django.conf import settings

try:
    EXPORT = settings.MODEL_TO_BE_EXPORTED
except AttributeError:
    EXPORT = 'chembl_migration_model'
try:
    DEFAULT_CHUNK_SIZE = settings.CHUNK_SIZE
except AttributeError:
    DEFAULT_CHUNK_SIZE = 1000

# ----------------------------------------------------------------------------------------------------------------------


class Command(BaseCommand):

# ----------------------------------------------------------------------------------------------------------------------

    def add_arguments(self, parser):
        parser.add_argument('--chunkSize', default=DEFAULT_CHUNK_SIZE, dest='chunk_size',
                            help='How many rows are migrated in single transaction.')
        parser.add_argument('--appLabel', default=EXPORT, dest='app_label',
                            help='Application whose model will be migrated.')
        parser.add_argument('--targetDatabase', dest='targetDatabase', default=None, help='Target database')
        parser.add_argument('--sourceDatabase', dest='sourceDatabase', default=None, help='Source database')
        parser.add_argument('--modelName', dest='modelName', default=None, help='name of the model to migrate')

# -----------------------------------------------------------------------------------------------------------------------

    def handle(self, *args, **options):
        import django.db
        django.db.reset_queries()

        appLabel = options.get('app_label')
        targetDatabase = options.get('targetDatabase')
        sourceDatabase = options.get('sourceDatabase')
        verbosity = int(options.get('verbosity'))
        django.db.connections[targetDatabase].close()
        django.db.connections[sourceDatabase].close()
        model_name = options.get('modelName')
        model = apps.get_model(appLabel, model_name)
        print "migrating " + model_name + '...'
        migrated = False
        size = options.get('chunk_size')
        while not migrated:
            if size < 1:
                print "Couldn't migrate %s using all sensible values of chunk size. Leaving model %s not migrated" % \
                      (model_name, model_name)
                break
            try:
                self.migrate(model, targetDatabase, sourceDatabase, size, verbosity)
                migrated = True
            except DatabaseError as e:
                if django.db.connections[targetDatabase].vendor == 'mysql' and 'MySQL server has gone away' in str(e):
                    size /= 2
                    print "Migration of %s failed. Retrying with reduced chunk size = %s" % (model_name, size)
                else:
                    print "Migration of %s failed due to database error: %s" % (model_name, str(e))
                    break
            except Exception as e:
                print "Migration of %s failed with unexpected error %s" % (model_name, str(e))
                break
        print model_name + ' migration finished (migrated = %s).' % str(migrated)

# ----------------------------------------------------------------------------------------------------------------------

    def migrate(self, model, target_db, source_db='default', size=1000, verbosity=1):
        from django.db import transaction
        import django.db.utils
        import random
        import sys

        count = model.objects.using(source_db).count()
        targetCount = model.objects.using(target_db).count()
        conn = django.db.connections[target_db]
        transaction.set_autocommit(False)

        if count == targetCount:
            print model.__name__ + " is already exported."
            return
        if verbosity > 1:
            print "source count = " + str(count) + ", target count = " + str(targetCount)
        pk = model._meta.pk.name
        start = targetCount - 1

        if verbosity > 1:
            letter = model.__name__[0]
            color = "\033[1;%dm" % (30 + random.randint(0,7))

        last_pk = None
        for i in range(start, count, size):
            if verbosity > 1:
                sys.stdout.write("\033[0m%s%s\033[0m" % (color, letter))
                sys.stdout.flush()
            with conn.constraint_checks_disabled():

                if i < 0:
                    original_data = model.objects.using(source_db).order_by(pk)[:size]
                else:
                    if not last_pk:
                        last_pk = model.objects.using(source_db).order_by(pk).only(pk).values_list(pk)[i][0]
                    original_data = model.objects.using(source_db).filter(pk__gt=last_pk).order_by(pk)[:size]
                actual_size = len(original_data)
                last_pk = original_data[actual_size-1].pk

                model.objects.using(target_db).bulk_create(original_data)

            django.db.transaction.commit(using=target_db)

# ----------------------------------------------------------------------------------------------------------------------
