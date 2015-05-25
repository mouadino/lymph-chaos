import collections
import random

import gevent

from lymph.client import Client
from lymph.logging import setup_logging


LOGGER = setup_logging(__name__)


Args = collections.namedtuple('Args', 'func_name body')


class Scenario(object):

    service_name = 'Chaos'

    def __init__(self, client, timeout=2):
        self._client = client
        self._timeout = timeout
        self._running = False
        self._service_cmds = collections.defaultdict(list)

    @classmethod
    def from_config(cls, config):
        return cls(Client.from_config(config))

    @classmethod
    def from_zookeeper_host(cls, zookeeper_host):
        config = {
            'container': {
                'registry': zookeeper_host,
            }
        }
        return cls(Client.from_config(config))

    def kill(self, name):
        self._service_cmds[name].append(Args('kill', {'name': name}))

    def inject_latency(self, name, latency):
        self._service_cmds[name].append(
            Args('inject_latency', {'name': name, 'latency': latency})
        )

    def play(self, interval=1):
        if self._running:
            raise RuntimeError('Already running')
        self._running = True
        greenlet = gevent.spawn(self._apply, interval)
        greenlet.start()

    def cancel(self):
        self._running = False

    @contextlib.contextmanager
    def with_(self):
        self.play()
        try:
            yield
        finally:
            self.cancel()

    def _play(self, interval):
        while self._running:
            self._send_commands()
            gevent.sleep(interval)

    def _send_commands(self):
        services_map = self._build_services_map()

        for service_name, args in self._service_cmds.items():
            chaos_endpoints = services_map[service_name]
            if not chaos_endpoints:
                LOGGER.warnings('skipping unknown service %r', service_name)
                continue
            for endpoint in chaos_endpoints:
                self._request(endpoint, args.func_name, args.body)

    def _build_services_map(self):
        """Return a dictionary of all running services and which 'chaos' instance
        handle them.

        """
        chaos_service = self._client.container.lookup(self.service_name)
        services_map = collections.defaultdict(list)
        for chaos_instance in chaos_service.instances.values():
            node_services = self._request(chaos_instance.endpoint, 'list_services', {})
            for name in node_services:
                services_map[name].append(chaos_instance.endpoint)
        return services_map

    def _request(self, identity, func_name, body):
        func_name = '%s.%s' % (self.service_name, func_name)
        resp = self._client.request(identity, func_name, body, timeout=self._timeout)
        return resp.body
