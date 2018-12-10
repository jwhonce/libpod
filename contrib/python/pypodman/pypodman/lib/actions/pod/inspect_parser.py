"""Remote client command for inspecting pods."""
import argparse
import json

import podman
from pypodman.lib import AbstractActionBase


class InspectPod(AbstractActionBase):
    """Class for reporting on pods and their containers."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Inspect command to parent parser."""
        parser = parent.add_parser(
            'inspect',
            help='configuration and state information about a given pod')
        parser.add_argument(
            'pod', nargs=argparse.ONE_OR_MORE, help='pod(s) to inspect')
        parser.set_defaults(class_=cls, method='inspect')

    def inspect(self):
        """Report on provided pods."""
        output = {}
        try:
            for ident in self._args.pod:
                try:
                    pod = self.client.pods.get(ident)
                except podman.PodNotFound:
                    self.error('Pod "{}" not found.'.format(ident))
                output.update(pod.inspect()._asdict())
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        else:
            print(json.dumps(output, indent=2))
        return 0
