# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
from future.moves import sys

import click

logger = logging.getLogger('sagify')

_ctx = click.get_current_context

LOGGER_KEY = __name__ + '.logger'
DEFAULT_LEVEL = logging.INFO

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode  # noqa
else:
    text_type = str


def _meta():
    return _ctx().meta.setdefault(LOGGER_KEY, {})


class ColorFormatter(logging.Formatter):
    colors = {
        'error': dict(fg='red'),
        'exception': dict(fg='red'),
        'critical': dict(fg='red'),
        'debug': dict(fg='blue'),
        'warning': dict(fg='yellow')
    }

    def format(self, record):
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg
            if level in self.colors:
                prefix = click.style('{}: '.format(level),
                                     **self.colors[level])

                if not PY2 and isinstance(msg, bytes):
                    msg = msg.decode(sys.getfilesystemencoding(),
                                     'replace')
                elif not isinstance(msg, (text_type, bytes)):
                    msg = str(msg)
                msg = '\n'.join(prefix + x for x in msg.splitlines())
            return msg
        return logging.Formatter.format(self, record)


class ClickHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname.lower()
            err = level in ('warning', 'error', 'exception', 'critical')
            click.echo(msg, err=err)
        except Exception:
            self.handleError(record)


_default_handler = ClickHandler()
_default_handler.formatter = ColorFormatter()


def _normalize_logger(logger, log_level):
    if not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)

    logger.setLevel(log_level)
    return logger


def configure_logger(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    global logger

    logger = _normalize_logger(logger, log_level)
    logger.handlers = [_default_handler]
    logger.propagate = False
