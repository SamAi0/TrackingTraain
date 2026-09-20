import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options

print("Starting selenium test...")

login = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'username': 'testuser', 'password': 'password123'})
token = login.json().get('access')

b_resp = requests.post('http://127.0.0.1:8000/api/bookings/', json={
    'train_number': '12951', 'source_code': 'BVI', 'destination_code': 'NDLS',
    'date_of_journey': '2027-10-10', 'ticket_class': '3A',
    'passengers': [{'name': 'Test User', 'age': 30, 'berth_preference': 'LB', 'gender': 'Unknown'}]
}, headers={'Authorization': f'Bearer {token}'})

booking_data = b_resp.json()
booking_id = booking_data.get('id')
print(f"Created Booking ID: {booking_id}")
print(f"API expires_at: {booking_data.get('expires_at')}")

options = Options()
options.add_argument('--headless')
options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

driver = webdriver.Edge(options=options)

try:
    driver.get("http://127.0.0.1:5500/pages/auth/login.html")
    driver.execute_script(f"localStorage.setItem('access_token', '{token}');")
    
    url = f"http://127.0.0.1:5500/pages/booking/payment.html?id={booking_id}"
    driver.get(url)
    
    timer_badge = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "timerBadge"))
    )
    
    time.sleep(3) # wait for fetch to complete and interval to tick a few times
    
    for log in driver.get_log('browser'):
        print(f"BROWSER LOG: {log}")
    
    text1 = timer_badge.text
    print(f"Timer after 3s: {text1}")
    
    time.sleep(1.5)
    text2 = timer_badge.text
    print(f"Timer after 4.5s: {text2}")
    
    if text1 == text2 or text1 == "10:00":
        print("FAIL: Timer is not decreasing or stuck at 10:00")
        exit(1)
        
    print("Timer is decreasing successfully.")
    
    # Wait for expiration overlay
    overlay = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "overlayContent"))
    )
    print(f"Overlay text: {overlay.text}")
    
    pay_resp = requests.post('http://127.0.0.1:8000/api/bookings/process-payment/', json={
        'booking_id': booking_id,
        'method': 'upi',
        'idempotency_key': 'key_expired2',
        'payment_details': {'upi_id': 'test@ok'}
    }, headers={'Authorization': f'Bearer {token}'})
    
    print(f"Payment response on expired: {pay_resp.status_code} {pay_resp.text}")
    if pay_resp.status_code == 200:
        print("FAIL: Backend accepted payment for expired booking")
        exit(1)
        
    print("ALL PASSED")
    
finally:
    driver.quit()
