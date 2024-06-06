
import random
import time

class User:
    def __init__(self, name, pickup_location, destination):
        self.name = name
        self.pickup_location = pickup_location
        self.destination = destination

    @staticmethod
    def register_user():
        name = input("Enter your name: ")
        pickup_location = input("Enter pickup location: ")
        destination = input("Enter destination: ")
        return User(name, pickup_location, destination)

    def request_ride(self):
        print(f"{self.name} requests a ride from {self.pickup_location} to {self.destination}")
        return Ride(self)

class Driver:
    def __init__(self, name, current_location):
        self.name = name
        self.current_location = current_location

    @staticmethod
    def register_driver():
        name = input("Enter driver's name: ")
        current_location = input("Enter driver's current location: ")
        return Driver(name, current_location)
    
    def accept_ride(self, ride):
        print(f"{self.name} accepts the ride request from {ride.user.name}")
        return ride

class Ride:
    def __init__(self, user):
        self.user = user

    def accept_ride(self, driver):
        print(f"{driver.name} accepts the ride request from {self.user.name}")
        return self

    def confirm_ride(self, driver):
        print(f"Ride confirmed by {driver.name}")
        return self

    def start_ride(self):
        print(f"Ride started from {self.user.pickup_location}")

    def complete_ride(self):
        print(f"Ride completed at {self.user.destination}")

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
    user = User.register_user()
    # Driver registration
    driver = Driver.register_driver()

    # User requests a ride
    ride = user.request_ride()

    # Driver accepts the ride
    ride = driver.accept_ride(ride)

    # Ride confirmation
    ride.confirm_ride(driver)

    # Start ride
    ride.start_ride()

    # Complete ride
    ride.complete_ride()

    # Simulate payment
    fare = 10.0  # Example fare
    Payment.process_payment(user, fare)

    # Simulate feedback
    rating = 5  # Example rating
    comment = "Great ride, very polite driver!"
    Feedback.give_feedback(user, driver, rating, comment)
