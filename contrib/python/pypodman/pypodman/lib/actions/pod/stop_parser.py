"""Remote client command for stopping pod and container(s)."""
import argparse

import podman
from pypodman.lib import AbstractActionBase
from pypodman.lib import query_model as query_pods


class StopPod(AbstractActionBase):
    """Class for stopping pod and container(s)."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Stop command to parent parser."""
        parser = parent.add_parser('stop', help='stop pod')
        parser.add_flag('--all', '-a', help='Stop all pods.')
        parser.add_argument(
            'pod',
            nargs=argparse.ZERO_OR_MORE,
            help='Pod to stop. Or, use --all')
        parser.set_defaults(class_=cls, method='stop')

    def __init__(self, args):
        """Contruct StopPod object."""
        if args.all and args.pod:
            raise ValueError('You may give a pod or use --all, not both')
        super().__init__(args)

    def stop(self):
        """Stop pod and container(s)."""
        idents = None if self._args.all else self._args.pod
        pods = query_pods(self.client.pods, idents)

        for pod in pods:
            try:
                pod.stop()
            except podman.ErrorOccurred as ex:
                self.error('{}'.format(ex.reason).capitalize())
                return 1
        return 0
