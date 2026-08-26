# Docker panel image security baseline

Last updated: 27/08/2026

Scope: [`master3395/cyberpanel`](https://hub.docker.com/r/master3395/cyberpanel) panel images built from [`docker/panel/`](../docker/panel/).

## Baseline before hardening (26/08/2026 Scout)

Docker Scout counts on Hub (Critical / High / Medium / Low / Unknown):

| Tag | C | H | M | L | U | Total | Notes |
|-----|---|---|---|---|---|-------|-------|
| almalinux10 / latest | 0 | 0 | 0 | 0 | 0 | 0 | Recommended default |
| openeuler2203 | 0 | 0 | 0 | 0 | 0 | 0 | Recommended |
| ubuntu2404 | 0 | 0 | 10 | 8 | 0 | 18 | Recommended |
| ubuntu2204 | 0 | 0 | 11 | 16 | 0 | 27 | OK |
| openeuler2003 | 0 | 4 | 7 | 1 | 0 | 12 | Legacy |
| almalinux8 | 0 | 11 | 12 | 3 | 0 | 26 | Legacy EL8 |
| almalinux9 | 0 | 7 | 17 | 3 | 0 | 27 | Moderate |
| centos-stream9 | 1 | 31 | 36 | 23 | 4 | 95 | Critical sqlite |
| rhel8 | 1 | 38 | 51 | 11 | 1 | 102 | Critical in base OS |
| rhel9 | 1 | 38 | 45 | 21 | 1 | 106 | Critical in base OS |
| debian13 | 2 | 2 | 4 | 61 | 3 | 72 | 2 critical |
| debian12 | 2 | 9 | 19 | 79 | 22 | 131 | 2 critical |
| rockylinux8 | 0 | 66 | 9 | 79 | 0 | 154 | Legacy EL8 |
| debian11 | 3 | 11 | 18 | 94 | 24 | 150 | Critical perl CVEs |
| rockylinux9 | 0 | 95 | 12 | 94 | 0 | 201 | Worst high count (openssl) |

Sample packages (not CyberPanel app code): sqlite, glibc, openssl, perl, xz, vim.

## Remediation implemented (v3.0.4-dev)

| Control | Location |
|---------|----------|
| OS security update during build | [`docker/panel/Dockerfile`](../docker/panel/Dockerfile) |
| Remove bootstrap `openssh-server` | Same (installer installs on first boot) |
| Optional base digest pins | [`docker/panel/os-matrix.json`](../docker/panel/os-matrix.json) |
| Digest refresh scripts | `refresh-base-digests.sh`, `refresh-base-digests.ps1` |
| Trivy scan + policy gate | [`.github/workflows/docker-panel.yml`](../.github/workflows/docker-panel.yml) |
| Weekly rebuild cron | Same workflow (`0 4 * * 1` UTC) |
| Policy script | [`docker/panel/check-trivy-policy.sh`](../docker/panel/check-trivy-policy.sh) |

### CI policy

- **Critical = 0** on every tag (build fails otherwise)
- **High <= 25** on recommended tags: `almalinux10`, `ubuntu2404`, `debian13`, `openeuler2203`
- Legacy tags may still report high counts until distro fixes land; monitor Scout and rebuild weekly

## After rebuild checklist

1. Open [Docker Hub tags](https://hub.docker.com/r/master3395/cyberpanel/tags) and compare Scout counts to this table
2. Confirm **Critical = 0** on all tags
3. Run `Test/docker/up.ps1 smoke-full` on `almalinux10`
4. Update the "Baseline before hardening" table above with new counts and date

## Residual risk (cannot eliminate)

| Risk | Mitigation |
|------|------------|
| `--privileged` systemd container | Isolate on dedicated host/VLAN; restrict network exposure |
| Nested Docker in container | Limit who can run containers; firewall egress |
| CVEs with no distro fix yet | Weekly rebuild + Scout alerts; document unfixed upstream |
| Full mail/FTP/DNS ports | Use `CYBERPANEL_MINIMAL=1` when services not needed |
| First-boot installer adds packages | Runtime `dnf update` in installer helps after boot; image rebuild keeps Hub layers current |

## Operator links

- [Docker Scout report](https://scout.docker.com/reports/org/master3395/images/host/hub.docker.com/repo/master3395%2Fcyberpanel)
- [Panel operator guide](DOCKER-PANEL.md)
