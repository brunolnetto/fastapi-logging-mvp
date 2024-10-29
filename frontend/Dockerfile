# Stage 1: Install dependencies
FROM node:22 AS dependencies
WORKDIR /app

# Copy package.json and lock files to the container
COPY package.json pnpm-lock.yaml ./

# Install dependencies using pnpm
RUN npm install -g pnpm
RUN pnpm install

# Stage 2: Build the application
FROM node:22 AS build
WORKDIR /app

# Copy the installed dependencies from the previous stage
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

# Build the Vue.js app
RUN pnpm run build

# Stage 3: Serve the built app
FROM node:22-alpine AS production
WORKDIR /app

# Install a lightweight HTTP server
RUN npm install -g serve

# Copy the built files to the production stage
COPY --from=build /app/dist ./dist

# Expose the port for the server
EXPOSE 5000

# Serve the app
CMD ["serve", "-s", "dist", "-l", "5000"]
