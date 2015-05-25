from lymph.chaos.scenarios import Scenario

sn = Scenario.from_zookeeper_host('zookeeper')

sn.kill('echo')
# TODO: How to control which instance/machine to inject latency into !?
sn.inject_latency(1)

with sn.play(interval=1):
    time.sleep(60)
