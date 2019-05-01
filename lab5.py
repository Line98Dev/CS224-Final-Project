#!/usr/bin/python3

import unittest
import math
from enum import Enum


class OpenAddressHashTable:
    """ A Hash Table implementation. This classroom exercise draws from CLRS3, 11.3. It is certainly not ready for the real world:
        * it accepts only strings as keys
        * its uses unsophisticated hashing schemes (division, multiplication)
        * only the 3 main dictionary operations are implemented (INSERT, SEARCH, DELETE)
        * the size of the table is static

    The goal is to get acquainted with the basic problems that come with hash tables, not to accomplish software engineering feats.

    .. note:: The TODO blocks in the class documentation identify the procedures you need to implement. The dependency graph below should help you understand how the methods work together:

        .. figure:: dependency_graph.png
            :scale: 90%
            :align: center
            :alt: dependency graph

            Dependency graph


        Keep in mind that some methods work independently from each other (`insert` and `delete`, f.i.), but their respective unit tests do not (the tests for `delete` call `insert` first). Assuming that you adopt the test-driven development (TDD) approach that this class advocates, you might find easier to follow the coding sequence below:

        1. string_to_int_
        2. hash_divide_
        3. hash_
        4. insert_
        5. search_
        6. delete_
        7. hash_multiply_
        8. string_to_hash_ (EXTRA-CREDIT: 10 pts)

        The sequence reflects the dependency relationships between functions. For example, no work should occur on function (3), until (1) and (2) pass all tests. Tests for (4) will only pass if functions (1) through (3) are correct, and so on. Since the hash_multiply_ function is a bit harder to debug and is not critical for a basic testing of the dictionary operations, it is better left for the end.

    :ivar _WORD_SIZE: size :math:`w` of a machine word, to be used by the multiplication method. Since Python allows for integers of arbitrary size, it has no bearing on the maximal size of the numerical keys to be hashed, and any reasonable value will do. However, it governs the choice of constant :math:`s=A\cdot 2^w`.
    :ivar _S: constant used by the multiplication method (we choose integer :math:`s` such that :math:`s=A\cdot 2^w \\text{ where } A=(\\sqrt(5)-1)/2=0.6180339887\ldots`).
    :ivar _P: the size of a new table is :math:`2^P` when the multiplication method is the default.
    :ivar size: Size of the table (initial value: :math:`89`): if the multiplication method is used, the size is :math:`2^p`.
    :ivar population: Number of elements in the table (initial value: 0)
    :ivar hash_method: A reference to the hashing method to used on numerical keys (initial value: HashTable.DIVISION)

    """

    class HashingMethod(Enum):
        DIVISION = 0
        MULTIPLICATION = 1

    def __init__(self, method=HashingMethod.DIVISION, wordsize=64, p=7):
        """
        Create a new HashTable object.

        :param method: the hashing method to be used. It can be either HashTable.HashingMethod.DIVISION (the default) or HashTable.HashingMethod.MULTIPLICATION.
        :type method: HashTable.HashingMethod
        :param wordsize: the number of bits used to encode a numerical key (default: 64); useful for the multiplication method implementation
        :type wordsize: int
        :param p: if using the multiplication method, the number of bits allocated to the table size :math:`m=2^p`
        """
        self.population = 0

        # Good practice: choose a prime number when hashing w/ division method
        self.size = 89
        self.hash_method = self.hash_divide

        self._WORD_SIZE = wordsize
        self._P = p
        self._S = int(((math.sqrt(5) - 1) / 2) * 2 ** self._WORD_SIZE)

        if method == self.HashingMethod.MULTIPLICATION:
            self.size = 2 ** (self._P)
            self.hash_method = self.hash_multiply

        self.array = [None] * self.size

    def insert(self, key):
        """
        .. _insert:

        Insert a new key in the table.

        .. todo:: Implement the following steps

            1. Hash the key to its slot, with the hash_ method
            2. If the slot is empty, store a new empty LinkedList_ in it
            3. Create a Node_ object with the given key, and add it to the existing list
            4. Insert the node into the list
            5. Update the population count (instance variable `population`)


        :param key: a string value
        :type key: str
        """
        hash_value = self.hash(key)
        location = self.array[hash_value]
        if location is None:
            list = LinkedList()
            self.array[hash_value] = list
            list.set(Node(key))
            self.population += 1
        else:
            list = location
            list.insert(Node(key))
            self.population += 1

    def search(self, key):
        """
        .. _search:

        Search for a key.

        .. todo:: Implement the following steps:

            1. Hash the key to its slot, with the hash_ method
            2. If the slot is empty, return None
            3. If the slot is not empty, search the existing LinkedList_ for the element that contains the key
            4. If the key is in the list, return the *key* (not the Node_); otherwise return None

        :param key: the key to be searched
        :type key: str
        :return: the key, if it exists; None otherwise.
        :rtype: Node
        """
        hash_value = self.hash(key)
        list = self.array[hash_value]
        value = list.search(key)
        if value == None:
            return value
        return value.key

    def delete(self, key):
        """
        .. _delete:

        Delete the key from the table.

        .. todo:: Implements the following steps

            1. Hash the key to its slot, with the hash_ method
            2. If the slot is empty, return None
            3. If the slot is not empty, search the existing LinkedList_ for the element that contains the key
            4. If the key is in the list, delete the element that contains the key, update the `population` instance variable, and return the key (not the Node_); otherwise return None.

        :param key: the key to be deleted
        :type key: str
        :return: the key that has been deleted; None if the key was not in the table
        :rtype: str
        """
        hash_value = self.hash(key)
        list = self.array[hash_value]
        if self.array[hash_value] is None:
            return
        value = list.search(key)
        if value is not None:
            list.delete(value)
            self.population -= 1
        return

    def hash(self, key):
        """
        .. _hash:

        Hash a string key, using the method set for the current table (i.e. the procedure referred to by the instance variable `hash_method`).

        .. todo::
            Implement the following steps:

            1. Convert the string value into a numerical key, with the string_to_int_ function
            2. Pass the resulting key to the instance procedure `hash_method`

        .. note:: The instance attribute `self.hash_method` is just a function reference. It is initialized at the same time the table is created, and refers, depending on the use cases (see tests), either to the hash_multiply_ procedure, or to the hash_divide_ procedure, which is the default. The `hash_method` reference is useless until both hashing methods have been implemented.

        :param key: a string value.
        :type key: str
        :return: an index in the array.
        :rtype: int
        """
        value = self.string_to_int(key)
        return self.hash_method(value)

    def hash_multiply(self, numkey):
        """
        .. _hash_multiply:

        Compute the slot index for a given numerical key, using the multiplication method exposed in CLRS3, p. 264. For a table size :math:`m`, the key results from the following computation:

        .. math::
            h(k) = \\lfloor m * ( kA \\text{ mod } 1) \\rfloor  \\text{ with } A=(\\sqrt{5}-1)/2

        .. todo:: Use low-level bitwise operations to implement this function.  Given

            * a choice of table size :math:`2^p`
            * a length of machine word :math:`w`, that fits the largest key
            * a choice of integer :math:`s = A \\times  2^w`

            Code the following steps:

            1.  Compute:

            .. math::
                 k \cdot s

            2. Extract the fractional part of :math:`ks`, i.e. the :math:`w` lower bits, through bitwise AND, with the appropriate mask:

            .. math::
                fractional = k\cdot s \\text{ & } (2^w -1)

            3. Extract :math:`p` most significant bits, through a shift-right operation:

            .. math::
                h = fractional \gg (w - p)

            Note that constants :math:`S`, :math:`w`, and :math:`p` are already defined above, as **instance variables _S, _WORD_SIZE, and _P**, respectively. Since Python 3.* uses integers of variable length, :math:`w` is at the programmer's discretion, and _S is initialized accordingly. Even if this implementation of the multiplication method takes advantage of Python's flexibility (returning correct results for even very large keys), the method string_to_hash_ challenges you nonetheless to deal with large numerical keys by using only a constant number of machine numbers.

        :param numkey: the key to be stored
        :type numkey: int
        :return: a position in the array
        :rtype: int
        """
        A = (math.sqrt(5) - 1) / 2
        s = int((2**self._WORD_SIZE)*A)
        fractional = numkey*s &(2**self._WORD_SIZE - 1)
        return fractional >> (self._WORD_SIZE - self._P)

    def hash_divide(self, numkey):
        """
        .. _hash_divide:

        Use the division method to hash a key. Given a table size :math:`m`:

        .. math::
            h(k) = k \\text{ mod } m

        .. todo:: Implement the procedure.

        :param numkey: a numerical key
        :type numkey: int
        :return: an index in the array
        :rtype: int
        """
        return numkey % self.size

    def string_to_int(self, s, radix=31):
        """
        .. _string_to_int:

        Interpret a string as a natural number, that can be fed to a hashing algorithm.

        The resulting integer has value:

        .. math::
            s[1] \\times 31^{n-1} + s[2] \\times 31^{n-2} + \cdots + s[n-2] \\times 31^2 + s[n-1] \\times 31 + s[n]

        .. todo:: Implement the procedure, following the idea exposed in CLRS3, 11.3,  p. 263 ("Interpreting keys as natural numbers").

            The radix value is passed as a parameter (default: 31) and should therefore not be hardcoded in the function definition. As for the Python function that returns the ASCII of a given character, look it up in the documentation.

        :param s: a string object
        :type s: str
        :param radix: the base chosen for the numerical expansion of a string (default: 31)
        :type radix: int
        :return: a positive (potentially large) integer
        :rtype: int
        """

        string_as_number = 0
        counter = len(s) - 1
        for i in range(0, len(s)):
            string_as_number += ord(s[i]) * radix ** counter
            counter = counter - 1
        return string_as_number

    def string_to_hash(self, s):
        """
        .. _string_to_hash:

        (EXTRA-CREDIT: 10 pts - RESTORE THE CORRESPONDING UNIT TESTS AT THE END OF THE MODULE) Interpret a string as a natural number, with radix 128, and then hash it with the multiplication method.  The following procedure follows CLRS3, 11.3,  p. 263 ("Interpreting keys as natural numbers") and 11.3.1 ("The multiplication method") , but ensures that the  computation, and the resulting key do not use more than a constant number of machine numbers of length :math:`w` (see Exercise 11.3.2). Hint: Use the **mod** operation wisely.

        .. todo:: Implement the following steps:

            1. From string `s`, compute a radix-128 numerical key, without using more than a constant number of machine numbers
            2. then pass the resulting key to the hash_multiply_ procedure

            Instance variable **_WORD_SIZE** stores the value of :math:`w` for the table.

        :param s: a string object
        :type s: str
        :return: an index in the table
        :rtype: int
        """
        pass

    def list_at(self, key):
        """ Return the list object for a given key.

        ** Used for testing purpose only. **

        :param key: an existing key
        :type key: str
        :return: a reference to the list stored in this slot.
        :rtype: LinkedList
        """
        index = self.hash(key)
        if index and index < len(self.array):
            return self.array[self.hash(key)]
        return None

    def __str__(self):
        """ Provide a string representation of the hash table.

        :return: a string representation of the table, suitable for use in a `print` statement.
        :rtype: str
        """
        output = ''
        for slot in range(0, self.size):
            output += 'T[{}]-> {}\n'.format(slot, self.array[slot])
        return output


########################### DO NOT MODIFY BELOW THIS LINE ##############################################

class Hash_UnitTest(unittest.TestCase):
    words = ('bloody', 'beautiful', 'bereft', 'blue', 'blues', 'Bolton', 'British', 'British-Railways',
             'complaints', 'ex-parrot', 'Feeweeweewee', 'Ipswitch', 'Norwegian', 'Notlob', 'Polly',
             'Praline', 'Rail', 'remarkable', 'stunned', 'Sergeant-Major', 'sorry', 'bird', 'blame', 'boss',
             'boutique', 'brain', 'bucket', 'cage', 'counter', 'curtain', 'customer', 'cuttle', 'daisies',
             'definitely', 'demised', 'deposited', 'discovered', 'examining', 'expired', 'fake', 'fish',
             'fjords', 'flat', 'floor', 'found', 'four', 'fresh', 'inquiry', 'invisible', 'irrelevant',
             'lovely', 'metabolic', 'mustache', 'nuzzled', 'o\'clock', 'palindrome', 'parrot', 'peek',
             'perch', 'pet', 'plumage', 'plummet', 'python', 'register', 'shuffled', 'slug', 'sorry',
             'spells', 'squawk', 'squire', 'stiff', 'stone', 'stun', 'stunned', 'surgeon')

    def setUp(self):
        self.ht = HashTable()

    def test_string_to_int_1(self):
        """ Radix-31 representation of a string (default) """
        numkey = self.ht.string_to_int('plumage')
        self.assertEqual(numkey, 102603756267)

    def test_string_to_int_2(self):
        """ Radix-17 representation of a string (default) """
        numkey = self.ht.string_to_int('plumage', 17)
        self.assertEqual(numkey, 2867089643)

    def test_string_to_int_3(self):
        """ Empty string yields 0 """
        numkey = self.ht.string_to_int('')
        self.assertEqual(numkey, 0)

    def test_string_to_int_4(self):
        """ Strings that share a prefix yield different values """
        numkey1 = self.ht.string_to_int('British-Railway')
        numkey2 = self.ht.string_to_int('British-Railway-System')
        self.assertNotEqual(numkey1, numkey2)

    def test_string_to_int_5(self):
        self.assertEqual(self.ht.string_to_int('pt', 128), 14452)

    def test_division_method_1(self):
        """ Test the division method """
        numkey = 12309879098
        self.assertEqual(self.ht.hash_method(numkey), 26)

    def test_division_method_2(self):
        """ Test the division method """
        numkey = 3
        self.assertEqual(self.ht.hash_method(numkey), 3)

    def test_create_new_hash(self):
        self.assertEqual(self.ht.population, 0)

    def test_hash_1(self):
        """ Hashing a string (division method)"""

        hashed = self.ht.hash('plumage')
        self.assertEqual(hashed, 1)

    def test_hash_2(self):
        """ Strings that share a prefix hash to different slots (short strings)"""
        slot1 = self.ht.hash('abc')
        slot2 = self.ht.hash('ab')

    def test_hash_2(self):
        """ Strings that share a prefix hash to different slots (long strings)"""
        slot1 = self.ht.hash('constitutional')
        slot2 = self.ht.hash('constitutionally')
        self.assertNotEqual(slot1, slot2)

    def test_insert_word_1(self):
        """ Insert a single key """
        self.ht.set('ex-parrot')
        # print(self.ht)
        self.assertEqual(self.ht.list_at('ex-parrot').length, 1)

    def test_insert_words_2(self):
        """ Colliding keys """
        self.ht.set('squire')
        self.ht.set('shuffled')
        # print(self.ht)
        self.assertEqual(self.ht.list_at('python'), self.ht.list_at('nuzzled'))

    def test_insert_words_3(self):
        """ Insert a set of keys """
        for w in self.words:
            self.ht.set(w)
        # print(self.ht)
        self.assertEqual(self.ht.population, 75)

    def test_search_word_1(self):
        """ Search for an existing key """
        for w in self.words:
            self.ht.set(w)
        # print(self.ht)
        self.assertEqual(self.ht.search('British-Railways'), 'British-Railways')

    def test_search_word_2(self):
        """ Unsuccessful search for a key """
        for w in self.words:
            self.ht.set(w)
        # print(self.ht)
        self.assertEqual(self.ht.search('Moby Dick'), None)

    def test_delete_word_1(self):
        """ Delete a key """
        for w in self.words:
            self.ht.set(w)
        self.ht.delete('discovered')
        self.assertEqual(self.ht.search('discovered'), None)

    def test_delete_word_2(self):
        """ Delete a key that does not exist """
        for w in self.words:
            self.ht.set(w)
        self.assertEqual(self.ht.delete('Moby Dick'), None)

    def test_multiplication_create_new_hash(self):
        """ Create a new hash, that uses the multiplication method """
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        self.assertEqual(self.ht.population, 0)

    def test_multiplication_method_1(self):
        """ Test the multiplication method: 14-bit table size """
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION, p=14)
        numkey = 123456
        self.assertEqual(ht.hash_method(numkey), 67)

    def test_multiplication_method_2(self):
        """ Test the multiplication method: changing word size W (32) does not affect the hash """
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION, p=14, wordsize=32)
        numkey = 123456
        self.assertEqual(ht.hash_method(numkey), 67)

    def test_multiplication_method_3(self):
        """ Test the multiplication method: changing word size W (128) does not affect the hash """
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION, p=14, wordsize=128)
        numkey = 123456
        self.assertEqual(ht.hash_method(numkey), 67)

    def test_multiplication_method_4(self):
        """ Test the multiplication method (P has default value 7)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        numkey = 123456
        self.assertEqual(ht.hash_method(numkey), 0)

    def test_multiplication_method_5(self):
        """ Test the multiplication method (P has default value 7)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        numkey = 3
        self.assertEqual(ht.hash_method(numkey), 109)

    def test_multiplication_hash_1(self):
        """ Hashing a string (multiplication method)"""

        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        hashed = ht.hash('plumage')
        self.assertEqual(hashed, 53)

    def test_multiplication_hash_2(self):
        """ Strings that share a prefix hash to different slots (short strings)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        slot1 = ht.hash('abc')
        slot2 = ht.hash('ab')

    def test_multiplication_hash_2(self):
        """ Strings that share a prefix hash to different slots (long strings)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        slot1 = ht.hash('constitutional')
        slot2 = ht.hash('constitutionally')
        self.assertNotEqual(slot1, slot2)

    def test_multiplication_insert_word_1(self):
        """Insert a key (multiplication method)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        ht.set('ex-parrot')
        # print(ht)
        self.assertEqual(ht.list_at('ex-parrot').length, 1)

    def test_multiplication_insert_words_2(self):
        """ Colliding keys (multiplication method) """
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        ht.set('stiff')
        ht.set('python')
        # print(ht)
        self.assertEqual(ht.list_at('register'), ht.list_at('Praline'))

    def test_multiplication_insert_words_3(self):
        """ Insert a set of keys (multiplication)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        for w in self.words:
            ht.set(w)
        # print(ht)
        self.assertEqual(ht.population, 75)

    def test_multiplication_search_words(self):
        """ Search a key (multiplication method)"""
        ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
        for w in self.words:
            ht.set(w)
        # print(ht)
        self.assertEqual(ht.search('British-Railways'), 'British-Railways')


#### RESTORE THE TESTS FOR THE EXTRA-CREDIT WORK ##############
#
#	def test_string_to_hash(self):
#		""" Constant storage string hashing and standard string hashing hash to the same slot
#		(long key)
#		"""
#		ht = HashTable( HashTable.HashingMethod.MULTIPLICATION, 14)
#		key = 'this parrot is dead'
#		long_hash = ht.hash_multiply( ht.string_to_int(key, 128 ))
#		constant_hash = ht.string_to_hash( key )
#		self.assertEqual( constant_hash, long_hash)
#
#	def test_string_to_hash_2(self):
#		""" Constant storage string hashing and standard string hashing hash to the same slot
#		(short key)
#		"""
#		ht = HashTable( HashTable.HashingMethod.MULTIPLICATION)
#		key = 'uk'
#		long_hash = ht.hash_multiply( ht.string_to_int(key, 128 ))
#		constant_hash = ht.string_to_hash( key )
#		self.assertEqual( constant_hash, long_hash)


def main():
    unittest.main()


if __name__ == '__main__':
    main()

