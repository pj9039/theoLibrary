import copy
import random
import collections
import os
import json


class DictList:
    """
    DictList is a simple data structure.
    DictList stores a list what is consist of dictionaries.

    If a key is set, quick sorting and binary searching is provided.
    The functionality gives us good performance for getting data.
    A variety importing and exporting methods is supported. JSON, CSV, MONGODB
    And to refine a data, walker feature is supported.

    Methods:
        dictlist = DictList(key=None)
        print()

        length = count()
        datum = get_datum(value)
        datum = get_datum(filters)
        datum = get_datum(key, value)
        data = get_data(filters=None)
        values = get_values(key, overlap=False, filters=None)

        append(datum)
        insert(datum)
        extend(dictlist)
        extend_data(data)

        remove_datum(datum)
        datum = pop_datum(datum)
        clear()

        import_json(file)
        export_json(file)
        TODO: import_csv(file)
        TODO: export_csv(file)
        TODO: import_mongodb(database, collection)
        TODO: export_mongodb(database, collection)

        TODO: walker_handler = plug_in_walker(walker, walker_delay=False, insert=False)
        TODO: plug_out_walker(walker_handler)

    Development guide:
        External function should validate parameters before calling an internal function.
    """

    def __init__(self, key=None):
        if key is not None and not isinstance(key, str):
            raise AssertionError('key(type:{}) should be str.'.format(type(key)))

        self.data = list()

        self.key = key
        self.sorted = True

        self.walkers = list()

    def print(self):
        self.sort_data()

        print('DictList(num:{}/key:{}) walkers({})'.format(len(self.data), self.key, self.walkers))
        if len(self.data) <= 6:
            for index, datum in enumerate(self.data):
                print('{} {}'.format(index, datum))
        else:
            for index in [0, 1, 2]:
                print('{} {}'.format(index, self.data[index]))
            print('...')
            for index in [-3, -2, -1]:
                print('{} {}'.format(len(self.data) + index, self.data[index]))

    def count(self):
        return len(self.data)

    def get_datum(self, attr1, attr2=None):
        # get_datum(filters)
        if attr2 is None and isinstance(attr1, list):
            self.validation_filters(attr1)

            filters = attr1
            for datum in self.data:
                for filter in filters:
                    if not (filter['key'] in datum.keys() and datum[filter['key']] == filter['value']):
                        break
                else:
                    return copy.copy(datum)

            return None

        # get_datum(value)
        elif attr2 is None:
            if self.key is None:
                raise AssertionError('get_datum(value) needs key in DictList.')

            value = attr1
            return copy.copy(self.binary_search_datum(value))

        # get_datum(key, value)
        else:
            if not isinstance(attr1, str):
                raise AssertionError('key(type:{}) should be str.'.format(type(attr1)))

            key = attr1
            value = attr2

            if self.key is not None and self.key == key:
                return copy.copy(self.binary_search_datum(value))
            else:
                for datum in self.data:
                    if key in datum.keys() and datum[key] == value:
                        return copy.copy(datum)

                return None

    def get_data(self, filters=None):
        self.validation_filters(filters)

        if filters is None:
            return copy.copy(self.data)

        else:
            data = list()
            for datum in self.data:
                for filter in filters:
                    if not (filter['key'] in datum.keys()
                            and datum[filter['key']] == filter['value']):
                        break
                else:
                    data.append(datum)

            return data

    def get_values(self, key, overlap=False, filters=None):
        self.validation_filters(filters)

        if filters is None:
            filters = list()

        values = list()
        for datum in self.data:
            if key not in datum.keys():
                continue

            for filter in filters:
                if not (filter['key'] in datum.keys() and datum[filter['key']] == filter['value']):
                    break
            else:
                values.append(datum[key])

        if overlap:
            return values
        else:
            return list(collections.OrderedDict.fromkeys(values))

    def append(self, datum):
        self.validation_datum(datum)

        self.data.append(datum)
        self.sorted = False

    def insert(self, datum):
        self.validation_datum(datum)

        self.data.insert(0, datum)
        self.sorted = False

    def extend(self, dictlist):
        self.validation_dictlist(dictlist)

        if len(dictlist.count()):
            self.data.extend(dictlist.get_data())
            self.sorted = False

    def extend_data(self, data):
        self.validation_data(data)

        if len(data):
            self.data.extend(data)
            self.sorted = False

    def pop_datum(self, datum):
        if datum in self.data:
            self.data.remove(datum)
            return datum

        return None

    def remove_datum(self, datum):
        if datum in self.data:
            self.data.remove(datum)

    def clear(self):
        self.data.clear()
        self.sorted = True

    def import_json(self, file):
        self.validation_file(file)

        if os.path.exists(file):
            file_handler = open(file, 'r')
            self.extend_data(json.load(file_handler))
            file_handler.close()

    def export_json(self, file):
        self.validation_file(file)
        self.sort_data()

        if not os.path.exists(os.path.dirname(os.path.abspath(file))):
            os.makedirs(os.path.dirname(os.path.abspath(file)))

        file_handler = open(file, 'w')
        json.dump(self.data, file_handler, ensure_ascii=False, indent="\t")
        file_handler.close()

    """
    Internal sorting, searching functions

    When the getting functionality such as get_datum, get_data is called, the data is sorted.

    Methods:
        sort_data
        sort_data > is_data_ascending_order
        sort_data > is_data_descending_order
        sort_data > reverse_data_order
        sort_data > recursive_quick_sort

        binary_search

    NOTE: Why the reverse function is worked?
            Theo usually use the DictList to store stock price data.
            From stock server, the price data is reversed.
            To sort reversed data, the sorting algorithm works as the worst performance.
            That is why the reverse function is exist.

    NOTE: The sorting method is the recursive quick sorting.
            If sorting works over limitation time recursively, exception happens.
            RecursionError: maximum recursion depth exceeded in comparison
            Iterative quick sorting could be needed.
            But, the recursive quick sorting's performance is better than the other.
    """
    def sort_data(self):
        if self.key is not None and not self.sorted:
            if self.is_data_ascending_order(self.data, self.key):
                self.sorted = True
            elif len(self.walkers):
                raise AssertionError('The data cannot be sorted. Walkers are working.')
            elif self.is_data_descending_order(self.data, self.key):
                self.reverse_data_order(self.data)
                self.sorted = True
            else:
                self.recursive_quick_sort_data(self.data, self.key)
                self.sorted = True

    @staticmethod
    def is_data_ascending_order(data, key):
        if len(data) < 2:
            return True

        for index in range(1, len(data)):
            if data[index - 1][key] > data[index][key]:
                return False

        return True

    @staticmethod
    def is_data_descending_order(data, key):
        if len(data) < 2:
            return True

        for index in range(2, len(data)):
            if data[index - 1][key] < data[index][key]:
                return False

        return True

    @staticmethod
    def reverse_data_order(data):
        source_data = copy.copy(data)
        data.clear()
        for datum in reversed(source_data):
            data.append(datum)

    @staticmethod
    def recursive_quick_sort_data(data, key):
        if len(data) > 1:
            pivot = data[random.randint(0, len(data) - 1)]
            left_list, middle_list, right_list = list(), list(), list()

            for index in range(len(data)):
                if data[index][key] < pivot[key]:
                    left_list.append(data[index])
                elif data[index][key] > pivot[key]:
                    right_list.append(data[index])
                else:
                    middle_list.append(data[index])

            return DictList.recursive_quick_sort_data(left_list, key) \
                + middle_list \
                + DictList.recursive_quick_sort_data(right_list, key)
        else:
            return data

    def binary_search_datum(self, value):
        self.sort_data()

        start_index = 0
        last_index = self.count() - 1

        while start_index <= last_index:
            index = (start_index + last_index) // 2

            if self.data[index][self.key] > value:
                last_index = index - 1
            elif self.data[index][self.key] < value:
                start_index = index + 1
            else:
                return self.data[index]

        return None

    """
    Internal validation functions

    Methods:
        validation_datum
        validation_data
        validation_dictlist
        validation_filters
    """
    def validation_datum(self, datum):
        if not isinstance(datum, dict):
            raise AssertionError('datum(type:{}) should be dict.'.format(type(datum)))

        if self.key is not None and self.key not in datum.keys():
            raise AssertionError('datum(keys:{}) does not have the key({}).'.format(list(datum.keys()), self.key))

    def validation_data(self, data):
        if not isinstance(data, list):
            raise AssertionError('data(type:{}) should be list.'.format(type(data)))

        if self.key is not None:
            for datum in data:
                if self.key not in datum.keys():
                    raise AssertionError(
                        'datum(keys:{}) does not have the key({}).'.format(list(datum.keys()), self.key))

    def validation_dictlist(self, dictlist):
        if not isinstance(dict, DictList):
            raise AssertionError('dictlist(type:{}) should be DictList.'.format(type(dictlist)))

        self.validation_data(dictlist.get_data())

    @staticmethod
    def validation_filters(filters):
        if filters is not None:
            if not isinstance(filters, list):
                raise AssertionError('filters(type:{}) should be list.'.format(type(filters)))

            for filter in filters:
                if not isinstance(filter, dict):
                    raise AssertionError('filter(type:{}) should be dict.'.format(type(filter)))

                if not ('key' in filter.keys() and 'value' in filter.keys()):
                    raise AssertionError('filter(keys:{}) does not have key or value.'.format(list(filter.keys())))

    @staticmethod
    def validation_file(file):
        if not isinstance(file, str):
            raise AssertionError('file(type:{}) should be str.'.format(type(file)))
