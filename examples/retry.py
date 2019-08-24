import plsnocrash

fail_counter = 0

@plsnocrash.retry(5)
def get_data():
    global fail_counter
    if fail_counter < 3:
        fail_counter += 1
        raise ValueError("Something went wrong")
    return "some data"


if __name__ == '__main__':
    print(get_data())
