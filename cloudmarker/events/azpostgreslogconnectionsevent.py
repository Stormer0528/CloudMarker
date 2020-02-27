"""Microsoft Azure Postgres Log Connections event.

This module defines the :class:`AzPostgresLogConnectionsEvent` class
that identifies Postgre SQL servers which log connections configuration
disabled. This plugin works on the  properties found in the ``com``
bucket of ``postgresql_server`` records.
"""


import logging

from cloudmarker import util

_log = logging.getLogger(__name__)


class AzPostgresLogConnectionsEvent:
    """Az Postgres log connections event plugin."""

    def __init__(self):
        """Create an instance of :class:`AzPostgresLogConnectionsEvent`."""

    def eval(self, record):
        """Evaluate Postgres for log connections.

        Arguments:
            record (dict): An RDBMS record.

        Yields:
            dict: An event record representing a Postgres where
            log connections is disabled

        """
        com = record.get('com', {})
        if com is None:
            return

        if com.get('cloud_type') != 'azure':
            return

        if com.get('record_type') != 'rdbms':
            return

        ext = record.get('ext', {})
        if ext is None:
            return

        if ext.get('record_type') != 'postgresql_server':
            return

        # True, None, missing key or any other value will not
        # genarated an event. An event will be generated only if
        # the value of `postgresql_server` is False.
        if ext.get('log_connections_enabled') is False:
            yield from _get_postgres_log_connections_disabled_event(
                com, ext)

    def done(self):
        """Perform cleanup work.

        Currently, this method does nothing. This may change in future.
        """


def _get_postgres_log_connections_disabled_event(com, ext):
    """Generate event for Postgres log connections disabled.

    Arguments:
        com (dict): Postgres record `com` bucket
        ext (dict): Postgres record `ext` bucket
    Returns:
        dict: An event record representing Postgres server
        with log connections disabled

    """
    friendly_cloud_type = util.friendly_string(com.get('cloud_type'))
    friendly_rdbms_type = util.friendly_string(ext.get('record_type'))

    reference = com.get('reference')
    description = (
        '{} {} {} has log connections disabled.'
        .format(friendly_cloud_type, friendly_rdbms_type, reference)
    )
    recommendation = (
        'Check {} {} {} and enable log connections.'
        .format(friendly_cloud_type, friendly_rdbms_type, reference)
    )

    event_record = {
        # Preserve the extended properties from the RDBMS
        # record because they provide useful context to
        # locate the RDBMS that led to the event.
        'ext': util.merge_dicts(ext, {
            'record_type': 'postgres_log_connections_event'
        }),
        'com': {
            'cloud_type': com.get('cloud_type'),
            'record_type': 'postgres_log_connections_event',
            'reference': reference,
            'description': description,
            'recommendation': recommendation,
        }
    }

    _log.info('Generating postgres_log_connections_event; %r', event_record)
    yield event_record
