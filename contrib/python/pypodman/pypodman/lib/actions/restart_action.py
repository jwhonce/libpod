"""Remote client command for restarting containers."""
import argparse
import logging

import podman
from pypodman.lib import AbstractActionBase, PositiveIntAction


class Restart(AbstractActionBase):
    """Class for Restarting containers."""

    @classmethod
    def subparser(cls, parent):
        """Add Restart command to parent parser."""
        parser = parent.add_parser('restart', help='restart container(s)')
        parser.add_argument(
            '--timeout',
            action=PositiveIntAction,
            default=10,
            help='Timeout to wait before forcibly stopping the container'
            ' (default: %(default)s seconds)')
        parser.add_argument(
            'targets',
            nargs=argparse.ONE_OR_MORE,
            help='container id(s) to restart')
        parser.set_defaults(class_=cls, method='restart')

    def restart(self):
        """Restart container(s)."""
        try:
            for ident in self._args.targets:
                try:
                    ctnr = self.client.containers.get(ident)
                    logging.debug('Restarting Container "%s"', ctnr.id)
                    ctnr.restart(timeout=self._args.timeout)
                    print(ident)
                except podman.ContainerNotFound as e:
                    self.error('Container "{}" not found.'.format(e.name))
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
