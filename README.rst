Chaos monkey for lymph services
===============================

What is chaos monkey ?
----------------------

http://en.wikipedia.org/wiki/Chaos_Monkey

Goals
-----

- As a system administrator I want to easily install lymph chaos agent w/o changing
  configuration, one click command will be the best.
- As a QA developer I want to control lymph chaos from code, so that I can write harness tests.
- As a backend developer I would like to reproduce a failure scenario so that I can debug
  it or write tests for it.
- As a backend developer I would like to exercise most common failures mode and see how my
  service react to them.

Usage
-----

Install lymph-chaos by running ::

    pip install git@github.com:mouadino/lymph-chaos.git

In you node configuration e.g. ``.lymph.yml`` just add a service ``chaos``
as an instance ::

    instances:
        ...
        chaos:
            command: lymph instance --interface lymph.chaos.interfaces:Chaos
        ...

Controlling lymph-chaos from code ::

    from lymph.chaos import Scenario

    sn = Scenario.from_zookeeper_host('127.0.0.1')

    sn.kill('echo')

    sn.inject_latency(1)

    with sn.play(interval=1):
        # Here you can put what you want to test while chaos monkey
        # is destroying services.
        import time
        time.sleep(30)


Need more examples, check the examples/ folder.

Supported commands:
-------------------

In this section we will discuss the current available command:

Killing a lymph service:
++++++++++++++++++++++++

This is done by killing lymph instance process.

N.B. lymph node will make sure that the service will recover.

Network manipulation:
+++++++++++++++++++++

We use under the hood the `tc` command to manipulate traffic control settings, for
now we can inject latency for all node/machine, in the future we can add more stuff
like packet corruption ... .

It goes without saying that this only work on linux machines.

TODO
----

- dry run.
- Auto discovery: It will be good if monkey agent can run standalone and discover services automagically.
- Killing any process (e.g. what happen when we lose one db node)
- filling disk, cpu burnout (only do it inside docker)
  https://github.com/Netflix/SimianArmy/tree/master/src/main/resources/scripts.
- recording events.
- unleashed mode of chaos monkey (i.e. killing stuff at random schedule)
