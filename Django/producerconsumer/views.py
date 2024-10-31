import logging
from django.shortcuts import render
from django.http import JsonResponse
from .models import SharedBuffer as shb, TaskOutput
from .tasks import producer_task, consumer_task
from mysite.celery import app
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def index(request):
    buffer, created = shb.objects.get_or_create(pk=1) # Get or create an object pk=1 (primary key = 1)
    return render(request, 'producer_consumer/index.html', {'buffer' : buffer}) # Renders the webpage passing the SharedBuffer to it

@csrf_exempt
def getTaskOutput(request):
    messages = TaskOutput.objects.order_by('-timestamp').values_list('message', flat=True)[:100]  # Get last 100 messages
    return JsonResponse({'output': '\n'.join(messages)})

@csrf_exempt
def startSimulation(request):
    if request.method == 'POST':
        TaskOutput.objects.all().delete() # Clear all entries in the getTaskOutput textarea

        app.control.purge()

        bufferSize = int(request.POST.get('bufferSize', 10))
        producerSleepTime = float(request.POST.get('producerSleepTime', 1.0))
        consumerSleepTime = float(request.POST.get('consumerSleepTime', 1.5))

        buffer, created = shb.objects.get_or_create(pk=1) # Get or create pk=1, created shows results
        buffer.buffer = []
        buffer.bufferSize = bufferSize
        buffer.in_index = 0
        buffer.out_index = 0
        buffer.count = 0
        buffer.producerSleepTime = producerSleepTime
        buffer.consumerSleepTime = consumerSleepTime
        buffer.shouldTerminate = False
        buffer.producerFinished = False
        buffer.save()

        producer_task.delay() # Queue the producer_task
        consumer_task.delay() # Queue the consumer_task

    return JsonResponse({'Status' : 'Started'})

@csrf_exempt
def adjustSleepTime(request):
    if request.method == 'POST':
        try:
            producer = request.POST.get('producer') == 'true'
            increase = request.POST.get('increase') == 'true'
            buffer = shb.objects.get(pk=1)
            
            if producer:
                if increase:
                    buffer.producerSleepTime = min(buffer.producerSleepTime + 0.25, 10)  # Max 5 seconds
                else:
                    buffer.producerSleepTime = max(buffer.producerSleepTime - 0.25, 0)  # Min 0 seconds
            else:
                if increase:
                    buffer.consumerSleepTime = min(buffer.consumerSleepTime + 0.25, 10)  # Max 5 seconds
                else:
                    buffer.consumerSleepTime = max(buffer.consumerSleepTime - 0.25, 0)  # Min 0 seconds
            
            buffer.save()
            
            return JsonResponse({
                'producerSleepTime': buffer.producerSleepTime,
                'consumerSleepTime': buffer.consumerSleepTime,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def terminateSimulation(request):
    if request.method == 'POST':
        try:
            buffer = shb.objects.get(pk=1)
            buffer.shouldTerminate = True
            buffer.save()

            logger.info("Simulation terminated successfully")
            return JsonResponse({'status': 'Simulation terminated successfully'})
        except shb.DoesNotExist:
            logger.error("Buffer not found")
            return JsonResponse({'status': 'Error: Buffer not found'}, status=404)
        except Exception as e:
            logger.error(f"Error terminating simulation: {str(e)}")
            return JsonResponse({'status': f'Error: {str(e)}'}, status=500)
    else:
        return JsonResponse({'status': 'Invalid request method'}, status=405)

@csrf_exempt
def getBufferStatus(request):
    if request.method == 'GET':
        logger.debug("Entering getBufferStatus view")
        try:
            buffer, created = shb.objects.get_or_create(pk=1)
            logger.debug(f"Retrieved or created buffer: {buffer}, Created: {created}")
            
            return JsonResponse({
                'buffer': list(buffer.buffer) if hasattr(buffer, 'buffer') else [],
                'count': buffer.count,
                'producerFinished': buffer.producerFinished,
                'shouldTerminate': buffer.shouldTerminate,
                'size': buffer.bufferSize,
                'producerSleep': buffer.producerSleepTime,
                'consumerSleep': buffer.consumerSleepTime,
            })
        except Exception as e:
            logger.error(f"Error in getBufferStatus: {str(e)}")
            return JsonResponse({
                'error': str(e)
            }, status=500)