
import random
import time

class Driver:
    def __init__(self, name, current_location):
        self.name = name
        self.current_location = current_location

    def receive_notification(self, user):
        print(f"Notification: Ride request from {user.name} at {user.pickup_location}")
        
        # Calculate distance between driver's current location and user's pickup location
        distance = calculate_distance(self.current_location, user.pickup_location)
        
        # Decide based on distance
        if distance <= 10:  # Accept the ride if within 10 km radius
            print(f"{self.name} accepts the ride.")
            return True
        else:
            print(f"{self.name} rejects the ride because it's too far.")
            return False

# Function to calculate distance (dummy implementation)
def calculate_distance(location1, location2):
    # Dummy implementation: calculate distance based on coordinates, such as latitude and longitude
    # Replace this with actual distance calculation method
    return 5  # Example: return a dummy distance of 5 km

class User:
    def __init__(self, name, pickup_location, destination):
        self.name = name
        self.pickup_location = pickup_location
        self.destination = destination

class Ride:
    def __init__(self, user, driver):
        self.user = user
        self.driver = driver

    def confirm_ride(self):
        if self.driver.receive_notification(self.user):
            print("Ride confirmed!")
            return True
        else:
            print("Ride rejected.")
            return False

    def start_ride(self):
        print("Ride started!")
        # Simulate ride experience with real-time tracking
        for i in range(10):  # Simulate 10 iterations for tracking
            time.sleep(1)  # Simulate real-time tracking interval
            print(f"{self.driver.name} is at location {random.randint(1, 100)}")
        print(f"{self.driver.name} has arrived at {self.user.pickup_location}")

    def complete_ride(self):
        print(f"{self.driver.name} has transported {self.user.name} to {self.user.destination}. Ride completed!")

# Sample usage
if __name__ == "__main__":
    # User requests a ride
    user = User(name="Alice", pickup_location="Home", destination="Work")

    # Driver receives notification
    driver = Driver(name="Bob", current_location="Street")

    # Ride confirmation
    ride = Ride(user, driver)
    if ride.confirm_ride():
        # Ride starts
        ride.start_ride()
        # Ride ends
        ride.complete_ride()
