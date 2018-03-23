""" Supervisor supervises account managers """

import sqlite3
import time

def check_account(account_num, pid, connection, cursor):
	#get the account number by given pid
	cursor.execute("SELECT a.account_no from accounts a, personnel p, account_managers am where supervisor_pid = :pid and p.pid = am.pid and am.pid = a.account_mgr",{"pid":pid})
	result = cursor.fetchall()
	lst=[]
	for i in result:
		lst.append(i[0])
	return account_num in lst

def supervisor(pid, connection, cursor):
	while True:
		check1 = True
		check2 = True
		check3 = True
		checkx = True
		respond = input("Enter 1 to create a new master account;\nEnter 2 to create a summary report for a customer;\nEnter 3 to create a summary report;\nEnter 'q' to quit\n")
		
		if respond == "1":
			while check1:
				# print out the manager the supervisor supervises
				cursor.execute("SELECT p.pid from personnel p, account_managers a where supervisor_pid = :pid and p.pid = a.pid",{"pid":pid})
				result = cursor.fetchall()
				lst=[]
				for i in result:
					lst.append(i[0])
					
				print("#################################################")
				print("Here are the managers that can be accessed")
				for i in range(0,len(lst)):
					print(lst[i])
				print("#################################################")
						
				# collect information
				acc = []
				instruction = ["account_no:","account_mgr:", "customer_name:", "contact_info:", "customer_type:", "start_date:", "end_date:", "total_amount:"]
				print("Enter the information of the master account")
				custype = ["municipal", "commercial", "industrial", "residential"]
				for i in range(0,len(instruction)):
					
					if i == 0:
						cursor.execute("SELECT a.account_no from accounts a, personnel p where p.supervisor_pid = :pid and p.pid = a.account_mgr ",{"pid":pid})
						r = cursor.fetchall()
						check=[]
						for j in r:
							check.append(j[0])						
						while True:
							
							master_acc = input(instruction[0])
							if master_acc in check:
								print("Master account already exist")
							else:
								acc.append(master_acc)
								break
					elif i == 1:
						while True:
							master_acc = input(instruction[1])
							if master_acc in lst:
								acc.append(master_acc)
								break
							else:
								print("You have no access to this manager")
					elif i == 4:
						while True:
							master_acc = input(instruction[i])
							if master_acc in custype:
								acc.append(master_acc)
								break
							else:
								print("Invalid input")
								
					elif i == 7:
						acc.append(0)
					else:
						master_acc = input(instruction[i])
						acc.append(master_acc)

				create_account(acc, connection, cursor)
				while True:
					result = input("create a new master account?(Y/N)")
					if result.lower() == "n":
						check1 = False
						break
					elif result.lower() == "y":
						break
					else:
						print("Invalid input")
						
		elif respond == "2":
			while check2:
				while checkx:
					# print out the master account
					cursor.execute("SELECT a.account_no from accounts a, personnel p where p.supervisor_pid = :pid and p.pid = a.account_mgr ",{"pid":pid})
					result = cursor.fetchall()
					lst=[]
					for i in result:
						lst.append(i[0])
						
					print("#################################################")
					print("Here are the account numbers that can be accessed")
					for i in range(0,len(lst)):
						print(lst[i])
					print("#################################################")
					
					master_acc = input("Enter the master_account to create a summary report or 'q' to exit:")
					if check_account(master_acc,pid, connection, cursor):
						#get the all the service number 
						cursor.execute("SELECT service_no from service_agreements;")
						x = cursor.fetchall()
						lst=[]
						for i in x:
							lst.append(int(i[0]))
						service_number = max(lst) +1						
						create_report(master_acc, connection, cursor)
						while True:
							result = input("Create another summary report?(Y/N)")
							if result.lower() == "n":
								check2 = False
								checkx = False
								break
							elif result.lower() == "y":
								break
							else:
								print("Invalid input")						
					elif master_acc.lower() == 'q':
						check2 = False
						break
					else:
						print("Invalid master_account")	
		elif respond == "3":
			while check3:
				create_summary(pid, connection, cursor)
				while True:
					result = input("Create another summary report?(Y/N)")
					if result.lower() == "n":
						check3 = False
						break
					elif result.lower() == "y":
						break
					else:	
						print("Invalid input")			
		elif respond == "q":
			break
		
def create_account(master_acc, connection, cursor):
	#add a new view which is called accounts, and it include account_no, account_mgr, customer_name, contact_info, customer_type, start_date, end_date, total_amount
	insert_accounts = "INSERT INTO accounts(account_no, account_mgr, customer_name, contact_info, customer_type, start_date, end_date, total_amount) VALUES (:account_no, :account_mgr, :customer_name, :contact_info, :customer_type, :start_date, :end_date, :total_amount);"
	cursor.execute(insert_accounts, {"account_no":master_acc[0], "account_mgr":master_acc[1], "customer_name":master_acc[2],"contact_info":master_acc[3],"customer_type":master_acc[4],"start_date":master_acc[5],"end_date":master_acc[6],"total_amount":master_acc[7]})
	connection.commit()	


def create_report(account_number, connection, cursor):
	# the total number of service agreements
	cursor.execute("select count(*) from service_agreements where master_account =:account;", {"account":account_number})
	information = cursor.fetchall()	
	lst=[]
	for i in information:
		lst.append(i[0])
	
	# the sum of the prices	
	cursor.execute("select sum(price) from service_agreements where master_account =:account;", {"account":account_number})
	price = cursor.fetchall()	
	q2=[]
	for i in price:
		q2.append(i[0])
			
	# sum of the internal cost of the service agreements	
	cursor.execute("select sum(internal_cost) from service_agreements where master_account =:account;", {"account":account_number})
	internal = cursor.fetchall()	
	q3=[]
	for i in internal:
		q3.append(i[0])
		
	# number of different waste types	
	cursor.execute("select count(distinct waste_type) from service_agreements where master_account =:account;", {"account":account_number})
	waste = cursor.fetchall()	
	q4=[]
	for i in waste:
		q4.append(i[0])
	
	# the name of the account manager who manages the account.
	cursor.execute("select p.name from personnel p, accounts a where a.account_mgr = p.pid and a.account_no =:account;", {"account":account_number})
	manager = cursor.fetchall()	
	q5=[]
	for i in manager:
		q5.append(i[0])	
	# print out the result
	print("#################################################")
	print("master account number:", account_number)
	print("the total number of service agreements:",lst[0])
	print("the sum of the prices:",q2[0])
	print("the sum of the internal cost:",q3[0])
	print("number of different waste types:",q4[0])
	print("the name of the account manager:",q5[0])
	print("#################################################")
	print(" ")



def create_summary(pid, connection, cursor):
	#cursor.execute("select p.pid from personnel p, account_managers am where p.pid = am.pid and #p.supervisor_pid = :pid;",{"pid":pid})
	#manager = cursor.fetchall()
	'''for n in range(0,len(manager)):
		pid = manager[n]'''
	cursor.execute("SELECT COUNT(distinct a.account_mgr), COUNT(distinct sa.master_account), SUM(sa.price) as totalPrice, SUM (sa.internal_cost) as totalInternal FROM accounts a, service_agreements sa, personnel p WHERE p.supervisor_pid= :pid AND a.account_mgr= p.pid GROUP BY a.account_mgr ORDER BY (totalPrice - totalInternal)",{"pid":pid})	
	manager1 = cursor.fetchall()	
	'''cursor.execute("select count(*) from service_agreements where master_account in (select account_no from accounts where account_mgr = :manager)",{"manager": manager})
	lst=[]'''
	for i in manager1:
		for n in range(0,len(i)):
			print(i[n])	
		print(" ")
