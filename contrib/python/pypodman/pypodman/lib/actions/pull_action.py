"""Remote client command for pulling images."""
import argparse

import podman
from pypodman.lib import AbstractActionBase


class Pull(AbstractActionBase):
    """Class for retrieving images from repository."""

    @classmethod
    def subparser(cls, parent):
        """Add Pull command to parent parser."""
        parser = parent.add_parser(
            'pull',
            help='retrieve image from repository',
        )
        parser.add_argument(
            'targets',
            nargs=argparse.ZERO_OR_MORE,
            help='image id(s) to retrieve.',
        )
        parser.set_defaults(class_=cls, method='pull')

    def pull(self):
        """Retrieve image."""
        for ident in self._args.targets:
            try:
                self.client.images.pull(ident)
                print(ident)
            except podman.ImageNotFound as e:
                self.error('Image {} not found.'.format(e.name))
            except podman.ErrorOccurred as e:
                self.error('{}'.format(e.reason).capitalize())
