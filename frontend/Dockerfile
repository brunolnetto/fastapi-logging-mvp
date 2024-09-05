# Use Node.js as base image for the frontend
FROM node:18 AS build

# Set working directory to /app
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml files to the container
COPY package.json pnpm-lock.yaml ./

# Install frontend dependencies using pnpm
RUN pnpm install

# Copy the rest of the frontend code
COPY . .

# Build the Vue.js app
RUN pnpm run build

# Use a lightweight server to serve the built app
FROM node:18 AS production

# Install `serve` globally
RUN npm install -g serve

# Set working directory
WORKDIR /app

# Copy the built frontend app from the previous stage
COPY --from=build /app/dist /app/dist

# Expose port 5000 for serve
EXPOSE 5000

# Serve the frontend app using `serve`
CMD ["serve", "-s", "dist", "-l", "5000"]

