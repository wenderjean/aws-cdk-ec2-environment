#!/bin/bash

sudo apt update -y
sudo apt install -y build-essential curl git software-properties-common libssl-dev zlib1g-dev libreadline-dev
sudo apt install -y tmux

git clone https://github.com/asdf-vm/asdf.git /opt/.asdf --branch v0.14.0

su admin

sudo touch /etc/profile.d/asdf.sh
sudo touch /etc/profile.d/tmux.sh

sudo echo 'export ASDF_DIR=/opt/.asdf' >> /etc/profile.d/asdf.sh
sudo echo '. "/opt/.asdf/asdf.sh"' >> /etc/profile.d/asdf.sh
sudo echo '. "/opt/.asdf/completions/asdf.bash"' >> /etc/profile.d/asdf.sh

source /etc/profile.d/asdf.sh 

sudo echo 'if [[ $- =~ i ]] && [[ -z "$TMUX" ]] && [[ -n "$SSH_TTY" ]]; then' >> /etc/profile.d/tmux.sh
sudo echo '  tmux attach-session -t default || tmux new-session -s default' >> /etc/profile.d/tmux.sh
sudo echo 'fi' >> /etc/profile.d/tmux.sh

source /etc/profile.d/tmux.sh

asdf plugin add ruby https://github.com/asdf-vm/asdf-ruby.git
asdf install ruby 3.1.1
