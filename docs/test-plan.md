# Plan de pruebas — Cocos QA Challenge

## Alcance

Decidí automatizar principalmente a **nivel de API** (~80% del esfuerzo) contra `https://dummy-api-topaz.vercel.app`, y dejar una capa chica de UI sobre `app-qa` (Appium) solo para los flujos más críticos (~20%).

**¿Por qué así?** la lógica de negocio con más riesgo real (reserva de saldo, liquidación de órdenes, cálculo de `avg_cost_price`) está en la API, no en la UI. La UI en gran parte solo muestra esos mismos datos. Además los tests de API son mucho más rápidos y no sufren la flakiness típica de UI, así que con el tiempo que tenía me rendía más cubrir casos límite ahí.

**Endpoints con suite automatizada (pytest):**
- `GET /instruments`
- `GET /search`
- `GET /portfolio`
- `GET /orders` y `POST /orders`

`POST /reset` lo usé como herramienta para aislar los tests entre sí, no lo testeo como feature de negocio (revisar "Fuera de alcance").

**Cuánto cubrí, en números** (64 tests en total):
- `GET /instruments` + `GET /search`: 26 tests, schema, unicidad de datos, headers (positivos y negativos), case-insensitivity, que `/search` coincida con `/instruments`, casos borde de búsqueda (parcial, vacío, sin resultados).
- `POST/GET /orders`: 27 tests, happy path de MARKET y LIMIT, validaciones de campos (parametrizadas), reglas de negocio (`Insufficient cash/shares`), headers, y 5 casos que quedaron marcados `skip` por un problema de no-determinismo que explico abajo.
- `GET /portfolio`: 11 tests, schema del holding, qué pasa con `cash`/`holdings` al comprar y vender (parcial y total), cálculo de `avg_cost_price`, que el valor de mercado sea calculable, headers.

**Cómo armé la suite:**
- Capas: cliente HTTP → servicio de dominio → schemas/assertions → tests, todo en `api-tests/`.
- Los headers `X-Enable-Bugs`/`X-Candidate-Id` van por default en el cliente, y cualquier test los puede pisar para probar casos negativos.
- Agregué un flag propio (`--bugs-tier`) para poder correr toda la suite contra cualquiera de los 4 niveles de bugs sin tocar código.
- En CI (GitHub Actions) corro la suite contra los 4 tiers en cada PR/push a `main`, pero solo dejé que `off` bloquee el merge. `easy`/`medium`/`hard` corren igual, pero informativamente, porque ya sé que van a fallar mientras la API tenga los bugs que encontré (revisar `findings.md`).
- Cada corrida de CI sube un reporte HTML (`pytest-html`) como artifact.

**UI (Appium):** [completar según lo que llegue a implementar; pensaba cubrir: buscar un instrumento, mandar una orden MARKET, y ver que el portafolio se actualice después].

## Fuera de alcance

| Qué no probé | Por qué |
|---|---|
| `POST /reset` como si fuera una feature de negocio | No aparece en las reglas de negocio de la consigna, y el propio enunciado lo trata como herramienta de testing. Además, es una fixture del `conftest` que se ejecuta en todos los tests, así que sería sencillo detectar algún problema. |
| Que una LIMIT quede específicamente en `PENDING`, con su reserva activa, probado de forma aislada | Confirmo que es muy difícil de testear de forma confiable: una LIMIT puede resolver en tan poco como ~187ms, incluso llamando de nuevo casi inmediatamente. Dejé 2 tests que documentan esto, marcados `skip` con la evidencia adentro. |
| Que una LIMIT resuelva específicamente a `FILLED` o `REJECTED` | Mismo problema. Probé poniendo el precio al doble del mercado y aun así dio 6 `REJECTED` / 4 `FILLED` en 10 intentos, no tengo forma de controlar el resultado. También quedaron 2 tests `skip` documentando esto. |
| Reservas acumuladas (2 LIMIT donde la segunda debería rechazarse porque la primera sigue reservando dinero) | Depende de que la primera orden siga `PENDING` justo en el momento en que se evalúa la segunda, entonces mismo problema. Queda `skip`. |
| `avg_cost_price` como promedio ponderado **real** (comprando el mismo instrumento a precios distintos) | Los precios de los instrumentos no cambian de valor. Cualquier compra del mismo instrumento siempre cae al mismo precio. Igual quedó el test calculando el promedio esperado a partir de los precios reales de las órdenes (no un valor fijo), así que si algún día el entorno varía los precios, el mismo test ya validaría el caso real sin tocarle nada. |
| [UI: casos que quedaron pensados pero sin implementar] | [completar con lo que no llegue a hacer por tiempo] |

## Priorización basada en riesgo

1. **Lo más crítico: integridad del saldo en `/orders`.** Las reglas de reserva/liquidación/liberación de cash y holdings son las que, si fallan, hacen que se pierda o se invente dinero de verdad. Acá entra el Bug 3 (LIMIT con `price` ≤ 0): mientras la orden queda `PENDING`, la reserva de cash se calcula mal (suma en vez de restar), así que aunque se autocorrige cuando la orden resuelve, hay una ventana real con el balance mal calculado.
2. **Alto: el ciclo de vida de las LIMIT bajo no-determinismo.** Es donde más tiempo de ingeniería metí (el helper de polling, decidir qué marcar `skip` y por qué, probar empíricamente antes de asumir nada), justamente porque es lo más riesgoso y lo más difícil de verificar con confianza.
3. **Medio: integridad de datos entre `/instruments` y `/search`.** Son de menor riesgo, ya que no manejan dinero, pero sí la confianza en lo que la app le muestra al usuario.
4. **Medio: el contrato HTTP en general** (códigos de estado, mensajes de error, headers). Afecta a cualquiera que consuma esta API.
5. **Informativo: los tiers `easy`/`medium`/`hard` en sí mismos.** No son el camino que va a producción, pero fueron el mecanismo que me permitió encontrar los 7 bugs.

## Supuestos

- Los precios (`last_price`/`close_price`) los valido como `number`, no como `int`. El ejemplo de orden LIMIT en la consigna usa un precio con decimales (`84.5`), así que asumo que los precios en general pueden tener decimales.
- `X-Candidate-Id` es un string libre, sin registro previo.
- Los precios de los instrumentos son estáticos durante una sesión de test en este entorno (lo comprobé a mano, no está en la doc). Esto limita qué tanto puedo probar del cálculo de `avg_cost_price` (ver "Fuera de alcance").
- El match parcial de `/search` (encuentra el substring en cualquier parte del ticker, no solo al principio) lo trato como comportamiento intencional, no como bug.
- Los campos `id` y `type` que aparecen en `/instruments` sin estar documentados los trato como parte estable del contrato, no como error. Aparecen siempre, de forma consistente.

## Cómo automatizaría esto sin `POST /reset`

Si no tuviera `POST /reset` (que es lo que pasaría en un ambiente real de producción), no asumiría ningún estado de partida fijo. Consultaría el estado real justo antes de cada prueba, usando los servicios que la propia app ya expone, en vez de inventar uno.

- **Balance/portafolio:** antes de una prueba que necesita dinero (por ejemplo, comprar algo en MARKET), consultaría el balance actual con el servicio de balance/portafolio que ya existe. Si no alcanza para lo que la prueba necesita, usaría un servicio de cash-in (la app debe tener alguna boca para cargar saldo) para cargar lo que haga falta antes de correr el test. No asumiría un `cash` de partida, lo garantizaría activamente.
- **Órdenes:** `/reset` las borra, y eso tampoco pasa en producción. El historial de órdenes crece para siempre y nunca está vacío. Ahí necesitaría una función genérica para poder recorrer/filtrar ese historial (buscar la última orden que hice, o las de un instrumento puntual) en vez de asumir "la única orden que existe es la que acabo de crear".
- Lo que sí también es tener usuarios dedicados al automation, separado del que uso para explorar a mano, para no pisarme mi propio estado entre corridas.