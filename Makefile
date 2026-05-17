VENV     := $(shell [ -f tools/.venv/bin/python ] && echo "tools/.venv/bin/python" || echo "python3")
TOOLS     = tools
SCRIPTS   = scripts

.PHONY: setup install-hooks validate export-rdf export-graph
.PHONY: check-enrichment query-rdf fetch-wettenbank lock clean ci webapp test test-fast test-cov test-e2e lint lint-fix

setup:
	@echo "Maak virtual environment aan..."
	@python3 -m venv tools/.venv
	@tools/.venv/bin/pip install -r requirements.lock
	@echo "Installeer Node.js dependencies voor SPARQL-bundle..."
	@cd sitegen/scripts && npm install --silent 2>&1 | tail -1
	@$(MAKE) install-hooks
	@echo "Setup voltooid: .venv + deps + npm + pre-commit hook"

install-hooks:
	@echo "Installeer pre-commit en pre-push hooks..."
	@ln -sf ../../$(SCRIPTS)/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@ln -sf ../../$(SCRIPTS)/pre-push .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "Done. Hooks geïnstalleerd in .git/hooks/"

validate:
	@$(VENV) $(TOOLS)/validate_note.py --full
	@echo "Exit code: $$?"

export-rdf:
	@$(VENV) $(TOOLS)/export_rdf.py

export-graph:
	@$(VENV) $(TOOLS)/export_graph.py

.build/comunica.min.js: sitegen/scripts/bundle-comunica.js sitegen/scripts/package.json
	@echo "Bundel Comunica SPARQL-engine voor browser..."
	@mkdir -p .build
	@cd sitegen/scripts && npm install --silent 2>&1 | tail -1 && \
	 npx esbuild --bundle --platform=browser --minify \
	   --outfile=../../.build/comunica.min.js \
	   bundle-comunica.js 2>&1 | grep -v "^npm" || \
	 (echo "Waarschuwing: kon Comunica niet bundelen (npx/node nodig). SPARQL werkt alleen met CDN." && \
	   touch ../../.build/comunica.min.js)

webapp: export-rdf .build/comunica.min.js
	@$(VENV) -m sitegen $(if $(OUT),--out $(OUT),)

check-enrichment:
	@$(VENV) $(TOOLS)/check_enrichment.py || true

query-rdf:
	@$(VENV) $(TOOLS)/query_rdf.py $(ARGS)

fetch-wettenbank:
	@echo "Gebruik: $(VENV) $(TOOLS)/fetch_wettenbank.py --input <bestand> --project-dir ."

lock:
	@tools/.venv/bin/pip install -r requirements.lock
	@tools/.venv/bin/pip freeze > requirements.lock
	@echo "requirements.lock bijgewerkt (geinstalleerd + gefreeze)"

clean:
	@rm -rf webapp/
	@rm -f kennisgraaf/*.dot kennisgraaf/*.ttl kennisgraaf/*.gexf kennisgraaf/*.graphml
	@rm -rf .build/
	@rm -f sitegen/static/comunica.min.js
	@rm -rf sitegen/scripts/node_modules sitegen/scripts/package-lock.json
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Opschoning voltooid"

test:
	@$(VENV) -m pytest tests/ -m "not e2e" -q; ret=$$?; [ $$ret -eq 0 ] || [ $$ret -eq 5 ]

test-fast:
	@$(VENV) -m pytest tests/unit/ -q -x; ret=$$?; [ $$ret -eq 0 ] || [ $$ret -eq 5 ]

test-cov:
	@$(VENV) -m pytest tests/ -m "not e2e" --cov --cov-report=term-missing; ret=$$?; [ $$ret -eq 0 ] || [ $$ret -eq 5 ]

test-e2e:
	@$(VENV) -m pytest tests/e2e/ -q; ret=$$?; [ $$ret -eq 0 ] || [ $$ret -eq 5 ]

lint:
	@tools/.venv/bin/ruff check sitegen/ tools/

lint-fix:
	@tools/.venv/bin/ruff check sitegen/ tools/ --fix

ci: test validate export-rdf export-graph check-enrichment
	@echo "CI-checks passed"
