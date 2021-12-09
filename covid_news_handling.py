#start
#API Key: 9276ffd05cb4487980d806b50a365674
import requests, datetime, json, logging, time, sched


articles = []
last_update = ''


logger = logging.getLogger('covid news')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False

def update_news(update_name, update_interval=1200,scheduler=sched.scheduler(time.time, time.sleep),config=None):
    '''Function to update news with a designated interval adding it to the scheduler
     and returning the scheduler'''
    if config == None:
        event = scheduler.enter(update_interval,2,news_API_request)
    else:
        event = scheduler.enter(update_interval,2,update_name, argument=(config['keywords'],
                                                                config['language'],
                                                                config['sortBy'],
                                                                config['api key'],))
    return scheduler, event



def news_API_request(covid_terms='covid coronavirus COVID-19',
                     language='en',
                     sortBy='publishedAt',
                     api_key='9276ffd05cb4487980d806b50a365674') -> list:
    '''Builds a url using the correct data and then makes a request to the news API.
    Saving the returned data in a file 'covid news.json'.'''

    logger.info('Requesting Update From NewsAPI...')

    #splits the keywords
    #builds the url using the keywords and api key with predefined structure
    #requests response using url
    #gets response as json (dictionary)
    #writes the dictionary into a json file for troubleshooting

    keywords = covid_terms.split(' ')
    try:
        url = 'https://newsapi.org/v2/everything?qInTitle='+' OR '.join(keywords)+'&language='+language+'&sortBy='+sortBy+'&apiKey='+api_key
        response = requests.get(url, timeout=15)
    except requests.exceptions.Timeout:
        logger.warning('NewsAPI Request Timed Out')
        return

    #global articles to be changed within function
    global articles, last_update
    news_dict = json.loads(response.text)

    if news_dict['status'] != 'ok':
        logger.error('NewsAPI Request Failed, Code: %s, Message: %s',news_dict['code'],news_dict['message'])
        return

    #save the news data in a file for troubleshooting
    file = open('data\\covid_news.json', 'w')
    file = json.dump(news_dict, file)

    #if there was no last update
    #get all articles from file
    #set new last_update to time of most recent article
    if last_update == '':
        articles = news_dict['articles']
        last_update = datetime.datetime.strptime(articles[0]['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
    
    #if there was a last_update
    #iterate though articles
    #compare last update to time of article
    #add articles that are new to a list
    #replace last update
    else:
        for article in reversed(news_dict['articles']):
            datetime_object = datetime.datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            if datetime_object > last_update:
                last_update = datetime_object
                articles.insert(0,article)
            else:
                break

    logger.info('Update Successful!')
    
    #returns articles and last_update
    return articles



def remove_article(del_article: str):
    '''Removes the article with a matching title to the parameter del_article'''

    #changes scope of articles variable allowing it to be changed
    #iterates through each article
    #if title = article to be deleted then
    #remove that article from the list
    global articles
    for x in range (len(articles)):
        if articles[x]['title'] == del_article:
            articles.pop(x)
            break
    return articles