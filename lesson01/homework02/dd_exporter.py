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