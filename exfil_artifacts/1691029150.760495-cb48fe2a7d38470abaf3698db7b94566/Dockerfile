
FROM ubuntu:18.04
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd

RUN useradd -M gnome 
RUN echo 'gnome:CL0UDV1LL4G3_SSH_KUB3' | chpasswd 

RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
RUN chmod go-rx /usr/bin/passwd

WORKDIR /jailed
COPY ./jailed .
# The directory "jailed" contains the binaries for bash and ls
# These binaries are necessary to execute the display flag binary

RUN chown -R root:root /jailed
RUN chmod -R 755 .
RUN chmod 1733 /tmp /var/tmp /dev/shm

RUN chsh -s /bin/bash gnome

RUN echo "Match User gnome" >> /etc/ssh/sshd_config
RUN echo "  ChrootDirectory /jailed" >> /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]