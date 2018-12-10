"""Remote client command for creating pod."""
import podman
from pypodman.lib import AbstractActionBase


class CreatePod(AbstractActionBase):
    """Implement Create Pod command."""

    @classmethod
    def subparser(cls, parent):
        """Add Pod Create command to parent parser."""
        parser = parent.add_parser('create', help='create pod')
        super().subparser(parser)

        parser.add_argument(
            '--cgroup-parent',
            dest='cgroupparent',
            type=str,
            help='Path to cgroups under which the'
            ' cgroup for the pod will be created.')
        parser.add_flag(
            '--infra',
            default=True,
            help='Create an infra container and associate it with the pod.')
        parser.add_argument(
            '-l',
            '--label',
            dest='labels',
            action='append',
            type=str,
            help='Add metadata to a pod (e.g., --label=com.example.key=value)')
        parser.add_argument(
            '--name', '-n', dest='ident', help='Assign name to the pod')
        parser.add_argument(
            '--share',
            choices=('ipc', 'net', 'pid', 'user', 'uts'),
            help='Comma deliminated list of kernel namespaces to share')

        parser.set_defaults(class_=cls, method='create')

        # TODO: Add golang CLI arguments not included in API.
        # parser.add_argument(
        #     '--infra-command',
        #     default='/pause',
        #     help='Command to run to start the infra container.'
        #     '(default: %(default)s)')
        # parser.add_argument(
        #     '--infra-image',
        #     default='k8s.gcr.io/pause:3.1',
        #     help='Image to create for the infra container.'
        #     '(default: %(default)s)')
        # parser.add_argument(
        #     '--podidfile',
        #     help='Write the pod ID to given file name on remote host')

    def create(self):
        """Create Pod from given options."""
        # config = {
        #     k: self.opts.get(k)
        #     for k in ('ident', 'cgroupparent', 'infra', 'labels', 'share')
        # }
        config = {'labels': {}}
        for key in ('ident', 'cgroupparent', 'infra', 'labels', 'share'):
            if key in self.opts:
                config[key] = self.opts[key]
        print(config)

        try:
            pod = self.client.pods.create(**config)
        except podman.ErrorOccurred as ex:
            self.error('{}'.format(ex.reason).capitalize())
            return 1
        else:
            print(pod.id)
        return 0
