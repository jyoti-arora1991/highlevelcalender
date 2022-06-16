import datetime
import enum
import random
import time

from playwright.sync_api import Playwright, sync_playwright, expect
calenderlink="https://link.gohighlevel.com/widget/appointment/test13june2022/13"
appointmentslink="https://app.gohighlevel.com/v2/location/6Sz3MjOWtMfiw7EQ8be7/calendars/appointments"
appointment_date ='2022-6-22'

class get_tz(enum.Enum):
    africa_algers=['Africa/Algiers' , '+01:00']
    Africa_Casablanca=['Africa/Casablanca','+01:00']
    Africa_Lagos=['Africa/Lagos','+01:00']
    Africa_Cairo=['Africa/Cairo','+02:00']
    Asia_Calcutta=['Asia/Calcutta', '+05:30']
    Asia_Dhaka=['Asia/Dhaka', '+06:00']
    Asia_Dubai=['Asia/Dubai', '+04:00']


def select_date(appointment_date,page):
    flag=False
    # time.sleep(10)
    page.wait_for_selector('//td[@data-id="%s"]' % appointment_date)
    ele=page.locator('//td[@data-id="%s"]' % appointment_date)
    print(ele.get_attribute("class"))
    if "selectable" in ele.get_attribute("class"):
        flag=True
        ele.click(timeout=3600)
    return flag

def select_timezone(timez,page):
    page.locator("//span[@class='multiselect__single']").click()
    page.locator("//input[contains(@placeholder,'timezone')]").fill(timez)
    page.keyboard.press("Enter")

def select_and_get_first_time(page):
    page.wait_for_selector("//ul[@class='widgets-time-slots']//li[1]")
    time_ele = page.locator("//ul[@class='widgets-time-slots']//li[1]")
    a=time_ele.text_content()
    time_ele.click(timeout=10000)
    return a

def get_time_timezone(t,format):
    return datetime.datetime.strptime(t, format).timestamp()


def run_calender(page):
    # Go to https://link.gohighlevel.com/widget/appointment/test13june2022/13
    page.goto(calenderlink)
    flag = select_date(appointment_date, page)
    print(flag)
    if not flag:
        print("Selected date '%s' is not schedulable" % appointment_date)
        assert flag == True
    tz = random.choice(list(get_tz))
    print(tz.value[0])
    select_timezone(tz.value[0], page)
    slot = select_and_get_first_time(page)
    page.wait_for_selector("text=Continue")
    page.locator("text=Continue").click()
    page.locator("id=first_name").fill("jyoti")
    page.locator("id=last_name").fill("arora")
    page.locator("id=phone").fill("08130727089")
    page.locator('//input[@name="email"]').fill("mail.jyotiarora1991@gmail.com")
    page.wait_for_timeout(10000)
    # page.wait_for_selector("text=Schedule Meeting >> button")
    # page.click("text=Schedule Meeting >> button")
    page.locator('//*[@id="appointment_widgets"]//footer//button').click()
    assert "Your Meeting has been Scheduled" in page.locator("text=Your Meeting has been Scheduled").text_content()
    schedule_time_user = "%s %s" % (appointment_date, slot)
    return get_time_timezone(schedule_time_user + tz.value[1], "%Y-%m-%d %I:%M %p %z")



def check_appointment(page):
    page.goto(appointmentslink)
    page.locator("id=email").fill("mail.jyotiarora1991@gmail.com")
    page.locator("id=password").fill("Test123!")
    page.locator("button:has-text(\"Sign in\")").click()
    app_time=page.locator("#pg-appt__link-contact-detail").first.text_content()
    return get_time_timezone(app_time.strip() + ' ' + '+05:30', "%b %d %Y, %I:%M %p %z")


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    schedule_time=run_calender(page)
    app_time=check_appointment(page)
    print(schedule_time,app_time)