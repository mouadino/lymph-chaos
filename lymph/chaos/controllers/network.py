import subprocess
import shlex
import functools

import gevent

from lymph.utils.logging import setup_logger


LOGGER = setup_logger(__name__)


class CommandError(Exception):
    pass


# TODO: Choose network interface !
# TODO: Check filter to apply this for only given port http://lartc.org/howto/lartc.qdisc.filters.html.
# TODO: Need a way to check if we need to call sudo with commands or no.
class TC(object):

    def __init__(self):
        try:
            self._call('tc')
        except CommandError:
            LOGGER.critical('"tc" command not found')
            raise

    def add_qdisc(self, device, what):
        self._call('tc qdisc add dev %s root netem %s' % (device, what))

    def delete_qdisc(self, device):
        self._call('tc qdisc del dev %s netem')

    def list_qdisc(self, device):
        return self._check_ouput('tc -s qdisc show dev %s' % device)

    def _call(self, cmd):
        # TODO: Capture output
        returncode = subprocess.call(shlex.split(cmd))
        if returncode != 0:
            raise CommandError()

    def _check_ouput(self, cmd):
        try:
            return subprocess.call(shlex.split(cmd))
        except subprocess.CalledProcessError:
            raise CommandError()


class NetworkController(object):

    def __init__(self):
        self.tc = TC()

    def inject_latency(self, latency, period):
        # TODO: Can't apply this rule more than once !
        if self.tc.list_qdisc():
            LOGGER.error('qdisc already exist')
            raise CommandError()
        LOGGER.info('injecting latency of %s seconds', latency)
        try:
            self.tc.add_qdisc('eth0', 'delay %ds' % latency)
        except CommandError:
            LOGGER.error('injecting latency failed')
            raise
        else:
            gevent.spawn_later(period, self.tc.delete_qdisc, 'eth0')  \
                  .link_exception(
                      functools.partial(LOGGER.error, 'fail to clean up injected latency: %r'))
