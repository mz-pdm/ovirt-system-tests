# Copyright 2017 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
#
import logging
import os
import pytest
import shutil

from lago import sdk as lagosdk

from repo_server import create_repo_server

from fixtures.cluster import default_cluster  # NOQA: F401

from fixtures.network import ovirtmgmt_network  # NOQA: F401

from fixtures.host import host_0  # NOQA: F401
from fixtures.host import host_1  # NOQA: F401

from fixtures.engine import engine  # NOQA: F401
from fixtures.engine import api  # NOQA: F401

from fixtures.storage import storage_domains_service  # NOQA: F401
from fixtures.storage import default_storage_domain  # NOQA: F401

from fixtures.data_center import data_centers_service  # NOQA: F401
from fixtures.data_center import default_data_center  # NOQA: F401

from fixtures.system import system  # NOQA: F401


def pytest_addoption(parser):
    parser.addoption('--lago-env', action='store')
    parser.addoption('--artifacts-path', action='store')


@pytest.fixture(scope='session')
def artifacts_path():
    p = pytest.config.getoption(
        '--artifacts-path',
        default='exported_artifacts'
    )
    if os.path.isdir(p):
        shutil.rmtree(p)

    os.makedirs(p)

    return p


@pytest.fixture(scope='session')
def env(artifacts_path):
    workdir = pytest.config.getoption('--lago-env')
    lago_log_path = os.path.join(workdir, 'default/logs/lago.log')
    lago_env = lagosdk.load_env(
        workdir=workdir,
        logfile=lago_log_path,
        loglevel=logging.DEBUG
    )

    lago_env.start()

    # TODO: once a proper solution for repo server w/o OST lago plugin
    # is available, remove this hack and use it instead.
    try:
        repo_server = create_repo_server(workdir, lago_env)
        yield lago_env
    finally:
        repo_server.shutdown()
        shutil.move(lago_log_path, artifacts_path)
        lago_env.destroy()


@pytest.fixture(scope='module', autouse=True)
def collect_artifacts(env, artifacts_path, request):
    yield
    p = os.path.join(artifacts_path, request.module.__name__)
    os.makedirs(p)
    env.collect_artifacts(output_dir=p, ignore_nopath=True)
