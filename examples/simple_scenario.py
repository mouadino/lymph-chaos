from lymph.chaos.scenario import Scenario

sn = Scenario.from_zookeeper_host('zookeeper')

sn.kill('echo')
sn.inject_latency('demo', 1)

with sn.repeat(interval=5):
    time.sleep(60)
