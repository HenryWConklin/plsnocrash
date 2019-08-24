import plsnocrash

import time
import pickle

def train():
    time.sleep(10)
    return [1,2,3,4,5]

@plsnocrash.let_me_try
def save(x):
    # Oops, that should be a file object, not a string
    pickle.dump(x, 'test.pkl')

if __name__ == '__main__':
    x = train()
    save(x)
    print("All done!")
