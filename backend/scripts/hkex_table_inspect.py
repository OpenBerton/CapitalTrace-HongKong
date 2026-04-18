import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.utils.html_utils import clean_html

base = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
headers = {'User-Agent': 'Mozilla/5.0'}

session = requests.Session()
resp = session.get(base, timeout=15, headers=headers)
resp.raise_for_status()
html = clean_html(resp.text)
soup = BeautifulSoup(html, 'html.parser')
form = soup.find('form')
action = urljoin(base, form.get('action') if form else base)
print('FORM ACTION', action)
form_values = {inp['name']: inp.get('value', '') for inp in soup.find_all('input') if inp.get('name')}
form_values.update({
    '__EVENTTARGET': 'btnSearch',
    '__EVENTARGUMENT': '',
    'today': form_values.get('today', ''),
    'sortBy': 'shareholding',
    'sortDirection': 'desc',
    'txtShareholdingDate': '2026/04/09',
    'txtStockCode': '07709',
    'txtStockName': '',
    'txtParticipantID': '',
    'txtParticipantName': '',
    'txtSelPartID': '',
})
print('PAYLOAD KEYS', list(form_values.keys()))
response = session.post(action, data=form_values, headers={**headers, 'Content-Type': 'application/x-www-form-urlencoded', 'Referer': base}, timeout=30)
print('POST STATUS', response.status_code)
html2 = clean_html(response.text)
soup2 = BeautifulSoup(html2, 'html.parser')
print('TABLE COUNT', len(soup2.find_all('table')))
for idx, table in enumerate(soup2.find_all('table')):
    print('\nTABLE', idx, 'class', table.get('class'))
    rows = table.find_all('tr')
    print('  tr count', len(rows))
    for row in rows[:4]:
        print('   row', [td.get_text(strip=True) for td in row.find_all(['th', 'td'])])
