#!/usr/bin/env python3

import argparse
import json
import random
from base64 import b16encode
from os import urandom, path


def random_password():
    password = ""
    characters = "abcdefghijklmnopqrstuvxyz0123456789~/|#$%&()"
    for index in range(12):
        password = password + random.choice(characters)
    return password


parser = argparse.ArgumentParser(
    prog='pyorm',
    description='A simple python orm',
)

parser.add_argument("-i", "--init", metavar="INIT", help="Initialize Salt and Password for Encrypted Database")
parser.add_argument("-d", "--decrypt", metavar="FILEPATH", help="Decrypt SQLite Database")


def cli():
    args = vars(parser.parse_args())
    if args["init"]:
        with open(".pyorm", "w") as f:
            f.write(json.dumps({
                "SALT": b16encode(urandom(16)).decode("utf-8"),
                "PASSWORD": b16encode(bytes(random_password(), "utf-8")).decode("utf-8")
            }))

    elif args['decrypt']:
        if path.exists(path.abspath(args['decrypt'])):
            from .adapter import decrypt_cdb, load_config

            cnf = load_config(".pyorm")
            decrypt_cdb(path.abspath(args['decrypt']), cnf["PASSWORD"], cnf["SALT"])


if __name__ == "__main__":
    cli()
