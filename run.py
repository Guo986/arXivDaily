from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import urllib, urllib.request
import time

def get_past_time_gmt(pastDays: int):
        # 获取当前UTC时间
        current_time = datetime.now(timezone.utc)
        # 计算pastDays天前的0点时间
        past_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=pastDays)
        # 格式化为YYYYMMDDTTTT
        formatted_time = past_time.strftime('%Y%m%d%H%M')
        return '['+formatted_time+'+TO+'+current_time.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y%m%d%H%M')+']'
def get_content(url):
    print(url)
    data = urllib.request.urlopen(url)
    xml = data.read().decode('utf-8')
    soup = BeautifulSoup(xml, "xml")
    # print(soup.prettify())
    allItems = soup.find_all('entry')
    papers = []
    for i in allItems:
        thisPaper = {}
        thisPaper['id'] = i.id.text
        thisPaper['updated'] = i.updated.text
        thisPaper['title'] = i.title.text
        thisPaper['author'] = ', '.join([j.text for j in i.find_all('name')])
        thisPaper['pdfLink'] = [link.attrs['href'] for link in i.find_all('link') if link.attrs['rel']=='related' and link.attrs['title']=='pdf'][0]
        if len(i.find_all('arxiv:comment'))>0:
            thisPaper['comment'] = i.find_all('arxiv:comment')[0].text
        else:
            thisPaper['comment'] = ''
        thisPaper['term'] = '; '.join([item.attrs['term'] for item in i.find_all('category')])
        papers.append(thisPaper)
    return papers

def main():
    for key in keywords:
        results[key] = []
        # build search time
        submittedDate = get_past_time_gmt(pastDays)
        search_query = '%s+AND+submittedDate:%s' % ('all:'+key, submittedDate)
        print('Searching arXiv for %s' % search_query)

        for i in range(start, total_results, results_per_iteration): # 0 5 10 15
            print("Results %i - %i" % (i, i+results_per_iteration))        
            query = 'search_query=%s&start=%i&max_results=%i&sortBy=lastUpdatedDate&sortOrder=descending' % (search_query, i, results_per_iteration)
            papers = get_content(base_url+query)
            results[key].extend(papers)

            print('Sleeping for %i seconds' % wait_time )
            time.sleep(wait_time)
    print(json.dumps(results, indent=4))

if __name__== "__main__" :
    keywords = ['agent', 'Time Series']
    pastDays = 1

    base_url = 'https://export.arxiv.org/api/query?'
    start = 0
    total_results = 100              # want xxx total results
    results_per_iteration = 100      # xxx results at a time
    wait_time = 5                    # number of seconds to wait beetween calls
    results = {}
    keywords = list(map(lambda x:'%22'+x.replace(' ', '+')+'%22' if ' ' in x else x, keywords))
    
    main()
