# Skill: /quartz

**Trigger:** `/quartz`

Publiceert de vault als statische website via GitHub Pages. Elke push naar `main` triggert automatisch een nieuwe deploy.

---

## Architectuur

```
juridische-analyses/ (vault, git-repo)
    ↓ push naar main
GitHub Actions (.github/workflows/deploy-quartz.yml)
    ↓ git clone quartz + vault → npx quartz build → upload artifact
GitHub Pages
    ↓
https://palmw01.github.io/juridische-analyses
```

---

## Gebruik

### Content bijwerken

Gewoon pushen naar `main` — de site is binnen ~30 seconden bijgewerkt. Geen verdere actie nodig.

### Quartz-configuratie aanpassen

De configuratie wordt tijdens de build gepatchet in `.github/workflows/deploy-quartz.yml` (stap "Patch quartz.config.ts"). Relevante velden:

- `pageTitle` — paginatitel
- `baseUrl` — `palmw01.github.io/juridische-analyses`
- `locale` — `nl-NL`
- `ignorePatterns` — bestanden die niet gepubliceerd worden

Na wijziging: commit + push → automatische deploy.

---

## Bestanden

| Bestand | Functie |
|---------|---------|
| `juridische-analyses/.github/workflows/deploy-quartz.yml` | Build + deploy naar GitHub Pages |
