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
import math
import string
import random
from pymongo import MongoClient
from bson.objectid import ObjectId
import inspect
#######################################################################
#
# The program setups the Users, Emails and Meetings per the Spec defined in a config file.
# v1.0 Created by Jeffrey, Zhang on Mar 28, 2017.
#
#######################################################################

def myFormula(p, formula):
    return eval(formula)

def logging(p_log,p_line):
	global currday
	now=datetime.datetime.today().strftime('%y%m%d-%H%M%S')
	today=datetime.datetime.today().strftime('%y%m%d')
	if log_dict.has_key(p_log): 
		log=log_dict[p_log]
		if  currday != today:
			try:
				log.close()
		 	except error:
				a=1
			log=open(bin_dir+'/../log/'+p_log+'.'+today+'.log','a')
			currday=today
			log_dict[p_log]=log
	else:
		log=open(bin_dir+'/../log/'+p_log+'.'+today+'.log','a')
		log_dict[p_log]=log
		if currday != today:
			currday=today
	insp=inspect.stack()[1][3]
	log.write(now+','+insp+','+p_line+'\n')
	

def id_generator(size=6, chars= string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def user_setting(p_SfdcUserId,p_Id,p_SfdcUserIdEmail,p_ExternalOrgId):
	sfdc_path='/v2/sfdc/v40.0/user/org/'+org+'/settings/preferences/boolean/set?settingName=AutomaticActivityCapture'
	print 'Posting at '+api_server+sfdc_path
	headers = {'content-type': 'application/json', 'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache', 'SfdcUserId': p_SfdcUserId}
	payload = {'name': 'AutomaticActivityCapture', 'label': 'Automatic activity capture enabled', 'readOnly': False, 'value': True}
	req = requests.post(api_server+sfdc_path, data=json.dumps(payload), headers=headers)
	new_org_settings=req.json()
	print new_org_settings['name'],new_org_settings['label'],new_org_settings['readOnly'],new_org_settings['lastModified'],new_org_settings['value'],new_org_settings['collection'],new_org_settings['className'],new_org_settings['valueContainerType']
	#logging('settings', p_SfdcUserId+','+new_org_settings['name']+','+str('' if new_org_settings['label'] is None else new_org_settings['label'])+','+str(new_org_settings['readOnly'])+','+str(new_org_settings['lastModified'])+','+str(new_org_settings['value'])+','+str(new_org_settings['collection'])+','+new_org_settings['className']+','+new_org_settings['valueContainerType'])
	logging('settings', p_SfdcUserId+','+p_Id+','+p_SfdcUserIdEmail+','+p_ExternalOrgId+','+new_org_settings['name']+','+str(new_org_settings['lastModified'])+','+new_org_settings['className'])

def create_user_settings():
	print 'Posting create User Settings for externalOrgId='+org
	for user in User.find({'externalOrgId':org}):	
		SfdcUserId=user['externalId']
		Id=str(user['_id'])
		SfdcUserIdEmail=user['sfdcemail']
		ExternalOrgId=user['externalOrgId']
		user_setting(SfdcUserId,Id,SfdcUserIdEmail,ExternalOrgId)

def admin_setting(p_SfdcUserId,p_Id,p_SfdcUserIdEmail,p_ExternalOrgId):
	sfdc_path='/v2/sfdc/v40.0/admin/org/'+org+'/settings/boolean/set?settingName=AutomaticActivityCapture'
	print 'Posting at '+api_server+sfdc_path
	headers = {'content-type': 'application/json', 'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache', 'SfdcUserId': p_SfdcUserId}
	payload = {'name': 'AutomaticActivityCapture', 'label': 'Automatic activity capture enabled', 'readOnly': False, 'value': True}
	req = requests.post(api_server+sfdc_path, data=json.dumps(payload), headers=headers)
	new_org_settings=req.json()
	print new_org_settings['name'],new_org_settings['label'],new_org_settings['readOnly'],new_org_settings['lastModified'],new_org_settings['value'],new_org_settings['collection'],new_org_settings['className'],new_org_settings['valueContainerType']
	#logging('settings', p_SfdcUserId+','+new_org_settings['name']+','+new_org_settings['label']+','+str(new_org_settings['readOnly'])+','+str(new_org_settings['lastModified'])+','+str(new_org_settings['value'])+','+str(new_org_settings['collection'])+','+new_org_settings['className']+','+new_org_settings['valueContainerType'])
	logging('settings', p_SfdcUserId+','+p_Id+','+p_SfdcUserIdEmail+','+p_ExternalOrgId+','+new_org_settings['name']+','+str(new_org_settings['lastModified'])+','+new_org_settings['className'])

def create_admin_settings():
	print 'Posting create Admin Settings for externalOrgId='+org
	for user in User.find({'externalOrgId':org}):	
		SfdcUserId=user['externalId']
		Id=str(user['_id'])
		SfdcUserIdEmail=user['sfdcemail']
		ExternalOrgId=user['externalOrgId']
		admin_setting(SfdcUserId,Id,SfdcUserIdEmail,ExternalOrgId)

def create_users(p_max_users,p_userId,p_firstName,p_lastName,p_email):
	sfdc_path='/v2/sfdc/v40.0/user/org/'+org+'/register'
	print 'Posting create Users for externalOrgId='+org
	print 'Posting at '+api_server+sfdc_path
	headers = {'content-type': 'application/json', 'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache'}

	suffix_size=18-len(p_userId)
	p_email_id,domain=p_email.split('@')
	for i in range(int(p_max_users)):
		rid=id_generator(suffix_size)
		userId=p_userId+rid
		firstName=p_firstName+rid
		lastName=p_lastName+rid
		email=p_email_id+rid+'@'+domain
		#print email
		payload = {'userId': userId, 'firstName': firstName, 'lastName': lastName, 'email': email}
		req = requests.post(api_server+sfdc_path, data=json.dumps(payload), headers=headers)
		id = req.json()['userId']
		new_user=User.find_one({'_id': ObjectId(id)})
		#print req.text,req.content,req.json()
		print new_user['externalId'],new_user['_id'],new_user['sfdcemail'],new_user['externalOrgId']
		logging('users',new_user['externalId']+','+id+','+new_user['sfdcemail']+','+new_user['externalOrgId'])
		admin_setting(new_user['externalId'],id,new_user['sfdcemail'],new_user['externalOrgId'])
		user_setting(new_user['externalId'],id,new_user['sfdcemail'],new_user['externalOrgId'])
	
def create_email(p_sendDate,p_author,p_owners,p_contributions,p_to_contacts,p_cc_contacts):
        sfdc_path='/v2/sfdc/v40.0/test/org/'+org+'/saveEmail'
	v_title='ES Performance Test Email'
	v_body='ES Performance test email body one two three'
	v_bodySummary='ES Performance Test Email Body'
	v_mine=True
        print 'Posting at '+api_server+sfdc_path
        headers = {'content-type': 'application/json', 'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache'}
	payload = {'type': 'com.siqaas.sfdc.mappings.SfdcEmailWrapper', 'date': p_sendDate, 'author': p_author, 'title': v_title,  'owners': p_owners, 'contributions': [{'owner':p_contributions}], 'body': v_body, 'bodySummary': v_bodySummary, 'mine': v_mine, 'email': {'to': p_to_contacts, 'cc': p_cc_contacts}}
	req = requests.post(api_server+sfdc_path, data=json.dumps(payload), headers=headers)
	##print req.json()
	print 'response',req.json()['eventKey']+','+req.json()['resourceId']
	if debug:
		logging('emails',str(p_sendDate)+','+req.json()['eventKey']+','+req.json()['resourceId']+','+p_author+','+str(p_to_contacts))
	else:
		logging('emails',str(p_sendDate)+','+req.json()['eventKey']+','+req.json()['resourceId'])
	#sys.exit(10)

def create_meeting(p_sendDate,p_author,p_owners,p_contributions,p_eventAttendees):
        sfdc_path='/v2/sfdc/v40.0/test/org/'+org+'/saveMeeting'
	v_title='ES Performance Test Meeting'
	v_body='ES Performance test meetiing body one two three'
        print 'Posting at '+api_server+sfdc_path
	startTime=p_sendDate+86400+random.randint(0,2*3600)
	endTime=p_sendDate+86400+random.randint(0,3*3600)
        headers = {'content-type': 'application/json', 'Authorization': 'Basic '+token, 'Cache-Control': 'no-cache'}
	payload = {'type': 'com.siqaas.sfdc.mappings.SfdcMeetingWrapper', 'date': p_sendDate, 'author': p_author, 'title': v_title,  'owners': p_owners, 'contributions': [{'owner':p_contributions}], 'body': v_body, 'calendar': {'eventAttendees': p_eventAttendees, 'startTime': startTime, 'endTime': endTime, 'timeZone': 'America/Los_Angeles', 'allDay': False, 'eventLocations': []}}
	req = requests.post(api_server+sfdc_path, data=json.dumps(payload), headers=headers)
	##print req.json()
	print 'response',req.json()['eventKey']+','+req.json()['resourceId']
	if debug:
		logging('meetings',str(p_sendDate)+','+req.json()['eventKey']+','+req.json()['resourceId']+','+p_author+','+str(p_eventAttendees))
	else:
		logging('meetings',str(p_sendDate)+','+req.json()['eventKey']+','+req.json()['resourceId'])
	#sys.exit(10)

def create_events(p_event_name,p_daily_emails,p_start_date,p_end_date,p_start_time,p_end_time,p_inv_contact_pct_dist,p_inv_contact_fun):
	customer_domain='google.com'
	global SfdcUserIdList
	SfdcUserIdList=[]
	SfdcUserEmailList=[]
	epoch = datetime.datetime(1970, 1, 1)
	print 'Posting Create '+p_event_name+' for externalOrgId='+org
	print p_start_date,p_end_date,p_start_time,p_end_time
	debug_cnt=5
	for user in User.find({'externalOrgId':org}):	
		SfdcUserIdList.append(user['externalId'])
		SfdcUserEmailList.append(user['sfdcemail'])
	dt=datetime.datetime.strptime(p_start_date,'%Y-%m-%d')
	tz=int(time.strftime('%z'))
	while dt<=datetime.datetime.strptime(p_end_date,'%Y-%m-%d'):
		if dt.weekday() < 5:
			dtepoch = (dt - epoch).total_seconds()
			#print dt,dtepoch
			for user in User.find({'externalOrgId':org}):	
				if debug:
					debug_cnt=debug_cnt-1
					if debug_cnt==0:
						debug_cnt=5
						break
				sfdcUserId=user['externalId']
				author='email::'+user['sfdcemail']
				#contributions=["{'owner','"+sfdcUserId+"'}"]	
				#contributions=[{'owner',sfdcUserId}]	
				contributions=sfdcUserId
				# t times of log(OrgSize)
				t=0
				switch=0
				#involvedContactURNs
				#bucketing e.g, 5 x 20%
				for i in range(len(p_inv_contact_pct_dist)):
					print 'bucket#',i,'#emails',int(math.ceil(int(p_inv_contact_pct_dist[i])*int(p_daily_emails)/100))
					t=t+1
					#each bucket need to send a percentage of the emails in related to the daily emails
					for j in range(int(math.ceil(int(p_inv_contact_pct_dist[i])*int(p_daily_emails)/100))):
						sendDate=int(dtepoch*1000+random.randint(int(p_start_time)*3600000,int(p_end_time)*3600000))-tz*36000
						owners=[sfdcUserId,SfdcUserIdList[random.randint(0,len(SfdcUserIdList)-1)],SfdcUserIdList[random.randint(0,len(SfdcUserIdList)-1)],SfdcUserIdList[random.randint(0,len(SfdcUserIdList)-1)],SfdcUserIdList[random.randint(0,len(SfdcUserIdList)-1)]]
						#print 'email prepared at'j,str(sendDate)
						to_contacts=[]
						cc_contacts=[]
						eventAttendees=[]
						#involvedURN (to_contacts+cc_contacts, or eventAttendees) would be t times of log(OrgSize)
						for k in range(int(math.ceil(t*myFormula(len(SfdcUserIdList),"math.log(p)")/2))):
							if p_event_name == 'meetings':
								eventAttendees.append({'urn': 'email::'+SfdcUserEmailList[random.randint(0,len(SfdcUserIdList)-1)], 'rsvpStatus': 'CONFIRMED'})				
								eventAttendees.append({'urn': 'email::'+'customer'+str(random.randint(0,999))+'@'+customer_domain, 'rsvpStatus': 'CONFIRMED'})				
								continue
							if switch == 0:
								to_contacts.append("email::"+SfdcUserEmailList[random.randint(0,len(SfdcUserIdList)-1)])
								cc_contacts.append("email::"+"customer"+str(random.randint(0,999))+'@'+customer_domain)
								switch=1
							else:
								to_contacts.append("email::"+"customer"+str(random.randint(0,999))+'@'+customer_domain)
								cc_contacts.append("email::"+SfdcUserEmailList[random.randint(0,len(SfdcUserIdList)-1)])
								switch=0
						if p_event_name == 'meetings':
							print 'send_mting',sendDate,author,owners,contributions,eventAttendees
							create_meeting(sendDate,author,owners,contributions,eventAttendees)
						else:
							print 'send_mail',sendDate,author,owners,contributions,to_contacts,cc_contacts
							create_email(sendDate,author,owners,contributions,to_contacts,cc_contacts)
		dt=dt+datetime.timedelta(days=1)
def main(argv):
	global api_server,es_search,org,token,User
	global log_dict
	log_dict={}
	global currday
	currday='170101'
	global debug,bin_dir
	debug=False
	token='NThiODdkYzRlNGIwNThkZTI3ODczNDY0OjBwbkNjbnNNRkpzZGhxeVFBWmVVRkNmdU9oRw=='
	bin_dir=os.path.dirname(os.path.realpath(__file__))
#
	try:
		opts, args = getopt.getopt(argv,"hc:a:e:d:",["config=","action=","env=","debug="])
	except getopt.GetoptError:
		print ('es-setup.py -c <config> -a <action> -e <env> -d <debug>')
		sys.exit(1)
	if len(sys.argv) <6:
		print ('es-setup.py -c <config> -a <action:org|users|admin_settings|user_settings|emails|meetings> -e <env> [-d <debug>]')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('es-setup.py -c <config> -a <action:org|users|admin_settings|user_settings|emails|meetings> -e <env> [-d <debug>]')
			sys.exit()
		elif opt in ("-c", "--config"):
			config = arg
		elif opt in ("-a", "--action"):
			action = arg
		elif opt in ("-e", "--env"):
			env = arg
		elif opt in ("-d", "--debug"):
			debug = True
	if env == 'staging':
		api_server = 'https://api-staging.salesforceiq.com'
		es_search = "http://timeline-search-staging.amz.relateiq.com:9200/indexedevent_templates/IndexedEvent/_search?pretty"
	else:
		print ('env '+env+' not supported yet.')
                sys.exit(3)
	if action == 'org':
		print ('action '+action+' not supported yet.')
		sys.exit(4)
	#if not os.path.exists('../conf/'+config):
	if not os.path.exists(bin_dir+'/../conf/'+config):
		print ('file '+bin_dir+'/../conf/'+config+' does not exist.')
		print ('es-setup.py -c <config> -a <action> -e <env>')
		sys.exit(5)

	User = MongoClient(host=['mongo-staging.amz.relateiq.com:27017'])['lucid_prod']['User']

	for cline in open(bin_dir+'/../conf/'+config,'r'):
		parts=cline.split(',')
		if re.search('^#',parts[0]):
			continue
		elif parts[0] == 'org':
			org=parts[1].rstrip()
		elif parts[0] == 'users':
			dummy,max_users=parts[1].split(':')
			dummy,userId=parts[2].split(':')
			dummy,firstName=parts[3].split(':')
			dummy,lastName=parts[4].split(':')
			dummy,email=parts[5].split(':')
			email=email.rstrip()
			if action == 'users':
				create_users(max_users,userId,firstName,lastName,email)
			elif action == 'admin_settings':
				create_admin_settings()
			elif action == 'user_settings':
				create_user_settings()
		elif (parts[0] == 'emails' or parts[0] == 'meetings') and parts[0] == action:
			dummy,daily_events=parts[1].split(':')
			dummy,start_date=parts[2].split(':')
			dummy,end_date=parts[3].split(':')
			dummy,start_time=parts[4].split(':')
			dummy,end_time=parts[5].split(':')
			dummy,inv_contact_pct=parts[6].split(':')
			inv_contact_pct_dist=inv_contact_pct.split('/')
			dummy,inv_contact_fun=parts[7].split(':')
			inv_contact_fun=inv_contact_fun.rstrip()
			create_events(parts[0],daily_events,start_date,end_date,start_time,end_time,inv_contact_pct_dist,inv_contact_fun)
				

if __name__ == "__main__":
	main(sys.argv[1:])
