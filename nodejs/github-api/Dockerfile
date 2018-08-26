FROM node:8.11-alpine

WORKDIR /app

ADD . /app

RUN npm install

EXPOSE 8080

ENV SERVER_NAME node_test_server

ENTRYPOINT ["node", "server.js"]
