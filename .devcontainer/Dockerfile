FROM python:3.13-slim

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    postgresql-client \
    redis-tools \
    openssh-client \
    gnupg \
    ca-certificates \
    zsh \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package installation
RUN pip install --no-cache-dir uv==0.5.11

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.4

# Install Node.js (for some development tools)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Install Task (Taskfile runner)
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /bin/zsh \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install Oh My Zsh for better terminal experience
RUN su - $USERNAME -c "sh -c \"\$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\" \"\" --unattended"

# Switch back to dialog for any ad-hoc use
ENV DEBIAN_FRONTEND=dialog

# Set the default user
USER $USERNAME

# Set working directory
WORKDIR /workspace
