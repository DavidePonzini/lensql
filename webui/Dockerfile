FROM node:slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install && npm cache clean --force
COPY . .
RUN npm run build

FROM nginx:latest
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80