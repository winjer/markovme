import sys
import codecs
import markovgen

if __name__ == "__main__":
    name = sys.argv[1]
    f = codecs.open(name, encoding="UTF-8")
    m = markovgen.Markov(f)
    print m.sentence()
