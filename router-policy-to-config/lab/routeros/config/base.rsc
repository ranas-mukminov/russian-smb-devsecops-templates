# RouterOS base configuration for lab
# Safe, minimal defaults for testing

/system identity set name="RouterOS-Lab"

# Enable API for testing
/ip service set api address=172.20.0.0/24

# Basic admin access (lab only!)
/user set admin password="lab-test-password"

# Enable SSH
/ip service enable ssh
/ip service set ssh port=22

# Time and NTP
/system clock set time-zone-name=UTC
/system ntp client set enabled=yes
/system ntp client servers add address=pool.ntp.org

# Logging
/system logging add topics=info action=memory

# Note: This is a base configuration for the lab.
# Generated policy configurations will be imported on top of this.
