# -*- coding: utf-8 -*-
# pylint: disable=C,R,W
"""Defines the templating context for SQL Lab"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime, timedelta
import inspect
import json
import random
import time
import uuid

from dateutil.relativedelta import relativedelta
from flask import g, request
from jinja2.sandbox import SandboxedEnvironment

from superset import app

config = app.config
BASE_CONTEXT = {
    'datetime': datetime,
    'random': random,
    'relativedelta': relativedelta,
    'time': time,
    'timedelta': timedelta,
    'uuid': uuid,
}
BASE_CONTEXT.update(config.get('JINJA_CONTEXT_ADDONS', {}))


def url_param(param, default=None):
    """Get a url or post data parameter

    :param param: the parameter to lookup
    :type param: str
    :param default: the value to return in the absence of the parameter
    :type default: str
    """
    if request.args.get(param):
        return request.args.get(param, default)
    # Supporting POST as well as get
    if request.form.get('form_data'):
        form_data = json.loads(request.form.get('form_data'))
        url_params = form_data['url_params'] or {}
        return url_params.get(param, default)
    return default


def current_user_id():
    """The id of the user who is currently logged in"""
    if hasattr(g, 'user') and g.user:
        return g.user.id


def current_username():
    """The username of the user who is currently logged in"""
    if g.user:
        return g.user.username

def get_filters_by_rol():
    """Return  SQL Where conditions  by ROL """
    """Credits: Everis Mexico"""
    """
        one rol found will return           : [condition sql]
        two roles or more  found will return: [condition sql] and [condition sql]
        no rol found wll return             : [0 = 0]
    """

    filters = { }
    filters['test_cordoba_1']                 = " centro = 'Hospital Cordoba' "
    filters['test_cordoba_uti_rol']           = " centro = 'Hospital Cordoba' and servicio = 'UTI' and seccion='UTI' "
    filters['Gestor clinico de Servicio CBA'] = " ODS_LK_CENTER_PARQUET.DES_CENTER_LONG = 'Hospital Cordoba' and  ODS_LK_SECTION_PARQUEt.DES_SECTION_LONG = 'UTI' and ODS_LK_SERVICE_PARQUET.DES_SERVICE_LONG='UTI' "

    #filters['GESTOR RED SANITARIA'] = ''
    #filters['Rol_validador'] = ''
    #filters['Admin'] = '1 = 1'
    #filters['Admin copy'] = '1 = 1'
    

    filters_found = []
    for role in g.user.roles:
        for key, value in filters.items():
            if key == str(role):
                filters_found.append(value)

    if not len(filters_found):
	    filters_found.append(' 0 = 0 ')

    return ' and '.join(filters_found)


class BaseTemplateProcessor(object):


    """Base class for database-specific jinja context

    There's this bit of magic in ``process_template`` that instantiates only
    the database context for the active database as a ``models.Database``
    object binds it to the context object, so that object methods
    have access to
    that context. This way, {{ hive.latest_partition('mytable') }} just
    knows about the database it is operating in.

    This means that object methods are only available for the active database
    and are given access to the ``models.Database`` object and schema
    name. For globally available methods use ``@classmethod``.
    """
    engine = None


   
    def __init__(self, database=None, query=None, table=None, **kwargs):
        self.database = database
        self.query = query
        self.schema = None
        if query and query.schema:
            self.schema = query.schema
        elif table:
            self.schema = table.schema
        self.context = {
            'url_param': url_param,
            'current_user_id': current_user_id,
            'current_username': current_username,
            'form_data': {},
            'user': g.user
            ,'filters_by_rol':get_filters_by_rol
        }
        
        self.context.update(kwargs)
        self.context.update(BASE_CONTEXT)

        if self.engine:
            self.context[self.engine] = self
        self.env = SandboxedEnvironment()

    def process_template(self, sql, **kwargs):
        """Processes a sql template

        >>> sql = "SELECT '{{ datetime(2017, 1, 1).isoformat() }}'"
        >>> process_template(sql)
        "SELECT '2017-01-01T00:00:00'"
        """
        template = self.env.from_string(sql)
        kwargs.update(self.context)
        return template.render(kwargs)


class PrestoTemplateProcessor(BaseTemplateProcessor):
    """Presto Jinja context

    The methods described here are namespaced under ``presto`` in the
    jinja context as in ``SELECT '{{ presto.some_macro_call() }}'``
    """
    engine = 'presto'

    @staticmethod
    def _schema_table(table_name, schema):
        if '.' in table_name:
            schema, table_name = table_name.split('.')
        return table_name, schema

    def latest_partition(self, table_name):
        table_name, schema = self._schema_table(table_name, self.schema)
        return self.database.db_engine_spec.latest_partition(
            table_name, schema, self.database)[1]

    def latest_sub_partition(self, table_name, **kwargs):
        table_name, schema = self._schema_table(table_name, self.schema)
        return self.database.db_engine_spec.latest_sub_partition(
            table_name=table_name,
            schema=schema,
            database=self.database,
            **kwargs)


class HiveTemplateProcessor(PrestoTemplateProcessor):
    engine = 'hive'


template_processors = {}
keys = tuple(globals().keys())
for k in keys:
    o = globals()[k]
    if o and inspect.isclass(o) and issubclass(o, BaseTemplateProcessor):
        template_processors[o.engine] = o


def get_template_processor(database, table=None, query=None, **kwargs):
    TP = template_processors.get(database.backend, BaseTemplateProcessor)
    return TP(database=database, table=table, query=query, **kwargs)
