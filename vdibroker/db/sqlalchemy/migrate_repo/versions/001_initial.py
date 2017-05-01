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

import sqlalchemy


def upgrade(migrate_engine):
    meta = sqlalchemy.MetaData()
    meta.bind = migrate_engine

    application = sqlalchemy.Table(
        'application', meta,
        sqlalchemy.Column("id", sqlalchemy.String(36), primary_key=True,
                          default=lambda: str(uuid.uuid4())),
        sqlalchemy.Column('created_at', sqlalchemy.DateTime),
        sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted_at', sqlalchemy.DateTime),
        sqlalchemy.Column('deleted', sqlalchemy.String(36)),
        sqlalchemy.Column("user_id", sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column("project_id", sqlalchemy.String(255),
                          nullable=False),
        sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
        sqlalchemy.Column("description", sqlalchemy.String(1024),
                          nullable=True),
        sqlalchemy.Column("image_id", sqlalchemy.String(255),
                          nullable=False),
        sqlalchemy.Column("type", sqlalchemy.Integer, nullable=False),
        sqlalchemy.Column("pool_size", sqlalchemy.Integer, nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8'
    )

    tables = (
        application,
    )

    for index, table in enumerate(tables):
        try:
            table.create()
        except Exception:
            # If an error occurs, drop all tables created so far to return
            # to the previously existing state.
            meta.drop_all(tables=tables[:index])
            raise
