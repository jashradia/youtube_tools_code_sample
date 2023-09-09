from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import Counter

# Function to scrape LinkedIn job postings and extract skills
def scrape_linkedin_jobs(keyword, num_pages):
    job_skills = []

    # Set up options for the Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode (optional)
    options.add_argument("--no-sandbox")

    # Start a Selenium WebDriver with options
    driver = webdriver.Chrome(options=options)


    url = f'https://www.linkedin.com/jobs/search/?keywords={keyword}'
    driver.get(url)
    j = 0
    # Scroll to load more jobs (you may need to adjust the number of scrolls)
    for _ in range(num_pages):
        print("scroll ######",j)
        j = j+1
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)  # Wait for content to load

    # Extract job titles and skills (modify as needed)
    job_cards = driver.find_elements(By.CSS_SELECTOR, '.base-card')
    break_element = 0
    for card in job_cards:
        try:

            job_title_element = WebDriverWait(card, 10)\
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, '.base-search-card__title')))
            company_element = WebDriverWait(card, 10)\
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, '.base-search-card__subtitle')))
            description = WebDriverWait(card, 10)\
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, '.base-card__full-link')))


            company_name = company_element.text
            job_title = job_title_element.text
            print(job_title, " ", company_name)
            job_link = description.get_attribute('href')
            print(job_link)

            #Hitting each job's URL to get more information
            job_driver = webdriver.Chrome(options=options)
            job_driver.get(job_link)

            #expand descriptions by clicking on show more
            expand_description(job_driver)
            #extract description element
            job_description = extract_job_description(job_driver)
            #extract skills from description
            extracted_skills = extract_skills(job_description)
            job_skills.append(extracted_skills)
            job_driver.quit()

        except Exception as e:
            print("Job details not found for this card.")
            continue

    # Close the WebDriver when done
    driver.quit()

    #print(job_skills)

    return job_skills


# Function to extract job description using JavaScript
def extract_job_description(driver):
    try:
        # Wait for the job description element to be present (you can adjust the timeout)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.description')))

        # Execute JavaScript code to extract job description
        job_description = driver.execute_script("return document.querySelector('.description').textContent")
        return job_description
    except TimeoutException:
        return "Job description not found or couldn't be loaded"

# Function to expand job description by clicking "show more" if available
def expand_description(driver):
    try:
        show_more_button = WebDriverWait(card, 10)\
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, '.show-more-less-html__button')))

        show_more_button.click()
        time.sleep(2)  # Wait for the description to expand
    except Exception as e:
        pass  # No "show more" button found or error occurred


# Function to extract skills from a job title
def extract_skills(description):
    # This is a basic example, you can extend this to match more skills
    skills = ['PostgreSQL','Snowflake','Databricks','Redshift','BigQuery','MongoDB','MySQL',
              'Kafka','Kinesis','PubSub','Pub/sub','event hub','Airflow','dbt','NiFi', 'Fivetran',
            'Collibra','Denodo','presto','Starburst','Immuta','PowerBI','Tableau','Looker',
             'Matillion','Alteryx','Informatica','Talend','EMR','Dataproc','Synapse']
    description = description.lower()
    skills_list = [skill for skill in skills if skill.lower() in description]
    print(skills_list)
    return skills_list

# Main function
if __name__ == "__main__":
    keyword = "data%20engineer"
    num_pages = 20 # You can adjust the number of pages to scrape

    job_skills = scrape_linkedin_jobs(keyword, num_pages)

    print(f'Data engineer jobs: {len(job_skills)}')

    flattened_skills = [skill for sublist in job_skills for skill in sublist]
    skill_counts = Counter(flattened_skills)
    top_skills = skill_counts.most_common(30)

    for skill, count in top_skills:
        print(f'{skill}: {count}')
