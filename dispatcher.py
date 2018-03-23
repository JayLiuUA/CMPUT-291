""" dispatcher is responsible for creating new schedules

source: https://github.com/Echo-Gambino/cmput291_MiniProject1/blob/master/dispatchers.py
 			https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python
			solution to assignment2 from eclass"""

import sqlite3
from datetime import datetime


def dispatcher(connection, cursor):

	print("Dispatcher's interface: \n")

	while True:
		decision = input("Please choose to create a new schedule(c) or logout(l): ")
		if decision == 'c':		# if user wanna proceed
			service_no = input('Please select a service agreement number: ')
			if check_service_no(service_no, connection, cursor): 		# if service_no exists
				print("Service number found.\n")
				create_schedule(service_no, connection, cursor)
			else:
				print("Service number not found, please retry.\n")
		elif decision == 'l':
			print("Bye!\n")
			return
		else:	# invalid input
			print("Invalid input, please try again.\n")

	connection.commit()
	connection.close()

	return

def create_schedule(service_no, connection, cursor):

	driver_id = input("Please enter the id of the driver: ")
	if not check_driver_id(driver_id, connection, cursor):		# if input id does not exist in database
		print("Driver_id not found.\n")
		return
	# if driver_id exist:
	if owns_truck(driver_id, connection, cursor):		# if already owns truck
		truck_id = get_truck_id(driver_id, connection, cursor)
		print("This driver already owns a truck, automatically selected.\n")
	else:		# assign a truck to driver
		truck_id = input("Please assign a truck to driver by entering truck's id (capital letters with numbers): ")
		if check_truck(truck_id, connection, cursor):		# if truck_id is available
			pass 		# truck_id remains the same
		else:
			print("Truck is either not in database or owned by another driver, please restart (watch for typos).\n")
			return

	cid_drop_off = input("Enter cid to be dropped off (capital letters with numbers): ")
	if not check_container(cid_drop_off, connection, cursor):
		print("Selected container to be dropped off is not available (watch for typos).")
		return

	print("Selected container found.\n")

	date = input("Enter date in format of (YYYY-MM-DD): ")
	if not check_time(date):	# if date is not in correct format
		print("Wrong date format.\n")
		return

	master_account = get_master_account(service_no, connection, cursor)

	# now create schedule
	cid_pick_up = get_cid_pick_up(service_no, connection, cursor)
	table = "service_fulfillments(date_time, master_account, service_no, truck_id, driver_id, cid_drop_off, cid_pick_up)"
	insert_query = "INSERT INTO {} " \
				   "VALUES (:date, :master_account, :service_no, :truck_id, :driver_id, :cid_drop, :cid_pick)".format(table)
	cursor.execute(insert_query, {"date":date, "master_account":master_account, "service_no":service_no, "truck_id":truck_id, "driver_id":driver_id, "cid_drop":cid_drop_off, "cid_pick":cid_pick_up})
	print("New schedule created!\n")
	connection.commit()


def get_cid_pick_up(service_no, connection, cursor):
	""" returns container to pick up when given a service_no"""
	query = "select cid_drop_off " \
			"from service_fulfillments " \
			"where service_no = :service_no " \
			"order by date_time desc limit 1"

	cursor.execute(query, {"service_no": service_no})
	result = cursor.fetchone()

	if result is None:
		return '0000'
	return result[0]


def get_truck_id(driver_id, connection, cursor):
	""" returns corresponding truck id when given driver_id """
	query = "select owned_truck_id " \
			"from drivers " \
			"where pid = :driver_id;"
	cursor.execute(query, {"driver_id":driver_id})
	result = cursor.fetchone()

	return result[0]


def get_master_account(service_no, connection, cursor):
	""" returns corresponding master_account when given service_no """
	query = "select master_account " \
			"from service_agreements " \
			"where service_no = :service_no;"
	cursor.execute(query, {"service_no":service_no})
	result = cursor.fetchone()

	return result[0]


def check_time(date):
	try:
		if date != datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d'):
			raise ValueError
		return True
	except ValueError:
		return False


def check_service_no(service_no, connection, cursor):
	""" returns true if service_no exists in database """

	query = "SELECT service_no from service_agreements"
	cursor.execute(query)
	result = cursor.fetchall()
	lst = []

	for i in result:
		lst.append(i[0])
	return service_no in lst


def check_driver_id(driver_id, connection, cursor):
	""" returns true if driver_id exists in database """

	query = "SELECT pid " \
			"from drivers;"
	cursor.execute(query)
	result = cursor.fetchall()
	lst = []

	for i in result:
		lst.append(i[0])
	return driver_id in lst


def owns_truck(driver_id, connection, cursor):
	""" returns true if driver_id owns truck in database """
	query = "SELECT pid " \
			"from drivers " \
			"where owned_truck_id is not NULL;"
	cursor.execute(query)
	result = cursor.fetchall()
	lst = []
	
	for i in result:
		lst.append(i[0])
	return driver_id in lst

def check_truck(truck_id, connection, cursor):
	""" returns true if truck_id exists in database AND not been owned by another driver """
	query = "SELECT truck_id " \
			"from trucks " \
			"except " \
			"select owned_truck_id " \
			"from drivers;"
	cursor.execute(query)
	result = cursor.fetchall()

	lst = []
	
	for i in result:
		lst.append(i[0])
	return truck_id in lst


def check_container(cid_drop_off, connection, cursor):
	if not check_container_exist(cid_drop_off, connection, cursor): 	# if cid_drop_off not in database
		print("Your cid is not in our database.\n")
		return

	query = '''
	        SELECT c.container_id
	        FROM containers c
	        WHERE NOT EXISTS (SELECT *
                  FROM service_fulfillments s
                  WHERE s.cid_drop_off = c.container_id)
	          UNION
	          SELECT c.container_id
	          FROM containers c
	          WHERE (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_pick_up = c.container_id)
	          >
	          (SELECT MAX(date_time) FROM service_fulfillments s WHERE s.cid_drop_off = c.container_id) 
	          ; '''

	cursor.execute(query)
	result = cursor.fetchall()
	lst = []
	
	for i in result:
		lst.append(i[0])
	return cid_drop_off in lst


def check_container_exist(cid_drop_off, connection, cursor):
	""" returns true if cid exists in database """

	query = "SELECT container_id from containers;"
	cursor.execute(query)
	result = cursor.fetchall()
	lst = []

	for i in result:
		lst.append(i[0])
	return cid_drop_off in lst
