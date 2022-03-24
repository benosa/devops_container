## Steps to reproduce ##

1) Setup host container
2) Install docker: please, visit to https://docs.docker.com/engine/install/centos/
3) Run first docker container: 
	```docker run --ipc=shareable -v ///tmp --name web -p 3000:80 -it --rm  --blkio-weight 1000 ubuntu /bin/bash```
4) Run second docker container with python: 
	```docker run -it --ipc=container:web --volumes-from web -p 3001:80 --rm --pid container:web python /bin/bash```
5) Run dd task in first container:
	```dd if=/dev/urandom of=/file.tmp bs=1024 count=1000000 oflag=direct 2> /tmp/stderr```
	
	
6) Create python exporter for prometheus:
	```
		from prometheus_client import start_http_server, Counter
		from subprocess import check_output
		import random
		import signal
		import os
		import time
		import subprocess

		dd_counter = Counter('dd_obtained_bytes', 'Time spent processing request')

		def get_pid(name):
			return int(check_output(["pgrep",name]))

		def tail(f, n):
			p1 = subprocess.Popen(["tail",n,f],stdout=subprocess.PIPE,text=True)
			#p2 = subprocess.Popen(["grep","-Po","\d*(?=\sbytes)"],stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
			p2 = subprocess.Popen(["grep","-Po","(?<=\()\d*.\d*(?=\sMB)"],stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
			p1.stdout.close()
			return float(p2.communicate()[0])

		def gather_metrics(t):
			print("collecting httpd metrics")
			os.kill(get_pid("dd"), signal.SIGUSR1)
			obtained_bytes = tail("/tmp/stderr","-1")
			print("obtained bytes: %d" % (obtained_bytes))
			dd_counter.inc((obtained_bytes - dd_counter._value.get()))
			print("gounted bytes: %d" % dd_counter._value.get())
			time.sleep(t)

		if __name__ == '__main__':
			# Start up the server to expose the metrics.
			start_http_server(80)
			# Generate some requests.
			while True:
				gather_metrics(1)
	```
	
7) Run exporter:
	```python ./dd_exporter.py```
	On address: {{ HOST }}:3001/metrics - external port of second container, we can see the metrics of dd task wich running in first container
8) Setup host for run prometheus
9) Install docker: please, visit to https://docs.docker.com/engine/install/centos/
10)Create prometheus config file prometheus.yml:
	```
		global:
		  scrape_interval: 15s
		  evaluation_interval: 15s

		scrape_configs:
		  # Self
		  - job_name: "prometheus-server"
			static_configs:
			  - targets:
				  - "localhost:9090"

		  # Python example
		  - job_name: "dd"
			scrape_interval: 5s
			static_configs:
			  - targets:
				  - "ec2-15-188-227-203.eu-west-3.compute.amazonaws.com:3001"
	```
	Set ```interval``` and ```targets``` of our exporter.
11)Run prometheus in docker with our config file:
	```docker run -p 9090:9090 --volume=/tmp/prometheus.yml:/etc/prometheus/prometheus.yml  prom/prometheus  --config.file=/etc/prometheus/prometheus.yml```
12)Execute our metric dd_obtained_bytes_total

In graph we can see our metric

Pictures:
	communication.png - communication between of three containers
	statistics_from_dd_exporter.png, statistics_from_dd_exporter2.png - example our metrics in prometheus