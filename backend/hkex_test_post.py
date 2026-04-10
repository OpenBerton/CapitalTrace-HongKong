import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.utils.html_utils import clean_html

base = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
headers = {'User-Agent': 'Mozilla/5.0'}

session = requests.Session()
resp = session.get(base, timeout=15, headers=headers)
print('GET status', resp.status_code)
html = clean_html(resp.text)
soup = BeautifulSoup(html, 'html.parser')
form = soup.find('form')
action = form.get('action') if form else ''
action_url = urljoin(base, action)
print('action_url', action_url)

fields = {inp['name']: inp.get('value', '') for inp in soup.find_all('input') if inp.get('name')}
print('form_fields', fields)

fields.update({
    '__EVENTTARGET': 'btnSearch',
    '__EVENTARGUMENT': '',
    'today': fields.get('today', ''),
    'sortBy': 'shareholding',
    'sortDirection': 'desc',
    'txtShareholdingDate': '2026/04/09',
    'txtStockCode': '07709',
    'txtStockName': '',
    'txtParticipantID': '',
    'txtParticipantName': '',
    'txtSelPartID': '',
})

response = session.post(action_url, data=fields, headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded', 'Referer': base}, timeout=15)
print('POST status', response.status_code)
print('response length', len(response.text))
print('first 800 chars:\n', response.text[:800])

soup2 = BeautifulSoup(clean_html(response.text), 'html.parser')
print('table count', len(soup2.find_all('table')))
for i, table in enumerate(soup2.find_all('table')):
    rows = table.find_all('tr')
    print('TABLE', i, 'rows', len(rows))
    for r in rows[:5]:
        print([td.get_text(strip=True) for td in r.find_all(['th','td'])])
