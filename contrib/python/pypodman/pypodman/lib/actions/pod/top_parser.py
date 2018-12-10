"""Remote client command for reporting on pod and container(s)."""
import podman
from pypodman.lib import AbstractActionBase


class TopPod(AbstractActionBase):
    """Report on containers in Pod."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Top command to parent parser."""
        parser = parent.add_parser('top', help='report on containers in pod')
        parser.add_argument('pod', nargs=1, help='Pod to report on.')
        parser.set_defaults(class_=cls, method='top')

    def top(self):
        """Report on pod and container(s)."""
        try:
            for ident in self._args.pod:
                pod = self.client.pods.get(ident)
                print(pod.top())
        except podman.PodNotFound as ex:
            self.error('Pod "{}" not found.'.format(ex.name))
        except podman.ErrorOccurred as ex:
            self.error('{}'.format(ex.reason).capitalize())
            return 1
        return 0
