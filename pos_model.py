from optparse import OptionParser
import os, logging
import utils
import collections


def create_model(sentences):
    uniTagCount = collections.defaultdict(int)  # verb :10
    biTagCount = collections.defaultdict(lambda: collections.defaultdict(int))  # noun:verb:10, p(t1/t2)
    triTagCount = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
    wordTagCount = collections.defaultdict(lambda: collections.defaultdict(int))  # himanish:noun:10 himanish:prep:5
    wordTagProb = collections.defaultdict(lambda: collections.defaultdict(int))  # likehood prob(word/tag)
    wordTypes = []  # all unique words
    tagset = []
    model = [triTagCount, wordTagProb, tagset, wordTypes]
    for sentence in sentences:
        sentence = [utils.Token('<s>', '<s>')] + sentence + [utils.Token('</s>', '</s>')]
        uniTagCount["<s>"] += 1
        biTagCount["<s>"][sentence[0].tag] += 1
        triTagCount["<s>"]["<s>"][sentence[0].tag] += 1
        for token in sentence:
            wordTagCount[token.word][token.tag] += 1  # bigram count
            if token.tag not in tagset:
                tagset.append(token.tag)
                uniTagCount[token.tag] += 1
            if token.word not in wordTypes:
                wordTypes.append(token.word)
                # identifying the unique tags available in the training set
        for index in range(0, len(sentence) - 1):
            biTagCount[sentence[index].tag][sentence[index + 1].tag] += 1
        for index in range(0, len(sentence) - 2):
            triTagCount[sentence[index].tag][sentence[index + 1].tag][sentence[index + 2].tag] += 1
    tempTagset = ["<s><s>"] + tagset  # dummy tagset for initial tag given tag

    # first matrix with tag X tag values
    for tag1 in tempTagset:
        for tag2 in tagset:
            for tag3 in tagset:
                triTagCount[tag1][tag2][tag3] = float(
                    (triTagCount[tag1][tag2][tag3] + 1.0) / (biTagCount[tag1][tag2] + len(tagset)))
                # print(tag1,tag2,pos_seqcount[tag1][tag2])

    # second matrix with word X tag values
    for tag in tagset:
        for word in wordTypes:
            wordTagProb[tag][word] = float((wordTagCount[word][tag] + 0.0) / uniTagCount[tag])
    # print model
    return model