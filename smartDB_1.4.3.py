#!/usr/bin/python

from influxdb import InfluxDBClient
import subprocess
import time
import os.path

global update
global bogus

# smartDB version 1.4.3

waittime = 60

    # this function creates the send2db.py script which runs the curl commands and sends the metrics to influxDB
    # the result is a file localed at /home/Script_Output called send2db.py
def create_send2db():

    send2dbText = """#!/usr/bin/python

from influxdb import InfluxDBClient
import subprocess
import time
import os.path
import os

# Wait time between curls in seconds
global waittime
waittime = """+str(waittime)+"""

def get_sites():
    websites = open("/home/Script_Output/websites.txt", "r")
    givenSites = websites.read()
    
    global sites
    sites = []
    global numSites
    
    numSplits = givenSites.count(",")
    numSites = numSplits + 1
    sites = givenSites.split(',')

    if numSites > 1:
        sites = givenSites.split(',')

    if numSites == 1:
        sites = givenSites

def get_db():
    global dbName
    database = open("/home/Script_Output/database.txt", "r")
    dbName = database.read()

## This function runs the curl commands and sends the results to the database

client = InfluxDBClient('localhost', 8086, 'root', 'root')
get_sites()
get_db()

metrics = ['lookup', 'connect', 'appconnect', 'pretransfer', 'redirect', 'starttransfer', 'total']
while 1:
    get_sites()
    get_db()
    if numSites > 1:
        for x in range(0, len(sites)):
            cmd = "curl -L --output /dev/null --silent --show-error --write-out 'lookup=$%{time_namelookup}$ connect=$%{time_connect}$ appconnect=$%{time_appconnect}$ pretransfer=$%{time_pretransfer}$ redirect=$%{time_redirect}$ starttransfer=$%{time_starttransfer}$ total=$%{time_total}' '" + sites[x] +"'"
            final = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            fromcurl, stderr = final.communicate()
            L, Lvalue, C, Cvalue, A, Avalue, P, Pvalue, R, Rvalue, S, Svalue, T, Tvalue  = fromcurl.split('$')
            values = [float(Lvalue), float(Cvalue), float(Avalue), float(Pvalue), float(Rvalue), float(Svalue), float(Tvalue)]
            curlOutput = sites[x]
            
            for y in range(0, len(metrics)):
                json = [
                        {
                            "measurement": sites[x],
                            "tags": {
                                "metric": metrics[y]
                            },
                            "fields": {
                                "value": values[y]
                            }
                        }
                    ]
                get_db()
                client = InfluxDBClient('localhost', 8086, 'root', 'root', dbName)
                client.write_points(json)
                curlOutput = curlOutput +'$'+ str(metrics[y]) + '$' + str(values[y])
            curlOutput = '_________________________________________$From: '+ curlOutput
            write2curl = open("/home/Script_Output/curlOutput.txt", "w")
            write2curl.write(curlOutput)
            write2curl.close()
    
    if numSites == 1:
        cmd = "curl -L --output /dev/null --silent --show-error --write-out 'lookup=$%{time_namelookup}$ connect=$%{time_connect}$ appconnect=$%{time_appconnect}$ pretransfer=$%{time_pretransfer}$ redirect=$%{time_redirect}$ starttransfer=$%{time_starttransfer}$ total=$%{time_total}' '" + sites +"'"
        final = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        fromcurl, stderr = final.communicate()
 
        L, Lvalue, C, Cvalue, A, Avalue, P, Pvalue, R, Rvalue, S, Svalue, T, Tvalue  = fromcurl.split('$')
        values = [float(Lvalue), float(Cvalue), float(Avalue), float(Pvalue), float(Rvalue), float(Svalue), float(Tvalue)]
        curlOutput = sites
        
        for y in range(0, len(metrics)):

            json = [
                    {
                        "measurement": sites,
                        "tags": {
                            "metric": metrics[y]
                        },
                        "fields": {
                            "value": values[y]
                        }
                    }
                ]
            get_db()
            client = InfluxDBClient('localhost', 8086, 'root', 'root', dbName)
            client.write_points(json)
            curlOutput = curlOutput +'$'+ str(metrics[y]) + '$' + str(values[y])
        curlOutput = '_________________________________________$From: '+ curlOutput
        write2curl = open("/home/Script_Output/curlOutput.txt", "w")
        write2curl.write(curlOutput)
        write2curl.close()
    curlOutput = '...Waiting '+str("""+str(waittime)+""")+' Seconds...'
    write2curl = open("/home/Script_Output/curlOutput.txt", "w")
    write2curl.write(curlOutput)
    write2curl.close()
    time.sleep("""+str(waittime)+""")""" 
    
        # create script file from text above
    write2db = open("/home/Script_Output/send2db.py", "w")
    write2db.write(send2dbText)
    write2db.close()
    

def create_sendmail():

    print '\nThis script can send the IP address and hostname of this Pi to your email on startup.\n'

    if os.path.exists("/home/Script_Output/emailAddress.txt") == True:
        openEmail = open("/home/Script_Output/emailAddress.txt", "r")
        emailTo = openEmail.read()
        print 'This email was used at last run of script: '+emailTo
        emailAnswer = raw_input('\nContinue with previous email? (yes/no)\n')
        if emailAnswer == 'yes':
            print '\nOkay, the IP address and hostname of this Pi will be sent to: '+emailTo+'\n'
            pass
        if emailAnswer == 'no':
            acceptEmail = raw_input('Would you like to send this information to your email on startup of this Pi? (yes/no)\n')
            if acceptEmail == 'yes':
                emailTo = raw_input('\nWhat email address would you like to use?\n')
                writeEmail = open("/home/Script_Output/emailAddress.txt", "w")
                writeEmail.write(emailTo)
                writeEmail.close()
            elif acceptEmail == 'no':
                return
            else:
                print '\nYou entered an unusable response. Please try again and type "yes" or "no"'
                time.sleep(3)
                print("\033c")
                create_sendmail()
    else:
        acceptEmail = raw_input('Would you like to send this information to your email on startup of this Pi? (yes/no)\n')
        if acceptEmail == 'yes':
            emailTo = raw_input('\nWhat email address would you like to use?\n')
            writeEmail = open("/home/Script_Output/emailAddress.txt", "w")
            writeEmail.write(emailTo)
            writeEmail.close()
            print '\nOkay, the IP address and hostname of this Pi will be sent to: '+emailTo+'\n'
        elif acceptEmail == 'no':
            return
        else:
            print '\nYou entered an unusable response. Please try again and type "yes" or "no"'
            time.sleep(3)
            print("\033c")
            create_sendmail()

# the r in front of the string allows the \n to be used as a literal (r=raw)
    bootsendmailText = r"""import subprocess
import yagmail

openEmail = open("/home/Script_Output/emailAddress.txt", "r")
emailTo = openEmail.read()

fromPing = '0% packet loss'
stderr = True

while stderr == True or "0% packet loss" not in fromPing:
    ping = "ping -c 2 -W 1 google.com"
    openPing = subprocess.Popen(ping, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fromPing, stderr = openPing.communicate()

getIPCmd = "ifconfig"
getIP = subprocess.Popen(getIPCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
fullIP, stderr = getIP.communicate()

IPgoods = []
goodstuff = []
IPs = []
ints = []

IPstuff = fullIP.split('collisions 0\n\n')

loop = 0

for x in range(0,len(IPstuff)):
    if "loop" not in IPstuff[x] and "inet" in IPstuff[x]:
       IPgoods.append(IPstuff[x])
   
stuff = [i.split() for i in IPgoods]

for x in range(0,len(stuff)):
    goodstuff.append(stuff[x][0])
    for y in range(0,len(stuff[x])):
        if "inet" in stuff[x][y] and "inet6" not in stuff[x][y]:
            goodstuff.append(stuff[x][y+1])
   
getHostCmd = "hostname"
getHost = subprocess.Popen(getHostCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
Host, stderr = getHost.communicate()

for x in range(0,len(goodstuff),2):
    ints.append(goodstuff[x])
for x in range(1,len(goodstuff),2):
    IPs.append(goodstuff[x])
IPsubject =''
body = '\nHostname of your Raspberry Pi:\n'+Host+'\n'+'IPs for each interface:\n'
for x in range(0, len(IPs)):
    IPsubject = IPsubject+str(IPs[x])
    if len(IPs)>1 and x+1!=len(IPs):
        IPsubject = IPsubject+', '
    body = body+ints[x]+' '+IPs[x]+'\n'

body = body +'\n- - - - - - - - - - - - - - - - - - - - -\nFull ifconfig output:\n'+fullIP
subject = "Pi: "+Host+" @ "+IPsubject+" just booted"
yagmail.SMTP('piperformancemonitoring','mcncadmin!').send(emailTo, subject, body)"""

        # create script file from text above
    writesendmail = open("/home/Script_Output/bootsendmail.py", "w")
    writesendmail.write(bootsendmailText)
    writesendmail.close()

    servicemailText = """[Unit]
Description=Sending IP info to email
Wants=network-online.target
After=network-online.target
Requires=network.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/Script_Output/bootsendmail.py

[Install]
WantedBy=multi-user.target"""

    writemailservice = open("/lib/systemd/system/bootsendmail.service", "w")
    writemailservice.write(servicemailText)
    writemailservice.close()
    
    os.system("sudo chmod 644 /lib/systemd/system/bootsendmail.service")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable bootsendmail.service")
    os.system("sudo systemctl start bootsendmail.service")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl restart bootsendmail.service")
    
    print '\nDaemon created for this process at /lib/systemd/system/bootsendmail.service\n'

    # this function reads the output from send2db.py and prints it to the console
    # its essentially just for the user to see what is going on
def print_curlOutput():
    curlText = """import time
fromCurl = ''
content = []
try: 
    while 1:
            previous = fromCurl
            openOutput = open("/home/Script_Output/curlOutput.txt", "r")
            fromCurl = openOutput.read()
            if fromCurl != previous:
                content = fromCurl.split('$')
                for x in range(0,len(content)):
                    print content[x]
except KeyboardInterrupt:
    print ''
    print 'Okay, the script has been halted. The data collection will resume in the background.' 
    print 'Restart script to edit websites or try again.'
    quit()"""
    curlFile = open("/home/Script_Output/printCurlOutput.py", "w")
    curlFile.write(curlText)
    curlFile.close()
    os.system('sudo python /home/Script_Output/printCurlOutput.py')

    # this function creates the daemon. it runs send2db.py as a service
    # it waits for network connection to start on boot and restarts on every failure
def create_daemon():
    serviceText = """[Unit]
Description=Sending Metrics to InfluxDB
Wants=network-online.target
After=network-online.target
Requires=network.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/Script_Output/send2db.py
Restart=always 
RestartSec=5

[Install]
WantedBy=multi-user.target"""

    write2service = open("/lib/systemd/system/send2db.service", "w")
    write2service.write(serviceText)
    write2service.close()
    
    os.system("sudo chmod 644 /lib/systemd/system/send2db.service")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable send2db.service")
    os.system("sudo systemctl start send2db.service")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl restart send2db.service")
    
    print '\nDaemon created for this process at /lib/systemd/system/send2db.service\n'
    print 'Monitoring will continue after this script is killed and upon reboot.\n'

    looped = 0
    while os.path.exists("/home/Script_Output/curlOutput.txt") == False:
        if looped == 0:
            print '...Waiting for service to begin...'
            looped = 1
    time.sleep(1)

    # this function creates the database file name and creates the retention policies as well as the continuous queries 
def create_db():
    global dbName
    print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    print('Please enter your desired database name followed by the enter key.\n')
    dbName = raw_input('database: ')
        # save database name to file
    database = open("/home/Script_Output/database.txt", "w")
    database.write(dbName)
    database.close()
    print('\nWe are going to create a database named: ')
    print "  ->  " + dbName
        #connect to influxdb
    client = InfluxDBClient('localhost', 8086, 'root', 'root', dbName)
    client.create_database(dbName)
        # create the rentention policies
    # 30day policy named 'thirtyDay'
    # 6month policy named 'sixMonth'
    # 52week policy named 'oneYear'
    client.create_retention_policy('thirtyDay','30d',1,database=dbName,default=True)
    client.create_retention_policy('sixMonth','26w',1,database=dbName,default=False)
    client.create_retention_policy('oneYear','52w',1,database=dbName,default=False)
        #create the continuous continuous query
    cqCmd = 'curl -POST http://localhost:8086/query --data-urlencode "q=CREATE CONTINUOUS QUERY cq_5m ON '+dbName+' BEGIN SELECT mean("value") as "value" INTO '+dbName+'."sixMonth".:MEASUREMENT FROM '+dbName+'."thirtyDay"./.*/ GROUP BY TIME(5m),* END"'
    openCQ = subprocess.Popen(cqCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fromCQ, stderr = openCQ.communicate()
    cqCmdb = 'curl -POST http://localhost:8086/query --data-urlencode "q=CREATE CONTINUOUS QUERY cq_30m ON '+dbName+' BEGIN SELECT mean("value") as "value" INTO '+dbName+'."oneYear".:MEASUREMENT FROM '+dbName+'."thirtyDay"./.*/ GROUP BY TIME(30m),* END"'
    openCQ = subprocess.Popen(cqCmdb, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fromCQ, stderr = openCQ.communicate()

    # this function is used to get the databases that exist in influxdb and ask the user which to use. it then confirms that givenDB exists
def test_dbName(dbList):
    dbName = raw_input('\nWhich database do you want to use? Please enter it exactly as printed above.\nType "exit" if you wish to go back.\n')
    database = open("/home/Script_Output/database.txt", "w")
    database.write(dbName)
    database.close()
    if dbName == 'exit':
        main()
    # these just check if database given exists and if it doesnt, restart this function
    for z in range(1,len(dbList)):
        if dbName != dbList[z]['name']:
                dbFound = 0
        if dbName == dbList[z]['name']:
                dbFound = 1
                break
    if dbFound == 0:
            print '\nDatabase not found! Please try again.'
            test_dbName(dbList)
    if dbFound == 1:
        print '\nOkay, going to use the "'+dbName+'" database!'
        client = InfluxDBClient('localhost', 8086, 'root', 'root', dbName)

    # this function just reads the database name file
def get_db():
    global dbName
    database = open("/home/Script_Output/database.txt", "r")
    dbName = database.read()

    # this function reads the websites file and splits them accordingly 
def get_sites():
    websites = open("/home/Script_Output/websites.txt", "r")
    givenSites = websites.read()
    
    global sites
    sites = []
    global numSites
    
    numSplits = givenSites.count(",")
    numSites = numSplits + 1
    sites = givenSites.split(',')

    if numSites > 1:
        sites = givenSites.split(',')
        for x in range(0, numSites):
            print "  ->  " + sites[x]
    
    if numSites == 1:
        sites = givenSites
        print "  ->  " + sites

    # this function creates the websites file and accounts for every possible scenerio of user error 
def create_file(update,bogus):
    if bogus != 1:
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print '*************************************************************************'
        print '**                                                                     **'
        print '**   VERY IMPORTANT!!!! PLEASE ENTER URL EXACTLY AS IT IS RESOLVED!!   **'
        print '** INCLUDING ANY PREFIX: "http://" or "https://" or "https://www." etc **'
        print '**                                                                     **'
        print '*************************************************************************'
        print('Please enter your desired websites in the form of the full url: \n"https://www.example.com" followed by the Enter key.\n')
        print('When you are finished with your desired entries, please type: \n"done" followed by the Enter key.')
        # new website list
    if update == 0:
        print('\nType websites below:\n')
        textInput = raw_input('website: ')
        nextInput = ""
        if textInput == "":
            print "\nYou did not type anything."
            update = 0
            bogus = 1
            create_file(update,bogus)
        elif textInput == "done":
            print "You didn't enter any websites. Let's try again."
            time.sleep(3)
            update = 0
            bogus = 1
            create_file(update, bogus)
        while(nextInput != "done"):
            nextInput = raw_input('website: ')
            websites = open("/home/Script_Output/websites.txt", "w")
            if nextInput == "done":
                websites.write(textInput)
                websites.close()
                pass
            elif nextInput == "":
                print "Empty field ignorned."
                continue
            else:
                nextInput = "," + nextInput
                textInput += nextInput 
                websites.write(textInput)        
        websites.close()

        print('\nWe are going to monitor metrics on these sites: ')
        get_sites()

        print('\nIf at any point you want to stop, use "Ctrl+C" to interrupt the script.') 
        raw_input("\nPress Enter to begin monitoring...")
        create_daemon()
        print_curlOutput()

        #append the file
    if update == 1:
        get_sites()
        print('Type websites to add below: \n')
        textInput = raw_input('website: ')
        if textInput == "":
            print "Empty field ignorned."
            nextInput = ""
        elif textInput == "done":
            print "You didn't enter any websites. Let's try again."
            time.sleep(3)
            update = 1
            bogus = 1
            create_file(update, bogus)
        else:
            textInput = "," + textInput
            nextInput = ""
        
        while(nextInput != "done"):
            nextInput = raw_input('website: ')
            websites = open("/home/Script_Output/websites.txt", "a")
            if nextInput == "done":
                websites.write(textInput)
                websites.close()
                pass
            elif nextInput == "":
                print "Empty field ignorned."
                continue
            else:
                nextInput = "," + nextInput
                textInput += nextInput 

        print('\nWe are going to monitor metrics on these sites: ')
        get_sites()

        print('\nIf at any point you want to stop, use "Ctrl+C" to interrupt the script.') 
        raw_input("\nPress Enter to begin monitoring...")
        create_daemon()
        print_curlOutput()

def main():
    print '________________________________________________________________________________________________'
    print 'Create InfluxDB Database\n'
    client = InfluxDBClient('localhost', 8086, 'root', 'root')
    dbList = client.get_list_database()
    size = len(dbList)
    # does database file exist?
    if size > 1:
    # yes - database does exist
        print '\nDatabase(s) already exist: '
        for x in range(1, size):
            print '  ->  ' + dbList[x]['name']
    # use old database file?
        dbanswer1 = raw_input('Do you want to use one of these databases? (yes/no/quit)\n')
        # no - dont use it
        if dbanswer1 == "no":
            # are you sure?
            dbanswer2 = raw_input("ARE YOU SURE YOU WANT TO CREATE A NEW DATABASE? (yes/no)\n")
            if dbanswer2 == "yes":
                # yes, delete the old file and 
                # create database from text file
                create_db()
            # no, don't delete the old file
            elif dbanswer2 == "no":
                main()
            else:
                print('\nYou entered an unusable response. Please try again and type "yes" or "no"')
                time.sleep(3)
                main()
        # yes - use the old database file
        elif dbanswer1 == "yes":
            # asks the user for desired database and checks that it exists
            test_dbName(dbList)

        elif dbanswer1 == "quit":
            # kills the script
            quit()
            
        # If they type something besides yes, no or exit
        else:
            print('\nYou entered an unusable response. Please try again and type "yes" or "no"')
            time.sleep(3)
            main()
    # no - database file does not exist, create a new one
    else:
        create_db()

    # does website file exist?
    if os.path.exists("/home/Script_Output/websites.txt") == True:
    # yes - website file does exist
        print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print('Website file already exists with website(s):')
        get_sites()
    # use old website file?
        webanswer1 = raw_input('\nDo you want to continue with these sites? (yes/no)\n')
        # no - dont use it 
        if webanswer1 == "no":
            # are you sure?
            webanswer2 = raw_input("Do you add sites or create a new file? (add/new)\n")
            if webanswer2 == "add":
                # append sites or use create file function
                update = 1
                bogus = 0
                create_file(update, bogus)
            elif webanswer2 == "new":
                webanswer3 = raw_input("ARE YOU SURE YOU WANT TO OVERWRITE THE OLD FILE? (yes/no)\n")
                if  webanswer3 == "yes":
                    # yes, delete the old file and
                    # create a new website file
                    update = 0
                    bogus = 0
                    create_file(update, bogus)
                # no, don't delete the old file
                elif webanswer3 == "no":
                    main()
                else:
                    print('\nYou entered an unusable response. Please try again and type "yes" or "no"')
                    time.sleep(3)
                    main()
            else:
                print('\nYou entered an unusable response. Please try again and type "yes" or "no"')
                time.sleep(3)
                main()
        # yes - use the old website file                               
        elif webanswer1=="yes":          
            print('\nOkay, we will keep using the old file. ')
            print('\nWe are going to monitor metrics on site(s): ')
            get_sites()
            print('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
            print('\nIf at any point you want to stop, use "Ctrl+C" to interrupt the script.') 
            raw_input("\nPress Enter to begin monitoring...")          
            create_daemon()
            print_curlOutput()
    ## If they type something besides yes or no                                              
        else:
            print('\nYou entered an unusable response. Please try again and type "yes" or "no"')
            time.sleep(3)
            main()

    # no - website file does not exist, create a new one
    else:
        update = 0
        bogus = 0
        create_file(update, bogus)
try:
    if os.path.exists("/home/Script_Output") == False:
        os.system('sudo mkdir /home/Script_Output')
    create_sendmail()
    time.sleep(1)
    create_send2db()
    time.sleep(1)
    main()

except KeyboardInterrupt:
    print '\nOkay, the script has been halted. If the process has been daemonized, the monitoring will continue in the background.'
    print 'Restart script to change websites or try again.' 
    quit()
