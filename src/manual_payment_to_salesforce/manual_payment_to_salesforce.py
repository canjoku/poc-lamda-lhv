from src.shared.salesforce import SalesforceClient
from datetime import datetime
import json


sf = SalesforceClient()
sf.init_salesforce()


def manual_payment_to_salesforce(event, context):

    # recheck validity of the sf connection for each Lambda invocation
    sf.init_salesforce()
    paymentDate = event["Payment_Date__c"]
    paymentMade = event["Payment_Made__c"]
    transactionId = event["Transaction_ID__c"]
    description = event["Description__c"]
    interestPaid = event["Interest_Paid__c"]
    principalPaid = event["Principal_Paid__c"]
    principalPentalty = event["Principal_Penalty__c"]
    interestPenalty = event["Interest_Penalty__c"]
    principalBalance = event["Principal_Balance__c"]
    loanId = event["Loan__c"]


    loanHistory = {
        "Payment_Date__c" : paymentDate,
        "Payment_Made__c": paymentMade,
        "Transaction_ID__c": transactionId,
        "Description__c": description,
        "Interest_Paid__c": interestPaid,
        "Principal_Paid__c": principalPaid,
        "Principal_Penalty__c": principalPentalty,
        "Interest_Penalty__c": interestPenalty,
        "Principal_Balance__c" : principalBalance,
        "Loan__c": loanId
    }

    payment = sf.sf_client.Loan_History__c.create(loanHistory)


    return {"Payment" : payment}