import os
import django
import time
import threading
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gumbuz_shop.settings')
django.setup()

def simulate_user(user_id, duration=30):
    client = Client(HTTP_HOST='127.0.0.1')
    # Force session creation
    session = client.session
    session['simulated_user'] = user_id
    session.save()
    
    print(f"User {user_id} connected.")
    
    # Keep sending requests
    start_time = time.time()
    while time.time() - start_time < duration:
        client.get('/panel/login/')
        time.sleep(5) # Stay active
        
    print(f"User {user_id} disconnected.")

def run_simulation(num_users=5, duration=30):
    print(f"Simulating {num_users} users for {duration} seconds...")
    threads = []
    for i in range(num_users):
        t = threading.Thread(target=simulate_user, args=(i, duration))
        threads.append(t)
        t.start()
        time.sleep(0.5) # Stagger connections
        
    for t in threads:
        t.join()
        
    print("Simulation finished.")

if __name__ == "__main__":
    # Simulate 5 extra users for 60 seconds
    run_simulation(num_users=5, duration=60)
