#!/bin/sh
cp sensor-daemon.service /etc/systemd/system/sensor-daemon.service
cp sensor-webapp.service /etc/systemd/system/sensor-webapp.service
cp sensor-sender.service /etc/systemd/system/sensor-sender.service

systemctl enable sensor-daemon
systemctl enable sensor-webapp
systemctl enable sensor-sender
systemctl start sensor-daemon
systemctl start sensor-webapp
systemctl start sensor-sender