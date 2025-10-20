Installation & Usage
Create the project structure:

bash
mkdir wifi-automation-tool
cd wifi-automation-tool
# Create all the files as shown above
Make install script executable and run:

bash
chmod +x install.sh
sudo ./install.sh
Run the tool:

bash
sudo ./main.py
Specific operations:

bash
# Only scan networks
sudo ./main.py --scan-only

# Only install drivers
sudo ./main.py --install-drivers

# Fix errors
sudo ./main.py --fix-errors
