This is basically a way to add bus priorities to powerworld onelines and display them in a relatively clean manner on google earth. 
To run this we take a powerworld pwb file and load its pwd oneline. We then export it as a KML (hawaiiwithtl.kml is an example), only selected the substation and transmission line options
We then take that file and the bus priorities (busimportance.csv), and run those into the genupdatedviz.py file. This will generate another kml file (Hawaiikmltogoogleearth.kml)
We upload that kml file to google earth, set the layer to clean and turn off 3D buildings. The vizualization is now visible and interactive on google earth.

<img width="960" alt="image" src="https://github.com/user-attachments/assets/b993975a-b9aa-4c91-8495-dc5f3cef38f8">
