"""Remote client command for starting containers."""
import argparse
import sys

import podman
from pypodman.lib import AbstractActionBase, DetachKeyAction


class Start(AbstractActionBase):
    """Class for starting container."""

    @classmethod
    def subparser(cls, parent):
        """Add Start command to parent parser."""
        parser = parent.add_parser('start', help='start container')
        parser.add_flag(
            '--attach', '-a', help="Attach container's STDOUT and STDERR.")
        parser.add_argument('--detach-keys', action=DetachKeyAction)
        parser.add_flag(
            '--interactive', '-i', help="Attach container's STDIN.")
        # TODO: Implement sig-proxy
        parser.add_flag(
            '--sig-proxy', help="Proxy received signals to the process.")
        parser.add_argument(
            'containers',
            nargs=argparse.ONE_OR_MORE,
            help='containers to start',
        )
        parser.set_defaults(class_=cls, method='start')

    def start(self):
        """Start provided containers."""
        stdin = sys.stdin if self.opts['interactive'] else None
        stdout = sys.stdout if self.opts['attach'] else None

        try:
            for ident in self._args.containers:
                try:
                    ctnr = self.client.containers.get(ident)
                    ctnr.attach(
                        eot=self.opts['detach_keys'],
                        stdin=stdin,
                        stdout=stdout)
                    ctnr.start()
                except podman.ContainerNotFound as e:
                    self.error('Container "{}" not found'.format(e.name))
                else:
                    print(ident)
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        return 0
