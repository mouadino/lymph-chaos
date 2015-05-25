import collections
import contextlib
import random

import gevent

from lymph.client import Client
from lymph.config import Configuration
from lymph.utils.logging import setup_logger


LOGGER = setup_logger(__name__)


Args = collections.namedtuple('Args', 'func_name body')


# TODO: Don't just apply commands to all instances, in some cases
# we want to apply command to only 1/2 or one ... !
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
        # FIXME: This is very hackish and fragile !
        config = Configuration({
            'container': {
                'registry': {
                    'class': 'lymph.discovery.zookeeper:ZookeeperServiceRegistry',
                    'zkclient': {
                        'class': 'kazoo.client:KazooClient',
                        'hosts': zookeeper_host,
                    }
                }
            },
            'event_system': {}
        })
        return cls(Client.from_config(config))

    def kill(self, name):
        self._service_cmds[name].append(Args('kill', {'name': name}))

    def inject_latency(self, name, latency, period=3):
        self._service_cmds[name].append(
            Args('inject_latency', {'name': name, 'latency': latency, 'period': period})
        )

    @contextlib.contextmanager
    def repeat(self, interval=5):
        # FIXME: Interval and latency period having both parameters is a problem !
        self._running = True
        gevent.spawn(self._repeat, interval).start()
        try:
            yield
        finally:
            self._running = False

    def _repeat(self, interval):
        while self._running:
            self.execute()
            gevent.sleep(interval)

    def execute(self):
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
