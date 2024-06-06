def example_func(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")


# Simulation
if __name__ == "__main__":

    example_func(a=1, b=2, c=3)