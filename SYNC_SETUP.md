# CORTEX-CI Automated Sync Setup

## Daily Sanctions Data Sync

The `sync_sanctions.py` script automatically:
1. Downloads latest data from OFAC, UN, and other sources
2. Compares file hashes to detect changes
3. Imports new/updated entities
4. Logs sync activity

## Setup Options

### Option 1: Cron Job (Recommended)

Add to crontab (`crontab -e`):

```bash
# Run daily at 6 AM UTC
0 6 * * * /usr/bin/python3 /root/cortex-ci/backend/sync_sanctions.py >> /var/log/cortex-sync.log 2>&1
```

### Option 2: Systemd Timer

Create `/etc/systemd/system/cortex-sync.service`:

```ini
[Unit]
Description=CORTEX-CI Sanctions Data Sync
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /root/cortex-ci/backend/sync_sanctions.py
WorkingDirectory=/root/cortex-ci/backend
StandardOutput=append:/var/log/cortex-sync.log
StandardError=append:/var/log/cortex-sync.log

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/cortex-sync.timer`:

```ini
[Unit]
Description=Daily CORTEX-CI Sync Timer

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable cortex-sync.timer
sudo systemctl start cortex-sync.timer
```

### Option 3: Docker-based (for Dokploy)

Add to `docker-compose.yml`:

```yaml
  sync:
    build:
      context: ./backend
    command: >
      sh -c "while true; do
        python sync_sanctions.py;
        sleep 86400;
      done"
    depends_on:
      - db
    restart: unless-stopped
```

## Manual Sync

Run manually:
```bash
cd /root/cortex-ci/backend
python3 sync_sanctions.py
```

## Monitoring

Check sync status via API:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://cortex.alexandratechlab.com/api/v1/dashboard/sync-status
```

## Data Sources

| Source | URL | Update Frequency |
|--------|-----|------------------|
| OFAC SDN | https://www.treasury.gov/ofac/downloads/sdn.xml | Daily |
| OFAC Consolidated | https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml | Daily |
| UN Sanctions | https://scsanctions.un.org/resources/xml/en/consolidated.xml | Weekly |

## Logs

Sync logs are stored in:
- `/root/cortex-ci/data/sanctions/sync_log.json` - JSON history
- `/var/log/cortex-sync.log` - Console output (if using cron/systemd)
