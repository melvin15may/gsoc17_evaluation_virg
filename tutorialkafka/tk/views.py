from django.http import HttpResponse
from kafka import KafkaProducer
from django.conf import settings

def producer(request):
	producer = KafkaProducer(bootstrap_servers=[settings.KAFKA_BROKER_URL])
	producer.send('sample-topic',bytes(request.GET["message"]))
	producer.flush()
	return HttpResponse('Produced message.')





