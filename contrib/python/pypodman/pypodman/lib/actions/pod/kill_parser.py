"""Remote client command for signaling pods and their containers."""
import argparse

import podman
from pypodman.lib import AbstractActionBase, SignalAction
from pypodman.lib import query_model as query_pods


class KillPod(AbstractActionBase):
    """Class for sending signal to processes in pod."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Kill command to parent parser."""
        parser = parent.add_parser('kill', help='signal containers in pod')

        parser.add_flag('--all', '-a', help='Sends signal to all pods.')
        parser.add_argument(
            '-s',
            '--signal',
            action=SignalAction,
            default=9,
            help='Signal to send to the pod. (default: %(default)s)')
        parser.add_argument(
            'pod', nargs=argparse.ZERO_OR_MORE, help='pod(s) to signal')
        parser.set_defaults(class_=cls, method='kill')

    def __init__(self, args):
        """Construct Pod Kill object."""
        if args.all and args.pod:
            raise ValueError('You may give a pod or use --all, but not both')
        super().__init__(args)

    def kill(self):
        """Signal provided pods."""
        idents = None if self._args.all else self._args.pod
        pods = [p for p in query_pods(self.client.pods, idents) if p.running]

        try:
            for pod in pods:
                pod.kill(self._args.signal)
                print(pod.id)
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        return 0
