"""Remote client command for signaling podman containers."""
import argparse

import podman
from pypodman.lib import AbstractActionBase, SignalAction
from pypodman.lib import query_model as query_containers


class Kill(AbstractActionBase):
    """Class for sending signal to main process in container."""

    @classmethod
    def subparser(cls, parent):
        """Add Kill command to parent parser."""
        parser = parent.add_parser('kill', help='signal container')

        parser.add_flag('--all', '-a', help='Signal all containers')
        parser.add_argument(
            '--signal',
            '-s',
            action=SignalAction,
            default=9,
            help='Signal to send to the container. (default: %(default)s)')
        parser.add_argument(
            'container',
            nargs=argparse.ZERO_OR_MORE,
            help='container(s) to signal',
        )
        parser.set_defaults(class_=cls, method='kill')

    def __init__(self, args):
        """Construct Kill parser."""
        if args.all and args.container:
            raise ValueError(
                'You may give container(s) or use --all, but not both')
        super().__init__(args)

    def kill(self):
        """Signal provided containers."""
        idents = None if self._args.all else self._args.container
        containers = [
            c for c in query_containers(self.client.containers, idents)
            if c.running
        ]

        try:
            for ctnr in containers:
                ctnr.kill(self._args.signal)
                print(ctnr.id)
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        return 0
