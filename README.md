odrl-ogc-cache-policies
=======================
An experimental implementation of a protocol for machine-readable cache policies in OGC and ISO geoservices.

Instructions
============
You need a Python 2.7.x interpreter to run this program. It has been developed and tested in Python 2.7.3 in Linux, 
but it should run in any other platform that supports Python 2.7.x 

Besides a number of Python 2.7 standard libraries, you need OWSLib 0.8.7, which allows to use OGC services
from Python code. You can find out more information about this library (including the license terms) in
<https://geopython.github.io/OWSLib/>. I have included the sources of this library in the repository to make
it easier to clone and test this, but that is clearly a quick-and-dirty solution.

On Linux, you can clone the repository locally with this command:

`$git clone https://github.com/rbejar/odrl-ogc-cache-policies`

After that, you can give ODRL_Paper.py file run permission and
then run it:

    $cd odrl-ogc-cache-policies
    $chmod u+x ODRL_Paper.py
    $./ODRL_Paper.py
    
As long as you have Python 2.7.x installed, this will work. This is
the result of a run of this program:

    ###### TEST1 #####
    Have you reviewed and agreed to the archive policies of http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs? (Y/N): y
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs
    Cache this content: 
    - Content id: Full Service
    - Request_rate?: False
    - Archive time limit?: False
    ###### TEST2 #####
    Have you obtained the consent to archive http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites? (Y/N): y
    Have you reviewed and agreed to the archive policies of http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites? (Y/N): y
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs
    Cache this content: 
    - Content id: http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites
    - Request_rate?: True
      (Times per minute:5)
    - Archive time limit?: True
      (Number of months: 6)
    ###### TEST3 #####
    Caching has not been allowed for the services and contents requested
    ###### TEST4 #####
    Have you reviewed and agreed to the archive policies of http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs#TestODRL3:states? (Y/N): y
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs
    Cache this content: 
    - Content id: http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs#TestODRL3:states
    - Request_rate?: False
    - Archive time limit?: False
    ###### TEST5 #####
    Have you obtained the consent to archive http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites? (Y/N): y
    Have you reviewed and agreed to the archive policies of http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites? (Y/N): y
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs
    Cache this content: 
    - Content id: http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:archsites
    - Request_rate?: True
      (Times per minute:5)
    - Archive time limit?: True
      (Number of months: 6)
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs
    Cache this content: 
    - Content id: http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:roads
    - Request_rate?: True
      (Times per minute:5)
    - Archive time limit?: False
    ###### TEST6 #####
    For this service: 
    - http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs
    Cache this content: 
    - Content id: http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs#TestODRL1:roads
    - Request_rate?: True
      (Times per minute:5)
    - Archive time limit?: False

