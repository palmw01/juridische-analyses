VENV      = tools/.venv/bin/python
TOOLS     = tools
SCRIPTS   = scripts

.PHONY: setup install-hooks validate views export-rdf pdf-graph check-enrichment query-rdf fetch-wettenbank lock clean ci

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

views:
	@$(VENV) $(TOOLS)/generate_views.py

export-rdf:
	@$(VENV) $(TOOLS)/export_rdf.py

pdf-graph: export-rdf
	@$(VENV) $(TOOLS)/generate_pdf_graph.py
	@echo "PDF-graaf gegenereerd in kennisgraaf/juridisch_kennismodel.pdf"

check-enrichment:
	@$(VENV) $(TOOLS)/check_enrichment.py

query-rdf:
	@$(VENV) $(TOOLS)/query_rdf.py

fetch-wettenbank:
	@echo "Gebruik: $(VENV) $(TOOLS)/fetch_wettenbank.py --input <bestand> --vault-root ."

lock:
	@tools/.venv/bin/pip install -r requirements.lock
	@tools/.venv/bin/pip freeze > requirements.lock
	@echo "requirements.lock bijgewerkt (geinstalleerd + gefreeze)"

clean:
	@rm -rf views/
	@rm -f kennisgraaf/*.dot kennisgraaf/*.pdf kennisgraaf/*.ttl kennisgraaf/*.gexf kennisgraaf/*.graphml
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "Opschoning voltooid"

ci: validate views
	@echo "CI-checks passed"
