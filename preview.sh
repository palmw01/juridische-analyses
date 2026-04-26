#!/usr/bin/env bash
# Lokale Quartz-preview — spiegelt deploy-quartz.yml maar voor localhost
set -e

VAULT="$(cd "$(dirname "$0")" && pwd)"
WORKDIR="/tmp/quartz-preview"

echo "==> Vault: $VAULT"
echo "==> Werkmap: $WORKDIR"

# Quartz klonen of bijwerken
if [ -d "$WORKDIR/quartz/.git" ]; then
  echo "==> Quartz al aanwezig, bijwerken..."
  git -C "$WORKDIR/quartz" pull --ff-only --quiet
else
  echo "==> Quartz klonen..."
  mkdir -p "$WORKDIR"
  git clone --depth=1 https://github.com/jackyzha0/quartz.git "$WORKDIR/quartz"
fi

cd "$WORKDIR/quartz"

# Dependencies installeren (alleen als nodig)
if [ ! -d node_modules ]; then
  echo "==> npm ci..."
  npm ci --silent
fi

# Vault-inhoud kopiëren
echo "==> Vault kopiëren..."
rm -rf content
cp -r "$VAULT" content

# quartz.config.ts patchen (localhost-variant)
echo "==> quartz.config.ts patchen..."
node -e "
  const fs = require('fs');
  let c = fs.readFileSync('./quartz.config.ts', 'utf8');
  c = c.replace(/pageTitle: \x22[^\x22]*\x22/, 'pageTitle: \x22Juridische wetsanalyse — Inning\x22');
  c = c.replace(/baseUrl: \x22[^\x22]*\x22/, 'baseUrl: \x22localhost:8080\x22');
  c = c.replace(/locale: \x22[^\x22]*\x22/, 'locale: \x22nl-NL\x22');
  c = c.replace(/ignorePatterns: \[[\s\S]*?\]/,
    'ignorePatterns: [\x22.obsidian\x22,\x22.claude\x22,\x22.git\x22,\x22.trash\x22,\x22README.md\x22,\x22CLAUDE.md\x22,\x22settings.json\x22,\x22**/template.md\x22]');
  fs.writeFileSync('./quartz.config.ts', c);
"

# quartz.layout.ts patchen
echo "==> quartz.layout.ts patchen..."
python3 << 'PYEOF'
import re

with open('./quartz.layout.ts', 'r') as f:
    c = f.read()

c = re.sub(
    r'Component\.Graph\(\)',
    '''Component.Graph({
  localGraph: {
    showTags: false,
    depth: 2,
    scale: 1.1,
    repelForce: 5,
  },
  globalGraph: {
    showTags: false,
    depth: -1,
    scale: 0.9,
    repelForce: 2,
  },
})''',
    c
)

c = c.replace(
    'Component.Backlinks(),',
    'Component.Backlinks(),\n    Component.RecentNotes({ title: "Recent toegevoegd", limit: 5 }),',
    1
)

with open('./quartz.layout.ts', 'w') as f:
    f.write(c)

print("quartz.layout.ts gepatcht")
PYEOF

# Aangepaste CSS injecteren
echo "==> CSS injecteren..."
python3 << 'PYEOF'
css = """
/* Juridische wetsanalyse — aangepaste stijlen */

blockquote {
  border-left: 3px solid var(--secondary) !important;
  background: var(--highlight);
  padding: 0.5em 1em;
  border-radius: 0 4px 4px 0;
  font-style: normal !important;
}

table {
  font-size: 0.88em;
}

#graph-container {
  border-radius: 6px;
  overflow: hidden;
}

.toc ul {
  font-size: 0.85em;
}
"""

with open('./quartz/styles/custom.scss', 'w') as f:
    f.write(css)

print("custom.scss geschreven")
PYEOF

# Bouwen
echo "==> Quartz bouwen..."
npx quartz build 2>&1

# JAS-graaf-script injecteren (lokaal pad)
echo "==> JAS-graaf-script injecteren..."
python3 << 'PYEOF'
import os

js = r"""(function () {
  'use strict';

  var JAS_KLEUREN = {
    'jas/rechtsbetrekking': '#FF0000',
    'jas/rechtssubject': '#4472C4',
    'jas/rechtsobject': '#70AD47',
    'jas/rechtsfeit': '#FFC000',
    'jas/voorwaarde': '#7030A0',
    'jas/afleidingsregel': '#00B0F0',
    'jas/variabele': '#92D050',
    'jas/parameter': '#FFD966',
    'jas/tijdsaanduiding': '#F4B942',
    'jas/plaatsaanduiding': '#9DC3E6',
    'jas/delegatiebevoegdheid': '#C9C9C9',
    'jas/brondefinitie': '#D6B4C8',
    'jas/operator': '#808080'
  };

  var TYPE_KLEUREN = {
    'annotatie': '#E8EAF6',
    'begrip':    '#F0F4FF',
    'afleidingsregel': '#E0F7FA'
  };

  var kleurMap    = {};
  var dataGeladen = false;

  async function laadData() {
    try {
      var resp = await fetch('/static/contentIndex.json');
      if (!resp.ok) return;
      var data = await resp.json();

      for (var slug in data) {
        var pagina = data[slug];
        var tags = (pagina.tags || []).map(function (t) { return t.toLowerCase(); });
        var kleur = null;

        for (var i = 0; i < tags.length; i++) {
          if (JAS_KLEUREN[tags[i]]) { kleur = JAS_KLEUREN[tags[i]]; break; }
        }
        if (!kleur) {
          for (var i = 0; i < tags.length; i++) {
            if (TYPE_KLEUREN[tags[i]]) { kleur = TYPE_KLEUREN[tags[i]]; break; }
          }
        }

        if (kleur) kleurMap[slug] = kleur;
      }

      dataGeladen = true;
      kleurKnooppunten();
    } catch (e) {}
  }

  function kleurKnooppunten() {
    if (!dataGeladen) return;
    document.querySelectorAll('svg .node').forEach(function (g) {
      var d = g.__data__;
      if (!d || !d.id) return;
      var kleur = kleurMap[d.id];
      if (!kleur) return;
      var cirkel = g.querySelector('circle');
      if (cirkel) cirkel.style.setProperty('fill', kleur, 'important');
    });
  }

  laadData();

  document.addEventListener('nav', function () {
    setTimeout(kleurKnooppunten, 400);
    setTimeout(kleurKnooppunten, 1200);
  });

  var obs = new MutationObserver(function () {
    if (dataGeladen) kleurKnooppunten();
  });
  obs.observe(document.body, { childList: true, subtree: true, attributes: false });
})();
"""

with open('./public/jas-graph.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Lokaal pad: /jas-graph.js (geen subpad voor localhost)
script_tag = '<script src="/jas-graph.js" defer></script>'
count = 0
for root, dirs, files in os.walk('./public'):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            c = f.read()
        if 'jas-graph.js' not in c:
            c = c.replace('</head>', script_tag + '</head>', 1)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(c)
            count += 1

print(f'JAS-graaf-script geïnjecteerd in {count} HTML-bestanden')
PYEOF

echo ""
echo "======================================"
echo "  Preview klaar: http://localhost:8080"
echo "======================================"
echo ""
echo "  Druk op Ctrl+C om te stoppen."
echo ""

# Serveer de gebouwde site
npx quartz build --serve --port 8080
