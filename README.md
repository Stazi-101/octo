# octo

A physics engine supporting elastic networks, gravity and terrain.
The example used is an octopus.

Main controls supported (dependent on version):
 - Left click to drag nodes
 - A to toggle gravity
 - I to increase length of all links temporarily
 - J to decrease length of all links temporarily

Creation controls supported (recommended to change visible objects at top of python file):
 - Right click in empty space to create node
 - Right click near nodes twice to join those nodes
 - D near nodes twice to delete any links from between them
 - S near nodes thrice to create a triangle (only aesthetic) between them

Nodes have mass
Links are light elastic connections
Triangles are just aesthetic

v0 - testing maths with hardcoded triangles
v1 - creating simple octopi which can be created using mouse, saved and loaded
v2 - reworking saving format, has support for controlling specific links 

Future developments:
 - Adding controls to specific links to move tentacles
 - Change drag system to apply forces to outside surfaces to allow modelling of swimming
 - Apply machine learning system to create 'naturally' generated movement
