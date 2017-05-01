# Copyright 2017 Cloudbase Solutions, SRL.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo_config import cfg
from oslo_db import api as db_api
from oslo_db import options as db_options
from oslo_db.sqlalchemy import enginefacade

from vdibroker.db.sqlalchemy import models
from vdibroker import exception

CONF = cfg.CONF
db_options.set_defaults(CONF)


_BACKEND_MAPPING = {'sqlalchemy': 'vdibroker.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(CONF, backend_mapping=_BACKEND_MAPPING)


def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()


def db_sync(engine, version=None):
    """Migrate the database to `version` or the most recent version."""
    return IMPL.db_sync(engine, version=version)


def db_version(engine):
    """Display the current database version."""
    return IMPL.db_version(engine)


def _session(context):
    return (context and context.session) or get_session()


def _model_query(context, *args):
    session = _session(context)
    return session.query(*args)


def _soft_delete_aware_query(context, *args, **kwargs):
    """Query helper that accounts for context's `show_deleted` field.
    :param show_deleted: if True, overrides context's show_deleted field.
    """
    query = _model_query(context, *args)
    show_deleted = kwargs.get('show_deleted') or context.show_deleted

    if not show_deleted:
        query = query.filter_by(deleted_at=None)
    return query


@enginefacade.reader
def get_applications(context):
    q = _soft_delete_aware_query(context, models.Application)
    return q.filter(
        models.Application.project_id == context.tenant).all()


@enginefacade.reader
def get_application(context, application_id):
    q = _soft_delete_aware_query(context, models.Application)
    return q.filter(
        models.Application.project_id == context.tenant,
        models.Application.id == application_id).first()


@enginefacade.writer
def add_application(context, application):
    application.user_id = context.user
    application.project_id = context.tenant
    context.session.add(application)


@enginefacade.writer
def delete_application(context, application_id):
    count = _soft_delete_aware_query(context, models.Application).filter_by(
        project_id=context.tenant, id=application_id).soft_delete()
    if count == 0:
        raise exception.NotFound("0 entries were soft deleted")


@enginefacade.writer
def add_remote_session(context, remote_session):
    remote_session.user_id = context.user
    remote_session.project_id = context.tenant
    context.session.add(remote_session)


@enginefacade.reader
def get_remote_session(context, session_id):
    q = _soft_delete_aware_query(context, models.RemoteSession)
    return q.filter(
        models.RemoteSession.project_id == context.tenant,
        models.RemoteSession.id == session_id).first()


@enginefacade.reader
def get_remote_sessions(context, application_id):
    q = _soft_delete_aware_query(context, models.RemoteSession)
    return q.filter(
        models.RemoteSession.project_id == context.tenant,
        models.RemoteSession.application_id == application_id).all()


@enginefacade.writer
def delete_remote_session(context, session_id):
    count = _soft_delete_aware_query(context, models.RemoteSession).filter_by(
        project_id=context.tenant, id=session_id).soft_delete()
    if count == 0:
        raise exception.NotFound("0 entries were soft deleted")
