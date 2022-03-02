#!/bin/sh
# Check statuses
service tor status
service privoxy status

# Configure tor
echo "ControlPort 9051" >> /etc/tor/torrc
echo "CookieAuthentication 0" >> /etc/tor/torrc
echo HashedControlPassword $(tor --hash-password "password" | tail -n 1) >> /etc/tor/torrc
tail -n 3 /etc/tor/torrc

# Start tor
service tor start
sleep 5
service tor status
sleep 5

# Configure privoxy
echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
sed -i "s/.*\[::1\]:8118/# &/" /etc/privoxy/config

# Start privoxy
service privoxy start
sleep 5
service privoxy status
sleep 5

# Launch script
python3 -u main.py