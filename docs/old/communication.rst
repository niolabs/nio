Communication Module
--------------------

Introduction
~~~~~~~~~~~~

Nio provides a robust mechanism for effecting communication between processes. Based around ZeroMQ, Publish/Subscribe, and the Broker Model, nio communication allows you to pass signals transparently between services, nio instances, or even physical devices (running nio, of course).

Configuration
~~~~~~~~~~~~~

- **mode** - communication mode
   * zmq.manager
- **matching** - topic matching class
   * nio.modules.communication.matching.default.DefaultMatching
- **master** - whether or not the master broker will run in this instance
   * true/false
- **bind_ip_address** - the IP address of the master broker. if **master** is true, this should be the IP address of the host machine. if **master** is false, this should match the "bind_ip_address" value of the communication module for the master.
- **xpub_port** - the port over which publishers are registered with the master broker.
- **xsub_port** - the port over which publishers are registered with the master broker.
- **ip_address** - the IP address of the host machine, regardless of whether **master** is true.
- **poll_rate_ms** - *mysterioso*
- **max_port** - upper bound of port range used for finding available local ports for publishers/subscribers
- **min_port** - lower bound
- **connect_timeout** - time to wait at start up when there is a communication failure due to ip address, port issues, etc.

  * 0 - no wait, module fails right away
  
  * > 0 - keep retrying for specified time unless IP Address is determined to be valid
  
  * < 0 - keep retrying indefinitely unless IP Address is determined to be valid


Capabilities
~~~~~~~~~~~~

When configured correctly with a single **master** instance, nio's communication module can be used to create failure-robust, dynamic publish/subscribe networks. However, there are a few limitations:

   - For two (or more) disparate machines to communicate (i.e. one pubs while the other subs), each must have an IP address which is accessible by the others. Within a local network, this shouldn't be a problem, but, if one or both of the IP addresses is behind a NAT, communication may not be possible.
   - Two slave instances running without a master can create publishers and subscribers; however, messages will not be transmitted between same until a master broker appears in the network. Even so, publishers and subscribers instantiated before the master node is running will be detected and connected by the master broker when it starts.
   
Beyond that, just about any configuration of publishers and subscribers, local or remote, should work seamlessly, irrespective of the order in which publishers, subscribers, masters, or slaves are instantiated.


