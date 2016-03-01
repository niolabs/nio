GroupBy Mixin
=============

Use this mixin to automatically group (and store) incoming signals based on a configurable expression.

Properties
----------

- **group_by** (ExpressionProperty): The expression by which to group signals. Evaluated on each incoming signal, individually, in order to determine its group. If any of the attributes do not exist in the signal, groupby == ‘null’

Special Methods
_______________

- **GroupBy.for_each_group(self, target, signals=None, kwargs=None): This method maps a callable 'target' over some signal groups. If the 'signals' list is not None, it is grouped in the normal way. Otherwise, 'target' is mapped over previously recorded groups.
If kwargs is given, they will be passed to the target in the form of `target(*args, **kwargs)`

For more information on ExpressionProperties, see [here](http://docs.n.io/en/latest/expressions.html).

