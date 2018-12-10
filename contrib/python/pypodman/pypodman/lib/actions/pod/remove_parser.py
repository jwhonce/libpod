"""Remote client command for deleting pod and containers."""
import argparse

import podman
from pypodman.lib import AbstractActionBase
from pypodman.lib import query_model as query_pods


class RemovePod(AbstractActionBase):
    """Class for removing pod and containers from storage."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Rm command to parent parser."""
        parser = parent.add_parser('rm', help='Delete pod and container(s)')
        parser.add_flag('--all', '-a', help='Remove all pods.')
        parser.add_flag(
            '--force',
            '-f',
            help='Stop and remove container(s) then delete pod.')
        parser.add_argument(
            'pod',
            nargs=argparse.ZERO_OR_MORE,
            help='Pod to remove. Or, use --all')
        parser.set_defaults(class_=cls, method='remove')

    def __init__(self, args):
        """Construct RemovePod object."""
        if args.all and args.pod:
            raise ValueError('You may give a pod or use --all, but not both')
        super().__init__(args)

    def remove(self):
        """Remove pod and container(s)."""
        idents = None if self._args.all else self._args.pod
        pods = query_pods(self.client.pods, idents)

        for pod in pods:
            try:
                pod.remove(self._args.force)
                print(pod.id)
            except podman.PodNotFound as ex:
                self.error('Pod "{}" not found.'.format(ex.name))
            except podman.ErrorOccurred as ex:
                self.error('{}'.format(ex.reason).capitalize())
                return 1
        return 0
