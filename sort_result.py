def sort_result(result, key):
    """ Сортируем результат для вывода наиболее релевантных подсказок. """
    sorted_result = {}
    for word in result:
        if word.startswith(key):
            sorted_result[word] = 1
        elif key in word:
            sorted_result[word] = 2
        elif word.startswith(key[:-1]):
            sorted_result[word] = 3
        elif word.startswith(key[1:]):
            sorted_result[word] = 4
        elif len(key) - len(set(key).intersection(set(word[:len(key)]))) < 2:
            sorted_result[word] = 5
        elif key[:-1] in word:
            sorted_result[word] = 6
        elif key[1:] in word:
            sorted_result[word] = 7
    for word in result:
        if word not in sorted_result:
            sorted_result[word] = 8

    result = sorted(sorted_result, key=sorted_result.get)

    return result
