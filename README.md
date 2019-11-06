# Traffic-Data-Scraping

This code pulls traffic data from the HERE maps service.<br/>
This data has vehicle speed data, and GeoCoordinates of the roadways.<br/>
A bounding box in lat-long format can be used to get the data of interest.<br/>
Real time data must be collected, because historical data is not avaliable.<br/>
<br/>
If this script is run by itself, a bounding box of bbox=[30.167808,-95.958910,29.495183,-94.911649]<br/>
is used, and the data is collected.<br/>
This script could be imported into another script, and the function<br/>
TrafficDataRealTime(bbox)<br/>
can be used on its own, if a bounding box is provided.<br/>
<br/>
Data collected from here:<br/>
https://wego.here.com/traffic/explore<br/>
using the API:<br/>
https://traffic.api.here.com/traffic/6.1/flow.json<br/>
and hijacking the app code and API key from the map service<br/>
This link helped interpret the json data:<br/>
https://traffic.api.here.com/traffic/6.0/xsd/flow.xsd?app_code=K2Cpd_EKDzrZb1tz0zdpeQ&app_id=bC4fb9WQfCCZfkxspD4z<br/>
<br/>
Each Output file is ~250 KB<br/>
If collected every 5 minutes, 72 MB of storage are needed every day.<br/>
26.28 GB is needed every year.<br/>
<br/>
#<br/>
Code Written by:<br/>
Kyle Shepherd, at Rice University<br/>
kas20@rice.edu<br/>
Oct 24, 2018<br/>
#<br/>

![](images/path955.png)
