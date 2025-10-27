FROM node:19
WORKDIR /Users/aleksej/Documents/Учёба/ВИС/docker_5
COPY package*.json .
RUN npm install
COPY . .
EXPOSE 4000
CMD ["npm", "run", "start"]