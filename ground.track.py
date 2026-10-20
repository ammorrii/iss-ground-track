def load_tle(path):
    with open(path) as text:
        tle = text.read().splitlines()[1:]
        return tle

if __name__ == "__main__":
    line1, line2 = load_tle('iss.txt')