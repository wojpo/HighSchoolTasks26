FROM debian:bookworm

RUN apt update && apt install -y \
    bash \
    curl \
    netcat-openbsd \
    openssh-server \
    openjdk-17-jdk \
    maven \
    nmap

RUN useradd -m user && echo "user:SuperT4jn3Hasl0" | chpasswd

RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
 && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

RUN mkdir /var/run/sshd

WORKDIR /home/user/app

COPY . .

RUN mvn clean package

EXPOSE 22
EXPOSE 80

CMD service ssh start && java -jar target/*-jar-with-dependencies.jar
