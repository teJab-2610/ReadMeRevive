#!/bin/bash

# # Function to automate input for Joern installation
# auto_input_joern() {
#     expect -c "
#         spawn ./joern-install.sh --interactive
#         expect \"Would you like to continue? (y/N)\"
#         send \"y\r\"
#         expect \"Please enter the path where joern shall be installed:\"
#         send \"\r\"
#         expect \"Please enter the path where you want to place symbolic links to joern executables:\"
#         send \"\r\"
#         expect eof
#     "
# }

# Install expect if not already installed
if ! command -v expect &> /dev/null
then
    echo "Installing expect..."
    sudo apt install -y expect
fi

# Install Python packages
echo "Installing Python packages:"
pip install nltk
pip install -U scikit-learn
pip install numpy
echo "Installed Classfier packages"
pip install pydriller
echo "Installed Pydriller"
pip install -q -U google-generative
echo "Instaleld Google Generative"

pip install spacy
python -m spacy download en_core_web_sm
pip install network
pip install matplotlib

# # Install Joern
# echo "Installing Joern..."
# curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" -o joern-install.sh
# chmod u+x joern-install.sh

# # Automate input for Joern installation
# auto_input_joern
# echo "Done installing Joern"

echo "Installation completed."
