FROM rabbitmq:latest

ENV RABBITMQ_DEFAULT_USER=user
ENV RABBITMQ_DEFAULT_PASS=password

RUN rabbitmq-plugins enable --offline \
    rabbitmq_management \
    rabbitmq_management_agent

EXPOSE 5672 15672
