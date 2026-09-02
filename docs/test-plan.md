# Plan de pruebas — Cocos QA Challenge

## Alcance

Decidí automatizar principalmente a **nivel de API** (~80% del esfuerzo) contra `https://dummy-api-topaz.vercel.app`, y dejar una capa chica de UI sobre `app-qa` (Appium) solo para los flujos más críticos (~20%).

**¿Por qué así?** la lógica de negocio con más riesgo real está en la API, no en el front. Además los tests de API son mucho más rápidos y no sufren la flakiness típica de UI, así que con el tiempo que tenía, opté por cubrir más casos límite ahí.

**Endpoints con suite automatizada (pytest):**
- `GET /instruments`
- `GET /search`
- `GET /portfolio`
- `GET /orders` y `POST /orders`

`POST /reset` lo usé como herramienta para aislar los tests entre sí, no lo testeo como feature de negocio (revisar "Fuera de alcance").

**Cuánto cubrí, en números** (64 tests de API + 12 de UI):

**API:**
- `GET /instruments` + `GET /search`: 26 tests, schema, unicidad de datos, headers (positivos y negativos), case-insensitivity, que `/search` coincida con `/instruments`, casos borde de búsqueda (parcial, vacío, sin resultados).
- `POST/GET /orders`: 27 tests, happy path de MARKET y LIMIT, validaciones de campos (parametrizadas), reglas de negocio (`Insufficient cash/shares`), headers, y 5 casos que quedaron marcados `skip` por un problema de no-determinismo que explico abajo.
- `GET /portfolio`: 11 tests, schema del holding, qué pasa con `cash`/`holdings` al comprar y vender (parcial y total), cálculo de `avg_cost_price`, que el valor de mercado sea calculable, headers.

**UI:**
- **Mercados** (4): que la pantalla cargue bien, que tocar la primera acción navegue al detalle, que "Operar ahora" abra el ticket de orden, y que el botón de volver desde el detalle te deje de nuevo en la home de Mercados.
- **Buscar** (2): que la pantalla cargue bien y que buscar un ticker devuelva el resultado esperado.
- **Órdenes** (3): que la pantalla cargue bien, que una compra por MARKET aparezca en el historial, y que enviar sin cantidad muestre el mensaje de validación.
- **Portafolio** (3): que la pantalla cargue bien, que una compra se refleje como holding, y el empty state cuando no hay posiciones.

**Cómo armé la suite:**

**API:**
- Capas: cliente HTTP → servicio de dominio → schemas/assertions → tests, todo en `api-tests/`.
- Los headers `X-Enable-Bugs`/`X-Candidate-Id` van por default en el cliente, y cualquier test los puede pisar para probar casos negativos.
- `reset_state` solo corre en los tests que crean o modifican datos (compran, venden); los de solo lectura no lo necesitan.
- Agregué un flag propio (`--bugs-tier`) para poder correr toda la suite contra cualquiera de los 4 niveles de bugs sin tocar código.
- En CI (GitHub Actions) corro la suite contra los 4 tiers en cada PR/push a `main`, pero solo dejé que `off` bloquee el merge. `easy`/`medium`/`hard` corren igual, pero informativamente, porque ya sé que van a fallar mientras la API tenga los bugs que encontré (revisar `findings.md`).
- Cada corrida de CI sube un reporte HTML (`pytest-html`) como artifact.

**UI:**
- Mismo criterio que la API: un archivo de test por pantalla, con Page Object Model y una página base compartida (`BasePage`).
- Reset de datos vía API (misma `reset_state` que en `api-tests`) y reinicio completo de la app antes de cada test, para garantizar que siempre arranca desde una pantalla conocida.
- `BasePage.dismiss_dev_warning_if_present()`: en modo dev, React Native muestra un banner de LogBox cuando hay un warning que se queda pegado abajo de la pantalla y puede tapar botones. Lo cierro defensivamente antes de tocar botones pegados al fondo — reduce la flakiness, pero no la elimina del todo, porque el banner puede aparecer justo entre el chequeo y el tap. No pasaría contra un `.apk` de release.
- Pensé la suite para Android (Appium + UiAutomator2). Cocos tiene app en Android e iOS, así que si quisiera correrla contra iOS haría falta adaptarla: el driver pasaría a ser XCUITest en vez de UiAutomator2 (con un simulador en vez de un emulador), y buena parte de los locators habría que duplicarlos por plataforma, porque hoy varios buscan por atributos propios de Android (`@text`, `@content-desc`) que en iOS no existen (ahí es `@name`/`@label`).

## Fuera de alcance

| Qué no probé | Por qué |
|---|---|
| `POST /reset` como feature de negocio | No es una regla de negocio, la consigna lo trata como herramienta de testing. Además corre en cada test vía fixture, así que cualquier problema se notaría solo. |
| LIMIT en `PENDING` de forma aislada | Confirmé que no se puede testear de forma confiable: una LIMIT puede resolver casi al instante. Quedaron 2 tests `skip` con la evidencia adentro. |
| LIMIT resolviendo a `FILLED`/`REJECTED` | Mismo problema: probé con el precio al doble del mercado y aun así dio 6 `REJECTED` / 4 `FILLED` en 10 intentos. Otros 2 tests `skip`. |
| 2 LIMIT pendientes que reservan cash acumulado | Depende de que la primera orden siga `PENDING` al evaluar la segunda — mismo problema de no-determinismo. La segunda debería rechazarse si ya no alcanza el cash disponible. Queda `skip`. |
| `avg_cost_price` como promedio ponderado real | Los precios no varían en este entorno. El test igual calcula el esperado a partir de los precios reales de las órdenes, no un valor fijo — si el entorno cambia, ya queda listo. |
| Reporte HTML para la suite de UI | A diferencia de `api-tests`, no llegué a agregar `pytest-html` ni el flag correspondiente a `ui-tests/`. Es una mejora pendiente, no una decisión. |

## Priorización basada en riesgo

1. **Lo más crítico: integridad del saldo en `/orders`.** Si las reglas de reserva/liquidación de cash y holdings fallan, se pierde o se inventa dinero de verdad. Acá entra el Bug 3: mientras la orden queda `PENDING`, la reserva de cash se calcula mal (suma en vez de restar) — se autocorrige al resolver, pero hay una ventana real con el balance mal.
2. **Alto: el ciclo de vida de las LIMIT bajo no-determinismo.** Es lo más riesgoso y difícil de verificar con confianza — ahí metí más tiempo de ingeniería (el helper de polling, decidir qué marcar `skip`, probar empíricamente antes de asumir nada).
3. **Medio: integridad de datos entre `/instruments` y `/search`.** Menor riesgo, no manejan dinero, pero sí la confianza en lo que la app le muestra al usuario.
4. **Medio: el contrato HTTP en general** (códigos de estado, mensajes de error, headers). Afecta a cualquiera que consuma esta API.
5. **Informativo: los tiers `easy`/`medium`/`hard` en sí mismos.** No es el camino a producción, pero me permitió encontrar 6 de los 9 bugs (los otros 3 aparecen igual bajo `off`, ver `findings.md`).

## Supuestos

- Los precios los valido como `number`, no como `int` — la consigna usa un precio con decimales (`84.5`) en su ejemplo de LIMIT.
- `X-Candidate-Id` es un string libre, sin registro previo.
- Los precios son estáticos en este entorno (lo comprobé a mano) — limita cuánto puedo probar `avg_cost_price` (ver "Fuera de alcance").
- El match parcial de `/search` lo trato como comportamiento intencional, no como bug.
- Los campos `id`/`type` en `/instruments`, aunque no documentados, los trato como parte estable del contrato — aparecen siempre, de forma consistente.

## Cómo automatizaría esto sin `POST /reset`

Sin `POST /reset` (el caso real de producción), no asumiría ningún estado de partida — consultaría el estado real antes de cada prueba con los servicios que la app ya expone.

- **Balance/portafolio:** consultaría el balance real antes de una prueba que necesita dinero, y si no alcanza, usaría un servicio de cash-in para cargar lo que falte — no asumiría un `cash` de partida, lo garantizaría.
- **Órdenes:** en producción el historial nunca está vacío, así que necesitaría una función genérica para filtrar ese historial (mi última orden, o las de un instrumento puntual) en vez de asumir que la única orden que existe es la que acabo de crear.
- Tener usuarios dedicados al automation, separados del que uso para explorar a mano, para no pisarme el estado entre corridas.

## Cómo escalaría la suite de UI si esto fuera una app real

El fixture `driver` reinicia la app entera antes de cada test para garantizar que siempre arranca desde una pantalla conocida. Simple y confiable, pero caro: con 12 tests ya tarda varios minutos, porque cada reinicio espera a que Metro le sirva el bundle de JS de nuevo. Escalado a una suite de UI de una app real con cientos de tests, este approach se vuelve prohibitivo.

Lo que haría distinto en ese escenario:
- **Testear contra un build de release** El `.apk` trae el JS empaquetado adentro, así que abrir la app de cero tarda segundos, no 15-20.
- **No reiniciar el proceso entre tests, navegar de vuelta a un estado conocido.** Un `go_home()` que devuelva a una pantalla base sin tener que reiniciar la app.
- **Correr en paralelo contra varios dispositivos/emuladores**, como los device farms (Firebase Test Lab, BrowserStack, Sauce Labs).
- **Reservar el reset completo de la app para cuando realmente hace falta**, no como default para todos.
- **Usar más llamadas a la API para el arrange, no solo para el reset.** Ejemplo hoy `bought_dyca` arma la compra navegando toda la UI (buscar, tocar, tipear, enviar) — se podría reemplazar por una llamada directa a `POST /orders` en vez de rehacer todo el proceso.
- **Sumarla al CI/CD.** Técnicamente GitHub Actions puede correr un emulador Android dentro del job, pero no estoy seguro de qué tan bien funcionaría en la práctica para esta suite puntual.

Para esta entrega elegí el approach pesado a propósito: la suite es chica, y priorizar determinismo simple por sobre velocidad me pareció la decisión correcta dado el tiempo que tenía.