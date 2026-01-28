# Use official Node runtime as the base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Install a simple server to serve the static files
RUN npm install -g serve

# Expose the port (will be assigned dynamically)
EXPOSE $PORT

# Start the application
CMD ["sh", "-c", "serve -s dist -l ${PORT:-8080}"]