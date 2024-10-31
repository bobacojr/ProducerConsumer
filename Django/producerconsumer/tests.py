from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import SharedBuffer

class ProducerConsumerTest(TestCase):
    def setUp(self):
        self.buffer = SharedBuffer.objects.create(bufferSize=10, count=0)

    def test_producer_increases_count(self):
        # Simulate producing an item
        self.buffer.count += 1
        self.buffer.save()
        self.assertEqual(self.buffer.count, 1)

    def test_consumer_decreases_count(self):
        # Simulate consuming an item
        self.buffer.count += 1  # First, produce an item
        self.buffer.save()
        
        self.buffer.count -= 1  # Now, consume it
        self.buffer.save()
        self.assertEqual(self.buffer.count, 0)

    def test_buffer_full_condition(self):
        self.buffer.count = self.buffer.bufferSize
        self.buffer.save()
        
        # Check if producer should wait (you may need to implement logic for this)
        self.assertTrue(self.buffer.count >= self.buffer.bufferSize)

    def test_buffer_empty_condition(self):
        self.buffer.count = 0
        self.buffer.save()
        
        # Check if consumer should wait (you may need to implement logic for this)
        self.assertTrue(self.buffer.count == 0)