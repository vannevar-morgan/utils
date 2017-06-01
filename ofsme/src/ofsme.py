#! /usr/bin/env python3

"""
Obfuscate Me, a tool to obfuscate your text from stylometric analysis and author attribution tools
"""

import sys
import random

def get_text(text, input_filename):
    """
    Import the user text.
    """
    with open(input_filename) as in_file:
        text.extend(in_file)


def get_wordlist(word_dict, wordlist_filename):
    """
    Import the word frequency list.
    It is assumed there are no duplicates.

    Fills word_dict with word frequencies.
    {key->value}
    {word->frequency}
    """
    with open(wordlist_filename) as in_file:
        freq = 1
        for word in in_file:
            word_dict[word.replace('\n', '')] = freq


def get_key_map(key_dict, key_map_filename):
    """
    Import the key neighbors map.
    
    Fills key_dict with nearby keys.
    {key->value}
    {key->list of nearby keys}
    """
    with open(key_map_filename) as in_file:
        for line in in_file:
            print(line)
            [key, nearby] = line.split(" ", 1)
            key_dict[key] = [x for x in nearby.replace('\n', '')]
    

def parse_words(words, text):
    """
    Parse text into words
    """
    temp = []
    for line in text:
        temp_line = line.replace(',', ' ').replace('…', ' ').replace('...', ' ').replace('.', ' ').replace(':', ' ').replace('!', ' ').replace('`', '').replace(';', ' ').replace('?',' ').replace('\n', ' ')
        temp = [w for w in temp_line.split(' ') if w != '']
        words.extend(temp)
    

def get_lowercase(words):
    """
    Return a list of all words in a collection, as lowercase
    """
    temp = []
    for w in words:
        temp.append(w.lower())
    return temp


def apply_key_filter(text, key_filter):
    """
    Mutate text using key_filter.
    
    text is a list of text to mutate.
    key_filter is a dict that maps keys to list of nearby keys
    {key->value}
    {key->list of nearby keys}

    Returns a list of mutated text.
    """
    p_mutate = 3
    m_text = []
    for line in text:
        m_line = ""
        for abc in line:
            next_char = abc
            if random.randint(0,699) < p_mutate:
                if abc in key_filter:
                    nearby_keys = key_filter[abc]
                    random.shuffle(nearby_keys)
                    next_char = nearby_keys[0]
            m_line += next_char
        m_text.append(m_line)
    return m_text
    
    

ENGLISH_FREQUENCY_LIST_FILENAME = "../lookups/google-10000-english.txt"
ENGLISH_FREQUENCY_LIST_USA_FILENAME = "../lookups/google-10000-english-usa.txt"
ENGLISH_FREQUENCY_LIST_20K_FILENAME = "../lookups/20k.txt"
NEIGHBOR_KEY_MAP_FILENAME = "../lookups/neighbor_keys_map.txt"


USAGE_MESSAGE = "./ofsme.py input_file output_file"

if len(sys.argv) != 3:
    print(USAGE_MESSAGE)
    sys.exit(1)

input_filename = sys.argv[1]
output_filename = sys.argv[2]

# import text to analyze and obfuscate
user_text = []
get_text(user_text, input_filename)

# import word frequency list
word_list = {}
get_wordlist(word_list, ENGLISH_FREQUENCY_LIST_20K_FILENAME)

# import neighbor key map
key_map = {}
get_key_map(key_map, NEIGHBOR_KEY_MAP_FILENAME)

# parse words from text
user_words = []
parse_words(user_words, user_text)

# for line in user_text:
#     print(line)

# for word in user_words:
#     print(word)

unique_user_words = set(get_lowercase(user_words))

uncommon_words = {}
for w in unique_user_words:
    if w not in word_list:
        if w not in uncommon_words:
            uncommon_words[w] = 1
        else:
            uncommon_words[w] += 1

print("these words are uncommon:")
for w in uncommon_words:
    print(w + "\t\t" + str(uncommon_words[w]))

# print("length of word_list: " + str(len(word_list)))

# print(unique_user_words)
# print("unique words: " + str(len(unique_user_words)))
# print("uncommon words: " + str(len(uncommon_words)))
# print("")

print("text with key exchange:")
m_text = apply_key_filter(user_text, key_map)
for line in m_text:
    print(line, end="")

# print(user_text)
