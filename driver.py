import sqlite3


'''For a given date range, list all the tours that they have been assigned to. The information about a tour consists of the the following:

        The location where to exchange containers.
        The local contact information for the service agreement.
        The waste_type involved in the service agreement.
        The container ID of the container to be dropped off.
        The container ID of the container to be picked up.
'''

def Drivers_information(assigned_start,assigned_end,pid, connection, cursor):
	#assigned_start = input('The start date of the assign: ')
	#assigned_end = input('The end date of the assign:')
	#get_start = "Select start_date from accounts"
	#get_end = "Select end_date from accounts"
	'''cursor.execute("select sa.location, sa.local_contact, sa.waste_type, sf.cid_drop_off, sf.cid_pick_up from service_agreements sa, service_fulfillments sf, accounts acc where sa.master_account = acc.account_no and acc.account_no = sf.master_account and account_no in (select account_no from accounts where julianday(:assigned_start) - julianday(start_date) >= 0 and julianday(:assigned_end) - julianday(end_date) <= 0 ) group by sa.location, sa.local_contact, sa.waste_type, sf.cid_drop_off, sf.cid_pick_up",{"assigned_start":assigned_start,"assigned_end":assigned_end})'''
	#get the users' information by given date range
	cursor.execute("select sa.location, sa.local_contact, sa.waste_type, sf.cid_drop_off, sf.cid_pick_up from service_agreements sa, service_fulfillments sf where sa.service_no = sf.service_no and sf.driver_id = :pid and date_time  between :assigned_start and :assigned_end group by sa.location, sa.local_contact, sa.waste_type, sf.cid_drop_off, sf.cid_pick_up",{"assigned_start":assigned_start,"assigned_end":assigned_end, "pid":pid})
	information = cursor.fetchall()
	
	if information:
		print('\n')
		print('\t\tTours Conducted Between {} and {}'.format(str(assigned_start),str(assigned_end)))
		for row in information:
			for n in range(0,len(row)):
				print(row[n])
			print('')
			'''print ('Location:', str(row['location']))
			print ('Local Contact Information:', str(row['local_contact']))
			print ('Waste Type:', str(row['waste_type']))
			print ('Drop Off Container ID:', str(row['cid_drop_off']))
			print ('Pick Up Container ID:', str(row['cid_pick_up']))
			print('\n')'''	
	else:
		print("No tours between {} and {}, please enter a new date range.".format(str(assigned_start),str(assigned_end)))	
	#contact_information(account_no)
	

def driver(pid, connection, cursor):
	#If it get into the loop, it will request users input a range of date, and then we will check who have been assigned.   
	
	while True:
		assigned_start = input('Please enter a start date in (YYYY-MM-DD) or print (q) to exit: ')
		if assigned_start == 'q':							#if users enter q, it will quit this function
			return
		assigned_end = input('Please enter a end date in (YYYY-MM-DD) or print (q) to exit: ')
		if assigned_end == 'q':
			return
		if assigned_start > assigned_end:
			print('Invalid time range. \n')
			return
		Drivers_information(assigned_start,assigned_end,pid, connection, cursor)
