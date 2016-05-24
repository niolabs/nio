API Conventions
===============

Most Nio binaries can be interacted with through a REST API. The API supports the standard HTTP request types and data responses are of JSON format.

The REST API is in Nio binaries that use the REST Nio Component. We will cover componenets later in the docs.

Authentication
--------------

Regardless of what form of authorization your project uses, you will have user permissions specified in the file permissions.json in the etc directory of your project.

Basic Auth
~~~~~~~~~~

When using basic authentication, the REST API is protected usernames and passwords. To use basic auth, include a base 64 encoded username and passowrd in the Authorization header of your request. For example:

.. code-block:: bash

    { 'Authorization': 'Basic VXNlcjpVU2Vy' }

OAuth2
~~~~~~

When using OAuth 2.0, you need to first get an access token. Once you have one, include it in the header. For example:

.. code-block:: bash

    { 'Authorization': 'Bearer 0b79bab50daca910b000d4f1a2b675d604257e42' }
