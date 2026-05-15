FROM eclipse-temurin:8-jre-jammy

RUN apt-get update && apt-get install -y \
    bash \
    curl \
    tar \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m user

WORKDIR /home/user/app

COPY . .

RUN mkdir -p /home/user/app/solr-8.11.0/server/logs \
    && chown -R user:user /home/user/app

EXPOSE 8983

USER user

ENV SOLR_SECURITY_MANAGER_ENABLED=false

CMD /home/user/app/solr-8.11.0/bin/solr start -f -a "-Dcom.sun.jndi.ldap.object.trustURLCodebase=true -Dcom.sun.jndi.rmi.object.trustURLCodebase=true -Dlog4j2.formatMsgNoLookups=false"
