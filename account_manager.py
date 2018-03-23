""" Manage information about customers, can extract customer's information, and add new things to the database.
 """
import sqlite3
import time

def check_account(account_num,pid, connection, cursor):
	# returns true if account_num is in database
	
	cursor.execute("SELECT account_no from accounts where account_mgr = :pid",{"pid":pid})
	result = cursor.fetchall()
	lst=[]
	for i in result:
		lst.append(i[0])
	return account_num in lst

def account_manager(pid, connection, cursor):

	while True:
		check1 = True
		check2 = True
		check3 = True
		check4 = True
		checkx = True
		respond = input("Enter 1 to access the accounts;\nEnter 2 to create a new master account;\nEnter 3 to add a new service agreement;\nEnter 4 to create a summary report;\nEnter 'q' to quit\n")

		# access the accounts 		
		if respond == "1":
			while check1:
				while checkx:
					# get the master account user input
					master_acc = input("Enter the master_account to access the information or 'q' to exit:")
					# check if the account number is accessable, if yes go into the function else get the user to re enter the account
					if check_account(master_acc,pid, connection, cursor):
						access_account(pid,master_acc, connection, cursor)
						# check if the user want to redo
						while True:
							result = input("Access another account?(Y/N)")
							if result.lower() == "n":
								check1 = False
								checkx = False
								break
							elif result.lower() == "y":
								break
							else:
								print("Invalid input")
					# quit
					elif master_acc == 'q':	
						check1 = False
						break		
					else:
						print("You cannot access this master_account")
		
		# create a new master account
		if respond == "2":
			while check2:
				# get the information
				acc = []
				instruction = ["account_no:","account_mgr:", "customer_name:", "contact_info:", "customer_type:", "start_date:", "end_date:", "total_amount:"]
				print("Enter the information of the master account")
				custype = ["municipal", "commercial", "industrial", "residential"]
				for i in range(0,len(instruction)):
				
					if i == 0:						
						while True:
							
							master_acc = input(instruction[0])
							if check_account(master_acc, pid, connection, cursor):
								print("Master account already exist")
							else:
								acc.append(master_acc)
								break					
					elif i == 1:
						acc.append(pid)
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
				# call the function
				create_account(acc,pid, connection, cursor)
				# ask if the user wants to redo
				while True:
					result = input("create a new master account?(Y/N)")
					if result.lower() == "n":
						check2 = False
						break
					elif result.lower() == "y":
						break
					else:
						print("Invalid input")				
		
		
		# add new service agreements
		if respond == "3":
			while check3:
				while checkx:
					# get the master account from user
					master_acc = input("Enter the master_account to add service agreement or 'q' to exit:")
					if check_account(master_acc,pid, connection, cursor):
						# get the service number
						cursor.execute("SELECT service_no from service_agreements;")
						x = cursor.fetchall()
						lst=[]
						for i in x:
							lst.append(int(i[0]))
						service_number = max(lst) +1	
						# call the function
						add_service(master_acc,service_number, connection, cursor)
						# ask if the user wants to redo
						while True:
							result = input("Add a new service agreement?(Y/N)")
							if result.lower() == "n":
								check3 = False
								checkx = False
								break
							elif result.lower() == "y":
								break
							else:
								print("Invalid input")						
					elif master_acc.lower() == 'q':
						check3 = False
						break
					else:
						print("You cannot access this master_account")				
				
		# create summary reports
		elif respond == "4":
			while check4:
				while checkx:
					# ask the user to enter the master account
					master_acc = input("Enter the master_account to create a summary report or 'q' to exit:")
					if check_account(master_acc,pid, connection, cursor):						
						create_report(master_acc, connection, cursor)
						# ask if the user wants to redo
						while True:
							result = input("Create another summary report?(Y/N)")
							if result.lower() == "n":
								check4 = False
								checkx = False
								break
							elif result.lower() == "y":
								break
							else:
								print("Invalid input")						
					elif master_acc.lower() == 'q':
						check4 = False
						break
					else:
						print("Invalid master_account")	
		elif respond == "q":
			break
		
		
# access the account
def access_account(pid,master_acc, connection, cursor):
	
	accounts = ["account_no:","account_mgr:", "customer_name:", "contact_info:", "customer_type:", "start_date:", "end_date:", "total_amount:"]	
	# get all the information for a customer
	cursor.execute("select * from accounts where account_mgr =:account_mgr and account_no =:account_no", {"account_mgr":pid,"account_no":master_acc})
	information1 = cursor.fetchall()
	for i in information1:
		for j in range(0,len(i)):
			print(accounts[j],i[j])	
	print(" ")
	service = ["service_no:", "master_account:", "location:", "waste_type:", "pick_up_schedule:", "local_contact:", "internal_cost:", "price:"]
	# get the service agreement for the customer
	cursor.execute("select * from service_agreements where master_account =:master_account order by service_no", {"master_account":master_acc})
	service_information = cursor.fetchall()
	lst2=[]
	for i in service_information:
		for j in range(0,len(i)):
			print(service[j],i[j])
		print(" ")
        
def create_account(master_acc,pid, connection, cursor):
		# insert the data in the tables
	insert_accounts = "INSERT INTO accounts(account_no, account_mgr, customer_name, contact_info, customer_type, start_date, end_date, total_amount) VALUES (:account_no, :account_mgr, :customer_name, :contact_info, :customer_type, :start_date, :end_date, :total_amount);"
	cursor.execute(insert_accounts, {"account_no":master_acc[0], "account_mgr":master_acc[1], "customer_name":master_acc[2],"contact_info":master_acc[3],"customer_type":master_acc[4],"start_date":master_acc[5],"end_date":master_acc[6],"total_amount":master_acc[7]})
	connection.commit()	
	
	
	
def add_service(master_account,service_number, connection, cursor):
	# get the information
	acc = []
	instruction = ["service_no:", "master_account:", "location:", "waste_type:", "pick_up_schedule:", "local_contact:", "internal_cost:", "price:"]
	print("Enter the information of the service agreement")
	for i in range(0,len(instruction)):
		if i == 0:
			acc.append(str(service_number))
			
		elif i == 1:
			acc.append(master_account)
		# check if the input is in the waste type list
		elif i == 3:
			cursor.execute("SELECT waste_type from waste_types")
			waste = cursor.fetchall()
			wastes=[]
			for j in waste:
				wastes.append(j[0])
			while True:
				master_acc = input(instruction[3])
				if master_acc in wastes:
					acc.append(master_acc)
					break
				else:
					print("Invalid input")
				
		else:
			master_acc = input(instruction[i])
			acc.append(master_acc)
	
	# insert into the table
	insert_service = "INSERT INTO service_agreements(service_no, master_account, location, waste_type, pick_up_schedule, local_contact, internal_cost, price) VALUES (:1,:2,:3,:4,:5,:6,:7,:8);"
	cursor.execute(insert_service, {"1":acc[0], "2":acc[1], "3":acc[2],"4":acc[3],"5":acc[4],"6":acc[5],"7":acc[6],"8":acc[7]})
	connection.commit()
	
	# update the total amount 
	update_amount = "UPDATE accounts  SET total_amount=total_amount + :price WHERE account_no = :account"
	cursor.execute(update_amount, {"price":acc[7], "account":master_account})

	connection.commit()	


def create_report(account_number, connection, cursor):
	# the total number of service agreements
	cursor.execute("select count(*) from service_agreements where master_account =:account;", {"account":account_number})
	information = cursor.fetchall()	
	lst=[]
	for i in information:
		lst.append(int(i[0]))
	
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
		
	# print out the result
	print("#################################################")
	print("master account number:", account_number)
	print("the total number of service agreements:",lst[0])
	print("the sum of the prices:",q2[0])
	print("the sum of the internal cost:",q3[0])
	print("number of different waste types:",q4[0])
	print("#################################################")
	print(" ")

