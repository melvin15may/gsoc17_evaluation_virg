## Django + Kafka Tutorial
# A Simple Producer-Consumer Project 

We will create 2 apps, producer and consumer. The producer will have an API endpoint to add custom messages to Kafka and the consumer will have 2 endpoints, one to start the consumer and another to view consumed messages. The consumer will have a basic functionality of writing the messages to a file.

### Requirements
* python 2.7.12 
* django v1.10.6
* kafka-python v1.3.3
* kafka v0.10.2

### System
* ubuntu 16.04 LTS

### Installation
##### Installing Django  
1. Create a virtual environment using virtualenv or virtualenvwrapper
2. After activating virtual environment, enter command ```$ pip install Django ``` in shell to install the latest stable release (1.10.6)

   [More info](https://docs.djangoproject.com/en/1.10/topics/install/)

##### Installing Apache Kafka
1. Install Java

   Before installing additional packages, update the list of available packages so you are installing the latest versions available in the repository:

   ```$ sudo apt-get update```

   As Apache Kafka needs a Java runtime environment, use apt-get to install the default-jre package:

   ```$ sudo apt-get install default-jre```

2. Install Zookeeper

   This package is available in Ubuntu’s default repository

   ```$ sudo apt-get install zookeeperd```
  
   Check if Zookeeper is working using telnet

   ```$ telnet localhost 2181```

   At the Telnet prompt, type in ruok and press ENTER. If everything is fine , ZooKeeper will say imok and end the Telnet session.

3. Download and Extract Kafka Binaries

   Download Kafka (v0.10.2) form https://www.apache.org/dyn/closer.cgi?path=/kafka/0.10.2.0/kafka_2.11-0.10.2.0.tgz

   Extract it.

4. Configure the Kafka Server

   By default Kafka doesn't allow you to delete topics so add ```delete.topic.enable = true```
to **/config/server.properties** file

5. Start Kafka server


   Run the **kafka-server-start.sh** script using nohup to start the Kafka server (also called Kafka broker) as a background process that is independent of your shell session.

   ```$ nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/kafka/kafka.log 2>&1 &```

   By default Kafka Server runs on port 9092 

##### Installing Kafka-python client
Within the virtual environment created above, enter command ```$ pip install kafka-python```, this will install the module.

  [More info](http://kafka-python.readthedocs.io/en/master/install.html)

### Procedure

1. To create a project from the command line, cd into a directory where you’d like to store your code, then run the following command:

   ```$ django-admin startproject tutorialkafka```

2. Create 2 apps: 

  * **tk**

    * This is the producer app. It will create the messages and add to Kafka using kafka-python client.
    * Create app

     ```$ python manage.py startapp tk```

  * **tkcons**

     * This is the consumer app. It will read the messages from Kafka and write it to a file
     * Create app
   
      ```$ python manage.py startapp tkcons```

   After executing the above mentioned commands, we get 2 folders.

3. To include the apps in our project, we need to reference the configuration class in the **INSTALLED_APPS** settings in the **tutorialkafka/settings.py** file. (Add **tk.apps.TkConfig** and **tkcons.apps.TkconsConfig** to the list)
4. Add the Kafka server URL to **tutorialkafka/settings.py** (using default port 9092)

   ```python 
   KAFKA_BROKER_URL = "localhost:9092"

5. The consumer app will write the messages to a file named **consumed_messages.txt**, so every time django is restarted we clear the consumed messages from this file. To do so add the following code to **tutorialkafka/settings.py**  

   ```python
   with open("static/consumed_messages.txt", "w") as f:
       f.write("")

6. To create the endpoint for producing the message, open the **tk/views.py** file and add the following code

   ```python
   from kafka import KafkaProducer
   from django.conf import settings
   
   def producer(request):
       producer = KafkaProducer(bootstrap_servers=[settings.KAFKA_BROKER_URL])
       producer.send('sample-topic',bytes(request.GET["message"]))
       producer.flush()
       return HttpResponse('Produced message.')

7. To call this view, we need to map it to a URL. Create a file called **urls.py** in the **tk** folder and add the following code

   ```python
   from django.conf.urls import url
   from . import views
   
   urlpatterns = [
      url(r'^$', views.producer, name='producer'),
      ]

8. We need to point the root URLconf to the tk.urls module. In **tutorialkafka/urls.py**, add an import for django.conf.urls.include and insert an include() in the urlpatterns list, so you have:

   ```python
   from django.conf.urls import url, include
   from django.contrib import admin
   
   urlpatterns = [
      url(r'^tkprod/', include('tk.urls')),
      url(r'^admin/', admin.site.urls)
      ]
  
9. To create endpoint to start the consumer, open **tkcons/views.py** file and add the following:

   ```python
   from django.http import HttpResponse
   from kafka import KafkaConsumer
   from django.conf import settings
   import threading
   
   def start_consumer(request):
      def start():
         cons = KafkaConsumer("sample-topic", bootstrap_servers=[settings.KAFKA_BROKER_URL])
         for m in cons:
            with open("static/consumed_messages.txt", "a") as f:
            f.write(str(m)+"<br>")
         return
      t = threading.Thread(target=start)
      t.daemon = True
      t.start()
      return HttpResponse("Started consumer")

> We are using threading to run the consumer in the background.

10. To call this view, we need to map it to a URL. Create a file called **urls.py** in the **tkcons** folder and add the following code

    ```python
    from django.conf.urls import url
    from . import views
    
    urlpatterns = [
       url(r'^$', views.start_consumer, name='start consumer'),
       ]

11. We need to point the root URLconf to the tkcons.urls module. In **tutorialkafka/urls.py**, insert an include() in the urlpatterns list, so you have:

    ```python
    from django.conf.urls import url, include
    from django.contrib import admin
    
    urlpatterns = [
       url(r'^tkprod/', include('tk.urls')),
       url(r'^tkcons/', include('tkcons.urls')),
       url(r'^admin/', admin.site.urls),
       ]

12. To view the file that contains the messages received by the consumer app, we create a view. To do so add the following code to the **tkcons/views.py** file:
	

    ```python
    def show_consumed_message(request):
       with open("static/consumed_messages.txt", "r") as f:
          return HttpResponse(f.read())
        

13. To call this view, we need to map it to a URL. In the **tkcons/urls.py** file, add ```url(r'^read/', views.show_consumed_message, name='read consumed messages')``` to urlpatterns list, so you have:

    ```python
    from django.conf.urls import url
    from . import views
    
    urlpatterns = [
       url(r'^read/', views.show_consumed_message, name='read consumed messages'),
       url(r'^$', views.start_consumer, name='start consumer'),
       ]

14. Create a folder /static in the outer /tutorialkafka folder to save the message file.
15. Run the server using the commands
    
    ```$ python manage.py runserver```
    
    The server will run on http://127.0.0.1:8000/ by default.

### Endpoints

We have 3 endpoints/views

1. /tkprod 
   
   Arguments: message
   
   This creates a message to be added to Kafka.
   
   E.g.
   
   http://127.0.0.1:8000/tkprod?message=hello
   
   Will add a message ‘hello’
2. /tkcons
   
   This creates a consumer for Kafka
   
   E.g.
   
   http://127.0.0.1:8000/tkcons
3. /tkcons/read
   
   Show messages already consumed by consumer
   
   E.g.
   
   http://127.0.0.1:8000/tkcons/read
