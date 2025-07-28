FROM node:slim AS build
WORKDIR /app
COPY webui/package.json webui/package-lock.json ./
RUN npm install --legacy-peer-deps && npm cache clean --force
COPY webui ./
RUN ["npm", "run", "build"] 

FROM nginx:latest
COPY nginx.prod/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
