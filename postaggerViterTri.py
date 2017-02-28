#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import utils
import collections
import pos_model


def predict_tags(sentences, model):
    # YOU CODE GOES HERE: use the model to predict tags for sentences
    prior = model[0]
    likelihood = model[1]
    tagset = model[2]
    wordTypes = model[3]

    for sentence in sentences:
        viterbi_value = [[[0.0 for j in range(len(tagset))] for a in range(len(tagset))] for i in range(len(sentence))]
        viterbi_loc = [[[0 for z in range(2)] for j in range(len(tagset))] for i in range(len(sentence))]
        for word_index in range(0, len(sentence)):
            for tag_index in range(0, len(tagset)):
                present_tag = tagset[tag_index]
                present_word = sentence[word_index].word
                if present_word not in wordTypes:
                    likelihood[present_word][present_tag] = 0.0000000001
                if word_index == 0:
                    viterbi_value[word_index][tag_index] = (likelihood[present_tag][present_word]) * (
                        prior["<s>"]["<s>"][present_tag])
                    viterbi_loc[word_index][tag_index] = [0, 0]
                else:
                    viterbi_value[word_index][tag_index] = 0
                    for index_before in range(0, len(tagset)):
                        current_viterbi_value = (viterbi_value[word_index - 1][index_before]) * (
                            likelihood[present_tag][present_word]) * (
                                                    prior[tagset[index_before]][tagset[tag_index]][present_tag])
                        if current_viterbi_value > viterbi_value[word_index][tag_index]:
                            viterbi_value[word_index][tag_index] = current_viterbi_value
                            prior_word_index = word_index - 1
                            prior_tag_index = index_before
                            viterbi_loc[word_index][tag_index] = [prior_word_index, prior_tag_index]
        mostlikely = 0
        # back tracking
        for last_tagindex in range(0, len(tagset)):
            if viterbi_value[len(sentence) - 1][last_tagindex] > mostlikely:
                mostlikely = viterbi_value[len(sentence) - 1][last_tagindex]
                last_tag = tagset[last_tagindex]
                temp = viterbi_loc[len(sentence) - 1][last_tagindex]
                sentence[len(sentence) - 1].tag = last_tag
                for token_index in range(len(sentence) - 2, -1, -1):
                    sentence[token_index].tag = tagset[temp[1]]
                    temp = viterbi_loc[temp[0]][temp[1]]
    return sentences


if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
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
        training_file = args[0]
        training_sents = utils.read_tokens(training_file)
        test_file = args[1]
        test_sents = utils.read_tokens(test_file)
    # create_model(training_sents)

    model = pos_model.create_model(training_sents)

    # read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    # read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in test [%s sentences]: %s" % (len(sents), accuracy)
