import myfitnesspal
import getpass
import datetime
from datetime import date
from datetime import timedelta
from MyFitnessPalMetrics import MyFitnessPalMetrics
import sys

from TwilioSms import TwilioSms

#See https://github.com/coddingtonbear/python-myfitnesspal for doc on myfitnesspal python lib

def main():
    #username = input(                 "Enter MyFitnessPal username: ")
    #password = getpass.getpass(prompt="Enter MyFitnessPal password: ")
    
    numberOfDaysAgo = int(float(sys.argv[1]))
    username = sys.argv[2]
    password = sys.argv[3]
    
    mfpClient = myfitnesspal.Client(username, password)
    
    yesterday = datetime.datetime.now() - timedelta(days=numberOfDaysAgo)
    
    mfpMetrics = MyFitnessPalMetrics(mfpClient, yesterday, username)

    #mfpMetrics.printMetrics()
    
    gradeMessage = mfpMetrics.getGradeMessage()
    
    print(gradeMessage)
    
    print("Texting message....")
    twilioClient = TwilioSms()
    twilioClient.sendMessage("-\n" + gradeMessage, "+14073739626")
    twilioClient.sendMessage("-\n" + gradeMessage, "+14435387234")
    
if __name__ == "__main__":
    main()
    
