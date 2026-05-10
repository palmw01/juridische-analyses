VENV      = tools/.venv/bin/python
TOOLS     = tools
SCRIPTS   = scripts

.PHONY: install-hooks validate views export-rdf pdf-graph lock ci

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

lock:
	@$(VENV) -m pip freeze > requirements.lock
	@echo "requirements.lock bijgewerkt"

ci: validate views
	@echo "CI-checks passed"
