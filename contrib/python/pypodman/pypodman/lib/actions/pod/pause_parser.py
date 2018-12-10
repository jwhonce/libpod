"""Remote client command for pausing processes in pod."""
import argparse

import podman
from pypodman.lib import AbstractActionBase
from pypodman.lib import query_model as query_pods


class PausePod(AbstractActionBase):
    """Class for pausing containers in pod."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Pause command to parent parser."""
        parser = parent.add_parser('pause', help='pause containers in pod')
        parser.add_flag('--all', '-a', help='Pause all pods.')
        parser.add_argument(
            'pod', nargs=argparse.ZERO_OR_MORE, help='pod(s) to pause.')
        parser.set_defaults(class_=cls, method='pause')

    def __init__(self, args):
        """Construct Pod Pause object."""
        if args.all and args.pod:
            raise ValueError('You may give a pod or use --all, but not both')
        super().__init__(args)

    def pause(self):
        """Pause containers in provided Pod."""
        idents = None if self._args.all else self._args.pod
        pods = query_pods(self.client.pods, idents)

        for pod in pods:
            try:
                pod.pause()
                print(pod.id)
            except podman.PodNotFound as ex:
                self.error('Pod "{}" not found'.format(ex.name))
            except podman.ErrorOccurred as ex:
                self.error('{}'.format(ex.reason).capitalize())
                return 1
        return 0
