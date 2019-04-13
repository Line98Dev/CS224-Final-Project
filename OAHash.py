#!/bin/py

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
