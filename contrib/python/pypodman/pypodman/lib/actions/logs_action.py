"""Remote client command for retrieving container logs."""
import logging
import sys
from collections import deque

import podman
from pypodman.lib import AbstractActionBase, PositiveIntAction


class Logs(AbstractActionBase):
    """Class for retrieving logs from container."""

    @classmethod
    def subparser(cls, parent):
        """Add Logs command to parent parser."""
        parser = parent.add_parser('logs', help='retrieve logs from container')
        parser.add_argument(
            '--tail',
            metavar='LINES',
            action=PositiveIntAction,
            help='Output the specified number of LINES at the end of the logs')
        parser.add_argument(
            'container',
            nargs=1,
            help='retrieve container logs',
        )
        parser.set_defaults(class_=cls, method='logs')

    def logs(self):
        """Retrieve logs from containers."""
        try:
            ident = self._args.container[0]
            try:
                logging.debug('Get container "%s" logs', ident)
                ctnr = self.client.containers.get(ident)
            except podman.ContainerNotFound as e:
                self.error('Container "{}" not found'.format(e.name))
            else:
                if self._args.tail:
                    logs = iter(deque(ctnr.logs(), maxlen=self._args.tail))
                else:
                    logs = ctnr.logs()

                for line in logs:
                    sys.stdout.write(line)
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        return 0
