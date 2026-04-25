# Skill: /quartz

**Trigger:** `/quartz`

Beheert de Quartz-publicatiesite van de vault. Quartz draait als Docker-container op Portainer en serveert de vault-inhoud als statische website op poort 8080.

---

## Architectuur

```
juridische-analyses/ (vault, git-repo)
    ↓ volume mount op NAS
/volume1/docker/quartz/content/
    ↓
quartz-site container (ghcr.io/palmw01/wetten-overheid-tools-quartz:latest)
    ↓ npx quartz build --serve
http://<host>:8080
```

De container leest `content/` als read-only bron en bouwt bij elke bestandswijziging opnieuw. Het is de vault die de content levert — de container is alleen de bouwer en server.

---

## Gebruik

### Content bijwerken

Quartz leest vanuit het volume mount. Wijzigingen in de vault zijn direct zichtbaar als de vault-directory gesynct is naar `/volume1/docker/quartz/content/` op de Portainer-host.

Syncoptions:
- **Synology Drive**: automatische sync van lokale vault naar NAS-pad
- **Git pull script**: cron-job op de NAS die `git pull` uitvoert op de geklonede vault

### Container herstarten (na config-wijziging)

```bash
# Via Portainer UI: Containers → quartz-site → Restart
# Of via docker CLI op de NAS:
docker restart quartz-site
```

### Nieuwe image deployen (na push naar GitHub)

1. GitHub Actions bouwt automatisch een nieuwe image op push naar `main`
2. In Portainer: Containers → quartz-site → Recreate → "Pull latest image"

### quartz.config.ts aanpassen

Bestand: `wetten-overheid-tools/quartz-site/quartz.config.ts`

Relevante velden:
- `pageTitle` — paginatitel
- `baseUrl` — URL of IP van de Portainer-host (bijv. `192.168.1.x:8080`)
- `ignorePatterns` — bestanden die niet gepubliceerd worden

Na wijziging: commit + push → GitHub Actions bouwt nieuwe image → Portainer recreate.

---

## Portainer-configuratie (referentie)

| Instelling | Waarde |
|-----------|--------|
| Image | `ghcr.io/palmw01/wetten-overheid-tools-quartz:latest` |
| Container naam | `quartz-site` |
| Poort | `8080:8080` |
| Volume content | `/volume1/docker/quartz/content:/app/content` |
| Volume logs | `/volume1/docker/quartz/logs:/app/logs` |
| Network | `homeinfra_internal` |
| Restart | `unless-stopped` |
| TZ | `Europe/Amsterdam` |

---

## Bestanden

| Bestand | Functie |
|---------|---------|
| `wetten-overheid-tools/quartz-site/Dockerfile` | Multi-stage build |
| `wetten-overheid-tools/quartz-site/quartz.config.ts` | Site-configuratie |
| `wetten-overheid-tools/docker-compose.yml` | Service-definitie |
| `wetten-overheid-tools/.github/workflows/deploy.yml` | CI/CD pipeline |
