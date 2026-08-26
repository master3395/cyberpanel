# CyberPanel v3.0.4 fork sync, PR slices, and live upgrade runbook

Last updated: 26/08/2026

This document tracks the fork integration work for `master3395/cyberpanel` against upstream `usmannasir/cyberpanel` v3.0.4, production fixes preserved from 25/08/2026, and focused upstream PR slices derived from PR #1901.

**Repo path:** `/home/Github/cyberPanel-repos/cyberpanel`

---

## Branch map (fork)

| Branch | Base | Purpose |
|--------|------|---------|
| `v3.0.4` | `upstream/v3.0.4` (`24b648f2`) | Exact upstream release tag |
| `v3.0.4-dev` | upstream + slices + live-ops | Your integrated fork dev line (push target for live upgrade) |
| `live-ops-2026-08-25` | `v3.0.4-dev` | Production fixes from 25/08/2026 (5 commits) |
| `slice/v304-parity-firewall-banned` | `v3.0.4-dev` | Banned IPs / blockIP parity from v3.0.2-dev |
| `slice/v304-parity-dashboard-503` | `v3.0.4-dev` | Dashboard poll storm / OLS 503 fix (PR #22) |
| `slice/v304-parity-login-static` | `v3.0.4-dev` | Login static, CSP, webauthn, rehash (PR #21) |
| `slice/v304-parity-snappymail` | `v3.0.4-dev` | SnappyMail OLS vhRoot fix (PR #23) |

**Do not merge PR #1901 wholesale.** Keep it open on upstream as reference only.

**Stashed WIP:** `wip-v255-dev-before-v304-bootstrap-20260826` (mail/sieveGuard/upgrade_modules from old `v2.5.5-dev` checkout). Port only if still needed on v3.

---

## Integration into `v3.0.4-dev` (completed)

Merge order applied on local `v3.0.4-dev`:

1. Upstream `upstream/v3.0.4-dev`
2. Slice merges (firewall, login, dashboard 503, snappymail)
3. `live-ops-2026-08-25` merge

**Conflict resolved:**

| File | Resolution |
|------|------------|
| `baseTemplate/static/baseTemplate/custom-js/system-status.js` | Kept production file combining **poll throttling** (503 slice) and **SSH alert ban + refresh UX** (live-ops). Same content mirrored under `static/baseTemplate/custom-js/system-status.js`. |

**Tip at integration:** `d1b959da` on `origin/v3.0.4-dev`.

---

## Live-ops commits (on `live-ops-2026-08-25`)

1. `fix(firewall): restore blockIP/unblockIP and batch-friendly firewalld reload`
2. `fix(phpmyadmin): accept GET handoff token for databases SSO`
3. `feat(dashboard): SSH alert ban button and refresh analysis UX`
4. `fix(autoban): ban all alert IPs via systemd monitors outside LSCPD`
5. `fix(plugins): restore pluginHolder routes and INSTALLED_APPS`

Includes systemd units:

- `systemd/cyberpanel-autoban.service`
- `systemd/cyberpanel-fail2ban-autoban.service`

---

## Upstream PR slice checklist

Target base for each PR: `usmannasir/cyberpanel` branch **`v3.0.4-dev`**.

| # | Fork branch | Theme | Smoke proof |
|---|-------------|-------|-------------|
| 1 | `slice/v304-parity-firewall-banned` | Firewall banned IPs + blockIP | Ban/unban IP; dashboard manual ban |
| 2 | `slice/v304-parity-dashboard-503` | Dashboard poll / OLS 503 | `/base/` loads; stats endpoints JSON 200 |
| 3 | `slice/v304-parity-login-static` | Login static / CSP / rehash | Login page; `webauthn.js` 200 |
| 4 | `slice/v304-parity-snappymail` | phpMyAdmin / SnappyMail OLS | `/phpmyadmin/`, `/snappymail/` 200 |

**Excluded from upstream PRs (fork-only):**

- `.cursor/plans/*`
- Local planning-only `to-do/` notes unless product-ready
- Snapshot-manager plugin WIP

**Suggested upstream PR title pattern:**

```
fix(firewall): restore banned IP APIs on v3.0.4-dev
```

Each PR body: 3 to 5 bullets, commands run, curl results. No secrets.

**Open draft PR (fork tracking):** `live-ops-2026-08-25` -> `v3.0.4-dev` on `master3395/cyberpanel` (optional).

---

## Pre-maintenance checklist

Run before the live upgrade window.

### 1. Snapshot and backups

- [ ] Contabo snapshot confirmed (snapshot manager or panel snapshot)
- [ ] Live tree tarball exists: `/home/cyberpanel/backups/pre-v304-live-ops/cybercp-live-20260826.tar.gz`
- [ ] Database export:

```bash
mysqldump --single-transaction cyberpanel > /home/cyberpanel/backups/pre-v304-live-ops/cyberpanel-$(date +%Y%m%d).sql
```

- [ ] Copy secrets and state:

```bash
cp -a /usr/local/CyberCP/CyberCP/settings.py /home/cyberpanel/backups/pre-v304-live-ops/settings.py.bak
# Also note: plugin_states, whitelist IPs (51.174.191.240 Kim-PC)
```

### 2. Fork branch ready

```bash
cd /home/Github/cyberPanel-repos/cyberpanel
git fetch origin
git log -1 --oneline origin/v3.0.4-dev
# Expect integrated tip (includes live-ops merge)
```

### 3. Baseline smoke (before upgrade)

```bash
curl -skI https://207.180.193.210:2087/ | head -3
curl -skI https://207.180.193.210:2087/base/ | head -5
curl -skI https://207.180.193.210:2087/phpmyadmin/ | head -3
systemctl is-active lscpd lsws cyberpanel-autoban.service cyberpanel-fail2ban-autoban.service
```

### 4. Whitelist verification

Confirm operator IP **51.174.191.240** is whitelisted and not in firewalld drop rules:

```bash
firewall-cmd --list-all | grep -i 51.174.191.240 || true
```

---

## Maintenance window: live upgrade

**Server:** `207.180.193.210`  
**Target branch:** `v3.0.4-dev`  
**Git user (fork):** `master3395`

### Option A: Modular upgrade script (recommended)

```bash
cd /usr/local/CyberCP
export CYBERPANEL_GIT_USER=master3395
bash cyberpanel_upgrade.sh --branch v3.0.4-dev --debug
```

When prompted for MariaDB, press Enter for default 11.8 LTS unless you need another version.

### Option B: Python upgrade module

```bash
cd /usr/local/CyberCP
export CYBERPANEL_GIT_USER=master3395
/usr/local/CyberCP/bin/python plogical/upgrade.py v3.0.4-dev
```

`upgrade.py` reads `CYBERPANEL_GIT_USER` (defaults to `usmannasir`). Set `master3395` so clone/checkout uses your fork.

---

## Post-upgrade steps

### 1. Restart services

```bash
systemctl restart lscpd lsws
systemctl daemon-reload
systemctl enable --now cyberpanel-autoban.service cyberpanel-fail2ban-autoban.service
systemctl restart cyberpanel-autoban.service cyberpanel-fail2ban-autoban.service
```

### 2. Re-verify plugins if upgrade overwrote trees

If autoban or fail2ban routes fail after upgrade, sync from fork:

```bash
cd /home/Github/cyberPanel-repos/cyberpanel
git archive origin/v3.0.4-dev autoBanSecurityAlerts fail2ban pluginHolder systemd | tar -x -C /tmp/v304-restore
# Copy only if paths differ post-upgrade; prefer git checkout in /usr/local/CyberCP if it is a git clone
```

Check `CyberCP/settings.py` for `autoBanSecurityAlerts` and `fail2ban` in `INSTALLED_APPS`, and `pluginHolder/urls.py` routes.

### 3. Smoke tests

```bash
curl -skI https://207.180.193.210:2087/ | head -3
curl -skI https://207.180.193.210:2087/base/ | head -5
curl -skI https://207.180.193.210:2087/phpmyadmin/ | head -3
curl -skI https://207.180.193.210:2087/snappymail/ | head -3
```

Panel Version Management should show branch `v3.0.4-dev` and fork repo when using `CYBERPANEL_GIT_USER=master3395`.

### 4. Version alignment

After successful cutover, confirm:

```bash
grep -E 'VERSION|BUILD' /usr/local/CyberCP/version.txt /usr/local/CyberCP/cyberpanel_version.py 2>/dev/null
```

Expect v3.0.4 lineage (not stale `2.5.5` marker).

### 5. Auto-ban sanity

- Trigger or wait for security alert cycle
- Confirm **all** alert IPs can be banned (not only Top IP)
- Confirm LSCPD workers stay healthy (`systemctl status lscpd`; no long `WAITQUE_DEPTH` backlog)

---

## Rollback

**Fastest:** Restore Contabo snapshot from before maintenance.

**Git tree rollback:**

```bash
# Restore from tarball
tar -xzf /home/cyberpanel/backups/pre-v304-live-ops/cybercp-live-20260826.tar.gz -C /
systemctl restart lscpd lsws
systemctl restart cyberpanel-autoban.service cyberpanel-fail2ban-autoban.service
```

**Database rollback:** Re-import mysqldump taken in pre-checks if schema/data changed.

---

## Pre-flight validation log (26/08/2026)

Automated checks run during repo integration (upgrade **not** executed; deferred to maintenance window per plan):

| Check | Result |
|-------|--------|
| `origin/v3.0.4-dev` pushed | OK (`d1b959da`) |
| Live tarball backup | OK (`cybercp-live-20260826.tar.gz`) |
| `lscpd`, `lsws` active | OK |
| `cyberpanel-autoban.service` active | OK |
| `cyberpanel-fail2ban-autoban.service` active | OK |
| `curl https://207.180.193.210:2087/base/` | OK (HTTP 302) |
| Kim-PC IP whitelist | Verify in firewall before/after upgrade |

**Execute the maintenance window section above when you schedule production cutover.**

---

## Risks

| Risk | Mitigation |
|------|------------|
| PR #1901 is thousands of commits behind v3.0.4 | Cherry-pick by topic only; slice branches |
| Live hybrid (2.5.5 marker + v3 files) | Treat as major upgrade; snapshot first |
| Auto-ban in LSCPD workers | Keep systemd monitor design from live-ops |
| Upgrade overwrites `INSTALLED_APPS` / urls | Re-apply from `live-ops` commits |
| Large upstream PRs rejected | One behavior per upstream PR |

---

## Quick reference commands

```bash
# Fetch fork branches
cd /home/Github/cyberPanel-repos/cyberpanel
git fetch origin upstream

# Show integration tip
git log -1 --oneline origin/v3.0.4-dev

# List slice branches
git branch -a | grep slice/v304

# Upgrade (maintenance window only)
export CYBERPANEL_GIT_USER=master3395
bash /usr/local/CyberCP/cyberpanel_upgrade.sh --branch v3.0.4-dev --debug
```

---

## Live upgrade executed (26/08/2026 22:46 CEST)

**Command used:**
```bash
bash /usr/local/CyberCP/cyberpanel_upgrade.sh \
  --branch v3.0.4-dev --repo master3395 \
  --mariadb-version 12.3 --no-backup-db --no-system-update --debug
```

**First attempt:** failed on 28GB `/var/lib/mysql` tarball (`--backup-db`). Use `--no-backup-db` when a recent `mysqldump` exists.

**Post-upgrade hotfixes applied on server:**
- `baseTemplate/models.py`: `UserNotificationPreferences` model (views imported it; table existed)
- `firewall/ruleOrder.py`: from v3.0.2-dev-fork (slice referenced it but file was missing)
- `pluginHolder/`: full views from v3.0.2-dev-fork + live-ops `urls.py`
- `CyberCP/originDedupeMiddleware.py`: required by `MIDDLEWARE` in settings
- `phpmyadmin/index.php`: restored from `CyberCPBak`
- `bin/lswsgi`: installed from build tree / backup

**Verified after restart:**
- `https://207.180.193.210:2087/` HTTP 200 (login)
- `/base/` HTTP 302
- Git tip: `46f9ba8a` + hotfix commit
- `cyberpanel_version.py`: VERSION 3.0, BUILD 4
