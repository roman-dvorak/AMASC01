#!/bin/bash
# Restart thermal control service

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Restarting thermal-control.service..."
sudo systemctl restart thermal-control.service

echo "Waiting for service to start..."
sleep 2

echo ""
echo "Service status:"
sudo systemctl status thermal-control.service --no-pager -l

echo ""
echo "Recent logs:"
sudo journalctl -u thermal-control.service -n 5 --no-pager
