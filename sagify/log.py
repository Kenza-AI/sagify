# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

logger = logging.getLogger('sagify')


def configure_logger(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format='%(message)s', level=log_level)
