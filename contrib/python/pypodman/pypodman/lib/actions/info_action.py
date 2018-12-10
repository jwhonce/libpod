"""Remote client command for reporting on Podman service."""
import json

import yaml

import podman
from pypodman.lib import AbstractActionBase


class Info(AbstractActionBase):
    """Class for reporting on Podman Service."""

    @classmethod
    def subparser(cls, parent):
        """Add Info command to parent parser."""
        parser = parent.add_parser(
            'info', help='report info on podman service')
        parser.add_argument(
            '--format',
            choices=('json', 'yaml'),
            default='yaml',
            help="Alter the output for a format like 'json' or 'yaml'."
            " (default: %(default)s)")
        parser.set_defaults(class_=cls, method='info')

    def info(self):
        """Report on Podman Service."""
        try:
            info = self.client.system.info()
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        else:
            if self._args.format == 'json':
                print(json.dumps(info._asdict(), indent=2), flush=True)
            else:
                print(
                    yaml.dump(
                        dict(info._asdict()),
                        canonical=False,
                        default_flow_style=False),
                    flush=True)
        return 0
