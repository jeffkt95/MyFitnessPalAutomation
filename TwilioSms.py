import twilio.rest

class TwilioSms:

    def __init__(self):
        account_sid = "ACe8f3bfc13bb2371944737aac8ce29cdc"
        auth_token = "e81dceb1e7ab129e4da96615e7a1a093"
        self.client = twilio.rest.Client(account_sid, auth_token)
        self.fromNumber = "+14073260562"
    
    def sendMessage(self, messageText, toNumber):
        message = self.client.messages.create(body=messageText, to=toNumber, from_=self.fromNumber)
        print("Message sent. Message ID: " + str(message.sid))

if __name__ == "__main__":
    main()
    
