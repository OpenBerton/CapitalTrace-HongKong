import requests
from bs4 import BeautifulSoup
from app.utils.html_utils import clean_html

url = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
headers = {'User-Agent': 'Mozilla/5.0'}
session = requests.Session()
resp = session.get(url, timeout=15, headers=headers)
html = clean_html(resp.text)
soup = BeautifulSoup(html, 'html.parser')
print('hidden inputs:')
for inp in soup.find_all('input', {'type': 'hidden'}):
    print(inp.get('name'), repr(inp.get('value')))
print('\nBUTTONS:')
for btn in soup.find_all(['input', 'button']):
    if btn.get('name') and 'Search' in (btn.get('value') or '') or btn.get('name') == 'btnSearch':
        print(btn.name, btn.get('type'), btn.get('name'), btn.get('value'))
print('\nFORM ACTION:')
form = soup.find('form')
print(form.get('action') if form else 'no form')
print('\nINPUT NAMES:')
for inp in soup.find_all('input'):
    if inp.get('name') in ['txtShareholdingDate', 'txtStockCode', 'btnSearch', '__EVENTTARGET', '__EVENTARGUMENT', '__VIEWSTATE', '__VIEWSTATEGENERATOR', 'today', 'sortBy', 'sortDirection', 'originalShareholdingDate', 'alertMsg']:
        print(inp.get('name'), inp.get('type'), repr(inp.get('value')))
print('\nTABLE COUNT', len(soup.find_all('table')))
for i, table in enumerate(soup.find_all('table')):
    rows = table.find_all('tr')
    if rows:
        print('\nTABLE', i, 'first row', [td.get_text(strip=True) for td in rows[0].find_all(['th','td'])][:5])
