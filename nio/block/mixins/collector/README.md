Collector (Mixin)
===========

Collects signals for a specified period of time before notifying them. Useful for buffering high volume streams.

By including this mixin, your block will get a new property added to it (`collect`) and it will start "collecting" or buffering signals for that period of time. You can continue to call `notify_signals` like normal, except that the block router and subsequent blocks won't be notified of the signals until the collection window is closed.

Properties
--------------

-   **collect**: How long to collect signals for. If set to 0, don't do any collection at all.

Dependencies
----------------
None

Commands
----------------
None

Input
-------
N/A

Output
---------
A buffered list of signals
