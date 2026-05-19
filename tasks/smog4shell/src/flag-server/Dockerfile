FROM eclipse-temurin:8-jre-jammy

RUN apt-get update && apt-get install -y \
    bash \
    curl \
    tar \
    netcat-traditional \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m user

WORKDIR /home/user/app

ARG SOLR_VERSION=8.11.0
ARG SOLR_TGZ_SHA512=

RUN wget "https://archive.apache.org/dist/lucene/solr/${SOLR_VERSION}/solr-${SOLR_VERSION}.tgz" \
    && echo "${SOLR_TGZ_SHA512}  solr-${SOLR_VERSION}.tgz" | sha512sum -c - \
    && tar -xzf "solr-${SOLR_VERSION}.tgz" \
    && rm "solr-${SOLR_VERSION}.tgz"

RUN mkdir -p /home/user/app/solr-8.11.0/server/logs && chown -R user:user /home/user/app

COPY . .

EXPOSE 8983

USER user

ENV SOLR_SECURITY_MANAGER_ENABLED=false

CMD /home/user/app/solr-8.11.0/bin/solr start -f -a "-Dcom.sun.jndi.ldap.object.trustURLCodebase=true -Dcom.sun.jndi.rmi.object.trustURLCodebase=true -Dlog4j2.formatMsgNoLookups=false"
