# Reporte de hallazgos — Cocos QA Challenge

Encontré 9 bugs reproducibles. Para cada uno: pasos, esperado vs. obtenido, severidad y evidencia.

Severidad: **Crítica** (dinero mal contabilizado), **Alta** (rompe una regla de negocio o hay datos inconsistentes entre endpoints), **Media** (contrato HTTP o UX). Aclaración: 6 de los 9 solo aparecen con `X-Enable-Bugs` en `easy`/`medium`/`hard` (son defectos simulados por la propia API para el challenge). La severidad asume como si esto pasara en un sistema real.

Los **Bugs 3, 8 y 9** son la excepción: aparecen incluso con `off`, sin ningún flag prendido (el 9 ni siquiera depende de la API, es un tema de UI). Son los tres 100% reales de los nueve.

---

## Bug 1 — `GET /instruments` devuelve `last_price: 0` para MIRG bajo `easy`/`medium`/`hard`

**Severidad:** Alta

**Pasos para reproducir:**
```bash
curl -H "X-Enable-Bugs: easy" -H "X-Candidate-Id: <cualquiera>" https://dummy-api-topaz.vercel.app/instruments
```

**Esperado:** el instrumento con `ticker: "MIRG"` (id 5) trae un `last_price` mayor a 0.

**Obtenido:** `last_price: 0` para ese instrumento puntual.

**Evidencia:** reproducible en `easy`, `medium` y `hard`. Con `off` el valor es correcto siempre. El resto de los 26 instrumentos no se ven afectados. Además, noté que `/search?query=MIRG` sí devuelve un `last_price` con sentido para ese mismo instrumento, al mismo tiempo y con el mismo tier: el mismo valor que da `off` (`40.88`). Apunta a que el problema está puntualmente en cómo `/instruments` arma su respuesta, no en el dato de precio en sí: dos endpoints que deberían leer la misma fuente están en desacuerdo.

---

## Bug 2 — `GET /search` deja de ser case-insensitive con cualquier tier de bugs activado

**Severidad:** Media

**Pasos para reproducir:**
```bash
curl -H "X-Enable-Bugs: easy" -H "X-Candidate-Id: <cualquiera>" "https://dummy-api-topaz.vercel.app/search?query=dyca"
```

**Esperado:** debería encontrar el ticker `DYCA` sin importar mayúsculas/minúsculas (así funciona bajo `off`).

**Obtenido:** devuelve `[]`, no encuentra nada. Buscas `DYCA` en mayúsculas, o un substring en mayúsculas (`DYC`), sigue funcionando bien; solo deja de encontrar resultados con minúsculas o mezcla de mayúsculas/minúsculas.

**Evidencia:** probé varios de los tickers de la API en minúscula contra los 4 tiers. Bajo `off`: pude encontrar los instrumentos. Bajo `easy`/`medium`/`hard`: ninguno matchea.

---

## Bug 3 — `POST /orders` acepta una LIMIT con `price` ≤ 0

**Severidad:** Alta

**Pasos para reproducir:**
```bash
curl -X POST -H "X-Enable-Bugs: off" -H "X-Candidate-Id: <cualquiera>" -H "Content-Type: application/json" \
  -d '{"instrument_id":1,"side":"BUY","type":"LIMIT","quantity":1,"price":0}' \
  https://dummy-api-topaz.vercel.app/orders
```

**Esperado:** `400`, un precio límite de `0` (o negativo) no es válido.

**Obtenido:** `201`, la orden se crea normalmente con `status: PENDING`.

**Evidencia:** a diferencia de los otros bugs, este pasa **siempre**, incluso con `X-Enable-Bugs: off`. No depende del tier. Probado con `price: 0` y `price: -10`, mismo resultado en ambos.

Utilizando el servicio de porfolio tambien encontre que con el `cash` mientras la orden está `PENDING`: con `price: -10` y `quantity: 100`, el `cash` sube de `1.000.000` a `1.001.000` apenas se crea la orden. Un segundo después la orden resuelve a `REJECTED` (tiene sentido: un LIMIT BUY con precio negativo nunca puede llenar) y el `cash` vuelve a `1.000.000`. No es dinero que quede generado de forma permanente, pero sí hay una pequeña ventana donde se podría ver incorrecto el balance.

---

## Bug 4 — `POST /orders` devuelve `200` en vez de `201` bajo `medium`/`hard`

**Severidad:** Media

**Pasos para reproducir:**
```bash
curl -i -X POST -H "X-Enable-Bugs: medium" -H "X-Candidate-Id: <cualquiera>" -H "Content-Type: application/json" \
  -d '{"instrument_id":1,"side":"BUY","type":"MARKET","quantity":1}' \
  https://dummy-api-topaz.vercel.app/orders
```

**Esperado:** `201 Created` (la respuesta indica que la orden se creó bien).

**Obtenido:** `200 OK`. El body de la respuesta viene perfecto (mismos campos, mismo `status: FILLED`, precio correcto). Es únicamente el código de estado HTTP el que está mal.

**Evidencia:** Bajo `off`/`easy` siempre da `201`. Afecta tanto a MARKET como a LIMIT. Cualquier cliente que valide estrictamente el código de estado (en vez de solo mirar el body) va a fallar acá sin motivo real.

---

## Bug 5 — Se puede vender un instrumento que nunca se tuvo, bajo `easy`/`medium`/`hard`

**Severidad:** Crítica

**Pasos para reproducir:**
```bash
curl -X POST -H "X-Enable-Bugs: easy" -H "X-Candidate-Id: <candidate nuevo, recien reseteado>" "https://dummy-api-topaz.vercel.app/reset"
curl -X POST -H "X-Enable-Bugs: easy" -H "X-Candidate-Id: <mismo candidate>" -H "Content-Type: application/json" \
  -d '{"instrument_id":1,"side":"SELL","type":"MARKET","quantity":1}' \
  https://dummy-api-topaz.vercel.app/orders
```

**Esperado:** `400` con `{"error":"Insufficient shares"}`, no podés vender algo que no tenés (así se comporta bajo `off`, y es la regla documentada).

**Obtenido:** `201`, la orden se llena (`FILLED`), y el `cash` del candidato sube como si la venta hubiera sido real, sin nunca haber comprado el instrumento.

**Evidencia:** repetí la venta 5 veces seguidas desde una cuenta recién reseteada bajo `easy`, las 5 se aceptaron. El portafolio quedó en `{"cash": 1000045.72, "holdings": []}`: dinero generado de la nada, repetible sin límite (podés hacerlo tantas veces como quieras). 

---

## Bug 6 — `quantity` fraccionaria se acepta (truncada) en vez de rechazarse, bajo `medium`/`hard`

**Severidad:** Alta

**Pasos para reproducir:**
```bash
curl -X POST -H "X-Enable-Bugs: medium" -H "X-Candidate-Id: <cualquiera>" -H "Content-Type: application/json" \
  -d '{"instrument_id":1,"side":"BUY","type":"MARKET","quantity":1.5}' \
  https://dummy-api-topaz.vercel.app/orders
```

**Esperado:** `400`, la consigna documenta explícitamente que "no se admiten fracciones de acciones". Así se comporta bajo `off`/`easy`.

**Obtenido:** `201`, `status: FILLED`, pero con `quantity: 1` en la respuesta. La API trunca el valor en vez de rechazarlo.

**Evidencia:** confirmado con `curl` bajo `medium` y `hard`. Viola una regla de negocio documentada explícitamente, y lo hace mutando el dato en vez de devolver un error. 

---

## Bug 7 — Luego de una compra/venta de tipo Market, el estado no se refleja en el GET orders o portfolio

**Severidad:** Media

**Pasos para reproducir (variante 1 — `/orders`):**
1. `POST /orders` una MARKET BUY bajo `hard`.
2. Inmediatamente después, `GET /orders`.

**Esperado:** el `status` de la orden en el listado debería ser `FILLED`, igual que en la respuesta del `POST`.

**Obtenido:** en algunas corridas, el listado muestra la misma orden como `PENDING`, contradiciendo lo que la propia API acababa de confirmar segundos antes. (pero intermitente, vale la pena que lo tengan en el radar aunque no sea 100% reproducible en cada intento)

**Pasos para reproducir (variante 2 — `/portfolio`):**
1. Comprar algo (MARKET BUY), después vender una parte (MARKET SELL), bajo `hard`.
2. Inmediatamente después de la venta, `GET /portfolio`.

**Esperado:** la `quantity` del holding debería reflejar la venta que se acaba de confirmar.

**Obtenido:** en algunas corridas, `/portfolio` sigue mostrando la cantidad de **antes** de vender.

**Evidencia:** no es reproducible en el 100% de los intentos: corriendo la secuencia 10 veces bajo `hard`, la variante 2 falló 1 de 10 veces; 10/10 salió bien bajo `off`. Encontré la variante 1 corriendo la suite completa repetidas veces contra `hard`, no fue algo que hubiera anticipado al diseñar los casos. Parece que el problema se da solo bajo ese tier, no algo específico de un endpoint: aparece tanto en `/orders` como en `/portfolio`.

---

## Bug 8 — `GET /instruments` incluye la moneda base (ARS) mezclada con las acciones, y se puede operar como si fuera una

**Severidad:** Alta

**Pasos para reproducir:**
```bash
curl -H "X-Enable-Bugs: off" -H "X-Candidate-Id: <cualquiera>" https://dummy-api-topaz.vercel.app/instruments
```

**Esperado:** la lista debería traer solo instrumentos operables de verdad (acciones), no la moneda con la que se paga.

**Obtenido:** el instrumento 26 (`ticker: "ARS"`, `type: "MONEDA"`, `last_price: 1` fijo) aparece mezclado con las 26 acciones, sin ningún flag prendido. La app no filtra por `type` en ningún lado (ni en Mercados, ni en Buscar, ni en el formulario de orden), así que se puede buscar, ver el detalle, y comprar/vender ARS exactamente igual que cualquier acción.

**Evidencia:** reproducible bajo `off`, no depende de ningún tier. Probé comprar de verdad: reseteé la cuenta y compré 100 ARS por MARKET, y quedó como holding en el portafolio (`{"instrument_id":26,"ticker":"ARS","quantity":100,"avg_cost_price":1}`), igual que cualquier acción. No genera ni destruye plata (el precio está fijo en 1, comprar/vender ARS es económicamente neutro), pero no tiene sentido de negocio: termina dejando "comprar" la moneda con la que estás pagando.

---

## Bug 9 — La barra de navegación inferior tapa el último instrumento de la lista de Mercados

**Severidad:** Media

**Pasos para reproducir:**
1. Ir a la pestaña Mercados.
2. Scrollear hasta el final de la lista de instrumentos.

**Esperado:** debería poder ver (y tocar) el último instrumento de la lista sin que nada lo tape.

**Obtenido:** la barra de navegación inferior (Mercados/Portafolio/Órdenes/Buscar) queda fija encima del contenido, y el último ítem de la lista termina parcial o totalmente tapado detrás de ella.

**Evidencia:** se ve a simple vista con los 26 instrumentos actuales. No depende de ningún tier de bugs, es un tema de layout: a la lista le falta padding/inset abajo para no meterse debajo de la tab bar. Con una lista más larga (como sería en una app real) el problema es el mismo, siempre el último ítem se va a comer la barra.
