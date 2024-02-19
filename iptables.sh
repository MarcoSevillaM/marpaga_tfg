#!/bin/bash
#iptables -P INPUT DROP
#iptables -P FORWARD DROP
#iptables -P OUTPUT DROP
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -i eth0 -p udp --dport 1194 -j ACCEPT
iptables -A OUTPUT -o eth0 -p udp --dport 1194 -j ACCEPT
iptables -A INPUT -i eth0 -s 192.168.144.4 -d 10.8.0.2 -p udp --dport 1194 -j ACCEPT
iptables -A OUTPUT -o eth0 -s 10.8.0.2 -d 192.168.144.4 -p udp --sport 1194 -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT


