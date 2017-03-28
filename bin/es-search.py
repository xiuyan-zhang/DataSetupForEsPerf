#!/usr/bin/env python
import datetime, sys, getopt
import requests
import json
import time
import glob
import os
import traceback
import re
#
#######################################################################
#
# The python util to search ES indecs by hash and/or timestamp.
# v1.0 Created by Jeffrey, Zhang on Mar 28, 2017.
#
#######################################################################

def search(uri, query):
	#response = requests.get(uri, data=json.dumps(query), timeout=(5, 60))
	response = requests.get(uri, data=query, timeout=(5, 60))
	results = json.loads(response.text)
	return results

def main(argv):
	global api_server,es_search,org,token,User
	global currday
	global debug
	debug=False
	token='NThiODdkYzRlNGIwNThkZTI3ODczNDY0OjBwbkNjbnNNRkpzZGhxeVFBWmVVRkNmdU9oRw=='
	try:
		opts, args = getopt.getopt(argv,"ht:a:r:e:",["time=","hash=","resource=","env=","debug="])
	except getopt.GetoptError:
		print ('es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]')
		sys.exit(1)
	if len(sys.argv) <4:
		print ('es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]')
			sys.exit()
		elif opt in ("-e", "--env"):
			env = arg
		elif opt in ("-r", "--resource"):
			resource = arg
		elif opt in ("-a", "--hash"):
			hash = arg
		elif opt in ("-t", "--epoch_ms"):
			epoch_ms = arg
		elif opt in ("-d", "--debug"):
			debug = True
	if 'env' not in locals():
		print ('es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]')
	if 'hash' not in locals() and epoch_ms not in locals():
		print ('es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]')

	if env == 'staging':
		api_server = 'https://api-staging.salesforceiq.com'
		es_search = "http://timeline-search-staging.amz.relateiq.com:9200/indexedevent_templates/IndexedEvent/_search?pretty"
	else:
		print ('env '+env+' not supported yet.')
                sys.exit(3)

	query=''
	if 'hash' in locals():
		query='{"query": {"bool": {"must": [{"match": {"eventKey.hash": "'+hash+'"}}'
	if 'epoch_ms' in locals():
		query=query+',{"match": { "eventKey.creationTime": "'+epoch_ms+'"}}'

	query=query+']}}}'
	print 'query = ',query
	print
	results=search(es_search, query)
	#print results['hits']['hits']
	for singleResults in results['hits']['hits']:
		#print singleResults["_source"]["contributorURNs"]
		print singleResults["_source"]["eventKey"]["type"],singleResults["_source"]["involvedContactURNs"]
if __name__ == "__main__":
	#print(os.path.dirname(os.path.realpath(__file__)))
	main(sys.argv[1:])
