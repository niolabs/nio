NIO Expressions
---------------

ExpressionProperty
~~~~~~~~~~~~~~~~~~

Given the event driven nature of most NIO applications, it can be difficult or impossible to completely describe the contents of Block properties statically. For this reason, we provide a simple syntax for accessing Signal attributes at run-time. If the value of a Block property should reflect some value that may vary from Signal to Signal, simply declare that property an ExpressionProperty and grab its value inside Block.process_signals.

Here's an example:

.. code-block:: python

   class MyBlock(Block):
       expr = ExpressionProperty(default='', attr_default=0)
		
       def process_signals(self, signals):
           for s in signals:
           try:
	       value = self.expr(s)
	   except Exception as e:
	       value = None
	       self._logger.error("Block property 'expr' failed to evaluate: {}".format(e))
	   # Do some stuff with the value
				
It's that simple. If the Signal under inspection is missing an attribute you ask for in the expression, the value of *attr_default* (provided at property initialization) is used in its place. As with other NIO properties, the value of 'default' will be evaluated if no expression is configured.

Any other errors in the expression will raise native exceptions whose handling is the responsibility of the Block developer. 

**Argument: attr_default**

Unique to ExpressionProperty is the attr_default argument. In evaluating an expression, if the $ notation is used to get an attribute value from a signal, but the attribute does not exist on the signal, then the value attr_default will be used in its place.

If attr_default is not specified on the ExpressionProperty, then an empty string is used.

attr_Default can be set to an Exception **class**. In this case, if the attribute does not exist on the signal, then that Exception will be raised.

**Handling Exceptions**

An ExpressionProperty should always be evaluated inside of a *try* block. Invalid python syntax inside of the expression will raise an Exception and the block needs to handle that. This is also where you would handle the Exception raised by *attr_default* if that is set to an Exception class. 


Scripting Syntax
~~~~~~~~~~~~~~~~

There are two types of results to consider when configuring an expression property:

* **Immediate Value** - A single python expression is evaluated and the result is returned without modification/stringification.

* **String Interpolation** - Snippets of Python code are evaluated and interpolated based on their position in an enclosing string.

**String Interpolation**

String interpolation in expression properties works similarly to string interpolation in other dynamic languages. Snippets of code are delimited as such:

.. code-block:: python
	
   ...{{ <code goes here> }}...
	
and the result of each evaluation is inserted directly into the surrounding string, replacing the code snippet and enclosing braces. The code inside the braces can be pure python, if you like, as in:

.. code-block:: python

   "{{1 + 5}} dogs went to the park" -> "6 dogs went to the park"
	
Or you can use our special syntax for accessing signal properties:

.. code-block:: python

    # given a signal s s.t. s.v1 == 6
    "{{$v1}} dogs went to the park" -> "6 dogs went to the park"
    
Naturally, you can combine the two approaches, as in:

.. code-block:: python

   "My favorite Integer is {{$v1 if isinstance($v1, int) else 'not an Integer...'}}"
	
If you'd like to include a '$' character in a string literal inside a code snippet, just escape it with a '\'. Similarly, escaping the '}}' or '{{' with a '\' causes them to be treated as strings rather than as delimiters. For example:

.. code-block:: python

   "Code snippets are delimited by \{{ and \}}" -> "Code snippets are delimited by {{ and }}"


**Immediate Value**

If you'd prefer that the result of your expression evaluation not be stringified, you can populate an expression field with a single snippet enclosed in double-curlies:

.. code-block:: python

   # given a signal s s.t. s.v1 == 1, s.v2 == 'two', s.v3 == [3]
   "{{[$v1, $v2, $v3]}}" -> [1, 'two', [3]]

**Raw Signal**

You can access the signal itself (rather than just its attributes) with a lone '$'. As long as it is followed by a character that could not be the first character of a valid Python identifier, the '$' evaluates to the incoming signal.


Examples
~~~~~~~~

Here are some more examples that we find particularly illustrative:

.. code-block:: python

   "{{1 + 5}} dogs went to the {{'p' + 'ark'}}" -> "6 dogs went to the park"
		
   # given a signal s s.t. s.v1 == {'who': 'Baron Samedi'}
   "{{$v1['who']}} and the Jets" -> "Baron Samedi and the Jets"
	
   # given a signal s s.t. s.v1 raises AttributeError, s.v2 == 'Cogito'
   # and a default value of None
   "{{$v1 or $v2}} ergo sum" -> "Cogito ergo sum"
	
   # given a signal s s.t. s.get_val() == 'foobar'
   "Opened it with a {{$get_val()}}" -> "Opened it with a foobar"

   # given a signal s s.t. s has the attribute v1 but not v2
   "{{hasattr($, 'v1') and hasattr($, 'v2')}}" -> False




