# EnrichSignals Mixin

Use this mixin to automatically enrich notified signals with data from incoming signals, if the block configuration specifies to do so. The mixin will provide a few helper methods to a block writer to make this common operation easier.

## Properties

- **Exclude Existing** (bool): Whether or not to exclude existing data. If this is checked, a new signal will be notified for every incoming signal. In other words, no data from the incoming signal will be included on the notified signal.
- **Results Field** (str): The attribute on the signal to store the results from this block. If this is empty, the results will be merged onto the incoming signal. This is the default operation. Having this field allows a block to "save" the results of an operation to a single field on an incoming signal and notify the enriched signal.
    

## Special Methods

### get_output_signal

```python
def get_output_signal(self, signal_data, incoming_signal, copy=True):
```

This method will return a Signal formatted the proper way according to the block configuration. Simply pass in the results of the operation you would like to notify to `signal_data` and the Signal that triggered the operation to `incoming_signal`. Optionally, tell the method to not deepcopy the incoming signal before returning the new signal by passing `copy=False`. 

### notify_output_signals

```python
def notify_output_signals(self, signals_data, incoming_signal, copy=True):
```

This method is a shortcut to calling `self.get_output_signal()` and then subsequently `self.notify_signals()`. It also has the ability to take a list of signal data for notification, rather than just a single signal.

The following two functions are essentially equivalent:

#### Using notify

```python
self.notify_output_signals(results, incoming_signal)
```

#### Using get

```python
out_sigs = []
for result in results:
    out_sigs.append(self.get_output_signal(result, incoming_signal))
self.notify_signals(out_sigs)
```
