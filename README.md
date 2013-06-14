Counter for Glass
========================

Sample counter Glassware for Google Glass written in Python. For each 
counter, users can set a name and a starting number via a Google App 
Engine web UI. Counters appear on Glass as timeline cards with the 
options to increment, decrement, reset, share, and delete.

This Glassware demonstrates how to use the sourceItemId field of a 
timeline item and JSON serialization to associate variables (custom fields) 
with timeline items. This technique can be used with jinja to automatically 
generate html and display these custom fields. The class CustomItemFields
(CustomItemFields.py) provides class methods to enable this functionality.
main_handler.py and notify/handler.py demonstrate how to use these methods.
