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

import sys

from oslo_config import cfg

from vdibroker.db import api as db_api
from vdibroker import utils

CONF = cfg.CONF


def main():
    CONF(sys.argv[1:], project='vdibroker',
         version="1.0.0")
    utils.setup_logging()

    db_api.db_sync(db_api.get_engine())


if __name__ == "__main__":
    main()
