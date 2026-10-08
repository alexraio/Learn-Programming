## 📋 Descrizione della Pull Request
<!-- Descrivi sinteticamente il motivo della modifica e cosa è stato implementato -->

### 🔗 Issue Correlata
Closes #<!-- numero issue o id bug, es. #101 -->

---

## 🛠️ Tipologia di Modifica
- [ ] 🌟 `feat`: Nuova funzionalità
- [ ] 🐛 `fix`: Correzione di un bug
- [ ] 🧪 `test`: Aggiunta o miglioramento della suite di test
- [ ] ♻️ `refactor`: Modifica architetturale senza impatto funzionale
- [ ] 📝 `docs`: Aggiornamento della documentazione o diario
- [ ] ⚙️ `ci`: Aggiornamento della pipeline GitHub Actions o tooling

---

## 🛡️ Checklist di Autovalutazione & Qualità
- [ ] Il codice rispetta le regole in `.agents/rules/coding_standards.md`.
- [ ] Ho eseguito il linter e il formatter (`uv run ruff check .` e `uv run ruff format .`) con 0 errori.
- [ ] Ho eseguito il type checker (`uv run mypy src tests`) con 0 errori.
- [ ] Tutti i test esistenti passano localmente (`uv run pytest`).
- [ ] (Se bugfix) Ho aggiunto un test di regressione dedicato in `tests/regression/`.
- [ ] La copertura dei test rispetta la soglia minima ($\ge 80\%$).
- [ ] Ho aggiornato il diario di bordo `JOURNAL.md` con l'avanzamento della sessione.
