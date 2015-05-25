import os

import lymph
from lymph.config import Configuration
from lymph.chaos.controllers import ServiceController, NetworkController, LymphNodeProxy


class Chaos(lymph.Interface):

    def on_start(self):
        super(Chaos, self).on_start()
        node_address = os.environ.get('LYMPH_NODE')
        # TODO: For now we only support running under lymph node.
        if not node_address:
            raise RuntimeError('No node service found.')
        proxy = LymphNodeProxy(self.proxy(node_address, namespace='node'))
        self.service = ServiceController(proxy)
        self.network = NetworkController()

    @lymph.rpc()
    def list_services(self):
        return self.service.list_services()

    @lymph.rpc()
    def kill(self, name):
        self.service.kill(name)

    @lymph.rpc()
    def inject_latency(self, latency=1):
        self.network.inject_latency(latency)
