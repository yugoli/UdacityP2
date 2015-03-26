# UdacityP2
Project 2: Explored Indianapolis from OpenStreetMaps XML in Python and MongoDB
Step One - Finish Lesson 6

Make sure all Lesson 6 programming exercises are solved correctly.

Step Two - Review the Rubric and Sample Project

The Project Rubric will be used to evaluate your project. It will need to Meet Specifications for all the criteria listed. The Sample Project is an example of what your final report could look like.

Step Three - Choose Your Map Area

Choose any area of the world from https://www.openstreetmap.org , and download a XML OSM dataset. The dataset should be at least 50MB in size (uncompressed). We recommend using one of following methods of downloading a dataset:

Download a preselected metro area from Map Zen (Note that data obtained from Map Zen is compressed and will usually expand to sizes that meet project requirements.)
Use the Overpass API to download a custom square area. Explanation of the syntax can found in the wiki . In general you will want to use the following query: (node(minimum_latitude, minimum_longitude, maximum_latitude, maximum_longitude);<;);out meta; e.g. (node(51.249,7.148,51.251,7.152);<;);out meta; the meta option is included so the elements contain timestamp and user information. You can use the Open Street Map Export Tool to find the coordinates of your bounding box. Note: You will not be able to use the Export Tool to actually download the data, the area required for this project is too large.
Step Four - Process your Dataset

Thoroughly audit and clean your dataset, converting it from XML to JSON format. It is recommended that you start with the Lesson 6 exercises and modify them to suit your chosen data set. As you unravel the data, take note of problems encountered along the way as well as issues with the dataset. You are going to need these when you write your project report. Finally, import the clean JSON file into a MongoDB database and run some queries against it.

Step Five - Document your Work

Create a document (pdf, html) that directly addresses the following sections from the Project Rubric .

Problems encountered in your map
Overview of the Data
Other ideas about the datasets
