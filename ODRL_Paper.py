#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

# Copyright (C) 2014 Rubén Béjar {http://www.rubenbejar.com/}
# An experimental implementation for the protocol defined in this paper:
# A protocol for machine-readable cache policies in OGC web services: Application to the EuroGeoSource information system.  R. BÉJAR, F.J. LOPEZ-PELLICER, J. NOGUERAS-ISO, F.J. ZARAZAGA-SORIA, P.R. MURO-MEDRANO.  Environmental Modelling & Software.  2014,  vol. 60,  p. 346-356, doi:10.1016/j.envsoft.2014.06.026.
# <http://dx.doi.org/doi:10.1016/j.envsoft.2014.06.026>

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import copy
import re
import urllib2
import xml.etree.ElementTree as ET
from owslib.wfs import WebFeatureService

def algorithm1(all_services, all_contents):
    # Numbers in comments show the correspondence between the line numbers
    # in the published algorithm and this program. Even though the published
    # algorithm is in a high-level pseudocode, and thus a line by line translation  
    # is not necessarily the best option, we have made an effort to
    # make this program as similar as possible to to that algorithm
      
    services_contents = zip(all_services, all_contents)  # 1,2    
    services_contents_out = copy.deepcopy(services_contents)  
    for (service, contents) in services_contents: # 3
        odrl_string = getODRL(service)
        odrl_policy = ET.fromstring(odrl_string) # 4 
        if protocol_version(odrl_policy) != 'Draft_Proposal': # 5, 6
            raise NotImplementedError('Protocol version not supported') # 7
        service_read_perm, service_uid = get_service_read_perm(odrl_policy) # 9
        if not are_service_read_duties_fulfilled(service_read_perm, service_uid): # 10, 11
            services_contents_out.remove((service, contents)) # 12
        else: # 13
            if len(contents) > 0:
                service_arch_perm = get_service_archive_perm(odrl_policy, service_uid) # 15
                if contents[0] == 'Full Service': # 14                    
                    if not are_service_archive_duties_fulfilled(service_arch_perm, service_uid): # 16 ,17                    
                        services_contents_out.remove((service, contents)) # 18
                else: # 20
                    contents_out = copy.deepcopy(contents)
                    for c in contents: # 21
                        content_arch_perm = get_content_archive_perm(odrl_policy, service_uid, c) # 22                                        
                        if not are_content_archive_duties_fulfilled(content_arch_perm, service_arch_perm, service_uid, c): # 23, 24
                            contents_out.remove(c) # 25
                    services_contents_out[services_contents.index((service, contents))] = (service, contents_out) 
    return services_contents_out            
                        

def algorithm2(all_services, all_contents):
    # Numbers in comments show the correspondence between the line numbers
    # in the published algorithm and this program. Even though the published
    # algorithm is in a high-level pseudocode, and thus a line by line translation  
    # is not necessarily the best option, we have made an effort to
    # make this program as similar as possible to that algorithm
    
    services_to_cache = [] # 1
    contents_to_cache = [] # 2
    services_contents = zip(all_services, all_contents)    
    for (service, contents) in services_contents: # 3
        odrl_string = getODRL(service)
        odrl_policy = ET.fromstring(odrl_string) # 4        
        if protocol_version(odrl_policy) != 'Draft_Proposal': # 5, 6
            raise NotImplementedError('Protocol version not supported') # 7
        service_read_perm, service_uid = get_service_read_perm(odrl_policy) # 9
        if not is_service_caching_prohibited(odrl_policy, service_uid): # 10
            if len(contents) > 0:
                service_arch_perm = get_service_archive_perm(odrl_policy, service_uid) # 13
                if contents[0] == 'Full Service': # 11
                    if is_service_caching_permitted(odrl_policy, service_uid): # 12                       
                        services_to_cache.append(service) # 14
                        contents_to_cache.append(('Full Service',  get_request_rate(service_read_perm),
                                                  get_elapsed_time(service_arch_perm))) # 14
                else: # 16  
                    for c in contents: # 17                        
                        if is_content_caching_permitted(odrl_policy, service_uid, c): # 18
                            content_arch_perm = get_content_archive_perm(odrl_policy, service_uid, c) # 19                            
                            services_to_cache.append(service) # 20
                            contents_to_cache.append((service+'#'+c, get_request_rate(service_read_perm),
                                                      get_elapsed_time(content_arch_perm))) # 20
                        else: # 21
                            if not is_content_caching_prohibited(odrl_policy, service_uid, c): # 22
                                services_to_cache.append(service) # 23
                                contents_to_cache.append((service+'#'+c, get_request_rate(service_read_perm), 
                                                          get_elapsed_time(service_arch_perm))) # 23
    # 30
    if len(services_to_cache) > 0:
        for service, contents in zip(services_to_cache, contents_to_cache):
            print("For this service: ")
            print("- " + service)
            print("Cache this content: ")
            print("- Content id: " + contents[0])
            req_rate = contents[1][0]
            print("- Request_rate?: " + str(contents[1][0]))
            if req_rate:
                print("  (Times per minute:" + str(contents[1][1]) + ")")
            arch_limit = contents[2][0]            
            print("- Archive time limit?: " + str(arch_limit)) 
            if arch_limit:
                print("  (Number of months: " + str(contents[2][1]) + ")")        
    else:
        print("Caching has not been allowed for the services and contents requested")
            
def algorithm1_to_algorithm2(services_contents_go_ahead):
    """
    Transforms the output of algorithm1 in something
    directly usable by algorithm2 (it just divides
    the response of algorithm1 in two different lists)
    """
    services_go_ahead = []
    contents_go_ahead = []
    for service, contents in services_contents_go_ahead:
        services_go_ahead.append(service)
        contents_go_ahead.append(contents)
    return (services_go_ahead, contents_go_ahead)
             
        
def getODRL(serviceURL):
    wfs = WebFeatureService(serviceURL)
    wfs.getcapabilities()    

    candidateURLs = re.findall(r'(https?://[^\s]+)', wfs.identification.accessconstraints)
    for url in candidateURLs:        
        response = urllib2.urlopen(url)
        response_text = response.read()
        if is_valid_protocol(response_text):
            return response_text
    # If we are here, there is not any valid ODRL XML in any of the URLs in Access Constraints
    return None
        
def is_valid_protocol(string):       
    # A robust implementation should use an XML parser 
    # to ensure validity and ODRL XML schema compliance
    # This experiment only checks for the existence
    # of a an ODRL Policy tag     
    if '<o:policy' in string:
        return True
    else:
        return False
    
def protocol_version(policy_element):    
    metadata = policy_element.find('{http://geoprotocol.odrl2.com/metadata}metadata')            
    version = metadata.find('{http://purl.org/dc/elements/1.1/}identifier')
    return version.text
        
def get_service_read_perm(policy_element):
    permissions = policy_element.findall('{http://w3.org/ns/odrl/2/}permission')
    for perm in permissions:
        action = perm.find('{http://w3.org/ns/odrl/2/}action')
        if action.attrib['name'] == 'http://w3.org/ns/odrl/vocab#read':
            service_uid = perm.find('{http://w3.org/ns/odrl/2/}asset').attrib['uid']
            return (perm, service_uid)
    return (None, None)

def are_permission_duties_fulfilled(permission_element, element_id, description):    
    if permission_element is None:
        return True # If there is no permission element, there are not any duties associated,  
                    # so we can't "unfulfill" them
    duties = permission_element.findall('{http://w3.org/ns/odrl/2/}duty')
    for duty in duties:
        action = duty.find('{http://w3.org/ns/odrl/2/}action')
        if action.attrib['name'] == 'http://w3.org/ns/odrl/vocab#obtainconsent':
            answer = ''
            while (answer not in ['y', 'Y', 'n', 'N']):
                answer = raw_input('Have you obtained the consent to ' + description +  
                                   ' ' + element_id + '? (Y/N): ')
            if answer not in ['y', 'Y']:
                return False
        elif action.attrib['name'] == 'http://w3.org/ns/odrl/vocab#reviewpolicy':
            answer = ''
            while (answer not in ['y', 'Y', 'n', 'N']):
                answer = raw_input('Have you reviewed and agreed to the ' + description + 
                                   ' policies of ' + element_id + '? (Y/N): ' )
            if answer not in ['y', 'Y']:
                return False
    return True

def are_service_read_duties_fulfilled(service_read_permission_element, service_uid):    
    return are_permission_duties_fulfilled(service_read_permission_element, service_uid, 'read')

def are_service_archive_duties_fulfilled(service_archive_permission_element, service_uid):    
    return are_permission_duties_fulfilled(service_archive_permission_element, service_uid, 'archive')

def are_content_archive_duties_fulfilled(content_archive_permission_element, 
                                         service_archive_permission_element, service_uid, c):    
    # If there is not an explicit permission for a content,
    # its duties are those established for the permission for the whole service
    if content_archive_permission_element is None:
        return are_permission_duties_fulfilled(service_archive_permission_element, service_uid+'#'+c, 'archive')
    else:
        return are_permission_duties_fulfilled(content_archive_permission_element, service_uid+'#'+c, 'archive')

def get_archive_perm(policy_element, uid):
    permissions = policy_element.findall('{http://w3.org/ns/odrl/2/}permission')
    for perm in permissions:
        action = perm.find('{http://w3.org/ns/odrl/2/}action')
        if action.attrib['name'] == 'http://w3.org/ns/odrl/vocab#archive':
            asset = perm.find('{http://w3.org/ns/odrl/2/}asset')            
            if asset.attrib['uid'] == uid:
                return perm
    return None
    
def get_service_archive_perm(policy_element, service_uid):
    return get_archive_perm(policy_element, service_uid)
    
def get_content_archive_perm(policy_element, service_uid, content_id):
    return get_archive_perm(policy_element, service_uid+"#"+content_id)
   
def get_request_rate(service_read_permission):
    constraints = service_read_permission.findall('{http://w3.org/ns/odrl/2/}constraint')
    exists_count = False
    exists_timeInterval = False
    for constr in constraints:
        if constr.attrib['name'] == 'http://w3.org/ns/odrl/vocab#count':
            count = int(constr.attrib['rightOperand'])
            exists_count = True 
        elif constr.attrib['name'] == 'http://w3.org/ns/odrl/vocab#timeInterval':    
            timeInterval = constr.attrib['rightOperand']
            exists_timeInterval = True
            n_hours = int(timeInterval[3:-1]) # Assuming format as in template RPTnH
            # An ISO 8601 parser would be necessary for other combinations in a complete
            # implementation
    if exists_count and exists_timeInterval:
        return (True, count / (n_hours * 60))
    else:
        return (False, 0)

def get_elapsed_time(archive_permission_element):
    if archive_permission_element is None:
        return (False, 0)
    constraints = archive_permission_element.findall('{http://w3.org/ns/odrl/2/}constraint')
    exists_elapsed = False
    for constr in constraints:
        if constr.attrib['name'] == 'http://w3.org/ns/odrl/vocab#elapsedTime':
            elapsed_time = constr.attrib['rightOperand']
            exists_elapsed = True 
            n_months = int(elapsed_time[1:-1]) # Assuming format as in template PnM
            # An ISO 8601 parser would be necessary for other combinations in a 
            # complete implementation
    if exists_elapsed:
        return (True, n_months)
    else:
        return (False, 0)
 
def is_service_caching_permitted(policy_element, service_uid):
    if get_service_archive_perm(policy_element, service_uid) is not None:    
        return True           
    else:
        return False

def is_content_caching_permitted(policy_element, service_uid, content_id):
    if get_content_archive_perm(policy_element, service_uid, content_id) is not None:    
        return True                    
    else:        
        return False
    

def is_element_caching_prohibited(policy_element, element_id):
    prohibitions = policy_element.findall('{http://w3.org/ns/odrl/2/}prohibition')
    for prohib in prohibitions:
        action = prohib.find('{http://w3.org/ns/odrl/2/}action')
        if action.attrib['name'] == 'http://w3.org/ns/odrl/vocab#archive':
            asset = prohib.find('{http://w3.org/ns/odrl/2/}asset')
            if asset.attrib['uid'] == element_id: 
                return True           
    return False

def is_service_caching_prohibited(policy_element, service_uid):
    return is_element_caching_prohibited(policy_element, service_uid)
  
def is_content_caching_prohibited(policy_element, service_uid, content_id):
    return is_element_caching_prohibited(policy_element, service_uid+'#'+content_id)       



################################################
################################################

# Three WFS services have been set up for testing:
# - TestODRL1 license does not allow full caching: permission for 
#   a FeatureType and prohibition for another one are explicitly
#   included. There are two duties and one constraint for the
#   permission: consent must be obtained and policies must be
#   reviewed (by a human), and the cache can only be kept for
#   6 months or lesss.
#   There is also a constraint associated to the read permission 
#   on the service: at most 300 accesss per hour to the service  
#   The protocol says there are implicit permissions without
#   duties or constraints for the other FeatureTypes. It is not a very
#   realistic case, but it is a good case for testing.
# - TestODRL2 license is a full cache prohibition.
# - TesTODRL3 license is a full cache permission with a duty: a
#   human must review the archive policy before proceeding.

testODRL1URL = 'http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL1/wfs'
testODRL2URL = 'http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL2/wfs'
testODRL3URL = 'http://mularroya05.cps.unizar.es:8081/geoserver/TestODRL3/wfs'

def test1():
    """
    We want to make a full cache of services TestODRL1, TestODRL2 and TestODRL3.
    The license for the first does not allow full caching,
    and the license of the second prohibits caching, so this
    test will end up showing that we can cache only TestODRL3 (without constraints), but only
    after confirming with the user that the archive policies of the service
    have been read.
    """
    print('###### TEST1 #####')
    all_services = [testODRL1URL,
                    testODRL2URL,
                    testODRL3URL]
    all_contents = [['Full Service'],['Full Service'],['Full Service']]
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead)
       
def test2():
    """
    We want to cache the only content allowed in TestODRL1 (archsites).
    After confirming that we have fulfilled the duties on that content
    (obtainconsent and reviewpolicy) we can proceed to cache with
    the given constraints (maximum 6 months of cache, 300 requests per
    hour (5 per minute) maximum). If the duties are not fulfilled, 
    no caching is allowed.
    """
    print('###### TEST2 #####')
    all_services = [testODRL1URL]
    all_contents = [['TestODRL1:archsites']]
   
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead)     
    
def test3():
    """
    We want to cache the only content prohibited in TestODRL1 (bugsites).
    No caching is allowed.
    """
    print('###### TEST3 #####')
    all_services = [testODRL1URL]
    all_contents = [['TestODRL1:bugsites']]
   
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead) 
    
def test4():    
    """
    We want to cache only one content from TestODRL3 (states).
    The license for that service says that full service caching
    is allowed, so after checking that duties associated with
    the full service caching are fulfilled (reviewPolicy), it 
    allows to cache the contents requested.
    """
    print('###### TEST4 #####')
    all_services = [testODRL3URL]
    all_contents = [['TestODRL3:states']]
   
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead)
    
def test5():    
    """
    We want to cache only two contents from TestODRL1 (archsites and roads).
    The license for that service says that caching archsites is
    permitted, and caching bugsites is prohibited.
    As far as no prohibition is related to
    roads, the protocol says that we must be allowed to 
    cache both (archsites and roads).
    There are two duties (reviewPolicy and obtainConsent) associated 
    with the permission to archive archsites: the algorithm1 will make sure 
    that we have fulfilled them before proceeding. If we don't, it will allow us
    to cache only roads, because that content does not have any duties associated.
    There is a constraint for the full service that says that we can
    at most make 300 requests per hour (5 per minute). This will be
    associated to both contents.
    There is a constraint for archsites, that says that we can only keep
    it cached for 6 months. As the protocol says, this does not apply to
    roads.
    """
    print('###### TEST5 #####')
    all_services = [testODRL1URL]
    all_contents = [['TestODRL1:archsites', 'TestODRL1:roads']]
   
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead)

def test6():    
    """
    We want to cache only two contents from TestODRL1 (bugsites and roads).
    The license for that service says that caching archsites is
    permitted, and caching bugsites is prohibited.
    As far as no prohibition is related to
    roads, the protocol says that we must be allowed to 
    cache roads, but not bugsites.
    There is a constraint for the full service that says that we can
    at most make 300 requests per hour (5 per minute). This will be
    associated to roads.    
    """
    print('###### TEST6 #####')
    all_services = [testODRL1URL]
    all_contents = [['TestODRL1:bugsites', 'TestODRL1:roads']]
   
    services_contents_go_ahead = algorithm1(all_services, all_contents)
    services_go_ahead, contents_go_ahead = algorithm1_to_algorithm2(services_contents_go_ahead)
    algorithm2(services_go_ahead, contents_go_ahead)

def main():    
    """
    Launch all the tests.
    """
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    
# Allow use both as module and script
if __name__ == "__main__": # script
    main()
else:    
    pass
    # Module specific initialization 
