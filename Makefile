VENV     := $(shell [ -f tools/.venv/bin/python ] && echo "tools/.venv/bin/python" || echo "python3")
TOOLS     = tools
SCRIPTS   = scripts

.PHONY: setup install-hooks validate export-rdf export-graph
.PHONY: check-enrichment query-rdf fetch-wettenbank lock clean ci webapp

setup:
	@echo "Maak virtual environment aan..."
	@python3 -m venv tools/.venv
	@tools/.venv/bin/pip install -r requirements.lock
	@$(MAKE) install-hooks
	@echo "Setup voltooid: .venv + deps + pre-commit hook"

install-hooks:
	@echo "Installeer pre-commit hook..."
	@ln -sf ../../$(SCRIPTS)/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Done. Hook geïnstalleerd in .git/hooks/pre-commit"

validate:
	@$(VENV) $(TOOLS)/validate_note.py --full
	@echo "Exit code: $$?"

export-rdf:
	@$(VENV) $(TOOLS)/export_rdf.py

export-graph:
	@$(VENV) $(TOOLS)/export_graph.py

webapp:
	@$(VENV) $(TOOLS)/generate_webapp.py

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
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Opschoning voltooid"

ci: validate export-rdf export-graph check-enrichment
	@echo "CI-checks passed"
