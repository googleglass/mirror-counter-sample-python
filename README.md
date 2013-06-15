Counter for Glass
========================

Sample counter Glassware for Google Glass written in Python.

To create a counter, users set a name and a starting number via a web
UI hosted on Google App Engine. Counters appear on Glass as timeline 
item with the options to increment, decrement, reset, share, and delete.

This Glassware demonstrates how to use the timelineItem.sourceItemId field 
of a timeline item and JSON serialization to associate variables (custom 
fields) with timeline items. This technique can be used with jinja to 
automatically generate html and display these custom fields. The class 
[CustomItemFields](CustomItemFields.py) provides class methods to enable 
this functionality. The [main handler](main_handler.py) and 
[notification handler](notify/handler.py) demonstrate how to use these methods.
