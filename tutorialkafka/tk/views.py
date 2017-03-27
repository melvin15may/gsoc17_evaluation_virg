from django.http import HttpResponse
from kafka import KafkaProducer
from django.conf import settings

# Create messages

def producer(request):
	producer = KafkaProducer(bootstrap_servers=[settings.KAFKA_BROKER_URL])
	# Send message with topic 'simple-topic'
	producer.send('sample-topic',bytes(request.GET["message"]))
	# Send all async messages
	producer.flush()
	return HttpResponse('Produced message.')





