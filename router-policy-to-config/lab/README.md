# Router Configuration Test Lab

This directory contains a Docker Compose-based test lab for validating router configurations.

## ⚠️ Warning

**This lab is for testing and development purposes only. Do not use these configurations in production networks.**

## Components

- **RouterOS node**: MikroTik CHR in Docker/QEMU (lab use only)
- **OpenWrt node**: OpenWrt in container
- **Test client**: For connectivity and firewall tests

## Requirements

- Docker and Docker Compose
- QEMU (for RouterOS CHR)
- At least 4GB RAM
- 10GB disk space

## Usage

### Starting the Lab

```bash
cd lab
docker-compose up -d
```

### Applying Configurations

**RouterOS:**
```bash
# Copy generated config to RouterOS
docker cp ../routeros-config.rsc lab-routeros:/tmp/
docker exec -it lab-routeros /tool import /tmp/routeros-config.rsc
```

**OpenWrt:**
```bash
# Copy UCI configs
for file in network wireless firewall dhcp; do
  docker cp ../openwrt-config/$file lab-openwrt:/etc/config/
done

# Reload services
docker exec -it lab-openwrt /etc/init.d/network reload
docker exec -it lab-openwrt /etc/init.d/firewall reload
```

### Running Tests

```bash
# From the router-policy-to-config directory
router-policy lab-test policy.yaml
```

Tests include:
- Internet connectivity from LANs
- Guest network isolation
- Firewall rule validation
- VPN connectivity
- DHCP functionality

### Stopping the Lab

```bash
docker-compose down
```

### Cleaning Up

```bash
docker-compose down -v  # Remove volumes
```

## Network Topology

```
         Internet
             |
         [WAN GW]
             |
     ┌───────┴────────┐
     │                │
[RouterOS]      [OpenWrt]
     │                │
 ┌───┴───┐        ┌───┴───┐
 │       │        │       │
LAN   Guest    LAN   Guest
```

## IP Ranges Used

- **Management**: 172.20.0.0/24
- **RouterOS LANs**: 192.168.10.0/24, 192.168.20.0/24
- **OpenWrt LANs**: 192.168.30.0/24, 192.168.40.0/24

## Test Scenarios

Test scenarios are defined in `tests/connectivity_scenarios.yaml` and `tests/firewall_scenarios.yaml`.

Example tests:
- Ping from LAN to internet
- Verify guest cannot reach main LAN
- Check firewall blocks unwanted traffic
- Validate VPN tunnel establishment
- Test DHCP lease assignment

## Obtaining Router Images

### RouterOS CHR

Download from official MikroTik website:
https://mikrotik.com/download

For lab/testing purposes only, subject to MikroTik CHR license.

### OpenWrt

Official OpenWrt downloads:
https://openwrt.org/downloads

Use appropriate images for your architecture.

## Troubleshooting

**Container won't start:**
- Check Docker logs: `docker-compose logs`
- Verify port conflicts: `docker ps`
- Ensure sufficient resources

**Cannot access router:**
- Check network configuration: `docker network ls`
- Verify container is running: `docker ps`
- Check firewall rules on host

**Tests fail:**
- Verify configuration was applied
- Check router logs
- Ensure network connectivity
- Review test expectations

## Security Notes

- Lab configurations use default/weak credentials for testing
- Do not expose lab to untrusted networks
- Reset configurations after testing
- Do not use lab images for production routing

## Contributing

To add new test scenarios:
1. Create scenario YAML in `tests/`
2. Implement test logic
3. Update this README
4. Submit pull request

## Support

- GitHub Issues: https://github.com/ranas-mukminov/russian-smb-devsecops-templates/issues
- Professional Services: https://run-as-daemon.ru
