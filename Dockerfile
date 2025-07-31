FROM node:22-alpine3.21

# Install git (optional)
RUN apk add --no-cache git

# Set working directory
WORKDIR /code

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the app
COPY . .

# Expose the dev server port
EXPOSE 3000

# Start the React development server
CMD ["sh", "-c", "HOST=0.0.0.0 npm start"]