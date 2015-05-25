import abc
import operator
import os

import six

from gevent import subprocess

from lymph.core.interfaces import Proxy
from lymph.utils.logging import setup_logger


LOGGER = setup_logger(__name__)


class ServiceController(object):

    def __init__(self, proxy):
        self._proxy = proxy

    def list_services(self):
        return self._proxy.list_services()

    def kill(self, service_name):
        pids = self._proxy.get_processes(service_name)
        for pid in pids:
            LOGGER.info('killing processe %s', pid)
            subprocess.call(['kill', '-9', str(pid)])


@six.add_metaclass(abc.ABCMeta)
class AbstractProxy(object):
    @abc.abstractmethod
    def list_services(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_processes(self, service_name):
        raise NotImplementedError()


class LymphNodeProxy(AbstractProxy):

    def __init__(self, client):
        self._client = client

    def list_services(self):
        return self._client.get_services()

    def get_processes(self, service_name):
        processes = self._client.get_processes(service_type=service_name)
        return [proc['pid'] for proc in processes]

# TODO: SystemProxy For controlling any process
