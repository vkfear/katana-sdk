import argparse

parser = argparse.ArgumentParser(description='A script that greets a user.')

parser.add_argument('name', type=str, help='The name of the person to greet.')

args = parser.parse_args()

print(f"Hello, {args.name}!")
