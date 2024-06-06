import random
import time

#Here's a sample Python code that simulates the ride experience, payment calculation, rating and feedback, 
#and driver earnings functionalities:


class Ride:
    def __init__(self, user, driver, distance):
        self.user = user
        self.driver = driver
        self.distance = distance

    def start_ride(self):
        print("Ride started!")
        # Simulate real-time tracking of the driver's location
        for i in range(10):  # Simulate 10 iterations for tracking
            time.sleep(1)  # Simulate real-time tracking interval
            driver_location = random.randint(1, 100)
            print(f"{self.driver.name} is at location {driver_location} out of {self.distance}")

    def calculate_fare(self):
        base_fare = 2.5  # Base fare for the ride
        distance_charge = self.distance * 0.1  # Charge $0.1 for each km
        time_charge = 0.5 * self.distance  # Charge $0.5 for each km traveled
        total_fare = base_fare + distance_charge + time_charge
        return total_fare

class Payment:
    def process_payment(self, user, fare):
        print(f"Processing payment of ${fare} for {user['name']}")  # Access 'name' attribute using dictionary key

class RatingAndFeedback:
    def rate_and_feedback(self, user, driver, rating, feedback):
        print(f"Rating {driver.name}: {rating} stars")
        print(f"Feedback for {driver.name}: {feedback}")

class DriverEarnings:
    def __init__(self):
        self.earnings = 0

    def update_earnings(self, fare, commission_rate):
        commission = fare * commission_rate
        driver_earnings = fare - commission
        self.earnings += driver_earnings
        print(f"Earnings updated: ${driver_earnings}")

class Driver:
    def __init__(self, name):
        self.name = name

# Sample usage
if __name__ == "__main__":
    # Create user and driver objects
    user = {"name": "Alice"}
    driver = Driver(name="Bob")  # Create a Driver object with a name attribute

    # Create a ride with the user and driver objects
    ride = Ride(user, driver, distance=10)  # Distance in km

    # Start the ride
    ride.start_ride()

    # Calculate fare
    fare = ride.calculate_fare()
    print(f"Total fare: ${fare}")

    # Process payment
    payment_processor = Payment()
    payment_processor.process_payment(user, fare)

    # Rate and provide feedback
    rating_feedback = RatingAndFeedback()
    rating_feedback.rate_and_feedback(user, driver, rating=5, feedback="Great ride!")

    # Update driver earnings
    driver_earnings = DriverEarnings()
    commission_rate = 0.2  # Assume 20% commission rate
    driver_earnings.update_earnings(fare, commission_rate)