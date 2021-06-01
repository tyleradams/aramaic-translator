#!/usr/bin/env python3

import click
import json
import sys
import textdistance

import flask
import flask_cors

app = flask.Flask(__name__)
flask_cors.CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "http://localhost:5000",
])


FINALIZEABLE_LETTERS = {
    "כ": "ך",
    "פ": "ף",
    "נ": "ן",
    "מ": "ם",
    "צ": "ץ",
}
FINALIZED_LETTERS = { v: k for k,v in FINALIZEABLE_LETTERS.items() }

PASSIVE_SWAP_LETTERS = {
    "ז": "ד",
    "צ": "ט",
}

DAGESHABLE_LETTERS = "שבגדוזטיךכלמנםףפצקרת"

DEBUG = False

DATA = []
with open('data.json') as d:
    DATA = json.load(d)

def finalize_word(word):
    if word[-1] in FINALIZEABLE_LETTERS:
        return word[:-1] + FINALIZEABLE_LETTERS[word[-1]]
    else:
        return word

def render_hebrew(s):
        return finalize_word(s)[::-1]

def weak_match_words(first, second):
    def stripped(word):
        # These letters are sometimes dropped,
        return word.replace("י", "").replace("ו", "").replace("ן", "")
    return stripped(first) == stripped(second)

# Returns if substring is a noncontiguous substring of string
def is_non_contiguous_substring(string, substring):
    # https://stackoverflow.com/questions/29954748/finding-subsequence-nonconsecutive
    return all(c in iter(string) for c in substring)

def apply_modification(word, modification):
    if modification["type"] == "add":
        l = modification["location"]
        # i >=0 means Insert to the left of the ith character
        if l >= 0:
            return word[0:l] + modification["string"] + word[l:]
        # -i means insert to the right of the -ith character.
        elif l == -1:
            return word + modification["string"]
        else:
            return word[0:l+1] + modification["string"] + word[l+1:]
    elif modification["type"] == "dagesh-reduce":
        l = modification["location"]
        if word[l + 1] in PASSIVE_SWAP_LETTERS:
            return word[0:l] + word[l+1] + PASSIVE_SWAP_LETTERS[word[l + 1]] + word[l+2:]
        elif word[l + 1] in DAGESHABLE_LETTERS:
            return word[0:l] + word[l+1:]
        else:
            return word
    elif modification["type"] == "noun-construct":
        if word[-1] == "ה":
            return word[:-1] + "ת"
        elif word[-2:] == "ימ":
            return word[:-2] + "י"
        else:
            return word
    else:
        raise Exception("Modification type {} not implemented".format(modification["type"]))

def word_rank(input_word):
    def noun_states_rank(noun_states):
        noun_states_rank = [
                "absolute",
                "construct",
                "emphatic"
        ]
        if len(noun_states) == 0:
            return len(noun_states_rank)
        elif len(conjugations) == 1:
            return noun_states_rank.index(noun_states[0]["noun-state"]),
        else:
            return len(noun_states_rank)

    def conjugations_rank(conjugations):
        tense_ranks = [
            "Past",
            "Future",
            "Imperative",
            "Active-Participle",
            "Passive-Participle",
            "Mis-Participle",
        ]
        binyan_ranks = [
            "Simple",
            "Causative",
            "Intensive",
            "Passive",
            "Intensive-Passive",
            "Causative-Passive",
        ]
        if len(conjugations) == 0:
            return [
                -1,
                -1
            ]
        elif len(conjugations) == 1:
            return [
                binyan_ranks.index(conjugations[0]["conjugation"]["binyan"]),
                tense_ranks.index(conjugations[0]["conjugation"]["tense"]),
            ]
        else:
            return [
                len(tense_ranks), len(binyan_ranks)
            ]

    def prefixes_rank(prefixes):
        if len(prefixes) == 0:
            return 0
        elif len(prefixes) == 1 and prefixes[0]["prefix"] == "None":
            return 1
        elif len(prefixes) == 1 and prefixes[0]["modifications"] == []:
            return 3
        else:
            return 2

    def suffixes_rank(suffixes):
        if len(suffixes) == 0:
            return 0
        elif len(suffixes) == 1 and suffixes[0]["suffix"]["type"] == "None":
            return 1
        elif len(suffixes) == 1 and suffixes[0]["modifications"] == []:
            return 3
        else:
            return 2

    def inner_word_rank(word):
        conjugations = [r for r in word.rules if r["type"] == "conjugation"]
        noun_states = [r for r in word.rules if r["type"] == "noun_state"]
        prefixes = [r for r in word.rules if r["type"] == "prefix"]
        suffixes = [r for r in word.rules if r["type"] == "suffix"]
        return [
            prefixes_rank(prefixes),
            suffixes_rank(suffixes),
            noun_states_rank(noun_states),
            conjugations_rank(conjugations),
            textdistance.levenshtein.distance(input_word, word.word())
    ]
    return inner_word_rank

class Word:
    def __init__(self, root, rules = []):
        self.root = root
        self.rules = rules

    def apply_rule(self, rule):
        return Word(self.root, self.rules + [rule])

    def word(self):
        w = self.root["root"]
        for rule in self.rules:
            for modification in rule["modifications"]:
                if "gender" not in modification or self.gender() == modification["gender"]:
                    w = apply_modification(w, modification)
        return w

    # Render is RL
    def render(self):
        s = self.word()[::-1] + "\n"
        s += "root: {}, meaning: {}\n".format(self.root["root"][::-1], self.root["meaning"])
        for rule in self.rules:
            s += "{}: {}\n".format(rule["type"], rule[rule["type"]])
        return s

    def as_dict(self):
        return {
            "root": self.root,
            "rules": self.rules,
            "word": self.word()
        }

    def as_grammar(self, input_word):
        d = {}
        d["language"] = self.root["language"]
        d["root"] = self.root["root"]
        d["meaning"] = self.root["meaning"]
        d["rank"] = word_rank(input_word)(self)
        d["word"] = self.word()
        for r in self.rules:
            d[r["type"]] = r[r["type"]]
        return d

    def gender(self):
        for rule in self.rules:
            # Example: adjective-gender, noun-gender
            if "gender" in rule["type"]:
                return rule[rule["type"]]
        return None

    def valid(self):
        return True

def flatten(ll):
    a = []
    for l in ll:
        a.extend(l)
    return a

def generate_roots(root):
    if root["weak-letters"] == []:
        return [root]
    unchanged_root = dict(root)
    weakened_root = dict(root)

    unchanged_root["weak-letters"] = root["weak-letters"][1:]

    w = root["weak-letters"][0]
    weakened_root["root"] = root["root"][:w] + root["root"][w+1:]
    weakened_root["weak-letters"] = [l - 1 for l in root["weak-letters"][1:]]
    return generate_roots(unchanged_root) + generate_roots(weakened_root)

def add_rules(words, rules, input_word):
    augmented_words = flatten([[Word(word.root, word.rules + [rule]) for rule in rules] for word in words])

    if DEBUG:
        print("DEBUG:AUGMENTED_WORDS:{}".format(len(augmented_words)), flush=True)

    if input_word:
        augmented_words = [word for word in augmented_words if is_non_contiguous_substring(input_word, word.word())]
        if DEBUG:
            print("DEBUG:PRUNED:AUGMENTED_WORDS:{}".format(len(augmented_words)), flush=True)
    return augmented_words

def generate_verbs(data, input_word):
    words = []
    raw_roots = [i for i in data if i["type"] == "root"]
    roots = flatten([generate_roots(root) for root in raw_roots])

    conjugations = [i for i in data if i["type"] == "conjugation"]
    prefixes = [i for i in data if i["type"] == "prefix"]
    suffixes = [i for i in data if i["type"] == "suffix"]

    if DEBUG:
        print("DEBUG:ROOTS:{}".format(len(roots)))
        print("DEBUG:CONJUGATIONS:{}".format(len(conjugations)))
        print("DEBUG:PREFIXES:{}".format(len(prefixes)))
        print("DEBUG:SUFFIXES:{}".format(len(suffixes)))

    if input_word:
        prefixes = [prefix for prefix in prefixes if prefix["modifications"] == [] or prefix["modifications"][0]["string"][0] == input_word[0]]
        if DEBUG:
            print("DEBUG:PRUNED:PREFIXES:{}".format(len(prefixes)))

    # It's generally bad form to reuse variables, but naming these is even harder.
    words = [Word(root, []) for root in roots]
    if DEBUG:
        print("DEBUG:WORDS:ROOTS:{}".format(len(words)))
    if input_word:
        words = [word for word in words if is_non_contiguous_substring(input_word, word.word())]
        if DEBUG:
            print("DEBUG:PRUNED:WORDS:ROOTS:{}".format(len(words)), flush=True)

    words = add_rules(words, conjugations, input_word)
    words = add_rules(words, prefixes, input_word)
    words = add_rules(words, suffixes, input_word)

    return words

def generate_nouns(data, input_word):
    nouns = [i for i in data if i["type"] == "noun"]


    words = []
    # HACK get noun data into word data.
    for noun in nouns:
        words.append(Word({
            "type": "root",
            "root-type": "noun",
            "root": noun["noun"],
            "meaning": noun["meaning"],
            "language": noun["language"],
        }, [{
            "noun-gender": noun["gender"],
            "type": "noun-gender",
            "modifications": [],
        }]))


    if DEBUG:
        print("DEBUG:WORDS:NOUNS:{}".format(len(words)))

    if input_word:
        words = [word for word in words if is_non_contiguous_substring(input_word, word.word())]
        if DEBUG:
            print("DEBUG:PRUNED:WORDS:NOUNS:{}".format(len(words)))

    noun_states = [i for i in data if i["type"] == "noun-state"]
    words = add_rules(words, noun_states, input_word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NOUNS:STATES:{}".format(len(words)))

    words = add_rules(words, [i for i in data if i["type"] == "noun-quantity"], input_word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NOUNS:QUANTITIES:{}".format(len(words)))

    construct_words = []
    for word in words:
        for rule in word.rules:
            for modification in rule["modifications"]:
                if modification["type"] == "noun-construct":
                     construct_words.append(word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NOUNS:CONSTRUCTS:{}".format(len(construct_words)))

    possessive_pronouns = [i for i in data if i["type"] == "suffix" and i["suffix"]["type"] == "Possessive-Pronoun"]
    words += add_rules(construct_words, possessive_pronouns, input_word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NOUNS:WITH_CONSTRUCTS:{}".format(len(words)))

    prefixes = [i for i in data if i["type"] == "prefix"]
    if input_word:
        prefixes = [prefix for prefix in prefixes if prefix["modifications"] == [] or prefix["modifications"][0]["string"][0] == input_word[0]]
        if DEBUG:
            print("DEBUG:PRUNED:PREFIXES:{}".format(len(prefixes)))

    words = add_rules(words, prefixes, input_word)

    return words

def generate_adjectives(data, input_word):
    adjectives = [i for i in data if i["type"] == "adjective"]
    adjective_genders = [i for i in data if i["type"] == "adjective-gender"]
    adjective_states = [i for i in data if i["type"] == "adjective-state"]
    adjective_quantities = [i for i in data if i["type"] == "noun-quantity"]

    words = []
    # HACK get adjective data into word data.
    for adjective in adjectives:
        words.append(Word({
            "type": "root",
            "root-type": "adjective",
            "root": adjective["adjective"],
            "meaning": adjective["meaning"],
            "language": adjective["language"],
        },[]))

    words = add_rules(words, adjective_genders, input_word)
    words = add_rules(words, adjective_states, input_word)
    words = add_rules(words, adjective_quantities, input_word)
    return words

def generate_misc(data, input_word):
    miscs = [i for i in data if i["type"] == "misc"]
    words = []
    # HACK get misc data into word data.
    for misc in miscs:
        words.append(Word({
            "type": "root",
            "root-type": "misc",
            "root": misc["misc"],
            "meaning": misc["meaning"],
            "language": misc["language"],
        }))
        if DEBUG:
            print("DEBUG:TMP:MISC:{}:{}".format(misc, words[-1].as_grammar(input_word)))
    if DEBUG:
        print("DEBUG:PRUNED:WORDS:MISC:{}".format(len(words)))
        print("DEBUG:PRUNED:WORDS:MISC:{}".format(json.dumps([w.as_grammar(input_word) for w in words])))
    prefixes = [i for i in data if i["type"] == "prefix"]
    if input_word:
        prefixes = [prefix for prefix in prefixes if prefix["modifications"] == [] or prefix["modifications"][0]["string"][0] == input_word[0]]
        if DEBUG:
            print("DEBUG:PRUNED:PREFIXES:{}".format(len(prefixes)))

    words = add_rules(words, prefixes, input_word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:MISC:PREFIXED:{}".format(len(words)))

    return words

def generate_names(data, input_word):
    names = [i for i in data if i["type"] == "name"]
    words = []
    # HACK get name data into word data.
    for name in names:
        words.append(Word({
            "type": "root",
            "root-type": "noun",
            "root": name["name"],
            "meaning": name["meaning"],
            "language": name["language"],
        }, [{
            "name-gender": name["gender"],
            "type": "name-gender",
            "modifications": [],
        }]))

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NAME:{}".format(len(words)))

    prefixes = [i for i in data if i["type"] == "prefix"]
    if input_word:
        prefixes = [prefix for prefix in prefixes if prefix["modifications"] == [] or prefix["modifications"][0]["string"][0] == input_word[0]]
        if DEBUG:
            print("DEBUG:PRUNED:PREFIXES:{}".format(len(prefixes)))

    words = add_rules(words, prefixes, input_word)

    if DEBUG:
        print("DEBUG:PRUNED:WORDS:NAME:PREFIXED:{}".format(len(words)))

    return words

def generate_words(data, input_word, weak_match=False):
    aramaic_data = [d for d in data if d["language"] in ["aramaic", "unknown"]]
    hebrew_data = [d for d in data if d["language"] in ["hebrew", "unknown"]]

    words = generate_verbs(aramaic_data, input_word)
    words += generate_nouns(aramaic_data, input_word)
    words += generate_adjectives(aramaic_data, input_word)
    words += generate_misc(aramaic_data, input_word)
    words += generate_names(aramaic_data, input_word)

    words += generate_nouns(hebrew_data, input_word)
    words += generate_misc(hebrew_data, input_word)

    if weak_match:
        words = [w for w in words if weak_match_words(w.word(), input_word)]
    else:
        words = [w for w in words if w.word() == input_word]

    words = sorted(words, key=word_rank(input_word))
    return words

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def translate(path):
    body = flask.request.get_json()
    word = body["word"]
    return json.dumps({
        "word": word,
        "words": [w.as_dict() for w in generate_words(DATA, word, True)],
    })


@click.command()
@click.option("--debug/--no-debug", default=False)
@click.option("--weak-match/--no-weak-match", default=False)
@click.option("--load-jastrow/--no-load-jastrow", "load_jastrow", default=True)
def main(debug, weak_match, load_jastrow):
    global DEBUG
    DEBUG = debug

    input_words = json.load(sys.stdin)

    data = json.load(open("data/data.json"))

    if load_jastrow:
        data += json.load(open("data/jastrow.json"))

    output = []
    for input_word in input_words:
        if DEBUG:
            print("DEBUG:INPUT_WORD:{}".format(input_word))
        output.append({
            "word": input_word,
            "matches": [word.as_grammar(input_word) for word in generate_words(data, input_word, weak_match)]
        })

    print(json.dumps(output))

if __name__ == "__main__":
    main()
