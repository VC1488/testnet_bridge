import random

def load_proxies():
    with open('data/proxies.txt', 'r') as file:
        proxies = file.readlines()
    return [proxy.strip() for proxy in proxies]

proxies = load_proxies()

def get_random_proxy():
    return random.choice(proxies)