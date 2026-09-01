# Cocos QA Challenge

Mi entrega del challenge de QA Automation de Cocos: evaluar la calidad de `app-qa` (app de inversiones en React Native) y automatizar la validación, principalmente a nivel de API.

- [`docs/test-plan.md`](docs/test-plan.md): alcance, fuera de alcance, priorización por riesgo, supuestos.
- [`docs/findings.md`](docs/findings.md): 7 bugs encontrados, con repro, esperado vs. obtenido, severidad y evidencia.

## Qué hay en este repo

```
api-tests/          # Suite de API (pytest): instruments, search, orders, portfolio
  clients/            # Cliente HTTP (requests.Session con headers por defecto)
  services/            # Un servicio por dominio (InstrumentsService, OrdersService, PortfolioService)
  schemas/              # Schemas de jsonschema
  assertions/            # Helpers de assert con lógica propia (no wrappers de una línea)
  tests/                  # conftest.py + test_instruments.py, test_orders.py, test_portfolio.py
docs/               # Plan de pruebas y reporte de hallazgos
.github/workflows/   # CI: corre la suite en matrix contra los 4 tiers de bugs
```

## Cómo correr la suite de API

**Prerrequisitos:** Python 3.14.5 (misma versión que uso en CI, para que local y CI se comporten igual).

```bash
cd api-tests
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # ya viene con valores que andan
```

**Correr todo:**
```bash
pytest -v
```

**Correr contra un nivel de bugs específico** (por default usa `off`, el que está en `.env`):
```bash
pytest -v --bugs-tier=easy      # o medium, hard
```
Con `off` la suite debería salir toda en verde (con 5 `skip` y 2 `xfail` esperados, ver más abajo). Con `easy`/`medium`/`hard` van a fallar los tests que exponen los bugs documentados en `findings.md`. Es lo esperado, no un problema de la suite.

**Correr solo un grupo** (con los markers `smoke`/`regression`/`negative`):
```bash
pytest -v -m smoke
```

**Reporte HTML:**
```bash
pytest -v --html=report.html --self-contained-html
```

## Por qué hay tests `skip` y `xfail`

- **5 `skip`**: son casos de LIMIT no determinística (que quede específicamente en `PENDING`, o que resuelva específicamente a `FILLED`/`REJECTED`) que **confirmé empíricamente que no se pueden testear de forma confiable**. Una LIMIT puede resolver en milisegundos, y ni jugando con el precio conseguí controlar el resultado. Cada uno tiene el motivo y la evidencia en el propio `reason` del `skip`. Más detalle en `docs/test-plan.md`.
- **2 `xfail`**: es el Bug 3 (LIMIT acepta `price ≤ 0`). A diferencia de los `skip`, esto sí es un bug real y estable (no depende de timing), así que lo dejo fallar a propósito, documentado, en vez de esconderlo. Uso `xfail(strict=True)` en vez de un assert que falla en rojo porque el `off` es el gate que bloquea merges en CI. Si lo dejara como un fallo común, nunca se podría mergear nada mientras el bug siga ahí.

## Decisiones de diseño (resumen — el detalle está en `test-plan.md`)

- **Client → Service → Schema/Assertions → Tests.** El cliente maneja `X-Enable-Bugs`/`X-Candidate-Id` como headers por defecto de la sesión; cualquier test los puede pisar para casos negativos.
- **`--bugs-tier`**: flag propio de pytest para correr toda la suite contra cualquiera de los 4 niveles sin tocar código ni el `.env`.
- **`reset_state`**: fixture que resetea el estado antes de cada test que crea/modifica órdenes (no en los de solo lectura, no la necesitan).
- **No hardcodeo valores que puedo derivar**: por ejemplo, si compro un instrumento, uso el `instrument_id` que devolvió esa compra en vez de repetir el número a mano en otro lado del test.

## CI/CD

GitHub Actions corre la suite en matrix contra los 4 tiers en cada PR/push a `main`. Solo el tier `off` es un check obligatorio (bloquea el merge si falla). `easy`/`medium`/`hard` corren igual pero de forma informativa, porque se espera que fallen mientras la API tenga los bugs documentados. Cada corrida sube un reporte HTML como artifact.

## UI (Appium)

[completar]
