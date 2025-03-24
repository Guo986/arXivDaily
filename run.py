from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import urllib, urllib.request
import time
import argparse
import yaml
import os
from translate import translate

def load_config(configFile):
    def getKeywords(config):
        keywords = {}
        for k,v in config['keywords'].items():
            keywords[k] = list(map(lambda x:'%22'+x.replace(' ', '+')+'%22' if ' ' in x else x, v))
        return keywords            
    with open(configFile, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        config['keywords'] = getKeywords(config)
    return config

def get_past_time_gmt(pastDays: int):
        # 获取当前UTC时间
        current_time = datetime.now(timezone.utc)
        # 计算pastDays天前的0点时间
        past_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=pastDays)
        # 格式化为YYYYMMDDTTTT
        formatted_time = past_time.strftime('%Y%m%d%H%M')
        return '['+formatted_time+'+TO+'+current_time.replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y%m%d%H%M')+']'

def get_content(url):
    global allTokens
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
        thisPaper['abstract'] = i.summary.text.replace('\n', ' ')
        thisPaper['Chinese_abstract'],token = translate(thisPaper['abstract'], True)
        allTokens += token
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
    results = {}
    for key in config['keywords'].keys():
        results[key] = []
        for value in config['keywords'][key]:
            # build search time
            submittedDate = get_past_time_gmt(config['pastDays'])
            search_query = '%s+AND+submittedDate:%s' % ('all:'+value, submittedDate)
            
            for i in range(config['start'], config['total_results'], config['results_per_iteration']):
                # print("Results %i - %i" % (i, i+config['results_per_iteration']))        
                query = 'search_query=%s&start=%i&max_results=%i&sortBy=lastUpdatedDate&sortOrder=descending' % (search_query, i, config['results_per_iteration'])
                print('Search arXiv:', config['base_url']+query)
                papers = get_content(config['base_url']+query)
                results[key].extend(papers)

                print('Sleeping for %i seconds' % config['wait_time'] )
                time.sleep(config['wait_time'])
    return results

def outResults(results):
    global allTokens
    print(f"{allTokens=}")
    # print(json.dumps(results, indent=4))
    for k,v in results.items():
        print('%s -- %d papers' % (k, len(v)))
    if not os.path.exists(config['saveBasePath']):
        os.makedirs(config['saveBasePath'])
    with open(os.path.join(config['saveBasePath'], get_past_time_gmt(config['pastDays'])+'.json'), 'a', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    
if __name__== "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path',type=str, default='config.yaml',
                            help='configuration file path')
    args = parser.parse_args()
    config = load_config(args.config_path)
    allTokens = 0
    results = main()
    outResults(results)