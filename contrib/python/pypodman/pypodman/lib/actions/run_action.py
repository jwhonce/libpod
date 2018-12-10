"""Remote client command for run a command in a new container."""
import logging

import podman
from pypodman.lib import AbstractActionBase

from ._create_args import CreateArguments


class Run(AbstractActionBase):
    """Class for running a command in a container."""

    @classmethod
    def subparser(cls, parent):
        """Add Run command to parent parser."""
        parser = parent.add_parser('run', help='Run container from image')

        CreateArguments.add_arguments(parser)

        parser.add_argument('image', nargs=1, help='source image id.')
        parser.add_argument(
            'command',
            nargs=parent.REMAINDER,
            help='command and args to run.',
        )
        parser.set_defaults(class_=cls, method='run')

    def __init__(self, args):
        """Construct Run class."""
        super().__init__(args)
        if args.detach and args.rm:
            raise ValueError('Incompatible options: --detach and --rm')

        # image id used only on client
        del self.opts['image']

    def run(self):
        """Run container."""
        self.opts['tty'] = True
        self.opts['detach'] = True
        print(self.opts['command'])

        for ident in self._args.image:
            try:
                try:
                    self.client.images.pull(ident)
                    logging.debug('Pulled image "%s"', ident)
                    img = self.client.images.get(ident)
                    logging.debug('Got image "%s"', ident)
                    ctnr = img.container(**self.opts)
                    logging.debug('Created container "%s"', ctnr.id)
                except podman.ImageNotFound as e:
                    self.error('Image "{}" not found.'.format(e.name))
                    continue

                if not self._args.detach:
                    ctnr.attach(eot=self.opts['detach_keys'])
                    logging.debug('Attached container "%s"', ctnr.id)

                ctnr.start()
                logging.debug('Started container "%s"', ctnr.id)
                print(ctnr.id)

                if self._args.rm:
                    ctnr.remove(force=True)
                    logging.debug('Removed container "%s"', ctnr.id)
            except (BrokenPipeError, KeyboardInterrupt):
                print('\nContainer "{}" disconnected.'.format(ctnr.id))
            except podman.ErrorOccurred as e:
                self.error('Run for container "{}" failed: {} {}'.format(
                    ctnr.id, repr(e), e.reason.capitalize()))
