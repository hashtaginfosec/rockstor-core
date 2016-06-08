"""
Copyright (c) 2012-2013 RockStor, Inc. <http://rockstor.com>
This file is part of RockStor.

RockStor is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published
by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

RockStor is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from storageadmin.exceptions import RockStorAPIException
from system.osi import run_command
from system.pkg_mgmt import rpm_build_info
from django.conf import settings
import traceback
import sys

import logging
logger = logging.getLogger(__name__)

#module level variable so it's computed once per process.
version = 'unknown'
try:
    version, date = rpm_build_info('rockstor')
except Exception, e:
    logger.exception(e)

def handle_exception(e, request, e_msg=None):
    """
    if e_msg is provided, exception is raised with that string. This is useful
    for optionally humanizing the message. Otherwise, error from the exception
    object is used.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if (e_msg is not None):
        e_msg = '%s. Lower level exception: %s' % (e_msg, e.__str__())
        logger.error(e_msg)
    else:
        e_msg = e.__str__()

    logger.error('request path: %s method: %s data: %s' %
                 (request.path, request.method, request.data))
    logger.exception('exception: %s' % e.__str__())
    logger.debug('Current Rockstor version: %s' % version)
    fpath = '%ssrc/rockstor/logs/error.tgz' % settings.ROOT_DIR
    logdir = '%svar/log' % settings.ROOT_DIR
    run_command(['/usr/bin/tar', '-c', '-z', '-f', fpath, logdir], throw=False)
    raise RockStorAPIException(detail=e_msg, trace=traceback.format_tb(exc_traceback))
