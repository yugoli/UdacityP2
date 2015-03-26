#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if second level tag "k" value contains problematic characters, it should be ignored
- if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if second level tag "k" value does not start with "addr:", but contains ":", you can process it
  same as any other tag.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
phone = re.compile(r'''
                # don't match beginning of string, number can start anywhere
    (\d{3})     # area code is 3 digits (e.g. '800')
    \D*         # optional separator is any number of non-digits
    (\d{3})     # trunk is 3 digits (e.g. '555')
    \D*         # optional separator
    (\d{4})     # rest of number is 4 digits (e.g. '1212')
    \D*         # optional separator
    (\d*)       # extension is optional and can be any number of digits
    $           # end of string
    ''', re.VERBOSE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS = ["lat", "lon"]
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Circle", "Crossing", "Pike", "Pass", "Row", "Run",
            "Trace", "Walk", "Way"]
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd": "Road",
            "Rd.": "Road",
            "Dr" : "Drive",
            "Dr." : "Drive",
            "Pkwy" : "Parkway",
            
            }

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def update_name(name, mapping):

    for key in mapping.keys():
            m = re.search(key, name)
            if m:
                name = re.sub(key+'$', mapping[key], name)
    return name

def shape_element(element):
    node = {}
    address = {}
    create = {}
    pos = {}
    node_refs=[]
    
    for key in element.attrib.keys():
        if key in CREATED:
            create[key] = element.attrib[key]
        elif key in POS:
            pos[key] = float(element.attrib[key])
        else:
            node[key]=element.attrib[key]
            #print key + "->  " +  element.attrib[key]
    #print create, pos
    node['created']=create
    if len(pos)==2:
        node['pos']=[pos['lat'],pos['lon']]
            
    if element.tag == "node" or element.tag == "way":
        for tag in element.iter("tag"):
            #print tag.attrib['k']
            if tag.attrib['k'].startswith("addr") and len(tag.attrib['k'].split(':'))==2:
                if is_street_name(tag):
                    street = update_name(tag.attrib['v'], mapping)
                    address[tag.attrib['k'].split(':')[1]] = street
                elif is_zipcode(tag):
                    zipcode = re.sub(r'\D', "", tag.attrib['v'])
                    address[tag.attrib['k'].split(':')[1]] = zipcode[0:5]
                else:
                    address[tag.attrib['k'].split(':')[1]] = tag.attrib['v']
                #print address
            elif tag.attrib['k'] == "phone":
                p = phone.search(tag.attrib['v'])
                #print tag.attrib['v'] + " => " + p.group(1) + p.group(2) + p.group(3)
                num = p.group(1) + p.group(2) + p.group(3)
                #print num
                node[tag.attrib['k']] = num
            else:
                node[tag.attrib['k']] = tag.attrib['v']
        
        node['type']=element.tag
        
        if(len(address)>0):
            node['address'] = address

        for nd in element.iter("nd"):
            node_refs.append(nd.attrib['ref'])
    
        if(len(node_refs)>0):
            node['node_refs'] = node_refs
                 
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('indy.osm')
    #pprint.pprint(data)
    
    '''assert data[0] == {
                        "id": "261114295", 
                        "visible": "true", 
                        "type": "node", 
                        "pos": [
                          41.9730791, 
                          -87.6866303
                        ], 
                        "created": {
                          "changeset": "11129782", 
                          "user": "bbmiller", 
                          "version": "7", 
                          "uid": "451048", 
                          "timestamp": "2012-03-28T18:31:23Z"
                        }
                      }
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]'''

if __name__ == "__main__":
    test()