#!/usr/bin/env python

from optparse import OptionParser
import os, logging

class Token:
    def __init__(self, word, tag):
        self.word = word
        self.tag = tag

    def __str__(self):
        return "%s/%s" % (self.word, self.tag)

def read_tokens(file):
    f = open(file)
    sentences = []
    for l in f.readlines():
        tokens = l.split()
        sentence = []
        for token in tokens:
            ## split only one time, e.g. pianist|bassoonist\/composer/NN
            try:
                word, tag = token.rsplit('/', 1)
            except:
                ## no tag info (test), assign tag UNK
                word, tag = token, "UNK"
            sentence.append(Token(word, tag))
        sentences.append(sentence)
    return sentences

def calc_accuracy(gold, system):
    assert len(gold) == len(system), "Gold and system don't have the same number of sentence"
    tags_correct = 0
    num_tags = 0
    for sent_i in range(len(gold)):
        assert len(gold[sent_i]) == len(system[sent_i]), "Different number of token in sentence:\n%s" % gold[sent_i]
        for gold_tok, system_tok in zip(gold[sent_i], system[sent_i]):
            if gold_tok.tag == system_tok.tag:
                tags_correct += 1
            num_tags += 1
    return (tags_correct / float(num_tags)) * 100

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD SYSTEM"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    gold = read_tokens(args[0])
    system = read_tokens(args[1])
    accuracy = calc_accuracy(gold, system)
    print "Accuracy: %s" % accuracy
