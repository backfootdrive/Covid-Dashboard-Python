#start
from uk_covid19 import Cov19API, exceptions
import logging, sched, time, sys

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)

logger = logging.getLogger('covid data')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False

data = {'local data': None, 'national data': None}

def schedule_covid_updates(update_interval: int,update_name, scheduler=sched.scheduler(time.time, time.sleep),config=None):
    '''Function for scheduling the updates to the covid data using a designated interval'''
    if config == None:
        event = scheduler.enter(update_interval,1,covid_API_request)
        
    else:
        event = scheduler.enter(update_interval,1,update_name,argument=(config['AreaName'],
                                                                        config['AreaType'],
                                                                        config['NationName'],))
    return scheduler, event



def covid_API_request(location='Exeter',location_type='ltla',nation='England') -> dict:
    '''This function gets data from an API to use and then saves it as a global variable,
    using different filters and a pre-defined structure'''

    logger.info('Requesting Update From Covid API...')

    #filter for the API to select data by area
    area_type = ('areaType={}'.format(location_type))
    area_name = ('areaName={}'.format(location))
    local_only = [area_type,
                  area_name]

    #filter for the API to select data by nation
    nation_name = ('areaName={}'.format(nation))
    nation_only = ['areaType=nation',
                   nation_name]

    #Creates a structure for the API to use when returning data
    cases_and_deaths = {
    'areaCode': 'areaCode',
    'areaName': 'areaName',
    'areaType': 'areaType',
    'date': 'date',
    'cumDailyNsoDeathsByDeathDate': 'cumDailyNsoDeathsByDeathDate',
    'hospitalCases': 'hospitalCases',
    'newCasesBySpecimenDate': 'newCasesBySpecimenDate'}

    global data
    #intialises the API using the nation_only filter and the structure above
    #puts the data from the API into a dictionary

    error = False
    try:
        api = Cov19API(filters=nation_only, structure=cases_and_deaths)
        data['national data'] = api.get_json(save_as='data\\national_data.json')
    except exceptions.FailedRequestError as inst:
        x = str(inst.args[0]).split('\n')
        logger.critical('UK COVID-19 API Request Failed (Nation), Message: %s',x[1])
        error = True

    #intialises the API using the local_only filter and the structure above
    #puts the data from the API into a dictionary
    try:
        api = Cov19API(filters=local_only, structure=cases_and_deaths)
        data['local data'] = api.get_json(save_as='data\\local_data.json')
    except exceptions.FailedRequestError as inst:
        x = str(inst.args[0]).split('\n')
        logger.critical('UK COVID-19 API Request Failed (Local), Message: %s',x[1])
        error = True

    if error == True:
        return

    logger.info('Update Successful!')

    #returns the two dictionaries
    return data



def process_covid_json_data(data: dict,type='local') -> int:
    '''Function used to process the data that was obtained via the API and get
    the relevent variables from within'''

    #gets the list of data under the key 'data'
    data = data['data']

    #sets 7day_cases to zero
    #iterates through each element of the list
    #if element has a value
    #add 7 values after that value
    #break out of loop once done
    last7days_cases = 0
    for x in range(len(data)):
        if data[x]['newCasesBySpecimenDate']:
            for y in range(7):
                last7days_cases = last7days_cases + data[(x+y+1)]['newCasesBySpecimenDate']
            break

    #if the data is national
    #iterate through each element of list using different keys
    #once a value for that key has been found append to list
    #break out of sub loop and start again using different key
    if type == 'national':
        keys = ['cumDailyNsoDeathsByDeathDate','hospitalCases']
        values = []
        for i in range(2):
            for x in range(len(data)):
                if data[x][keys[i]]:
                    values.append(data[x][keys[i]])
                    break
        return last7days_cases,values[0],values[1]
    return last7days_cases



def parse_csv_data(csv_filename: str) -> list:
    '''Function to open the sample csv file data and return as list'''

    #opens file
    #reads all lines of file and puts in list
    #closes the file
    f = open(csv_filename, 'r')
    data = f.readlines()
    f.close()
    
    #returns list
    return data



def process_covid_csv_data(data: list) -> int:
    '''Function to process the data extracted from the csv file'''

    values = []
    last7days_cases = 0
    #gets first value of hospital cases and total deaths that isn't null
    for x in range(4,6):
        for y in range(1,len(data)):
            string = data[y].strip('\n').split(',')
            if string[x] != '':
                values.append(int(string[x]))
                break

    #adds the new cases for 7 days starting from line 4
    for x in range(3,10):
        string = data[x].strip('\n').split(',')
        last7days_cases = last7days_cases + int(string[6])

    return last7days_cases, values[1], values[0]



#covid_API_request('Exeter','ltla')
#schedule_covid_updates(1,covid_API_request)

#parse_csv_data('data\\nation_2021-10-28.csv')
#print(process_covid_json_data.__doc__)
#process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))