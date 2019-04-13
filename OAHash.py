#!/bin/python3

from collections import namedtuple

TableEntry = namedtuple('Element', 'hash key value')


class HashTable(object):
	DefaultSize = 8
	NoValue = TableEntry(None, None, None)
	LoadFactor = 2 / 3
	MinFactor = 1 / 3
	
	def __init__(self):
		self.container = [self.NoValue] * self.DefaultSize
		self.size = 0
		self.deletedSize = 0
		self.containerSize = self.DefaultSize
	
	def __len__(self):
		return self.size
	
	def __contains__(self, key):
		try:
			_ = self.get(key)
			return True
		except KeyError:
			return False
	
	def _resize(self):
		oldContainer = self.container
		oldSize = self.size
		self.containerSize = int(oldSize // self.MinFactor)
		self.container = [self.NoValue] * self.containerSize
		self.size = 0
		self.deletedSize = 0
		for element in oldContainer:
			if element is not self.NoValue and element is not self.NoValue:
				self.set(element.key, element.value)
	
	def __repr__(self):
		tokens = []
		for element in self.container:
			if element is not self.NoValue and element is not self.NoValue:
				tokens.append("{0} : {1}".format(element.key, element.value))
		return "{" + "\n".join(tokens) + "}"
	
	def _get_entry(self, key):
		""" Return (E0,E1) where E0 is the value or EMPTY_VALUE
		E1 is the index where it was found or if E0 is
		EMPTY_VALUE then the next insert index for the given key
		"""
		key_hash = hash(key)
		root_index = key_hash
		for offset in range(self.containerSize):
			index = (root_index + offset) % self.containerSize
			element = self.container[index]
			if element is self.NoValue \
					or element.hash == key_hash and element.key == key:
				return element, index
		raise KeyError
	
	def set(self, key, value):
		entry, index = self._get_entry(key)
		self.container[index] = TableEntry(hash(key), key, value)
		if entry is self.NoValue:
			self.size += 1
		if (self.deletedSize + self.size) / self.containerSize > self.LoadFactor:
			self._resize()
	
	def __setitem__(self, key, value):
		self.set(key, value)
	
	def get(self, key):
		entry, _ = self._get_entry(key)
		if entry is self.NoValue:
			raise KeyError('Key {0} not in hash table'.format(key))
		else:
			return entry.value
	
	def __getitem__(self, key):
		return self.get(key)
	
	def delete(self, key):
		entry, index = self._get_entry(key)
		if entry is self.NoValue:
			raise KeyError('Key {0} not in hash table'.format(key))
		else:
			self.container[index] = self.NoValue
			self.size -= 1
			self.deletedSize += 1
	
	def __delitem__(self, key):
		self.delete(key)

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
		self.ht.insert('ex-parrot')
		# print(self.ht)
		self.assertEqual(self.ht.list_at('ex-parrot').length, 1)

	def test_insert_words_2(self):
		""" Colliding keys """
		self.ht.insert('squire')
		self.ht.insert('shuffled')
		# print(self.ht)
		self.assertEqual(self.ht.list_at('python'), self.ht.list_at('nuzzled'))

	def test_insert_words_3(self):
		""" Insert a set of keys """
		for w in self.words:
			self.ht.insert(w)
		# print(self.ht)
		self.assertEqual(self.ht.population, 75)

	def test_search_word_1(self):
		""" Search for an existing key """
		for w in self.words:
			self.ht.insert(w)
		# print(self.ht)
		self.assertEqual(self.ht.search('British-Railways'), 'British-Railways')

	def test_search_word_2(self):
		""" Unsuccessful search for a key """
		for w in self.words:
			self.ht.insert(w)
		# print(self.ht)
		self.assertEqual(self.ht.search('Moby Dick'), None)

	def test_delete_word_1(self):
		""" Delete a key """
		for w in self.words:
			self.ht.insert(w)
		self.ht.delete('discovered')
		self.assertEqual(self.ht.search('discovered'), None)

	def test_delete_word_2(self):
		""" Delete a key that does not exist """
		for w in self.words:
			self.ht.insert(w)
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
		ht.insert('ex-parrot')
		# print(ht)
		self.assertEqual(ht.list_at('ex-parrot').length, 1)

	def test_multiplication_insert_words_2(self):
		""" Colliding keys (multiplication method) """
		ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
		ht.insert('stiff')
		ht.insert('python')
		# print(ht)
		self.assertEqual(ht.list_at('register'), ht.list_at('Praline'))

	def test_multiplication_insert_words_3(self):
		""" Insert a set of keys (multiplication)"""
		ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
		for w in self.words:
			ht.insert(w)
		# print(ht)
		self.assertEqual(ht.population, 75)

	def test_multiplication_search_words(self):
		""" Search a key (multiplication method)"""
		ht = HashTable(HashTable.HashingMethod.MULTIPLICATION)
		for w in self.words:
			ht.insert(w)
		# print(ht)
		self.assertEqual(ht.search('British-Railways'), 'British-Railways')

def main():
	unittest.main()


if __name__ == '__main__':
	main()