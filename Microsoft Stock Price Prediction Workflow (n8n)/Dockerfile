FROM n8nio/n8n:latest

# Install additional Python packages if needed
USER root

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    curl \
    wget

# Install Python packages commonly used in trading workflows
RUN pip3 install --no-cache-dir \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    tensorflow \
    torch \
    yfinance \
    requests \
    matplotlib \
    seaborn \
    plotly \
    discord-webhook

# Switch back to n8n user
USER node

# Set environment variables
ENV NODE_ENV=production
ENV N8N_USER_FOLDER=/home/node/.n8n

# Create necessary directories
RUN mkdir -p /home/node/.n8n/workflows
RUN mkdir -p /home/node/.n8n/nodes

# Copy workflow file
COPY --chown=node:node trading-workflow.json /home/node/.n8n/workflows/

# Copy any custom nodes or scripts
COPY --chown=node:node scripts/ /home/node/scripts/

# Expose port
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5678/healthz || exit 1

# Start n8n
CMD ["n8n"]
