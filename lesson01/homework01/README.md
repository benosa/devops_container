## Steps to reproduce ##

1) Setup host container
2) Install docker: please, visit to https://docs.docker.com/engine/install/centos/
3) Run first docker container: 
	docker run --ipc=shareable -v ///tmp --name web -p 3000:80 -it --rm  --blkio-weight 1000 ubuntu /bin/bash 
4) Run second docker container: 
	docker run -it --ipc=container:web --volumes-from web -p 3001:80 --rm --pid container:web alpine /bin/ash
5) Run dd task in first container:
	dd if=/dev/urandom of=/file.tmp bs=1024 count=1000000 oflag=direct 2> /tmp/stderr
	** stderr redirect to file /tmp/stderr **
6) Getting progress from running dd task in first container from second container every 5 seconds
	while kill -USR1 "$(pgrep dd)" ; do tail -1 /tmp/stderr ; sleep 5 ; done
	
	In picture, we have to see the communication process between two conteiners.