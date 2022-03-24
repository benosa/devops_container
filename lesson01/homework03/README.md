## Steps to reproduce ##

1) Setup host container
2) Install docker: please, visit to https://docs.docker.com/engine/install/centos/
3) Run first docker container: 
	```docker run --ipc=shareable -v ///tmp --name web -p 3000:80 -it --rm --device-write-bps  /dev/xvda:1kb ubuntu /bin/bash```
	** limit write speed to 1 KB/s on /dev/xvda **
4) Run second docker container with python: 
	```docker run -it --ipc=container:web --volumes-from web -p 3001:80 --rm --pid container:web python /bin/bash```
5) Run dd task in first container:
	```dd if=/dev/urandom of=/file.tmp bs=1024 count=1000000 oflag=direct 2> /tmp/stderr```
6) Getting progress from running dd task in first container from second container every 5 seconds
	```while kill -USR1 "$(pgrep dd)" ; do tail -1 /tmp/stderr ; sleep 5 ; done```
	
On picture, we can see the dd copy task is limited by speed in first container. We can to incrase speed limit. 
We can use CGROUP file interface, where we can set ```echo "202:0 1048576" > ./blkio.throttle.write_bps_device```
On picture, we can see how speed incrased of dd command.
	
