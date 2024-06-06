import random
import time

class User:
    def __init__(self, name, pickup_location, destination):
        self.name = name
        self.pickup_location = pickup_location
        self.destination = destination

    def request_ride(self):
        print(f"{self.name} requests a ride from {self.pickup_location} to {self.destination}")
        return Ride(self)

class Driver:
    def __init__(self, name, current_location):
        self.name = name
        self.current_location = current_location

    def accept_ride(self, ride):
        if ride.user.pickup_location == self.current_location:
            print(f"{self.name} accepts the ride request")
            return ride
        else:
            print(f"{self.name} cannot accept the ride request as it is not at the pickup location")
            return None

class Ride:
    def __init__(self, user):
        self.user = user

    def confirm_ride(self, driver):
        if driver:
            self.driver = driver
            print(f"Ride confirmed! {self.driver.name} is on the way to pick up {self.user.name} at {self.user.pickup_location}")
        else:
            print("Ride could not be confirmed due to driver unavailability.")

    def start_ride(self):
        if hasattr(self, 'driver'):
            print(f"{self.user.name} is now in the car with {self.driver.name}. Heading towards {self.user.destination}")
        else:
            print("Ride cannot start as driver is not available.")

    def complete_ride(self):
        if hasattr(self, 'driver'):
            print(f"{self.user.name} has reached the destination. Thank you for riding with us!")
        else:
            print("Ride could not be completed as driver is not available.")

class Payment:
    @staticmethod
    def process_payment(user, fare):
        print(f"Processing payment of ${fare} for {user.name}")

class Feedback:
    @staticmethod
    def give_feedback(user, driver, rating, comment):
        print(f"{user.name} rates {driver.name} with {rating} stars and leaves the following comment: {comment}")

# Simulation
if __name__ == "__main__":
    # User registration
    user = User(name="Alice", pickup_location="Home", destination="Work")
    # Driver registration
    driver = Driver(name="Bob", current_location="Home")

    # User requests a ride
    ride = user.request_ride()

    # Driver accepts the ride
    ride = driver.accept_ride(ride)

    # Ride confirmation
    ride.confirm_ride(driver)

    # Start ride
    ride.start_ride()

    # Simulate ride progress
    time.sleep(5)  # Simulate ride duration

    # Complete ride
    ride.complete_ride()

    # Simulate payment
    fare = 10.0  # Example fare
    Payment.process_payment(user, fare)

    # Simulate feedback
    rating = 5  # Example rating
    comment = "Great ride, very polite driver!"
    Feedback.give_feedback(user, driver, rating, comment)
