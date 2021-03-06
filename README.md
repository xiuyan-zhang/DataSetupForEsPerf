# DataSetupForEsPerf
The initial version of the IQ system data setup for ES Performance Project.

1) Executive Summary

This project is used to setup the Users including the Admin and User Settings, Emails and Meetings per the specs defined in a configuration file.

1.1) ./es-setup.py

es-setup.py -c <config> -a <action:org|users|admin_settings|user_settings|emails|meetings> -e <env> [-d <debug>]

1.2) ./es-search.py

es-setup.py -e <env> -h <hash> [-t <epoch_ms> -d <debug>]

2) The Specification 

The specs include 

2.1) the number of users, userId prefix, firstName and lastName prefix, email name prefix and the domain for the org.

2.2) the number of emails daily, start date and end_date, start_time and end_time, percentage distributions of the emails with a specific number of InvolvledContracts, the function for the number of InvolvledContracts in related to the org size

2.3) the number of meetings daily, start date and end_date, start_time and end_time, percentage distributions of the meetings with a specific number of InvolvledContracts, the function for the number of InvolvledContracts in related to the org size.

3) You Might Want to Know

3.1) The emails/meetings are generated to simulate the crawl results. hence the save API used.

3.2) As long as the programs are in the PATH, and you re on the IQ VPN you could run it from current directory

3.3) The org has to  exist, defined in the config file, in order set up data under the org.

3.4) When an user is created, it is assigned to admin_settings and user_settings. However the options are given to associate the settings to all users under the org.

3.5) Token used is hard coded for now.

3.6) It is only supported in staging environment.

4) To be Enhanced

4.1) The meeting is scheduled for an hour at the hour 25 hours later. This might be enhanced by introducing knobs in the config file

4.2) There re 5 Contributors in an email/meeting. This is because we dont focus on the contributors for this project. This might be enhanced to be varying by introducing knobs in the config file.

4.3) This is single thread now. To protect the backend system, we initially want to run it in single thread. If you really want to speed up the process, you could run multiple instances of the program with different config files.

4.4) As of Mar 28, 2017, the util meets all needs to set up the data for the project Elasticsearch Performance. Further enhancments will be done upon requests or as needed.

5) Further Reference

https://confluence.salesforceiq.com/display/ENG/Data+Shape+Design
