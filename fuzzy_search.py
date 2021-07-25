import itertools
import json
import time

from change_keyboard_layout import reverse


class Node:
    """Узел дерева. """

    def __init__(self, key, value, full: list, type_="literal"):
        self.key = key
        self.full = full
        self.value = value
        self.children = {}
        self.type_ = type_

    def add_child(self, key, value, full, type_="literal"):
        """Добавление в дерево дочернего узла. """
        if not self.children.get(key):
            self.children[key] = [Node(key=key, value=value, full=full, type_=type_)]
        else:
            self.children[key].append(Node(key=key, value=value, full=full, type_=type_))

    # def __repr__(self):
    #     return "***" + str(self.key) + " " + self.type_ + \
    #            " " + str(self.full) + "***"


class Trie:
    """Дерево."""

    def __init__(self):
        self.root = Node(key=None, value=None, full=[])

    def add_node(self, key, value):
        """Добавление узла. """
        self._add_node(self.root, key, value, 0)

    def _add_node(self, root, key, value, idx):
        if key[idx] not in root.children:
            root.add_child(key[idx].lower(), value, [key])

        root = root.children[key.lower()[idx]][0]
        if key not in root.full:
            root.full.append(key)

        if idx == len(key) - 1:
            root.add_child(key.lower(), value, [key], "word")
            return

        idx += 1
        self._add_node(root, key, value, idx)

    def _search(self, root, key, idx):
        """ Основная функция четкого поиска. """
        if len(key) == idx:  # if root.children.get(key)
            try:
                return [root.children.get(key.lower())[0].full[0]]  # возвращаем полное слово
            except TypeError:
                return None
        try:
            root = root.children[key[idx].lower()][0]
        except (IndexError, KeyError, AttributeError):
            return None

        idx += 1
        return self._search(root, key, idx)

    def search(self, key):
        """ Вызов основной функции четкого поиска. """
        return self._search(self.root, key, 0)

    def _fuzzy_search(self, root, key, idx, typo_count=0):
        """Основная функция нечеткого поиска. """

        # region выход из рекурсии
        if typo_count > 1:
            return [None]

        if root.children.get(key.lower()):
            return [*root.children.get(key.lower())[0].full]

        if len(key) == idx:
            return [*root.full]
        # endregion

        res = []

        # region нечеткий поиск
        # лишняя буква
        k1 = key.lower()[:idx] + key.lower()[idx + 1:]
        res.extend(self._fuzzy_search(root, k1, idx, typo_count + 1))

        for key_, value in root.children.items():
            if key_ == key.lower()[idx]:
                r1 = root.children[key_][0]
                res.extend(self._fuzzy_search(r1, key, idx + 1, typo_count))
            else:
                # замена буквы
                r1 = root.children[key_][0]
                k1 = key[:idx] + key_ + key[idx + 1:]
                res.extend(self._fuzzy_search(r1, k1, idx + 1, typo_count + 1))

                # отсутствие буквы
                k1 = key[:idx] + key_ + key[idx:]
                res.extend(self._fuzzy_search(r1, k1, idx + 1, typo_count + 1))
        # endregion

        return res

    def fuzzy_search(self, key):
        """ Вызов основной фнукции нечеткого поиска и подготовка результата. """
        s = set(self._fuzzy_search(self.root, key, 0))
        try:
            s.remove(None)
        except KeyError:
            pass
        return list(s)


def try_fuzzy_search():
    """ Пробный поиск. """
    t = Trie()
    with open('./dictionary.txt') as f:
        words = f.readlines()
    for word in words:
        word = word.split('\n')[0]
        t.add_node(word, 1)

    start_time = time.time()
    res = t.fuzzy_search("каг")
    print(json.dumps(list(itertools.islice(res, 10))))
    print("--- %s seconds ---" % (time.time() - start_time))

    word = reverse("pth")
    res = t.fuzzy_search(word)
    print(json.dumps(list(itertools.islice(res, 10))))
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    try_fuzzy_search()
