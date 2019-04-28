import mysql.connector



class DatabaseEstablishment:
    def __init__(self,username,password):
        self.username=username
        self.password=password

    def connectMainDatabase(self):
        self.mydb = mysql.connector.connect(user=self.username, password=self.password,
                                       host='127.0.0.1', database="sys",
                                       auth_plugin='mysql_native_password')

        self.mycursor = self.mydb.cursor()

    def createNewDatabase(self,newdatabasename):
        self.newdatabasename=newdatabasename
        self.connectMainDatabase()
        query = "CREATE DATABASE %s" % (self.newdatabasename)

        return self.mycursor.execute(query)

    def connectNewDatabase(self):
        self.mydb = mysql.connector.connect(user=self.username, password=self.password,
                                            host='127.0.0.1', database="kuveytturkcustomer",
                                            auth_plugin='mysql_native_password')

        self.mycursor = self.mydb.cursor()

        return self.mycursor

    def createTables(self):
        self.connectNewDatabase()

        self.mycursor.execute(
            "CREATE TABLE Transaction (TransactionID INTEGER PRIMARY KEY,Amount NUMERIC(9,2),Category VARCHAR(255), Date VARCHAR(255), City VARCHAR(255))")

        self.mycursor.execute(
            "CREATE TABLE TransactionInfo (TransactionID INTEGER, Iban VARCHAR(255), FOREIGN KEY(TransactionID) REFERENCES Transaction(TransactionID),PRIMARY KEY (TransactionID))")

        self.mycursor.execute(
            "CREATE TABLE IbanInfo (Iban VARCHAR(255) PRIMARY KEY, Cvc INTEGER)")

        self.mycursor.execute(
            "CREATE TABLE Customer (Iban VARCHAR(255) PRIMARY KEY,Name VARCHAR(255),Surname VARCHAR(255), PhoneNumber VARCHAR(255), Address VARCHAR(255))")
