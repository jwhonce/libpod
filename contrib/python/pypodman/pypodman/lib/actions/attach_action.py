"""Remote client command for attaching to a container."""
import podman
from pypodman.lib import AbstractActionBase, DetachKeyAction


class Attach(AbstractActionBase):
    """Class for attaching to a running container."""

    @classmethod
    def subparser(cls, parent):
        """Add Attach command to parent parser."""
        parser = parent.add_parser('attach', help='attach to container')
        parser.add_argument('--detach-keys', action=DetachKeyAction)
        parser.add_flag('--stdin', default=True, help='Attach to STDIN')
        parser.add_flag(
            '--sig-proxy',
            default=True,
            help='proxy received signals to the process')
        parser.add_argument(
            'container', nargs=1, help='Identifier of running container')
        parser.set_defaults(class_=cls, method='attach')

    def attach(self):
        """Attach to instantiated image."""
        ident = self._args.container[0]
        try:
            try:
                ctnr = self.client.containers.get(ident)
            except podman.ContainerNotFound as e:
                self.error('Container {} not found.'.format(e.name))
                return 1
            else:
                if not ctnr.running:
                    self.error('You can only attach to running containers')
                    return 1

            ctnr.attach(eot=self._args.detach_keys)
            try:
                ctnr.start()
                print()
            except (BrokenPipeError, KeyboardInterrupt):
                print('\nContainer disconnected.')
        except podman.ErrorOccurred as e:
            self.error('{}'.format(e.reason).capitalize())
            return 1
        return 0
