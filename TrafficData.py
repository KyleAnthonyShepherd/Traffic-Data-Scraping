'''
This code pulls traffic data from the HERE maps service
This data has vehicle speed data, and GeoCoordinates of the roadways
A bounding box in lat-long format can be used to get the data of interest
Real time data must be collected, because historical data is not avaliable

If this script is run by itself, a bounding box of bbox=[30.167808,-95.958910,29.495183,-94.911649]
is used, and the data is collected.
This script could be imported into another script, and the function
TrafficDataRealTime(bbox)
can be used on its own, if a bounding box is provided

Data collected from here:
https://wego.here.com/traffic/explore
using the API:
https://traffic.api.here.com/traffic/6.1/flow.json
and hijacking the app code and API key from the map service
This link helped interpret the json data:
https://traffic.api.here.com/traffic/6.0/xsd/flow.xsd?app_code=K2Cpd_EKDzrZb1tz0zdpeQ&app_id=bC4fb9WQfCCZfkxspD4z

Each Output file is ~250 KB
If collected every 5 minutes, 72 MB of storage are needed every day
26.28 GB is needed every year

#
Code Written by:
Kyle Shepherd, at Rice University
kas20@rice.edu
Oct 24, 2018
#
'''
#### Import BLock ####
# the import block imports needed modules, and spits out a json file with
# version numbers so the code can be repeatable
file = open("ModuleVersions.json", 'w')
modules = {}

import os

import sys
modules['Python'] = dict([('version', sys.version_info)])

import json
modules['json'] = dict([('version', json.__version__)])

import requests
modules['requests'] = dict([('version', requests.__version__)])

json.dump(modules, file, indent=4, sort_keys=True)
file.close()
#### END Import Block ####

def TrafficDataRealTime(bbox):
    '''
This function does the data import.
It gets data within a given bounding box

Inputs:
###
bbox:
defines the geographic bounding box to collect all the data. Need the upper
left corner, and the lower right corner
Format:
list of 4 elements [lat UL, long UL, lat LR, long LR]
example:
[30.167808,-95.958910,29.495183,-94.911649]
###

This function outputs two files deliminated by |
the first file is a Index file.
this file contains information about the roadways.
###
Index File Headers:
Time of creation
MapVersion number
ID number|PC number|Road Name|Towards Road Name|Road Length|Road Coordinates
###
This file is only updated when the map of roads changes, which occurs approximately monthly
This limited updating of the index file is done to conserve file space

The second file is the data file, TrafficFlowData
this contains information about the road conditions
###
TrafficFlowData Headers:
Time of creation
MapVersion number
Current Speed (SU)|Free Flow Speed (FF)|Jam Factor (JF)|Confidence Number (CN)
###
the data is stored as Metric data, km/hr, because of the greater granularity of
the data (1 km is smaller than 1 mile)
HERE maps updates once a minute
The MapVersion number allows you to connect a data file with the index number
so analysis can be performed even if the roadway maps update
'''
    # creates folders if they do not exist
    bbox=str(bbox[0])+','+str(bbox[1])+';'+str(bbox[2])+','+str(bbox[3])
    if not os.path.exists('DataIndexes'):
        os.makedirs('DataIndexes')
    if not os.path.exists('TrafficFlowData'):
        os.makedirs('TrafficFlowData')

    # GET request URL
    url='https://traffic.api.here.com/traffic/6.1/flow.json?app_code=K2Cpd_EKDzrZb1tz0zdpeQ&app_id=bC4fb9WQfCCZfkxspD4z&bbox='+str(bbox)+'&i18n=true&lg=en&responseattributes=simplifiedShape&units=metric'
    r=requests.get(url) # The requests python package does the heavy lifting
    text=r.json() # get response

    # A LI and PC number uniquely identifies each road, an ID number.
    # These are sorted, so they can be compated to the current Index file to
    # determine if the roadway map has updated
    IDs=[]
    for k in text["RWS"][0]["RW"]:
        for k2 in k["FIS"][0]["FI"]:
            IDs.append(k["LI"]+' '+str(k2["TMC"]["PC"]))

    #sorts and saves the index to produce the sort
    SortedIdsIndex=sorted(range(len(IDs)),key=IDs.__getitem__)

    # initialze lists using the length of the IDs above
    index=[None]*len(IDs)
    data=[None]*len(IDs)
    SortedIndex=[None]*len(IDs)

    # extracts data from the json response
    # data is saves to a list, as strings with delimiters in place
    i=0
    for k in text["RWS"][0]["RW"]:
        for k2 in k["FIS"][0]["FI"]:
            index[i]=k["LI"]+'|'
            index[i]=index[i]+str(k2["TMC"]["PC"])+'|'
            index[i]=index[i]+k["DE"]+'|'
            index[i]=index[i]+k2["TMC"]["DE"]+'|'
            index[i]=index[i]+str(k2["TMC"]["LE"])+'|'
            for shp in k2["SHP"]: # sometimes the geocoordinates of the road comes in 2 parts, is unexplained in API
                index[i]=index[i]+str(shp["value"])+'|'
            index[i]=index[i]+'\n'

            # SU speed is the actual speed of cars
            # SP speed is bounded by the speed limit
            try: # if the road is closed, the SU speed is not given, so must check for existence, and otherwise use SP speed
                data[i]=str(k2["CF"][0]["SU"])+'|'
            except KeyError:
                data[i]=str(k2["CF"][0]["SP"])+'|'
            data[i]=data[i]+str(k2["CF"][0]["FF"])+'|'
            data[i]=data[i]+str(k2["CF"][0]["JF"])+'|'
            data[i]=data[i]+str(k2["CF"][0]["CN"])+'\n'
            i=i+1

    #sorts the index to produce the sort
    i=0
    for k in SortedIdsIndex:
        SortedIndex[i]=index[k]
        i=i+1

    # Code to catch condition if the code is being run for the first time.
    # if first time, use default values of CurrentIndex and MapVersion
    # otherwise, load DataIndexCurrent file to compare it to the newly requested
    # Index data to determine if the map has changed
    if os.path.exists('DataIndexCurrent'):
        CurrentIndexFile=open('DataIndexCurrent','r')
        CurrentIndex=[]
        CurrentIndexData=CurrentIndexFile.readlines()
        MapVersion=CurrentIndexData[1]
        i=0
        for k in CurrentIndexData[3:]:
            CurrentIndex.append(k)
            i=i+1
        CurrentIndexFile.close()
    else:
        CurrentIndex=[]
        MapVersion="MapVersion|0\n"

    # if the map has not changed, just write data to a TrafficFlowData file
    # filename contains timestamp
    if SortedIndex==CurrentIndex:
        time=text["CREATED_TIMESTAMP"].replace(':','') #fix time so it can be a filename
        dataFile=open('TrafficFlowData/TrafficFlowData'+time,'w')
        dataFile.write(text["CREATED_TIMESTAMP"]+'\n')
        dataFile.write(MapVersion)
        dataFile.write("Current Speed (SU)|Free Flow Speed (FF)|Jam Factor (JF)|Confidence Number (CN)\n")
        for k in SortedIdsIndex:
            dataFile.write(data[k])
    # if the map has changed, rename DataIndexCurrent to the map version it was using
    # increment the MapVersion number
    # create a new Current Index file
    # write data to a TrafficFlowData file
    else:
        MapVersionNumber=MapVersion[0:-1].split('|')
        if os.path.exists('DataIndexCurrent'):
            os.rename('DataIndexCurrent','DataIndexes/DataIndexMapVersion'+MapVersionNumber[1])
        indexFile=open('DataIndexCurrent','w')
        MapVersion="MapVersion|"+str(int(MapVersionNumber[1])+1)+"\n" # increment the MapVersion number
        #headers
        indexFile.write(text["CREATED_TIMESTAMP"]+'\n')
        indexFile.write(MapVersion)
        indexFile.write("ID number|PC number|Road Name|Towards Road Name|Road Length|Road Coordinates\n")
        for k in SortedIdsIndex:
            indexFile.write(index[k])
        time=text["CREATED_TIMESTAMP"].replace(':','') #fix time so it can be a filename
        dataFile=open('TrafficFlowData/TrafficFlowData'+time,'w')
        #headers
        dataFile.write(text["CREATED_TIMESTAMP"]+'\n')
        dataFile.write(MapVersion)
        dataFile.write("Current Speed (SU)|Free Flow Speed (FF)|Jam Factor (JF)|Confidence Number (CN)\n")
        for k in SortedIdsIndex:
            dataFile.write(data[k])

if __name__ == "__main__":
    bbox=[30.167808,-95.958910,29.495183,-94.911649]
    TrafficDataRealTime(bbox)
