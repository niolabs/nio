Component - Management Publisher
--------------------------------

The Management Publisher Component hooks to service_status_change and notifies a ManagementSignal to the configured Publisher topics.

It also makes the Publisher available to services and blocks. Blocks can publish ManagementSignals with self.notify_mangement_signal(signal), as well as StatusSignals that will chage that status of the block.


Configuration
~~~~~~~~~~~~~

The management publisher topics are configurable. The Default value is:
"topics": "{\"type\": \"management\"}"

Set confiugration by putting a management_publisher.cfg file in the project's etc/ directory with a dictionary that sets "topics".

{ "topics": "{\"type\": \"mgmt\"}" }

ManagementSignal
~~~~~~~~~~~~~~~~

Subscribers to the management publisher can get the status with $status.name and the name of the service with $service.

Blocks that publish a ManagmentSignal or StatusSignal will also have a status that can be retrieved through $status.name, along with a $msg. As a standard block developers should put the notifing block's name in $name and set $source to "Block". The [RESTPolling block](https://github.com/nio-blocks/http_blocks#RESTPolling) is an example of that.
