import random
import time
from .models import SharedBuffer as shb, TaskOutput
from celery import shared_task
from django.db import transaction
from threading import Lock

buffer_mutex = Lock() # Buffer protection
io_mutex = Lock() # Input/Output protection

def custom_print(message):
    TaskOutput.objects.create(message=message)

@shared_task(queue='producer')
def producer_task():
    items_produced = 0
    while True:

        with buffer_mutex: # Lock the SharedBuffer
            with transaction.atomic():

                buffer = shb.objects.select_for_update().get(pk=1) # Lock pk=1 for updates
                if buffer.shouldTerminate or items_produced >= buffer.bufferSize:
                    break
                if buffer.count < buffer.bufferSize:
                    item = random.randint(1000, 9000) # Generate a random 4 digit number
                    bin = buffer.in_index
                    buffer.buffer.append(item) # Add the item to the buffer
                    buffer.in_index = (buffer.in_index + 1) % buffer.bufferSize
                    buffer.count += 1
                    items_produced += 1
                    buffer.save()

                    print(f'Producer: Put {item} into bin {bin}')
                    custom_print(f'Producer: Put {item} into bin {bin}')
        
        time.sleep(buffer.producerSleepTime)

    with buffer_mutex:
        with transaction.atomic():
            buffer = shb.objects.select_for_update().get(pk=1)
            buffer.producerFinished = True
            buffer.save()

    print('Producer: Execution has completed')
    custom_print('Producer: Execution has completed')

@shared_task(queue='consumer')
def consumer_task():
    while True:

        with buffer_mutex: # Lock the SharedBuffer
            with transaction.atomic():

                buffer = shb.objects.select_for_update().get(pk=1)
                if buffer.count == 0 and buffer.producerFinished:
                    break

                if buffer.count > 0:
                    item = buffer.buffer[buffer.out_index]
                    bin = buffer.out_index
                    buffer.out_index = (buffer.out_index + 1) % buffer.bufferSize
                    buffer.count -= 1

                    buffer.save()
                    print(f'-------------------------> Consumer: Grabbed {item} from bin {bin}')
                    custom_print(f'-------------------------> Consumer: Grabbed {item} from bin {bin}')

        time.sleep(buffer.consumerSleepTime)
        
    print('-------------------------> Consumer: Execution has completed')
    custom_print('-------------------------> Consumer: Execution has completed')