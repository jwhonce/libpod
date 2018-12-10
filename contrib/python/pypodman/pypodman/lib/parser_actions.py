"""
Supplimental argparse.Action converters and validaters.

The constructors are very verbose but remain for IDE support.
"""
import argparse
import copy
import os
import signal

# API defined by argparse.Action therefore shut up pylint
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=too-few-public-methods
# pragma pylint: disable=too-many-arguments


class ChangeAction(argparse.Action):
    """Convert and validate change argument."""

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar='OPT=VALUE'):
        """Create ChangeAction object."""
        help = (help or '') + ('Apply change(s) to the new image.'
                               ' May be given multiple times.')
        if default is None:
            default = []

        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        """Convert and Validate input."""
        items = getattr(namespace, self.dest, None) or []
        items = copy.copy(items)

        choices = ('CMD', 'ENTRYPOINT', 'ENV', 'EXPOSE', 'LABEL', 'ONBUILD',
                   'STOPSIGNAL', 'USER', 'VOLUME', 'WORKDIR')

        opt, _ = values.split('=', 1)
        if opt not in choices:
            parser.error('Option "{}" is not supported by argument "{}",'
                         ' valid options are: {}'.format(
                             opt, option_string, ', '.join(choices)))
        items.append(values)
        setattr(namespace, self.dest, items)


class DetachKeyAction(argparse.Action):
    """Validate input as a detach key."""

    KEY_LABELS = ('ctrl-@', 'ctrl-a', 'ctrl-b', 'ctrl-c', 'ctrl-d', 'ctrl-e',
                  'ctrl-f', 'ctrl-g', 'ctrl-h', 'ctrl-i', 'ctrl-j', 'ctrl-k',
                  'ctrl-l', 'ctrl-m', 'ctrl-n', 'ctrl-o', 'ctrl-p', 'ctrl-q',
                  'ctrl-r', 'ctrl-s', 'ctrl-t', 'ctrl-u', 'ctrl-v', 'ctrl-w',
                  'ctrl-x', 'ctrl-y', 'ctrl-z', 'ctrl-[', 'ctrl-\\', 'ctrl-]',
                  'ctrl-^', 'ctrl-_')

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=4,
                 type=str,
                 choices=None,
                 required=False,
                 help='Override the key sequence for detaching a container.'
                 ' (format: a single character [a-Z], the string DEL, or '
                 r' ctrl-<value> where <value> is from [@a-z[\]^_])'
                 ' (default: ctrl-d)',
                 metavar='KEY'):
        """Create DetachKeyAction object."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate input is a detach key."""
        try:
            key = self.KEY_LABELS.index(values)
        except ValueError:
            if values == 'DEL':
                key = 127
            elif len(values) == 1:
                key = ord(values)
            else:
                parser.error(
                    '"{}" must be a single character [a-Z],'
                    r' the string ctrl-<value>, value from [@a-z[\]^_]'
                    ' or the string DEL'.format(option_string))
        setattr(namespace, self.dest, key)


class SignalAction(argparse.Action):
    """Validate input as a signal."""

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=str,
                 choices=None,
                 required=False,
                 help='The signal to send.'
                 ' It may be given as a name or a number.',
                 metavar='SIGNAL'):
        """Create SignalAction object."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

        if hasattr(signal, "Signals"):

            def _signal_number(signame):
                cooked = 'SIG{}'.format(signame)
                try:
                    sig = signal.Signals[cooked]  # pylint: disable=no-member
                    return sig.value
                except ValueError:
                    pass
        else:

            def _signal_number(signame):
                cooked = 'SIG{}'.format(signame)
                return signal.__dict__.get(cooked, None)

        self._signal_number = _signal_number

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate input is a signal for platform."""
        if values.isdigit():
            signum = int(values)
            if not 1 <= signum < signal.NSIG:
                raise ValueError('"{}" is not a valid signal. 1-{}'.format(
                    values, signal.NSIG))
        else:
            signum = self._signal_number(values)
            if signum is None:
                parser.error(
                    '"{}" is not a valid signal,'
                    ' see your platform documentation.'.format(values))
        setattr(namespace, self.dest, int(signum))


class UnitAction(argparse.Action):
    """Validate number given is positive integer, with optional suffix."""

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar='UNIT'):
        """Create UnitAction object."""
        help = (help or metavar or dest)\
            + ' (format: <number>[<unit>], where unit = b, k, m or g)'
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate input as a UNIT."""
        try:
            val = int(values)
        except ValueError:
            if not values[:-1].isdigit():
                msg = ('{} must be a positive integer,'
                       ' with optional suffix').format(option_string)
                parser.error(msg)
            if not values[-1] in ('b', 'k', 'm', 'g'):
                msg = '{} only supports suffices of: b, k, m, g'.format(
                    option_string)
                parser.error(msg)
        else:
            if val <= 0:
                msg = '{} must be a positive integer'.format(option_string)
                parser.error(msg)

        setattr(namespace, self.dest, values)


class PositiveIntAction(argparse.Action):
    """Validate number given is positive integer."""

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=int,
                 choices=None,
                 required=False,
                 help='Must be a positive integer.',
                 metavar='>0'):
        """Create PositiveIntAction object."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate input."""
        if values > 0:
            setattr(namespace, self.dest, values)
            return

        msg = '{} must be a positive integer'.format(option_string)
        parser.error(msg)


class PathAction(argparse.Action):
    """Expand user- and relative-paths."""

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar='PATH'):
        """Create PathAction object."""
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        """Resolve full path value on local filesystem."""
        setattr(namespace, self.dest,
                os.path.abspath(os.path.expanduser(values)))
