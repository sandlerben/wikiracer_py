import argparse

from wikiracer.workers import race


def cli():
    parser = argparse.ArgumentParser(description="Race from one page to another!")
    parser.add_argument("--start", type=str, help="Page to start from")
    parser.add_argument("--end", type=str, help="Page to get to")
    args = parser.parse_args()

    result = race(args.start, args.end)
    print(result)


if __name__ == "__main__":
    cli()
