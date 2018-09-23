pip install -r requirements.txt

sudo npm install castnow -g

sudo apt-get install flite

sudo cp castbot.service /lib/systemd/system/castbot.service

sudo systemctl daemon-reload
sudo systemctl enable castbot.service
sudo systemctl restart castbot.service

sudo cp castbot.service /lib/systemd/system/detector.service

sudo systemctl daemon-reload
sudo systemctl enable detector.service
sudo systemctl restart detector.service
