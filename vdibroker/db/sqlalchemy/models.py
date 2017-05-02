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

import uuid

from oslo_db.sqlalchemy import models
import sqlalchemy
from sqlalchemy.ext import declarative
from sqlalchemy import orm

from vdibroker.db.sqlalchemy import types

BASE = declarative.declarative_base()


class RemoteSession(BASE, models.TimestampMixin, models.SoftDeleteMixin,
                    models.ModelBase):
    __tablename__ = 'session'

    id = sqlalchemy.Column(sqlalchemy.String(36),
                           default=lambda: str(uuid.uuid4()),
                           primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    project_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    instance_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    connection_data = sqlalchemy.Column(types.Json, nullable=False)
    application_id = sqlalchemy.Column(
        sqlalchemy.String(36),
        sqlalchemy.ForeignKey('application.id'), nullable=False)


class Application(BASE, models.TimestampMixin, models.SoftDeleteMixin,
                  models.ModelBase):
    __tablename__ = 'application'

    id = sqlalchemy.Column(sqlalchemy.String(36),
                           default=lambda: str(uuid.uuid4()),
                           primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    project_id = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    type = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String(1024), nullable=True)
    image_data = sqlalchemy.Column(types.Json, nullable=False)
    pool_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    instances_data = sqlalchemy.Column(types.List, nullable=False)
    sessions = orm.relationship(RemoteSession, cascade="all,delete",
                                backref=orm.backref('application'),
                                primaryjoin="and_(RemoteSession."
                                "application_id==Application.id, "
                                "Application.deleted=='0')")
