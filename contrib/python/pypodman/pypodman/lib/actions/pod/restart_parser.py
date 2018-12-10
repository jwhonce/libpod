"""Remote client command for restarting pod and container(s)."""
import argparse

import podman
from pypodman.lib import AbstractActionBase
from pypodman.lib import query_model as query_pods


class RestartPod(AbstractActionBase):
    """Class for restarting containers in Pod."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Restart command to parent parser."""
        parser = parent.add_parser('restart', help='restart containers in pod')
        parser.add_flag('--all', '-a', help='Restart all pods.')
        parser.add_argument(
            'pod',
            nargs=argparse.ZERO_OR_MORE,
            help='Pod(s) to restart. Or, use --all')
        parser.set_defaults(class_=cls, method='restart')

    def __init__(self, args):
        """Construct RestartPod object."""
        if args.all and args.pod:
            raise ValueError('You may give a pod or use --all, not both')
        super().__init__(args)

    def restart(self):
        """Restart pod and container(s)."""
        idents = None if self._args.all else self._args.pod
        pods = query_pods(self.client.pods, idents)

        for pod in pods:
            try:
                pod.restart()
                print(pod.id)
            except podman.PodNotFound as ex:
                self.error('Pod "{}" not found.'.format(ex.name))
            except podman.ErrorOccurred as ex:
                self.error('{}'.format(ex.reason).capitalize())
                return 1
        return 0
