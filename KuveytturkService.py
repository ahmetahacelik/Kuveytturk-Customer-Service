import mysql.connector
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from pylab import title, figure, xlabel, ylabel, xticks, bar, legend, axis, savefig
from fpdf import FPDF
import numpy as np
from sklearn.cluster import KMeans

class KuveytturkCustomerService:
    def __init__(self,iban,cvc):
        self.iban=iban
        self.cvc=cvc

    def databaseConnection(self):
        self.mydb=mysql.connector.connect(user="root", password="toor",
                                               host='127.0.0.1', database="KuveytturkCustomer",
                                               auth_plugin='mysql_native_password')

        self.mycursor = self.mydb.cursor()
        return self.mycursor

    def fetchFromTable(self,tableName):
        self.mycursor.execute("SELECT * FROM %s" % (tableName))
        records=self.mycursor.fetchall()
        self.values=[]
        for value in records:
            self.values.append(value)
        return self.values

    def takeAccountTransactionID(self):
        query="SELECT TransactionID FROM Transactioninfo \
        WHERE Iban = '%s'" % self.iban
        self.mycursor.execute(query)
        self.transactionIDs=self.mycursor.fetchall()
        self.transactionIDs=[i[0] for i in self.transactionIDs]
        return self.transactionIDs

    def takeAccountTransactionMoves(self,transactionID):
        self.accountMoves=[]
        for transid in transactionID:
            query="SELECT Amount, Category, Date FROM Transaction \
                  WHERE TransactionID = '%s'" % transid
            self.mycursor.execute(query)
            self.transactionMoves=self.mycursor.fetchall()
            for i in self.transactionMoves:
                h = i[2].split(" ")[0]
                month = (h[3:5])
                day = (h[0:2])
                self.accountMoves.append([transid,i[0],i[1],[month,day]])
        return self.accountMoves

    def calculatePerMonth(self,accountTransaction):
        self.spendPerMonth={}
        for line in accountTransaction:
            if line[3][0][0]=='0':
                month=line[3][0][1] #To make sure each month formats are same

                self.spendPerMonth[month]={}

        for line in accountTransaction:
            if line[3][0][0]=='0':
                month=line[3][0][1]
                if month in self.spendPerMonth:
                    self.spendPerMonth[month][line[2]]=[]
                    self.spendPerMonth[month][line[2]].append(int(line[1]))
        return self.spendPerMonth

    def barChartPerMonth(self):
        self.months={'1':"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July","8":"August","9":"September", \
                      "10":"October","11":"November","12":"December"}
        self.mainPerMonth={}

        self.Categories=(self.spendPerMonth[str(4)].keys())
        for cat in self.Categories:
            self.mainPerMonth[cat]=[]
            self.mainPerMonth[cat].append(sum(self.spendPerMonth[str(4)][cat]))
        self.spends=[i[0] for i in self.mainPerMonth.values()]

        xs=[i  for i,_ in enumerate(self.Categories)]
        plt.bar(xs,self.spends)

        plt.ylabel("Expenses")
        plt.xlabel("Categories")
        for i, v in enumerate(self.spends):
            plt.text(v + 3, i + .25, str(v), color='blue', fontweight='bold')
        plt.title('CREDIT CARD SPENDING CHART FOR '+ (self.months[str(4)]).upper(),y=1.05)
        plt.xticks(xs,self.Categories,size=8.35)
        plt.yticks(size=8.5)
        for i, v in enumerate(self.spends):
            plt.text(i - 0.20, v + 0.25, str(v))
        plt.tight_layout()

        plt.savefig(self.iban+" barChart")
        plt.close()

    def lineChartPerYear(self):
        self.lineChart={}
        self.lineChartMain={}
        self.comparableMonths=[str(i) for i in range(1,4)]
        for month in self.comparableMonths:
            for cat in self.Categories:
                if cat in self.lineChart:
                    self.lineChart[cat]+=self.spendPerMonth[month][cat]
                else:
                    self.lineChart[cat] = self.spendPerMonth[month][cat]
        for cat in self.Categories:
            self.lineChartMain[cat]=sum(self.lineChart[cat])/len(self.comparableMonths)

        values=[i+0.2 for i in self.lineChartMain.values()]
        cats=list(self.Categories)
        plt.plot(cats,values,color="green",marker="o",linestyle="solid")

        plt.plot(cats,self.spends,color="blue",linestyle="solid",marker="o")
        plt.title("SPENDING HABITS CHANGE BETWEEN THIS MONTH AND PREVIOUS MONTHS",y=1.26)
        plt.legend(labels=["Average Expenses Of Previous Months","This Month's Expenses"],bbox_to_anchor=(0., 1.09, 1., 0.), handletextpad=0.3,
                    loc='lower left', ncol=6, mode="expand", borderaxespad=0,
                    numpoints=1, handlelength=0.5)


        plt.ylabel("Expenses")
        plt.xlabel("Categories")
        plt.xticks(size=8.35)
        plt.yticks(size=8.5)
        plt.tight_layout()

        plt.savefig(self.iban+" lineChart")
        plt.close()

    def transactionIdToIban(self):
        self.IbanTransactionMoves={}
        query = "SELECT TransactionID,Iban FROM Transactioninfo"
        self.mycursor.execute(query)
        self.entireDataForTransactioninfo = self.mycursor.fetchall()
        self.IbanTransaction={}
        for k,v in self.entireDataForTransactioninfo:
            if v not in self.IbanTransaction:
                self.IbanTransaction[v]=[k]
            else:
                self.IbanTransaction[v].append(k)
        for k,v in self.IbanTransaction.items():
            self.IbanTransactionMoves[k]=self.takeAccountTransactionMoves(v)
        return self.IbanTransactionMoves

    def ibanvsExpenses(self):
        self.IbanvsExpenses={}
        for i in self.IbanTransactionMoves.keys():
            self.new_dict={}
            for j in self.IbanTransactionMoves[i]:
                if j[2] not in self.new_dict:
                    self.new_dict[j[2]] = int(j[1])
                else:
                    self.new_dict[j[2]] += int(j[1])
            self.IbanvsExpenses[i]=self.new_dict


    def KMeansClustering(self):
        veriler=df = pd.io.json.json_normalize(self.IbanvsExpenses.values())
        X=(veriler.iloc[:,1:])
        kmeans = KMeans(n_clusters=2, init="k-means++")
        clusters=kmeans.fit_predict(X)
        self.ibans_=(list(self.IbanTransaction.keys()))
        self.clustersVsIban=dict(zip(self.ibans_,clusters))
        return self.clustersVsIban

    def compareSameSegment(self):
        self.spendingForCluster={}
        self.ourCustomerSegment=self.clustersVsIban[self.iban]
        self.sameClusterCustomerWithOurCustomer=[k for k in self.clustersVsIban if self.clustersVsIban[k]==self.clustersVsIban[self.iban]]
        for k in self.sameClusterCustomerWithOurCustomer:
            for cat in self.Categories:
                if cat not in self.spendingForCluster:
                    self.spendingForCluster[cat]=self.IbanvsExpenses[k][cat]/len(self.sameClusterCustomerWithOurCustomer)
                else:
                    self.spendingForCluster[cat] += self.IbanvsExpenses[k][cat]/len(self.sameClusterCustomerWithOurCustomer)
        self.avgForWholeSegmentCategories = list(self.spendingForCluster.keys())
        self.avgForWholeSegmentExpenses = list(self.spendingForCluster.values())
        self.ourCustomerKeys=list(self.IbanvsExpenses[self.iban].keys())
        self.ourCustomerValues=list(self.IbanvsExpenses[self.iban].values())

    def clusterLineChart(self):
        plt.plot(self.ourCustomerKeys, self.ourCustomerValues, color="green", marker="o", linestyle="solid")
        plt.plot(self.avgForWholeSegmentCategories, self.avgForWholeSegmentExpenses, color="blue", linestyle="solid", marker="o")
        plt.title("COMPARISON OF ANNUAL EXPENSE BY CUSTOMER SEGMENTS",y=1.26)
        plt.ylabel("Expenses")
        plt.xlabel("Categories")
        plt.xticks(size=8.35)
        plt.yticks(size=8.5)
        plt.tight_layout()
        plt.legend(labels=["Your Expenses","Your Segment's Average Expenses"],
                   bbox_to_anchor=(0., 1.09, 1., 0.), handletextpad=0.3,
                   loc='lower left', ncol=6, mode="expand", borderaxespad=0,
                   numpoints=1, handlelength=0.5)
        #plt.legend(loc=2,prop={'size': 7},labels=["Your Expenses","Your Segment's Average Expenses"])
        plt.savefig(self.iban + " clusterLineChart")
        plt.close()

    def PDF(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_xy(0, 0)
        self.pdf.set_font('arial', 'B', 15)
        self.pdf.cell(208, 20, "KUVEYTTURK CUSTOMER ACTIVITY REPORT", 0, 13,'C')
        self.pdf.image(self.iban+" barChart.png", x=15, y=30, w=170, h=90, type='', link='')
        self.pdf.image(self.iban+" lineChart.png",x=5,  y=120, w=200, h=90, type='', link='')
        self.pdf.image(self.iban+" clusterLineChart.png",x=15,y=210, w=170, h=80, type='', link='')

        return self.pdf.output(self.iban+".pdf", 'F')

    def ibanCvcMerge(self):
        self.databaseConnection()
        self.ibanCvcMerge={}
        query = "SELECT * FROM ibaninfo"
        self.mycursor.execute(query)
        self.entireDataForTransactioninfo = self.mycursor.fetchall()
        for line in self.entireDataForTransactioninfo:
            self.ibanCvcMerge[line[0]]=line[1]
        return self.ibanCvcMerge

    def main(self):
        self.currentDay = datetime.now().day
        self.currentMonth = datetime.now().month
        self.databaseConnection()
        self.takeAccountTransactionMoves(self.takeAccountTransactionID())
        self.calculatePerMonth(self.takeAccountTransactionMoves(self.takeAccountTransactionID()))
        self.barChartPerMonth()
        self.lineChartPerYear()
        self.transactionIdToIban()
        self.ibanvsExpenses()
        self.KMeansClustering()
        self.compareSameSegment()
        self.clusterLineChart()
        self.PDF()

