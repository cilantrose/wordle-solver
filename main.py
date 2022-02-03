from math import log10, ceil


def loadWords(common=True, numbers=False):
    word_list = []
    # get words from preset files
    f = open("words_common.txt", "r") if common else open("words_all.txt", "r")
    for line in f:
        line = line.lower().strip("\n")
        if numbers:
            word_list.append(line)
        elif not any([c.isdigit() for c in line]):
            word_list.append(line)
    print(f'Loaded wordlist of size {len(word_list)}')
    f.close()
    return word_list


def search(word_list, dialogue=False, length=None, letters=None):
    return_set = []
    # add all words matching given filters to the return set
    for word in word_list:
        if (letters is None or any([c in letters for c in word])) and (length is None or len(word) == length):
            return_set.append(word)
    if dialogue:
        print(f'Modified wordlist with parameters length = {length} and letters = {letters}')
    return return_set


def contains(word_list, search_chars, inverse=False, threshold=0):
    if threshold != 0:
        threshold = len(search_chars) - threshold
    return_list = []
    for word in word_list:
        temp = search_chars
        # check if each word contains the search chars, and remove matching letters from search array
        for c in word:
            temp = temp.replace(c, "")
        # depending on whether it should check if it should or should not contain, add to the output array
        if (inverse is True and temp == search_chars) or (inverse is False and len(temp) <= threshold):
            return_list.append(word)
    return return_list


def matchPattern(word_list, search_chars, inverse=False):
    return_list = []
    for word in word_list:
        # check all words against the word position filter, add if each one passes the respective test
        if inverse and not any(search_chars[i] != " " and word[i] == search_chars[i] for i in
                               range(0, min(len(word), len(search_chars)))):
            return_list.append(word)
        elif not inverse and not any(search_chars[i] != " " and word[i] != search_chars[i] for i in
                                     range(0, min(len(word), len(search_chars)))):
            return_list.append(word)
    return return_list


def findDist(word_list, no_rep=False, char_only=True):
    return_dict = {}
    repeats = []
    for word in word_list:
        # initialize repeat tracker if option is enabled
        if no_rep:
            repeats = []
        for c in word:
            # assumes that numbers and punctuation may be included
            if c.isalnum() or not char_only:
                # if the user has specified that it shouldn't count repeats then it skips the next step
                if no_rep is False or c not in repeats:
                    return_dict[c] = return_dict[c] + 1 if c in return_dict else 1
                    if no_rep:
                        repeats.append(c)
    return len(word_list), return_dict


def printDistFancy(dist: tuple[int, dict], percentages=False, ordered=None, limit=0, precision=2):
    i = 0
    if len(dist[1]) != 0:
        print_list = []
        for letter in dist[1]:
            string = f'{letter}: {dist[1][letter]}'
            # append percentages to the end of the string, if flag enabled
            if percentages:
                string = '{:<9} {} {:>7.2f}%'.format(string, '|',
                                                     (dist[1][letter] / dist[0] * 100).__round__(precision))
            # if ordered flag is specified, add to a list to be sorted, otherwise print directly
            if ordered:
                print_list.append((dist[1][letter], string))
            else:
                print(string)
                i += 1
                if i >= limit != 0:
                    return
        if ordered == "freq":
            for line in radixSort(list(print_list), 0):
                print(line[1])
                i += 1
                if i >= limit != 0:
                    return
    else:
        print("No items in this set")


def radixSort(in_list: list[tuple], sort_index, high_low=True):
    # get max number of digits
    max_digits = ceil(log10(max(in_list)[sort_index]))
    for i in range(0, max_digits):
        # messy bucket init because i think it's faster due to presorted buckets
        # don't quote me on that though, maybe the object creation has more overhead in python
        # wtf did pycharm do to my formatting lmao
        buckets = {9: [], 8: [], 7: [], 6: [], 5: [], 4: [], 3: [], 2: [], 1: [], 0: []} if high_low else {0: [], 1: [],
                                                                                                           2: [], 3: [],
                                                                                                           4: [], 5: [],
                                                                                                           6: [], 7: [],
                                                                                                           8: [], 9: []}
        for item in in_list:
            # get rightmost unchecked digit and appends to appropriate bucket
            buckets[item[0] // 10 ** i % 10].append(item)
        # override the previous list
        in_list.clear()
        for bucket in buckets:
            for item in buckets[bucket]:
                in_list.append(item)
    return in_list


def parseCmd(command, word_list):
    cmd_list = command.split(" ", 1)
    if cmd_list[0] == "g":
        if len(cmd_list) != 2:
            print("invalid guess")
            return
        return guess(cmd_list[1], word_list)
    elif cmd_list[0] == "dist":
        opts = []
        no_rep = True
        char_only = True
        if len(cmd_list) > 1:
            opts = cmd_list[1].split(" ")
        if opts.__contains__("r"):
            no_rep = False
        if opts.__contains__("s"):
            char_only = False
        printDistFancy(findDist(word_list, no_rep, char_only), True, "freq")
        return
    elif cmd_list[0] == "print":
        if len(cmd_list) > 1:
            print("invalid cmd")
            return
        print(word_list)
        return
    elif cmd_list[0] == "contains":
        opts = cmd_list[1].split(" ")
        if len(cmd_list) != 2 or len(opts) != 2:
            print("invalid contains - format 'contains [characters] [threshold]'")
            return
        print(contains(word_list, opts[0], False, int(opts[1])))
        return
    elif cmd_list[0] == "pattern_match":
        opts = cmd_list[1].split(" ")
        if len(cmd_list) != 2 or len(opts) != 1:
            print("invalid pattern_match - format 'pattern_match [characters]'")
            return
        printDistFancy(pattern_distribution(word_list, opts[0]), True, "freq", 10)
        return


def guess(g, word_list):
    pattern = ""
    should_not_contain = ""
    not_pattern = ""
    should_contain = ""
    i = 0
    while i < len(g):
        if g[i] == "*":
            pattern += g[i + 1]
            not_pattern += " "
            i += 2
        elif g[i] == "^":
            not_pattern += g[i + 1]
            should_contain += g[i + 1]
            pattern += " "
            i += 2
        else:
            should_not_contain += g[i]
            not_pattern += " "
            pattern += " "
            i += 1
    return matchPattern(matchPattern(contains(contains(word_list, should_not_contain, True), should_contain), not_pattern, True), pattern)


def pattern_distribution(word_list, letters):
    vowel_patterns = {}
    for word in word_list:
        temp = ""
        for c in word:
            temp += c if c in letters else "-"
        vowel_patterns[temp] = vowel_patterns[temp] + 1 if temp in vowel_patterns else 1
    return len(word_list), vowel_patterns


def main():
    word_list = loadWords()
    word_list = search(word_list, False, 5)
    filtered = word_list
    shouldRun = True
    threshold = 10

    while shouldRun:
        cmd = input("> ")
        temp = parseCmd(cmd, filtered)
        if type(temp) == list and temp is not None:
            if len(temp) == 1:
                print(f'your word is {temp[0]}')
                return
            filtered = temp
            if len(filtered) <= threshold:
                print(filtered)
            else:
                print(f'options filtered to list of size {len(filtered)}')


main()
