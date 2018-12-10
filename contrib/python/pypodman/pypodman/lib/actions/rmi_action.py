"""Remote client command for deleting images."""
import argparse

import podman
from pypodman.lib import AbstractActionBase


class Rmi(AbstractActionBase):
    """Class for removing images from storage."""

    @classmethod
    def subparser(cls, parent):
        """Add Rmi command to parent parser."""
        parser = parent.add_parser('rmi', help='delete image(s)')
        parser.add_flag(
            '--force',
            '-f',
            help='force delete of image(s) and associated containers.')
        parser.add_argument(
            'targets',
            nargs=argparse.ONE_OR_MORE,
            help='image id(s) to delete')
        parser.set_defaults(class_=cls, method='remove')

    def remove(self):
        """Remove image(s)."""
        for ident in self._args.targets:
            try:
                img = self.client.images.get(ident)
                img.remove(self._args.force)
                print(ident)
            except podman.ImageNotFound as e:
                self.error('Image {} not found.'.format(e.name))
            except podman.ErrorOccurred as e:
                self.error('{}'.format(e.reason).capitalize())
                return 1
        return 0
