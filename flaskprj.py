from flask import Flask, request, render_template, url_for, redirect, flash
import pandas as pd
from datetime import datetime, timedelta


def remove_lead_trail_white_space(some_string):
    return some_string.lstrip().rstrip()


#load in the data
tot_data = pd.read_csv('19_s_courseData_csv')

#get rid of data with no value
tot_data.drop(tot_data[tot_data["Time"] == ''].index, inplace=True)
#all profs
all_profs = sorted(list(set(tot_data['Instructor(s)'])))
#building tags
all_buildings = list(set([i.split()[0] for i in tot_data['Location'].unique()])) #gets all the buildings
#building names that will be used
building_names = ['Activity Center', 'Administration', 'Arts and Humanities 1', 'Arts and Humanities 2','Edith O’Donnell Arts and Technology Building','Lloyd V. Berkner Hall','Bioengineering and Sciences Building','Classroom Building','Classroom Building 1', 'Classroom Building 2', 'Classroom Building 3', 'Callier Center Richardson', 'Callier Center Richardson Addition', 'Engineering and Computer Science North', 'Engineering and Computer Science South', 'Engineering and Computer Science West', 'Founders North', 'Founders Building', 'Cecil H. Green Hall','Karl Hoblitzelle Hall', 'Erik Jonsson Academic Center', 'Naveen Jindal School of Management','LLC', 'Eugene McDermott Library', 'Modular Lab 1' ,'Physics Building', 'Research and Operations Center', 'Research and Operations Center West', 'Science Learning Center', 'Synergy Park North','Student Services Building (Admissions)', 'Theatre']
#all lab locations

#---------------------------------------------------------------------------------------------------------
#read in rate my prof data
# rmp_df = pd.read_csv('rmp_csv') => this data can be obtained by running the ipynb notebook

prof_rmp_id = {} #put all dataframe info into dict
for i in range(len(rmp_df)):
    prof_rmp_id[rmp_df.iloc[i]['Prof']] = rmp_df.iloc[i]['url']

temp = {}
for key, value in prof_rmp_id.items():
    if(key.find(',') != -1):
        rmp_urls_list = []
        for i in key.split(','):
            if(i != 'Not found'):
                try:
                    rmp_urls_list.append(prof_rmp_id[remove_lead_trail_white_space(i)])
                except KeyError:
                    print(remove_lead_trail_white_space(i))
        temp[key] = rmp_urls_list

    else:
        temp[key] = [prof_rmp_id[key]]

prof_rmp_id = temp
del temp

#-------------------------------------------------------------------------------------------------

#used to generate links to utd grades to show prof info, class grade dist.
# %20 => translate to a space
utdGrades_baseUrl = 'https://utdgrades.com/app/results?search='
utdGrades_prof_urls = {i:utdGrades_baseUrl + '%20'.join(i.split()) if i.find(',') == -1 else 'Not found' for i in all_profs}

#-----------------------------------------------------------------------------------------------------

building_tags = {x:y for x,y in zip(sorted(all_buildings),building_names)}
all_possible_locs = set(map(lambda x: remove_lead_trail_white_space(x), tot_data['Location']))

loc_tags = {}
for i in all_possible_locs:
    loc_tags[i] = building_tags[i.split()[0]]

loc_tags = dict(sorted(loc_tags.items()))

lab_locs = {'ATC 1.406',
 'ATC 1.910',
 'ATC 3.601',
 'ATC 3.910',
 'ATC 3.914',
 'BE 2.330',
 'ECSN 3.108',
 'ECSN 3.110',
 'ECSN 3.112',
 'ECSN 3.114',
 'ECSN 3.118',
 'ECSN 3.120',
 'ECSN 4.324',
 'ECSS 2.103',
 'ECSS 2.312',
 'ECSS 3.618',
 'ECSW 1.315',
 'ECSW 2.315',
 'ECSW 2.325',
 'ECSW 2.335',
 'ECSW 3.325',
 'ECSW 3.335',
 'ECSW 4.315',
 'ECSW 4.325',
 'FN 2.102',
 'FN 2.212',
 'FN 2.214',
 'FO 3.222',
 'GR 4.204',
 'GR 4.708',
 'JO 3.209',
 'ML1 1.110',
 'ML1 1.114',
 'SLC 1.102',
 'SLC 1.202','SLC 1.205','SLC 1.206',
 'SLC 1.211',
 'SLC 2.202','SLC 2.203','SLC 2.206',
 'SLC 2.207',
 'SLC 2.215',
 'SLC 2.216','SLC 2.302',
 'SLC 2.303',
 'SLC 2.304','SLC 3.102',
 'SLC 3.202','SLC 3.203',
 'SLC 3.210','SLC 3.215','SLC 3.220'}



tot_data['Location'] = list(map(remove_lead_trail_white_space, tot_data['Location'])) #strips leading and trailing white space, set operations work
tot_data['Time'] = list(map(remove_lead_trail_white_space, tot_data['Time']))
tot_data['Days'] = list(map(remove_lead_trail_white_space, tot_data['Days']))
tot_data['Class Name'] = list(map(lambda x: remove_lead_trail_white_space(x.split('(')[0]), tot_data['Class Title']))
tot_data['Course Number'] = list(map(lambda x: x.split('.')[0] + '.' + x.split('.')[1][:3], tot_data['Class SectionClass Number']))
tot_data['Course pre'] = list(map(lambda x: x.split('.')[0], tot_data['Class SectionClass Number']))
#data extraction functions




def does_it_fall_between(time_range, time1, time2):
    '''Given a time range, start time, and end time => check to see if there is overlap'''
    p1 = pd.to_datetime(time_range.split()[0]) #start of range
    p2 = pd.to_datetime(time_range.split()[2]) #end of range
    time1 = pd.to_datetime(time1) #start of user time range
    time2 = pd.to_datetime(time2) #end of user time range
    return (p1 <= time1 and p2 >= time1) or (p1 <= time2 and p2 >= time2) or (p1 >= time1 and p2 <= time2) or (p1 <= time1 and p2 >= time2)



def get_open_locs(day, time_start, time_end, loc_pref=all_buildings, df=tot_data, show_labs=False): #loc_preference defaults to all
    ''' find all open locations given a day(day) and time(time)
        day: what day it is
        time: what time it is
        => day = monday, time = 3:30pm
        => first find all classes that are held on monday
        => for all classes on monday, find locations of classes that intersect with the time given(3:30pm)
        => all_locs - occupied_locs = free_locs
        => return free_locs
        => labs are turned off by default meaning open lab locations will not be shown since there are closed most of the times'''
    data = df.copy()

    import functools
    inds = list(map(lambda x: True if x.find(day) != -1 else False, data['Days']))
    classes_that_intersect = list(map(functools.partial(does_it_fall_between, time1=time_start, time2=time_end), data[inds]['Time']))
    free_locs = list(set(data['Location']) - set(data[inds][classes_that_intersect]['Location']) - lab_locs)

    if(type(loc_pref) == str):
        loc_pref = [loc_pref]
	
	
    sorted_by_locs_nums = sorted([i for i in free_locs if i.split()[0] in loc_pref])
    #sorts the locations by building then room number
    return sorted_by_locs_nums 



def classes_given_loc_day(locs, day, data=tot_data):
    '''Find all classes given location and day'''
    info = []
    for loc in locs:
        inds = list(map(lambda x: True if x.find(day) != -1 else False, data['Days']))
        temp = tot_data.iloc[inds][tot_data['Location'] == loc]
        temp['Sort_time'] = temp['Time'].apply(lambda x: pd.to_datetime(x.split()[0]))
        temp = temp.sort_values(by=['Sort_time']).drop(['Sort_time'], axis=1).drop(['Class SectionClass Number', 'Schedule &Location'], axis=1).drop_duplicates()
        info.append(temp)

    return info


def get_prof_data(prof_list, data=tot_data):
    '''Gets all the classes taught by the given profs.'''
    prof_data_list = []
    for i in prof_list:
        temp = tot_data[data['Instructor(s)'] == i].drop(['Class Title', 'Instructor(s)','Schedule &Location'], axis=1).drop_duplicates().sort_values(by='Class SectionClass Number')
        prof_data_list.append(temp)
    return prof_data_list

def get_time_slots(class_sch, min_gap=0):
    '''Given the class timings, it will find and calculate the open times
       min_gap will be used to filter out time_slot less than min_gap
    '''
    if(len(class_sch)==0):
        return 'No Classes'

    times_list = [i for i in class_sch['Time']] #gets the class timings
    if(len(times_list) == 1): #if only one class happens
        return[('Before', remove_lead_trail_white_space(times_list[0].split('-')[0])),
              ('After', remove_lead_trail_white_space(times_list[0].split('-')[1]))]

    gap_list = [] #keeps track of the open times
    gap_list.append(('Before', remove_lead_trail_white_space(times_list[0].split('-')[0])))

    p2 = remove_lead_trail_white_space(times_list[0].split('-')[0])
    #used to filter out classes with diffrent names but with the same timings
    for i in range(len(times_list)-1):
        if(remove_lead_trail_white_space(times_list[i+1].split('-')[0]) != p2):
            p1 = remove_lead_trail_white_space(times_list[i].split('-')[1])
            p2 = remove_lead_trail_white_space(times_list[i+1].split('-')[0])
            if(((pd.to_datetime(p2) - pd.to_datetime(p1)).seconds // 60) >= min_gap):
                time_gap_hrs = (pd.to_datetime(p2) - pd.to_datetime(p1)).seconds // 3600 #get time gap in hrs
                time_gap_mins = ((pd.to_datetime(p2) - pd.to_datetime(p1)).seconds // 60)%60 #gets the remaining time gap in minutes

                gap_list.append((p1,p2, time_gap_hrs, time_gap_mins))

    gap_list.append(('After', remove_lead_trail_white_space(times_list[-1].split('-')[1])))

    return gap_list


def process_oneClassTime(timeSlot):
    return timeSlot[0][0] + ' ' + timeSlot[0][1] + ' and ' + timeSlot[1][0] + ' ' + timeSlot[1][1]


def processMultiClass(timeSlots):
    processed = []
    processed.append(timeSlots[0][0] + ' ' + timeSlots[0][1])
    for i in timeSlots[1:-1]:
        if(i[2] != 0):
            temp = i[0] + ' to ' + i[1] + ' (' + str(i[2]) + 'hr and ' + str(i[3]) + ' min)'
        else:
            temp = i[0] + ' to ' + i[1] + ' (' + str(i[3]) + ' min)'

        processed.append(temp)
    processed.append(timeSlots[-1][0] + ' ' + timeSlots[-1][1])
    return processed


def get_timeSlots_given_loc(locations, day, min_time):
    '''Returns all timeslots proccesed given locations, day, and min_time
       Format: for each location => [[no_classesList], {oneClassDict}, {multiClassDict}]'''

    time_slot_data_by_loc = []
    for i in locations:
        no_class_locs = []
        one_class_locs = []
        multi_class_locs = []

        one_class_times = []
        multi_class_times = []
        all_class_locs = set(filter(lambda x:True if x.split()[0] == i else False, tot_data['Location']))
        #line below removes all lab_locs so they are not considered for empty rooms
        all_class_locs = sorted(all_class_locs - lab_locs)
        for j in all_class_locs:
            temp = get_time_slots(classes_given_loc_day([j],day)[0], min_gap=min_time)
            if(type(temp) == str): #if its no classes
                no_class_locs.append(j)
            elif(len(temp) == 2): #if its one class location
                one_class_locs.append(j)
                one_class_times.append(process_oneClassTime(temp))
            else: #if its multi class location
                multi_class_locs.append(j)
                multi_class_times.append(processMultiClass(temp))

        oneClassDict = dict(zip(one_class_locs,one_class_times))
        multiClassDict = dict(zip(multi_class_locs, multi_class_times))
        time_slot_data_by_loc.append([', '.join(no_class_locs), oneClassDict, multiClassDict])

    return time_slot_data_by_loc


def get_class_data(class_list, course_name_list, data=tot_data):
    '''Gets all the class info'''
    if(len(class_list) == 0 and len(course_name_list) == 0):
        return 'Nothing selected'

    class_data_list = []
    if(len(class_list) != 0):
        for i in class_list:
            temp = data[data['Course pre'] == i].drop(['Class Title', 'Schedule &Location', 'Course pre'], axis=1).drop_duplicates()
            class_data_list.append(temp)

    if(len(course_name_list) != 0):
        for i in course_name_list:
            temp = data[data['Class Name'] == i].drop(['Class Title', 'Schedule &Location', 'Course pre'], axis=1).drop_duplicates()
            class_data_list.append(temp)

    return class_data_list










#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



app = Flask(__name__)

@app.route("/f3")
def my_form():
	curr_time = ':'.join(str(datetime.now().time()).split(':')[:2]) + ':00' #get the curr time
	twohr_time = datetime.now() + timedelta(hours=2)
	twohr_time = ':'.join(str(twohr_time).split(' ')[1].split(':')[:2]) + ':00'
	return render_template('my_form.html', time=curr_time, delay=twohr_time, building=zip(building_names, sorted(all_buildings)))

@app.route('/f3', methods=['POST'])
def my_form_post():
	day = request.form.get('days')
	start_time = request.form['start-time']
	end_time = request.form['end-time']
	locations = request.form.getlist('locations')


	curr_time = ':'.join(str(datetime.now().time()).split(':')[:2]) + ':00' #get the curr time
	twohr_time = datetime.now() + timedelta(hours=2)
	twohr_time = ':'.join(str(twohr_time).split(' ')[1].split(':')[:2]) + ':00'

	if(pd.to_datetime(start_time) == pd.to_datetime(end_time)): #will happen if times are equal
		return render_template('my_form.html', time=curr_time, delay=twohr_time, times=True, building=zip(building_names, sorted(all_buildings)))

	open_classes = get_open_locs(day, start_time, end_time, locations) #gets the open locations

	if(len(open_classes) == 0): #will happen if no rooms are found
		return render_template('my_form.html', time=curr_time, delay=twohr_time, norooms=True, building=zip(building_names, sorted(all_buildings)))


	data = []
	p1 = open_classes[0].split()[0]
	data.append('<h1 class="display-4" style="color: #000;">'+p1+'</h1>')
	for i in open_classes:
		if(i.split()[0] != p1):
			p1 = i.split()[0]
			data.append('<hr>')
			data.append('<h1 class="display-4" style="color: #000;">'+p1+'</h1>')
		data.append('<p class="lead" style="color: #000;">'+i+'</p>')

	data = [i for i in data if not(i in lab_locs)]
	return render_template('form_data.html', data=data, build_data=all_buildings)


@app.route('/')
def time_slot_form():
	return render_template('time_slot_form.html', building=zip(building_names, sorted(all_buildings)))

@app.route('/', methods=['POST'])
def time_slot_post():
	day = request.form.get('days')
	min_time = int(request.form['min-time'])
	locations = request.form.getlist('locations')
	if(len(str(min_time)) < 1 or len(locations) < 1):
		return render_template('time_slot_form.html', building=zip(building_names, sorted(all_buildings)), invalidSub = True)
	

	full_time_slot_data = get_timeSlots_given_loc(locations, day, min_time)

	
	return render_template('time_slot_data.html', data=full_time_slot_data, locs=locations, nums=range(len(locations)))





@app.route('/f2')
def class_give_loc_form():
	return render_template('classes_given_loc_form.html', data=loc_tags)


@app.route('/f2', methods=['POST'])
def class_given_loc_post():
	day = request.form.get('days')
	locations = request.form.getlist('locations')

	if(len(locations) == 0): #will happen if no locations are entered
		return render_template('classes_given_loc_form.html', nolocs=True, data=loc_tags)

	tot_data = classes_given_loc_day(locations,day)
	data_dict = {i:j for i,j in zip(locations,tot_data)}
	empty_locs = ', '.join([i for i,j in data_dict.items() if len(j) == 0])
	locations = [i for i,j in data_dict.items() if len(j) != 0]

	tot_data_to_print = []
	data_to_print = []
    #adding in temp_time to hold time of last class, doing this to remove duplicate listings
	temp_time = ''
	for classdata in tot_data:
		if (len(classdata) != 0):
			for i in range(len(classdata)):
			    temp = classdata.iloc[i]
			    if(temp['Time'] != temp_time):
				    class_title = temp['Class Name'] + ' '
				    class_prof = temp['Instructor(s)'] + ' '
				    time = temp['Time'] + ' '
				    temp_time = temp['Time']
				    data_to_print.append([class_title, class_prof, time])
			    else:
				    #skip the element if the time for that element matches the pervious time
					#I can do this b/c the elements are ordered by time
				    pass

			tot_data_to_print.append(data_to_print)
			data_to_print = []
		else:
			pass

	return render_template('classes_given_loc_form_data.html', data=tot_data_to_print, emptylocs=empty_locs, locs=locations, nums=range(len(locations)))


@app.route('/f1')
def prof_form():
	return render_template('prof_data_from.html', data=list(prof_rmp_id.keys()))


@app.route('/f1' , methods=['POST'])
def prof_data_form():
	profs_selected = request.form.getlist('profs')
	if(len(profs_selected) == 0): #will happen if no locations are entered
		return render_template('prof_data_from.html', noprofs=True, data=list(prof_rmp_id.keys()))

	prof_data = get_prof_data(profs_selected)
	rmp_base_p1 = 'http://www.google.com/search?rlz=1C1CHBF_enUS813US813&ei=1MsTXOGuBorytAW06ZWIAw&q='
	rmp_base_p2 = '+at+University+of+Texas+at+Dallas+site%3Aratemyprofessors.com'
	prof_urls = list(map(lambda x: rmp_base_p1+ '+'.join(x.split()) + rmp_base_p2, profs_selected))

	data_to_print = []
	tot_data_to_print = []
	for prof in prof_data:
		if (len(prof) != 0):
			for i in range(len(prof)):
				temp = prof.iloc[i]
				class_number = temp['Class SectionClass Number'] + ' '
				class_title = temp['Class Name'] + ' '
				class_day = temp['Days'] + ' '
				time = temp['Time'] + ' '
				class_loc = temp['Location'] + ' '



				data_to_print.append([class_number, class_title, class_day, time, class_loc])

			tot_data_to_print.append(data_to_print)
			data_to_print = []
		else:
			tot_data_to_print.append('Nothing Found')

	return render_template('prof_data.html', data=tot_data_to_print, profs=profs_selected, rmpData=prof_rmp_id, nums=range(len(profs_selected)))


@app.route('/f4')
def course_form():
	return render_template('course_form.html', nums=sorted(set(tot_data['Course pre'])), classNames=sorted(set(tot_data['Class Name'])))


@app.route('/f4', methods=['POST'])
def course_data_form():
	courseByNums = request.form.getlist('coursenums')
	classNames = request.form.getlist('classnames')
	course_form_data = get_class_data(courseByNums, classNames)
	if(len(courseByNums) == 0 and len(classNames) == 0):
		return render_template('course_form.html', noselection=True, nums=sorted(set(tot_data['Course pre'])), classNames=sorted(set(tot_data['Class Name'])))



	data_to_print = []
	tot_data_to_print = {}

	utd_grades_urls = {}
	for course in course_form_data:
		if(len(course) != 0):
			user_course_name = course.iloc[0]['Class Name']

			for i in range(len(course)):
				temp = course.iloc[i]
				classNumber = temp['Course Number']

				utd_grades_urls[user_course_name] = utdGrades_baseUrl + '%20'.join(classNumber.split('.')[0].split())

				profName = temp['Instructor(s)']
				classDay = temp['Days']
				classTime = temp['Time']
				classLoc = temp['Location']
				
				profLink = prof_rmp_id[remove_lead_trail_white_space(profName)]
				utdGrades_url = utdGrades_baseUrl + '%20'.join(classNumber.split())

				data_to_print.append([classNumber, profName, classDay, classTime, classLoc, profLink, utdGrades_url])

			tot_data_to_print[user_course_name] = data_to_print
			data_to_print = []
		else:
			pass


	return render_template('course_data_form.html', data=tot_data_to_print, utdGradesDict=utd_grades_urls)

	
from flask_mail import Mail, Message

app.config.update(dict(
    MAIL_SERVER = 'smtp.googlemail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'utdRooms@gmail.com',
    MAIL_PASSWORD = 'tryMe123'
))

mail = Mail(app)

@app.route('/f5')
def email_form():
	return render_template('emailForm.html')
	

@app.route('/f5', methods=['POST'])
def process_email():
	email = request.form.get('email')
	name = request.form.get('name')
	email_body = request.form.get('content')
	if(len(email) < 12): #7 b/c @.com is 5 charcs then 5 more just to make sure
		return render_template('emailForm.html', invalidEmail = True)
	else:
		wholeMesg = email + '\n' + name + '\n' + email_body
		msg = Message('From ' + email, sender='utdRooms@gmail.com', recipients=['utdRooms@gmail.com'])
		msg.body = wholeMesg #Customize based on user input
		mail.send(msg)
		return render_template('emailForm.html', emailSent = True)
	
#Another feature can be added which can help students figure out course info for next semester,Course Planner
