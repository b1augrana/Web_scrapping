import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers
from unicodedata import normalize

HOST = 'https://spb.hh.ru'
MAIN = f'{HOST}/search/vacancy?text=python&area=1&area=2'
KEYWORDS = ['django', 'flask']
headers = Headers(browser='firefox', os='win').generate()
main_page = requests.get(MAIN, headers=headers).text
bs = BeautifulSoup(main_page, features='lxml') 

filtered_links = []
salary_list = []
company_list = []
cities_list = []
vacancies_list = []


def get_links():
    vac_list = bs.find_all('a', class_='serp-item__title')
    for vacancy in vac_list:
        links = vacancy['href']   
        descr = (BeautifulSoup(requests.get(links, headers=headers).text, features='lxml')).find('div', {'data-qa': 'vacancy-description'}).text
        for word in KEYWORDS:
            if descr:
                 if word in descr.lower():
                      filtered_links.append(links)
    return filtered_links


def get_salary(filtered_links):
    for link in filtered_links:
        bs_salary = (BeautifulSoup(requests.get(link, headers=headers).text, features='lxml'))
        salary = bs_salary.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite')
        if not salary:
            continue
        salary_normal = normalize('NFKD', salary.text)
        salary_list.append(salary_normal)
    return salary_list    


def get_company(filtered_links):
    for link in filtered_links:
        bs_company = (BeautifulSoup(requests.get(link, headers=headers).text, features='lxml'))
        company_ = bs_company.find('a', class_='bloko-link bloko-link_kind-tertiary')
        if not company_:
            continue
        company_href = f'https://spb.hh.ru{company_["href"]}'
        bs2_company = (BeautifulSoup(requests.get(company_href, headers=headers).text, features='lxml'))
        company_2 = bs2_company.find('span', class_='company-header-title-name')
        if not company_2:
            continue
        company_normal = normalize('NFKD', company_2.text)
        company_list.append(company_normal)
    return company_list   

    
def get_city(filtered_links):
    for link in filtered_links:
        bs_city = (BeautifulSoup(requests.get(link, headers=headers).text, features='lxml'))
        city = bs_city.find('p', {'data-qa': 'vacancy-view-location'})
        if not city:
            city = bs_city.find('span', {'data-qa': 'vacancy-view-raw-address'})
            if not city:
                continue
            cities_list.append(city.text)
    return cities_list        


def get_vacancies(links, salaries, companies, cities):
    vacancies = zip(links, salaries, companies, cities)
    for link, salary, company, city in vacancies:
        vacancies_list.append({
            "link" : link,
            "salary" : salary,
            "company" : company,
            "city" : city
                 })
    return vacancies_list
            
            
        
get_links()  
get_salary(filtered_links)    
get_company(filtered_links)
get_city(filtered_links)
get_vacancies(filtered_links, salary_list, company_list, cities_list)

if __name__ == '__main__':
    with open('vacancies.json', 'w', encoding='utf-8') as vac:
        json.dump(vacancies_list, vac, indent=2, ensure_ascii=False)
    
