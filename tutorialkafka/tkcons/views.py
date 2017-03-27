from django.http import HttpResponse
from kafka import KafkaConsumer
from django.conf import settings
import threading

# Start a consumer

def start_consumer(request):
	def start():
		cons = KafkaConsumer("sample-topic",bootstrap_servers=[settings.KAFKA_BROKER_URL])
		for m in cons:
			with open("static/consumed_messages.txt", "a") as f:
				f.write(str(m)+"<br>")
		return

	# Run consumer in background on a separate thread
	t = threading.Thread(target=start)
	t.daemon = True
	t.start()

	return HttpResponse("Started consumer")


# Show messages that have been consumed

def show_consumed_message(request):

	with open("static/consumed_messages.txt", "r") as f:
		return HttpResponse(f.read())
