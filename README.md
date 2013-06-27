Counter for Glass
========================

Sample counter Glassware written in Python.

To create a counter, a user accesses a web UI hosted on Google App Engine
and sets a name and starting number. Counters appear on Glass devices as 
timeline items with the options to increment, decrement, reset, share, 
and delete.

This Glassware demonstrates how to use the timelineItem.sourceItemId field 
of a timeline item and JSON serialization to associate variables (custom 
fields) with timeline items. This technique can be used with Jinja2 to 
automatically generate html and display these custom fields. The file 
[custom_item_fields](custom_item_fields.py) provides functions to enable 
this capability. The [main handler](main_handler.py) and 
[notification handler](notify/handler.py) demonstrate how to use these methods.


**Note**: This is a snapshot sample. That means that although we think you will 
find it useful, it is not being actively maintained. Pull requests are always 
apprecaited.
