FROM node:18-bullseye
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY . .
EXPOSE 3000
CMD ["npm", "start"]