FROM node:8.9-alpine

RUN mkdir -p /app
WORKDIR /app

COPY . /app

RUN npm install -g @vue/cli

RUN npm install
RUN npm ls \
RUN npm cache clean --force

EXPOSE 8080

CMD ["npm run serve"]
