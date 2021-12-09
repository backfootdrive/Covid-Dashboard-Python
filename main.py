#start
import time, datetime, sched, json, logging
from flask import Flask, render_template, redirect, request
import covid_data_handler as data
import covid_news_handling as news

s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)

app.logger = logging.getLogger(__name__)

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False


@app.route('/')
def url_redirect():
    '''Function that redirects the url to /index'''
    return redirect('/index')



@app.route('/index')
def template():
    '''Main flask route, this function checks if anything needs updating and then
    renders the associated template'''

    global s, updates, auto_updates

    #iterates through all updates
    #if they are to repeat compare against current time
    #if lower schedule new event in 24 hours
    #adds a day to the date of the update
    for x in range(len(updates)):
        if updates[x]['repeat'] == True:
            if updates[x]['date'] < datetime.datetime.today():
                logger.info('Re-Scheduling Repeat Update')
                s,events = update_data(updates[x]['schedule'],86400,s)
                updates[x]['date'] = updates[x]['date'] + datetime.timedelta(days=1)
                updates[x]['events'] = events
        
        #if it is not meant to repeat
        #check if is still queued
        #if it is not queued delete from updates list
        else:
            if updates[x]['date'] < datetime.datetime.today():
                logger.info('Removing Finished Update From Displayed List...')
                updates.pop(x)

    #gets notif argument from url if exists
    #checks if argument exists
    #call function to delete the story from the dashboard
    del_article = request.args.get('notif')
    if del_article:
        logger.info('Removing Desired Article From Displayed List...')
        news.remove_article(del_article)
        logger.info('Article Removed Successfully!')

    #gets update argument from url
    #if argument exists
    #update the data
    update = request.args.get('update')
    if update:
        manual_schedule_update(update)

    #gets deleted event argument from url
    #checks if there is an event to be deleted
    #iterates through updates
    #deletes the event and cancels the associated sched items
    del_event = request.args.get('update_item')
    if del_event:
        logger.info('Cancelling Desired Update...')
        for x in range(len(updates)):
            if updates[x]['title'] == del_event:
                for item in updates[x]['events']:
                    try:
                        logger.info('Removing Update From Scheduler...')
                        s.cancel(item)
                    except ValueError:
                        logger.error('Failed To Cancel Update!!!')
                updates.pop(x)
                break

    #checks if the auto update for news and data is in the scheduler
    #if not it reschedules it using its respective interval
    for x in range(len(auto_updates)):
        if auto_updates[x]['event'][0] not in s.queue:
            logger.info('Re-Scheduling Automatic Update - %s',auto_updates[x]['name'])
            s, events = update_data(x+1,auto_updates[x]['interval'],s)
            auto_updates[x]['event'] = events

    #runs the scheduler if the jobs are overdue
    logger.info('Running Due Events From Scheduler...')
    s.run(blocking=False)

    local_7day_cases = data.process_covid_json_data(data.local_data,'local')
    national_7day_cases,total_deaths,hospital_cases = data.process_covid_json_data(data.national_data,'national')

    #renders the index.html template with given variables
    return render_template('index.html',
                            title='Daily update',
                            favicon=config['favicon'],
                            image='stat-icon.png',
                            location=config['data']['AreaName'],
                            local_7day_infections=local_7day_cases,
                            nation_location=config['data']['NationName'],
                            national_7day_infections=national_7day_cases,
                            hospital_cases='Hospital Cases: ' + str(hospital_cases),
                            deaths_total='Total Deaths: ' + str(total_deaths),
                            news_articles=news.articles,
                            updates=updates)



def update_data(x: int,update_interval: int,s):
    '''Function that schedules the update of one or both functions with a given interval'''

    #if x = 1, only covid data is updated
    #if x = 2, only news is updated
    #if x = 3, both are updated
    events = []
    if x == 1 or x == 3:
        logger.info('Scheduling Update To Covid Data...')
        s, e1 = data.schedule_covid_updates(update_interval,data.covid_api_request,s,config['data'])
        logger.info('Update Scheduled Successfully!')
        events.append(e1)
    if x >= 2:
        logger.info('Scheduling Update To News Data...')
        s, e2 = news.update_news(update_interval+1,news.news_api_request,s,config['news'])
        logger.info('Update Scheduled Successfully!')
        events.append(e2)
    return s, events



def time_to_seconds(update: str) -> int:
    '''Function to get the difference in seconds between the current time
    and the time given'''

    #splits the time as a string by the colon
    update_time = update.split(':')

    #replaces the curent date and time with the new time
    update_time = datetime.datetime.today().replace(hour=int(update_time[0]),
                                                    minute=int(update_time[1]),
                                                    second=0,
                                                    microsecond=0)
    #compares the new time to current time
    #if lower it will add an extra day to the new time
    if update_time < datetime.datetime.today():
        update_time = update_time + datetime.timedelta(days=1)
    
    #gets the difference between the times
    #converts the difference to seconds
    difference = update_time - datetime.datetime.today()
    difference_seconds = difference.total_seconds()

    #returns the difference in seconds
    return difference_seconds, update_time



def manual_schedule_update(update: str) -> None:
    '''Function used to schedule updates should there be an update request'''

    #gets the difference in seconds between the time and current time
    update_interval, update_time = time_to_seconds(update)

    #gets arguments from the url to be checked
    covid_data = request.args.get('covid-data')
    news = request.args.get('news')
    text = request.args.get('two')
    repeat = request.args.get('repeat')

    title = update + ': ' + text

    x = 0
    #checks if covid data is to be updated
    if covid_data:
        x += 1
        string = 'Covid Data Update'
    #checks if news is to be updated
    if news:
        x += 2
        string = 'News Update'
    #checks if both news and covid data are to be updated
    if x == 3:
        string = 'Covid Data & News Update'
    #if nothing is to be updated return from function
    elif x == 0:
        return

    #use global keyword to change variable in global scope
    #update the content of the dictionary to include what is being updated
    #add the dictionary to the list of updates
    #schedule the data
    global updates, s
    s, events = update_data(x,update_interval,s)
    updates_dic = {'title': title,
                   'content': string,
                   'events':events,
                   'time': update,
                   'date': update_time,
                   'schedule': x,
                   'repeat': False}

    #if the update is to be repeated
    #add the update to repeated updates list
    if repeat:
        updates_dic['content'] = 'Repeat ' + string
        updates_dic['repeat'] = True

    updates.append(updates_dic)
    logger.info('Added Manual Update To Updates List!')




#starting the program
if __name__ == '__main__':
    logger.info('Starting The Program...')
    #imports config settings
    logger.info('Getting Config Settings From Config File')
    f = open('config.json','r')
    config = json.load(f)
    f.close()

    auto_updates = [{'name': 'Data','interval': config['data']['interval'],'event': ['']},
                    {'name': 'News','interval': config['news']['interval'],'event': ['']}]
    updates = []

    #updating both news and covid data before launching dashboard
    s, events = update_data(3,1,s)
    s.run()
    
    #running the flask application
    logger.info('Flask App Is Starting...')
    app.run()