# GARUM TPV Manager — v7.4
### Herramienta interna de gestión de integración de TPVs GARUM

---

## Qué es

GARUM TPV Manager es una aplicación web de uso interno para técnicos que gestionan estaciones de servicio con el software **GARUM de 4GL Solutions**. Sustituye los scripts `.BAT` y `.sql` manuales por una interfaz visual que ejecuta las operaciones correctas en todos los TPVs afectados de forma automática, con confirmación previa y registro de todas las operaciones.

---

## Instalación

### Requisitos
- Windows 7 / 10 / 11 de **64 bits**
- **No requiere conexión a internet** — Python y las librerías van incluidas en el paquete
- Ejecutar como **Administrador**
- Puerto `5432` accesible en la red local entre los TPVs

### Pasos — solo la primera vez

1. Extrae el ZIP en cualquier carpeta
2. Entra en la carpeta extraída (la que contiene `INSTALAR.bat` y `runtime\`)
3. Clic derecho sobre `INSTALAR.bat` → **"Ejecutar como administrador"**
4. **Selecciona la ruta de instalación** en el menú:
   - `[1]` `C:\GarumTPV` (por defecto)
   - `[2]` `C:\GARUMTOOLS\GarumTPV` (subcarpeta dentro de GARUMTOOLS)
   - `[3]` Otra ruta personalizada
5. Espera menos de 1 minuto (instala Python 3.11 y las librerías ya incluidas en el paquete)
6. Al terminar se crea el acceso directo **"GARUM TPV Manager"** en el Escritorio
7. Doble clic en el acceso directo para abrir la app

### Qué instala y dónde

La ruta se elige al instalar. Estructura interna (sustituye `<INST>` por la ruta elegida):

```
<INST>\                        ← C:\GarumTPV, C:\GARUMTOOLS o ruta custom
├── python\                    ← Python 3.11 embebido — no toca el sistema
├── app\
│   ├── server.py              ← Servidor Flask (backend)
│   └── templates\
│       ├── index.html         ← Interfaz web (diseño corporativo 4GL)
│       └── diagnostico.html   ← Página de diagnóstico
└── ARRANCAR.bat               ← Arranque diario
```

La instalación no modifica el registro de Windows ni interfiere con GARUM ni PostgreSQL.

---

## Uso diario

1. Doble clic en **"GARUM TPV Manager"** del Escritorio
2. Se abre una ventana negra (servidor) y el navegador en `http://127.0.0.1:5050`
3. Selecciona la IP en el desplegable, escribe la contraseña de postgres y pulsa **Conectar**
4. La app escanea los TPVs y muestra su estado real
5. Para cerrar: cierra la ventana negra o pulsa Ctrl+C

> La contraseña nunca se guarda en disco. Solo existe en memoria mientras la app está abierta.

---

## Pantalla de conexión

### Selector de IP

| Opción | IP | Cuándo usarla |
|--------|----|---------------|
| TPV 1 | 10.0.0.101 | Primera opción a probar |
| TPV 2 | 10.0.0.102 | Si el TPV 1 no responde |
| TPV 3 | 10.0.0.103 | Si los TPVs 1 y 2 no responden |
| TPV 4 | 10.0.0.104 | Si los TPVs 1, 2 y 3 no responden |
| Este equipo | 127.0.0.1 | Si la app corre en el mismo TPV al que conectar |
| Otra IP... | — | Escribe manualmente cualquier IP de la red |

> La app detecta automáticamente qué TPV es el Principal al escanear.

### Opciones avanzadas

Puerto, base de datos y usuario están ocultos (nunca cambian). Se despliegan con "▸ Opciones avanzadas".

---

## Backup de configuración

El botón **"💾 Backup config"** en la esquina superior izquierda exporta un fichero `.txt` con la configuración completa de todos los TPVs accesibles:

- Todas las claves de la tabla `propiedad` (BD `tpv`)
- Estado de la tabla `pos` (BD `controlpista`)
- Rol, estado e integración de cada TPV

El fichero se descarga con nombre `garum_backup_config_FECHA-HORA.txt`.

> **Recomendado:** hacer backup antes de cualquier operación importante.

---

## Panel de TPVs

Vista principal con una tarjeta por TPV. El estado se lee directamente de las BDs en cada escaneo.

### Detección del rol real (Principal / Secundario)

El rol no está hardcodeado. Se determina leyendo `BackupDirectoriesBOS` de la tabla `propiedad`:

- Ruta **local** (`C:/integracion/4GLExport`) → **Principal**
- Ruta de **red** (`//10.0.0.X/...`) → **Secundario**

### Colores del borde izquierdo

| Color | Significado |
|-------|-------------|
| Azul marino | TPV Principal — activo e integrado |
| Verde | TPV Secundario — activo e integrado |
| Gris | TPV desactivado de la integración |
| Rojo | TPV inaccesible (apagado o sin red) |
| Ámbar pulsante | Escaneando... |

### Avisos en las tarjetas

**`⚠ No apunta a: TPV X`** (ámbar) — el `CopyDirectories` de ese TPV no incluye la IP indicada. Configuración desincronizada. Ejecuta la operación correspondiente para corregirlo.

**`PRINCIPAL ⚠`** (badge rojo) + **`⚠ Conflicto: TPV X también es principal`** — hay dos TPVs con configuración de principal simultáneamente. Usa el botón "Dejar como secundario" para resolverlo.

### Botones de acción

| Botón | Cuándo aparece | Qué hace |
|-------|---------------|----------|
| **Anular** | TPV integrado y accesible | Desactiva el TPV |
| **Anular de la red** | TPV inaccesible | Actualiza los demás sin tocar el averiado |
| **Reintegrar como secundario** | TPV desactivado | Devuelve el TPV a la integración |
| **Hacer principal** | TPV secundario (también si el principal está caído) | Cambia el principal |
| **Dejar como secundario** | TPV con conflicto de principal (vuelve tras avería) | Resuelve el conflicto reconvirtiendo a secundario |
| **Ver config** | TPV accesible | Abre su configuración de integración |
| **💾 Backup config** | Siempre (header izquierdo) | Exporta configuración a .txt |

---

## Operaciones — flujo detallado

### Anular un TPV averiado (no enciende)

1. Tarjeta en **rojo** — "Inaccesible"
2. Pulsa **"Anular de la red"**
3. Checklist obligatoria antes de confirmar
4. La app ejecuta en **todos los TPVs accesibles**:
   - `tpv.propiedad`: recalcula `CopyDirectories` eliminando la IP del anulado
   - `controlpista.pos`: `online = FALSE` para el TPV anulado
   - `tpv.sesion_tpv_activo`: `DELETE WHERE id_tpv = N`
   - `controlpista.local_config.ip_server`: **no se toca** — se actualizará al designar nuevo principal
5. El TPV roto **no se toca**

> Si el anulado era el Principal: guía de 3 pasos para gestionar el cambio.

### Anular un TPV encendido

1. Pulsa **"Anular"** en su tarjeta
2. Confirma con la checklist
3. La app vacía `CopyDirectories` en su BD, recalcula los del resto, actualiza `pos.online = FALSE` y `sesion_tpv_activo`

### Reintegrar como secundario

1. Tarjeta en **gris** — "Desactivado"
2. Pulsa **"Reintegrar como secundario"**
3. Confirma con la checklist
4. La app actualiza en **todos los TPVs afectados**:
   - `tpv.propiedad`: configura todas las rutas apuntando al principal actual
   - `controlpista.local_config`: `ip_server` → IP del principal actual
   - `controlpista.pos`: `online = TRUE` para el TPV reintegrado
   - `sesion_tpv_activo`: **no se toca** — GARUM crea la sesión al arrancar
5. Aviso hibernate para editar `hibernateCentral.cfg.xml` en el TPV reactivado

### Cambiar el TPV Principal

1. Pulsa **"Hacer principal"** en el TPV deseado
2. Checklist obligatoria
3. La app actualiza en **todos los TPVs accesibles**:
   - **Nuevo principal**: `BackupDirectoriesBOS` local, `CopyDirectories` y `CopyDirectoriesMaestros` activos
   - **Ex-principal y secundarios**: `BackupDirectoriesBOS` apunta al nuevo, `CopyDirectoriesMaestros` vacío
   - `controlpista.local_config`: **`ip_server` → nuevo principal en TODOS** ← aquí se actualiza automáticamente
   - `controlpista.pos`: `online = TRUE` activos, `online = FALSE` caídos
   - `sesion_tpv_activo`: `DELETE WHERE id_tpv = N` para los TPVs caídos
4. TPV caído **no se toca** — aviso para reintegrarlo cuando vuelva
5. Aviso hibernate con instrucciones exactas TPV por TPV

### Resolver conflicto de principal (TPV vuelve tras avería)

Cuando un TPV que era principal vuelve a arrancar con su IP definitiva, la app detecta que hay dos TPVs con configuración de principal simultáneamente y muestra en su tarjeta:

- Badge rojo `PRINCIPAL ⚠`
- Aviso ámbar con el nombre del otro principal activo
- Botón verde **"Dejar como secundario"**

Al pulsar "Dejar como secundario":
1. Modal explicativo con checklist
2. Configura la BD del TPV que vuelve como secundario apuntando al principal actual
3. Recalcula `CopyDirectories` en todos los TPVs para incluirle
4. Actualiza `ip_server` y `pos`
5. Aviso hibernate para verificar `hibernateCentral.cfg.xml`

---

## Cuándo se actualiza ip_server en controlpista

| Operación | ip_server en controlpista |
|-----------|--------------------------|
| Anular TPV (cualquiera) | ❌ No se toca |
| **Hacer principal** | ✅ Se actualiza en **TODOS** los TPVs accesibles → nuevo principal |
| Reintegrar como secundario | ✅ Se actualiza en el TPV reactivado → principal actual |
| Dejar como secundario | ✅ Se actualiza en ese TPV → principal actual |

> El flujo correcto cuando cae el principal es:
> 1. **Anular de la red** → recalcula CopyDirectories (ip_server no se toca aún)
> 2. **Hacer principal** en otro TPV → aquí se actualiza ip_server en todos
> 3. Cuando el caído vuelve → **Reintegrar como secundario** o **Dejar como secundario**

---

## Tabla sesion_tpv_activo

Registra qué TPVs tienen sesión activa en GARUM. Columnas: `id_sesion`, `id_tpv` (entero), `fecha_ultima_activo`.

| Operación | Acción en `sesion_tpv_activo` |
|-----------|-------------------------------|
| Anular TPV N | `DELETE WHERE id_tpv=N` en **todos** los accesibles |
| Cambiar principal | `DELETE WHERE id_tpv=N` de los TPVs **caídos** en todos los accesibles |
| Reintegrar | **No se toca** — GARUM crea la sesión al arrancar |
| Dejar como secundario | **No se toca** — GARUM la gestiona |

El `id_tpv` se calcula desde la IP: último octeto menos 100 (`10.0.0.102` → `id_tpv=2`).

---

## Avisos de ficheros hibernate

La app genera avisos con instrucciones exactas en estas situaciones:

### Al cambiar el Principal

```
[10.0.0.102] NUEVO PRINCIPAL
  C:\GARUM\hibernateCentral.cfg.xml
  Buscar:    jdbc:postgresql://10.0.0.101:5432/tpv
  Sustituir: jdbc:postgresql://localhost:5432/tpv

[10.0.0.103] secundario
  Buscar:    jdbc:postgresql://10.0.0.101:5432/tpv
  Sustituir: jdbc:postgresql://10.0.0.102:5432/tpv

[10.0.0.101] secundario ⚠ ESTABA CAIDO — editar cuando arranque
  Buscar:    jdbc:postgresql://10.0.0.101:5432/tpv
  Sustituir: jdbc:postgresql://10.0.0.102:5432/tpv
```

Botón **"Copiar instrucciones"** para portapapeles.

### Al anular el Principal

Guía de 3 pasos: designar nuevo principal → editar hibernate → reiniciar GARUM.

### Al reintegrar o dejar como secundario

Aviso específico con la línea exacta que debe contener `hibernateCentral.cfg.xml`.

> `hibernate.cfg.xml` (sin "Central") **nunca se modifica** en ningún TPV.

---

## Pestaña Control Pista

Accesible desde el tab **"🖧 Control Pista"** en el header. Lee en paralelo la BD `controlpista` de todos los TPVs y muestra para cada uno:

### ip_server (tabla local_config)

- Valor actual leído de la BD
- Indicador **verde ✓** si apunta al principal detectado
- Indicador **rojo ⚠** si apunta a una IP diferente al principal actual
- Desplegable para seleccionar a qué TPV debe apuntar
- Botón **"Aplicar"** para cambiarlo manualmente en ese TPV

> En condiciones normales no es necesario usar esta pantalla — las operaciones del panel actualizan `ip_server` automáticamente. Esta pantalla es para verificación y corrección manual en casos excepcionales.

### Tabla pos

- Una fila por TPV declarado con IP, preference y estado online/offline
- Botón **"Poner offline"** o **"Poner online"** para cambiar manualmente cada fila

---

## Base de datos controlpista

### Tabla local_config

| Campo | La app lo toca | Cuándo |
|-------|----------------|--------|
| `ip` | ❌ Nunca | — |
| `ip_server` | ✅ Sí | Al hacer principal, reintegrar o dejar como secundario |
| `ip_forecourt_controller` | ❌ Nunca | — |

### Tabla pos

| Campo | La app lo toca | Cuándo |
|-------|----------------|--------|
| `ip` | ❌ Nunca | — |
| `preference` | ❌ Nunca | — |
| `online` | ✅ Sí | Al anular (`FALSE`) / reintegrar o cambiar principal (`TRUE/FALSE`) |

---

## Configuración de integración (Propiedades)

Pestaña **"Configuración"** o botón **"Ver config"** en cada tarjeta. Lee la tabla `propiedad` directamente. Formato vertical con descripción y valor completo. Solo se editan las 16 claves de integración.

### Valores correctos por rol

| Clave | Principal | Secundario |
|-------|-----------|------------|
| `CopyDirectories` | IPs de los otros TPVs **con** `/` final | IPs de los otros TPVs **sin** `/` final |
| `CopyDirectoriesMaestros` | Igual que `CopyDirectories` | `''` vacío |
| `BackupDirectoriesBOS` | `C:/integracion/4GLExport` (local) | `//IP_PRINCIPAL/c/integracion/4GLExport` |
| `BackupDirectoryMaestroMovidosTpvPrincipal` | `C:/integracion/XADBackup/maestros_principal` | `''` vacío |
| `InputDirectory` | `C:/integracion/XADInput` | `C:/integracion/XADInput` |
| `InputDirectoryCopy` | `C:/integracion/XADExport` | `C:/integracion/XADExport` |
| `ErrorDirectory` | `C:/integracion/XADError` | `C:/integracion/XADError` |
| `BackupDirectoryMaestro` | `C:/integracion/XADBackup/maestros/` | `C:/integracion/XADBackup/maestros/` |
| `BackupDirectoryTransaccion` | `C:/integracion/XADBackup/transacciones/` | `C:/integracion/XADBackup/transacciones/` |

---

## Pestaña Ajustes

- **Editar nombre e IP** de cualquier TPV
- **Añadir TPV** si hay más de 4 en la instalación
- **Eliminar TPV** si alguno ya no existe
- **Guardar y reescanear** — aplica cambios y relanza el escaneo
- **Restaurar valores por defecto** — vuelve a los 4 TPVs estándar (10.0.0.101–104)

La configuración persiste durante la sesión. Al cerrar el servidor se pierde.

---

## Equivalencia con los scripts BAT anteriores

| Script BAT original | Equivalente en la app | Diferencia clave |
|---------------------|-----------------------|-----------------|
| `ANULAR_TPV1.sql` | Tarjeta TPV 1 → Anular | Actualiza todos + `controlpista` + `sesion_tpv_activo` |
| `ANULAR_TPV2.sql` | Tarjeta TPV 2 → Anular | Ídem |
| `PONER_TPV_2.sql` | Tarjeta TPV 2 → Reintegrar como secundario | Actualiza todos + `controlpista` |
| `TPV1_COMO_PRINCIPAL.sql` | Tarjeta TPV 1 → Hacer principal | Actualiza todos + `controlpista` + aviso hibernate |
| `ANULAR_TPV1_PONE_PRINCIPAL_TPV2.BAT` | Anular TPV 1 + Hacer principal TPV 2 | Dos pasos en la app |
| `DEVOLVER_TPV1_COMO_PRINCIPAL.BAT` | Hacer principal TPV 1 + Reintegrar TPV 2 | Dos pasos en la app |

---

## Arquitectura técnica

```
TPV Windows (donde corre la app)
│
├── ARRANCAR.bat
│     └── <INST>\python\python.exe server.py
│           │
│           ├── Flask en 127.0.0.1:5050  (solo local)
│           │
│           └── psycopg2 ──► PostgreSQL 9.5 · puerto 5432
│                             ├── 10.0.0.101  BD: tpv + controlpista
│                             ├── 10.0.0.102  BD: tpv + controlpista
│                             ├── 10.0.0.103  BD: tpv + controlpista
│                             └── 10.0.0.104  BD: tpv + controlpista
│
└── Navegador → http://127.0.0.1:5050
```

**Diseño visual:** Paleta corporativa 4GL Solutions — azul marino `#1a2b4a`, rojo `#e63329`, fondo blanco.

---

## Seguridad

| Medida | Detalle |
|--------|---------|
| Solo localhost | El servidor escucha en `127.0.0.1`. No accesible desde la red. |
| Contraseña en RAM | Nunca se escribe en disco. Desaparece al cerrar. |
| Validación de IPs | Solo acepta `10.0.0.0/24` y `127.0.0.0/8`. |
| Token CSRF | Token de 64 caracteres por sesión. POST sin token → 403. |
| Lista blanca de claves | Solo 16 claves de integración modificables. |
| SQL parametrizado | Sin riesgo de inyección SQL. |
| Sin internet | Ninguna petición externa: ni durante la instalación ni en uso. |

---

## Solución de problemas

**El instalador se cierra solo / no llega a "INSTALACION COMPLETADA"** → Es el antivirus bloqueando el instalador. Añade una **exclusión** en el antivirus para la carpeta de instalación (`C:\GarumTPV` o `C:\GARUMTOOLS`) y para la carpeta del paquete, o desactiva la protección en tiempo real durante el minuto que dura la instalación. Después vuelve a ejecutar `INSTALAR.bat`.

**La app no abre el navegador** → `http://127.0.0.1:5050`

**"Error al conectar"** → Verifica contraseña, IP y que PostgreSQL está activo.

**Todos los TPVs "Inaccesible"** → Verifica red local y puerto 5432.

**Un TPV muestra el rol incorrecto** → Ve a "Ver config" y verifica `BackupDirectoriesBOS`.

**Aparece "⚠ No apunta a: TPV X"** → Ejecuta "Reintegrar como secundario" o "Hacer principal" para recalcular rutas.

**Aparece "PRINCIPAL ⚠" con conflicto** → Usa "Dejar como secundario" en el TPV que vuelve de avería.

**ip_server incorrecto en Control Pista** → En condiciones normales se corrige automáticamente al ejecutar "Hacer principal". Si persiste, usa el desplegable de la pestaña Control Pista para corregirlo manualmente.

**psycopg2 aparece como False** → psycopg2 viene incluido en el runtime del paquete. Si aparece como no disponible, vuelve a ejecutar `INSTALAR.bat`, que reinstala el runtime desde `runtime\python-embed.zip`.

**Diagnóstico** → `http://127.0.0.1:5050/diagnostico`

---

## Desinstalación

1. Cierra la app
2. Borra la carpeta de instalación (`C:\GarumTPV`, `C:\GARUMTOOLS` o la ruta que elegiste)
3. Borra el acceso directo del Escritorio

---

## Historial de versiones

| Versión | Cambios principales |
|---------|---------------------|
| v7.4 | **Mejoras de UX y reorganización de pestañas — 12 cambios acumulados sobre v7.3, todos compatibles.** Sin cambios de schema ni de protocolo. **Usuario sistema (3 cambios):** (1) Comportamiento real "solo crea si no existe" — si `integracion4gl` ya existe en el equipo, NO se toca (ni contraseña, ni grupo, ni flags). Textos UI alineados con esa realidad: el botón pasa de "▶ Crear / actualizar en este equipo" a "▶ Crear si no existe en este equipo"; el texto descriptivo pasa de "Idempotente: si ya existe, solo se actualiza contraseña + flags + grupo" a "Si el usuario ya existe, **no se toca** (ni contraseña, ni grupo, ni flags). Solo se crea cuando falta". Docstring del endpoint `api_usuario_sistema_crear` también actualizada. (2) **Fix descripción 49→38 caracteres**: el campo `-Description` de `New-LocalUser` en PowerShell tiene un límite duro de 48 caracteres; la descripción anterior `"Usuario tecnico para integracion entre TPVs GARUM"` (49 chars) producía error `"El argumento 49 tiene una longitud de caracteres excesiva. Acorte la longitud de caracteres del argumento para que sea menor o igual que '48' e intente ejecutar el comando de nuevo"` al crear el usuario. Nueva descripción `"Usuario tecnico integracion TPVs GARUM"` (38 chars, holgura de 10). Como PowerShell valida el parámetro antes de crear el usuario, los intentos fallidos NO dejaban usuarios huérfanos. (3) UI rediseñada con tarjetas por paso (check / create / group) con 5 estados visuales (`pending` / `running` / `done` / `skipped` / `error`) y animación stagger. **Combustibles, antes "Artículos" (4 cambios):** (4) Sidebar y página renombrados de "Artículos" a "⛽ Combustibles" para diferenciarlos claramente del módulo "Artículos MPE" (otro contexto, otra tabla, distinto schema). (5) Columna **Comisión** ahora **EDITABLE** en la sub-tab "Ver" mediante toggle clicable que aplica el cambio en RED a todos los TPVs accesibles vía nuevo endpoint `POST /api/articulos/comision/red` (DELETE+UPDATE parametrizado por `articulo.codigo`). (6) Nueva columna `codigo_concentrador` (read-only, mono) mostrando el código numérico del articulo en el concentrador físico. (7) Imágenes `cc_<codigo_concentrador>.png` junto al nombre del articulo en **AMBAS** sub-tabs (Ver e Impuestos). Nuevo endpoint `GET /api/combustibles/imagen/<N>` sirve los PNG desde `C:\GARUM\images\carburante\imagenes_surtidor` con `send_file` + path traversal defense (`os.path.abspath().startswith(base_abs)`). Frontend usa `<img src="..." onerror="this.style.display='none'">` para degradación graceful si el PNG no existe. **Pista (1 cambio):** (8) La tabla de mangueras (sub-tab Surtidores) muestra también la imagen `cc_<codigo_concentrador>.png` en la columna Producto, junto al nombre del articulo asociado al tanque. Reutiliza el mismo endpoint `/api/combustibles/imagen/<N>`. La query `api_get_pista` ahora hace JOIN incluyendo `a.codigo_concentrador` y lo propaga al JSON de cada manguera. **Medios de pago (1 cambio):** (9) "Artículos MPE" eliminado del sidebar como módulo independiente y **movido como sub-tab dentro de "Medios de pago"**: ahora hay 2 sub-tabs (`💳 Medios de pago` con tabla `mpe`, `📦 Artículos` con tabla `articulo_mpe`). Cada sub-tab conserva su propio grupo de acciones de cabecera (search + selector TPV + botón Leer BD) que se intercambia según el sub-tab activo. El selector de TPV NO se comparte (cada sub-tab puede estar viendo un TPV distinto). Compatibilidad backward: `irA('articulos')` sigue funcionando — redirige a `irA('integrados')` y activa el sub-tab Articulos. Estado del sub-tab activo persiste en `window.mpState.tab` durante la sesión. **Reintegrar TPV (2 cambios):** (10) Plan en vivo rediseñado como **step-cards** (mismo patrón visual que el módulo Usuario sistema): cada paso es una tarjeta con icono + texto descriptivo + estado, con animación de transición suave entre estados. CSS `.step-card*` extraído del previo `.usys-card*` para reutilización. (11) Aviso "Para TPVs que ya estaban en la red. Si es nuevo → 🔧 Nuevo TPV" **movido al INICIO** del módulo. Antes quedaba enterrado debajo de la tarjeta de detección y muchos técnicos lo pasaban por alto. Cero modificaciones en módulos no afectados (Panel, Propiedades integración, Impresoras, Sondas, Personal, Configuración TPV, Control Pista, Series, Clientes, Nuevo TPV, Tipo de estación, Ajustes). |
| v7.3 | **Nuevo módulo "🔐 Usuario sistema" integrado dentro de Reintegrar TPV + importación de contadores de serie desde XML + 4 mejoras en Reintegrar.** Todos los cambios son compatibles con v7.2. **Módulo "🔐 Usuario sistema"**: crea o actualiza un usuario local de Windows con datos hardcoded (`integracion4gl` / pwd hardcoded / grupo Administradores via SID built-in `S-1-5-32-544` para soportar Windows en cualquier idioma / `-PasswordNeverExpires` / `-AccountNeverExpires`). 2 endpoints nuevos: `GET /api/usuario-sistema/info` (devuelve el nombre del user sin pwd) y `POST /api/usuario-sistema/crear` (ejecuta script PowerShell `Get-LocalUser` / `New-LocalUser` / `Set-LocalUser` + `Add-LocalGroupMember`, idempotente). UI: como sección `<details>` colapsable "PASO PREVIO" al **inicio del módulo Reintegrar TPV** (no como módulo independiente en sidebar) con badge ámbar indicador. Render del resultado parsea los markers `USER_CREATED/USER_UPDATED/GROUP_ADDED:NAME/GROUP_ALREADY:NAME/GROUP_ERROR:msg` devueltos por PowerShell para mostrar checklist con iconos por paso. **Integración SMB en Reintegrar paso 6**: antes del `robocopy \\IP\C$\GARUM`, el job hace `net use \\IP\C$ /delete` (cleanup silencioso) → `net use \\IP\C$ /user:integracion4gl <pwd>` para autenticar la sesión SMB con credenciales explícitas; tras el robocopy, `net use /delete` en `finally` (cleanup). Esto permite que el robocopy funcione independientemente del usuario Windows activo en el TPV destino — la única condición es que `integracion4gl` exista también en el principal (precisamente lo que el módulo Usuario sistema ejecutado allí garantiza). Si `net use` falla, step 6 queda en `error` con mensaje claro "comprueba que el usuario integracion4gl existe en {ip}". **Módulo "📅 Series" — sub-tab "↑ Importar números"**: la página Series ahora tiene 2 sub-tabs con patrón `ctab-bar` reutilizado. La nueva sub-tab permite subir un XML con la lista de `serie.numero` (la gestoría/cliente lo entrega tras un Reintegrar para fijar los contadores reales). Flujo: `<input type="file" accept=".xml">` con `FileReader` lee el contenido en el navegador → POST `/api/series/numero/preview` (parser flexible que acepta atributos `<serie codigo="X" numero="Y"/>`, hijos `<serie><codigo>X</codigo><numero>Y</numero></serie>` o alias `<item><nombre>X</nombre><contador>Y</contador></item>` — busca recursivamente con `el.iter()` y deduplica) → devuelve `[{serie, numero_xml, numero_actual, accion}]` con `accion` ∈ {`actualizar`, `sin_cambio`, `no_existe`} → render con código de colores (verde/gris/rojo) en tabla con scroll vertical y header sticky → botón "✓ Aplicar al TPV local" filtra solo `actualizar` y POST `/api/series/numero/aplicar` que hace UPDATE atómico en transacción contra `127.0.0.1` por cada serie devolviendo `{actualizadas, no_encontradas, errores}`. Resultado se muestra en modal `ovRed` reutilizado. Parser defensivo contra XXE (usa `xml.etree.ElementTree` stdlib sin entidades externas). **Reintegrar paso 3 mejorado**: ahora marca `serie.propia=TRUE` buscando primero el marcador `(N)` en `serie.descripcion` (`UPDATE serie SET propia = TRUE WHERE descripcion LIKE '%(N)%'`). Si no encuentra nada cae al método antiguo (regex 4 chars sobre `serie.codigo` + `LIKE _0X{num}`). Convención del cliente: el campo descripción contiene `(N)` donde N es el número de TPV. **Reintegrar step 6 → step 7 encadenado**: si la copia de C:\GARUM falla (`step 6 = error`) y el usuario había pedido editar hibernate (`editar_hibernate=true`), se salta el step 7 marcándolo como `skipped` con log claro "Como la copia de C:\GARUM falló en el paso 6, hibernateCentral.cfg.xml puede no existir en este equipo o estar obsoleto. NO se va a editar automáticamente. Realiza AMBOS pasos manualmente: 1) copia C:\GARUM. 2) edita el XML con jdbc:postgresql://<ip>:5432/tpv". Frontend lo refleja en la tarjeta final con banner ámbar, fila roja en la tabla resumen, y lista numerada de pasos manuales. **Reintegrar — modal de progreso en vivo durante la copia**: nuevo modal `ovCopia` que se abre automáticamente cuando `r.steps['6'] === 'running'` y se cierra cuando sale de ese estado. Muestra el origen `\\IP\C$\GARUM` + destino `C:\GARUM` + spinner ⏳ animado + **contador `MM:SS`** en `var(--blue-bg)` que se actualiza cada 500ms via `setInterval` + bloque `<pre>` con la **última línea del log** (busca hacia atrás los últimos 40 logs ignorando separadores `═══`). Cleanup del timer en `done`, `irA()` y `visibilitychange='hidden'`. Backend cambiado de `subprocess.run` a `subprocess.Popen` con `bufsize=1` y stream línea a línea para que cada fichero copiado aparezca en tiempo real (quitado el flag `/NFL` de robocopy). Throttling: cada línea pasa por `_job_log` con prefijo cortado a 160 chars y eliminando el prefijo de path largo. **UI menor**: helper text del checkbox "Copiar C:\GARUM" acortado de 3 frases a una sola línea ("Útil tras reinstalar Windows. Requiere admin en el principal."). Cero cambios en módulos no afectados — Panel, Propiedades, Impresoras, Sondas, Pista, Personal, Medios de pago, Configuración TPV, Control Pista, Artículos MPE, Artículos, Clientes, Nuevo TPV, Tipo de estación intactos. |
| v7.2 | **Nuevo módulo "📋 Artículos" + mejoras importantes en Reintegrar TPV + fix crítico en Panel.** Release de feature + fixes acumulados sobre v7.1, todos compatibles. **Módulo "📋 Artículos"** (pestaña nueva en sidebar entre "Artículos MPE" y "Series"): dos sub-tabs `ctab-bar`: (1) **"📋 Ver artículos"** — tabla read-only de articulos con filtro fijo `asignable_tanque=TRUE AND carburante=TRUE` (gasolinas, dieseles), columnas ID/Código/Nombre/Comisión/Impuesto. La columna Impuesto muestra el porcentaje grande (mono+negrita+teal, alineado a la derecha en 54px) seguido del nombre. (2) **"💶 Impuestos"** — editor visual: cada articulo presenta un badge clickable con borde punteado teal mostrando porcentaje grande + nombre + ✏. Click abre el modal `ovImpuesto` con grid 3 columnas de cards (porcentaje gigante 22px en monoespaciada + nombre debajo + id pequeño en esquina); card actual marcada con ✓ + fondo teal; hover lift 2px; click aplica el cambio en RED via `aplicarRedYMostrar` reutilizando el modal `ovRed`. **Schema real**: tabla intermedia `articulo_impuesto(id_articulo, id_impuesto)` + master `impuesto(id_impuesto, nombre, clase, cantidad, id_impuesto_externo, update_date, update_user)`. **3 endpoints nuevos:** `GET /api/articulos_carburante` (LEFT JOIN `articulo` → `articulo_impuesto` → `impuesto` con alias `nombre_impuesto/cantidad_impuesto/clase_impuesto`, cantidad convertida a float para JSON), `GET /api/tipos_impuesto` (`SELECT id_impuesto, nombre, clase, cantidad, id_impuesto_externo FROM impuesto ORDER BY clase, cantidad, id_impuesto`), `POST /api/articulos/tipo_impuesto/red` (estrategia DELETE+INSERT atómica por TPV: valida que el `id_impuesto` existe + localiza `id_articulo` local por `codigo` con filtros defensivos + `DELETE FROM articulo_impuesto WHERE id_articulo=local` + `INSERT (id_articulo, id_impuesto)`; body acepta tanto `id_impuesto` como `id_tipo_impuesto` por backward-compat). El articulo se identifica por `codigo` (estable entre BDs, los `id_articulo` locales pueden diferir). **Reintegrar TPV — DROP+CREATE en lugar de `--clean --if-exists`:** algunas versiones de pg_restore en Windows rechazaban los flags `--clean --if-exists` cuando iban después del filename con "demasiados argumentos en la línea de órdenes". Nueva estrategia: terminar sesiones activas + `DROP DATABASE` + `CREATE DATABASE` con ENCODING UTF8 + `pg_restore` sobre BD recién creada sin flags conflictivos. Más robusto, independiente de la versión de PostgreSQL, garantiza BD limpia (sin objetos huérfanos de intentos previos). Si la preparación de BD falla, marca step 2 como error con mensaje claro (antes solo logueaba "Aviso" y seguía, ocultando problemas). **Reintegrar TPV — nuevo paso 6: copia de C:\GARUM:** entre los ajustes de BD y la edición de hibernate, robocopy recursivo de `\\IP\C$\GARUM` → `C:\GARUM` con `/E /COPY:DAT /R:1 /W:2` + flags silenciosas (`/NFL /NDL /NJH /NJS /NC /NS /NP`). Opcional via checkbox "Copiar C:\GARUM del principal" (default ON) en la tarjeta de opciones avanzadas. Salvaguardas: si `ip_origen` es localhost se skippea (no tiene sentido copiar de uno mismo); timeout 10 min en el subprocess; si robocopy.exe no existe o falla con exit≥8, paso 6 queda en `error` con log claro (sugiere "¿este usuario es admin en {ip_origen}?") pero el job entero NO se marca como error porque el resto del proceso fue OK. El plan en vivo pasa de 6 a 7 pasos (hibernate ahora step 7). Tarjeta de resultado actualizada: banner ámbar también cuando falla la copia GARUM (no solo hibernate); título contextual con 4 variantes; nueva fila en la tabla resumen "C:\GARUM (carpeta)" con 3 estados; lista de próximos pasos manuales combinada (copia + hibernate + reinicio). **ConfTPV — nuevo toggle borrar_display_surtidor_sin_suministros:** campo de `configuracion_estacion` (no `configuracion_tpv`) expuesto en la pestaña "⚙ Configuración TPV". `api_get_conf_tpv` ahora hace dos queries en la misma conexión (una a cada tabla) y fusiona el resultado en un único dict `config`. Si la query de `configuracion_estacion` falla (tabla vacía, schema viejo), se loguea warning pero el endpoint no se rompe. Endpoint `/api/configuracion_tpv/red` ahora **despacha a la tabla correcta** según el campo recibido: si está en `_CAMPOS_CONFTPV` escribe a `configuracion_tpv`; si está en nueva whitelist `_CAMPOS_ESTACION_DESDE_TPV` escribe a `configuracion_estacion`. Defensa multi-nivel mantenida (`_TABLAS_PERMITIDAS_RED` + `_CAMPOS_PERMITIDOS_POR_TABLA`). **Fix crítico Panel — botón "Dejar como secundario":** en v7.1 el HTML generado para este botón contenía comillas dobles literales dentro del atributo `onclick="..."` (que ya estaba delimitado por `"`), rompiendo el parseo HTML del navegador en el primer `"` interno. Resultado: el onclick se cortaba a `pedirDejarSecundario(2,` y el resto se interpretaba como atributos HTML basura. El click no ejecutaba la función. Solo se manifestaba en el escenario de conflicto de principal (2 TPVs con `principal=TRUE` simultáneamente). Fix: usar `&quot;` (entidad HTML) en lugar de `"` literal + escape con `H()` para defensa adicional contra caracteres especiales en nombres de TPV. **Otros detalles internos v7.2:** helper genérico `_job_step(job, n, status)` ahora gestiona estados de 7 pasos (no 6); `range(1, 8)` en inicialización; tracking de `lastCopiarGarum` en `reiState` con persistencia en `sessionStorage`; recuperación de job activo tras refresh restaura también el flag de copia; CSS nuevo para `.imp-badge` (selector cerrado), `.imp-grid` + `.imp-card` (modal de tipos de impuesto), con `:hover` lift, estado `.active` con ✓ y `--blue-bg` como fallback de `--teal-bg` (que no existía como variable); modal nuevo `ovImpuesto` con título dinámico, subtítulo con artículo seleccionado y aviso ámbar de impacto en red. Cero modificaciones en módulos no afectados (Sondas, Personal, Medios de pago, Pista, Control Pista, Artículos MPE, Series, Clientes, Nuevo TPV, Tipo de estación, Propiedades, Impresoras). |
| v7.1 | **Nuevo módulo "🔄 Reintegrar TPV"** — flujo independiente para reintegrar a la red un TPV cuya BD se ha perdido (corrupción / reinstalación de Windows / equipo nuevo con el mismo rol). Reusa el ~70% del código de "🔧 Nuevo TPV" pero SALTA los pasos que solo aplican a un puesto nuevo (crear series, registrar fila en `tpv` del principal, insertar `pos`, propagar `propiedad.CopyDirectories` al resto). **Operación 100% local**: lectura remota del TPV1 vía `pg_dump`, todas las escrituras (`pg_restore`, UPDATEs, edición de XML) van a `127.0.0.1` y a ficheros locales — ningún otro TPV se toca. **Backend nuevo:** constante `_REINT_IP_PRINCIPAL = "10.0.0.101"`, helpers `_detectar_num_tpv_local()` / `_detectar_ip_local()` (auto-detección por `socket.gethostbyname_ex` + `socket.getaddrinfo` con `sorted()` para reproducibilidad en dual-NIC, rango `10.0.0.101..10.0.0.109`), `_job_step(job, n, status)` (helper genérico para marcar pending/running/done/error/skipped — reutilizable por futuros jobs paso-a-paso). **2 endpoints nuevos:** `GET /api/reintegrar/info` (pre-vuelo: detección + sugeridos `num_tpv_sugerido` + `ip_origen_sugerida`) y `POST /api/reintegrar/iniciar` (acepta overrides opcionales `num_tpv` ∈ [2,9], `ip_origen` validada con `val_host()` reusado + whitelist `_REDES`, `ip_local` con default `10.0.0.10{num_tpv}`, `editar_hibernate` bool default True). Reutiliza `GET /api/instalar/progreso/<job_id>` para el polling (ahora devuelve también `job["steps"]`). **`_job_reintegrar` en 4 fases / 6 pasos del plan:** (1) `pg_dump` TPV1 → step 1, (2) `pg_restore` a 127.0.0.1 con `--clean --if-exists` → step 2, (3a) detección de `id_estacion` por regex en `serie`, `UPDATE serie SET propia=TRUE WHERE serie LIKE %s` + reapuntar `regla_facturacion` tienda/carburante → step 3, (3b) `UPDATE tpv SET principal=FALSE` + `UPDATE tpv SET principal=TRUE WHERE id_tpv=%s` → step 4, (3c) `UPDATE local_config SET ip = %s` + `UPDATE local_config SET pos_version_id_local = 10+num_tpv` → step 5, (4) edición de `C:\GARUM\hibernateCentral.cfg.xml` con `re.subn` (distingue n=0 "URL no encontrada" de "ya apuntaba bien"), backup `.bak`, escritura atómica `.tmp + os.replace`, fallback `utf-8 → cp1252` → step 6 (skippable). **Frontend:** botón sidebar `🔄 Reintegrar TPV`, página `page-reintegrar` con 3 inputs editables (TPV destino, IP principal/origen, IP local — esta última auto-recalcula `10.0.0.10{num_tpv}` salvo que el técnico la haya tocado manualmente, tracked via `rei_ipLocalManual`), checkbox "Editar hibernateCentral.cfg.xml automáticamente" (ON por defecto), plan en vivo con 6 ítems que se van tachando con CSS `.rei-pending/-running/-done/-error/-skipped` (icono `::before` + `text-decoration:line-through` + `@keyframes rei-pulse` para el running), log técnico colapsable `<details>` (cerrado en éxito, auto-abierto en error o cuando step 6 falla con `editar_hibernate=true`), tarjeta de resultado tri-estado: verde (todo OK), ámbar (`hibernate` falló pero el resto OK — banner "⚠ TPV X reintegrado — falta editar hibernate a mano" + URL JDBC concreta en el bloque "Próximo paso"), rojo (fallo crítico — log auto-abierto + botón reintentar). **Resiliencia:** persistencia del jobId + params en `sessionStorage` (clave `rei_activeJob`) para sobrevivir refresh del navegador o cambios de pestaña — `rei_inicializar` consulta el storage y reanuda el polling; auto-cancel en respuesta 404 "Job no encontrado" con cleanup completo (timer + storage + UI); `irA()` y `visibilitychange` cancelan `reiState._pollTimer` además del `instState._pollTimer` (evita polls fantasma). **Coordinación con módulos existentes:** `api_instalar_progreso` ahora añade `"steps": job.get("steps", {})` a la respuesta — backward-compatible (jobs sin `steps` devuelven `{}`, `_instPollJob` del módulo "Nuevo TPV" lo ignora). Cero modificaciones en la lógica de los 14 módulos preexistentes (Panel, Propiedades, Impresoras, Sondas, Personal, Medios de pago, Configuración TPV, Pista, Control Pista, Artículos MPE, Series, Clientes, Nuevo TPV, Tipo de estación). Auditoría doble por agente (revisión funcional + revisión de regresiones) confirmó 0 críticos, 0 colisiones, 14/14 módulos intactos. |
| v7.0 | **Salto mayor — integración del módulo "👥 Clientes" desde el proyecto independiente `tpv-clientes` (Electron + Express + PostgreSQL).** Ya no se necesitan dos aplicaciones para gestionar la estación: toda la gestión de **clientes, vehículos, tarjetas y asociaciones cliente-tarjeta-vehículo** queda dentro de garum_tpv_manager con un solo instalador. **Nueva pestaña "👥 Clientes"** en sidebar con 4 sub-tabs (Clientes / Vehículos / Tarjetas / Asociaciones), selector de TPV propio igual que el resto de módulos (Sondas/Impresoras/Pista...) y **5 modales** (`ovCliente` con 3 sub-tabs internas Datos/Direcciones/Asociaciones, `ovVehiculo`, `ovTarjeta`, `ovBaja`, `ovAsociacion`). **21 endpoints nuevos** portados de Express a Flask: `GET/POST/PUT /api/clientes`, `GET /api/clientes/<id>` (con direcciones y asociaciones anidadas), `GET /api/cliente-tipos`, `GET/POST/PUT /api/vehiculos`, `GET/POST/PUT /api/tarjetas`, `GET /api/tarjeta-tipos`, `GET/POST/PUT /api/asociaciones` (con `?search` + `?show_deleted`), `GET /api/asociaciones/<id>`, `DELETE /api/asociaciones/<id>` (soft delete con `fecha_baja` opcional), `PATCH /api/asociaciones/<id>/restore`, `GET /api/provincias`, `POST /api/clientes/<id>/direcciones`, `PUT /api/direcciones/<id>`. Todos con `@need_conn` + `@csrf` en escrituras + patrón `c=None/try/finally` + mensajes genéricos. **Helper `_cli_conn()`** que resuelve `host_tpv` automáticamente del request (args → body JSON → `sess["host"]`) para que cada endpoint trabaje contra el TPV elegido sin tocar el código de cada función. Wrappers JS `cli_get`/`cli_post`/`cli_req` que inyectan `host_tpv` en URLs y bodies. **Validación de unicidad** en asociaciones: una tarjeta o vehículo no puede estar asignado a dos clientes activos. **NO portado:** `/api/config*` (garum tiene su login propio), `setInterval(checkConnection)`, sidebar oscuro de Electron, sección `#sec-config`, carga de provincias en UI (el endpoint sigue disponible). **Otros cambios acumulados en v7.0:** Pista — DOMS IP editable (`POST /api/pista/doms/ip/red`), sub-pestañas Surtidores/Productos/EPT (con `GET /api/pista/productos` filtrando `articulo.asignable_tanque=TRUE` y `GET /api/pista/ept`), layout compacto 1024×768, `accion_cola_completa` con desplegable estricto A/B. Impresoras — UI rediseñada sin duplicación de inputs (datalist abandonado por filtrado automático; reemplazado por `<select>` con todas las opciones + "Escribir manualmente"), detección PC local vs TPV remoto (aviso amarillo si remoto), pre-validación de tipos en backend (fix del 500 al guardar), `log()` con `flush=True` (logs inmediatos en `preview_logs`). Artículos MPE — quitadas columnas Precio/Actualización/Usuario, clase editable toggle vacío↔R (`POST /api/articulos_mpe/<id>/clase`). Personal — botón "Ver claves" funciona de nuevo (endpoint dedicado `GET /api/personal/passwords` bajo demanda; el GET normal sigue sin password por seguridad). Instalador — ruta por defecto `C:\GARUMTOOLS\GarumTPV`, NO pregunta (página Directory del NSIS eliminada + menú del .bat eliminado), `SetShellVarContext all` en NSIS para que el acceso directo aparezca para todos los usuarios del TPV. Distribución — script `sync-to-onedrive.bat` (robocopy `/E /XO`) replica el proyecto a OneDrive como backup acumulativo; el flujo de empaquetado lo ejecuta automáticamente tras cada bump. |
| v6.0 | **Salto de versión mayor — consolidación del módulo "⛽ Pista" como funcionalidad estable.** v6.0 agrupa todos los cambios de v5.13 en un release con número mayor para reflejar la magnitud del nuevo módulo (nueva pestaña completa con lectura + edición individual + edición global + reasignación de tanque + UI colapsable animada). Sin cambios respecto a v5.13 más allá del bump de versión, documentación reorganizada y reempaquetado. **Lo que aporta el módulo Pista:** vista jerárquica `Pista → Surtidores → Mangueras → Tanque → Producto`; cabecera con DOMS IP (`pista.ip_concentrador`); franja superior con 5 campos editables que aplican a **todos los surtidores simultáneamente** (`aviso_manguera_descolgada`, `alarma_manguera_descolgada`, `id_modo_operacion_surtidor_por_defecto`, `suministros_cola`, `accion_cola_completa`); cada surtidor tiene **cabecera clickable** con animación CSS suave (`grid-template-rows: 0fr ↔ 1fr`, transición 0.28s ease) que despliega su sección "Campos editables" individuales (6 mini-tarjetas grandes con etiquetas snake_case coincidentes con nombres de columnas SQL: `bajo_informatica` toggle bool, `numero_logico_concentrador`, `puerto_concentrador`, `direccion_fisica_concentrador`, `interface_tipo_general`, `interface_tipo_protocol` como int); cada surtidor expone botón "Ver mangueras (N)" como sub-toggle independiente que abre tabla con columnas Manguera / **Tanque (selector con todos los tanques visibles del TPV, reasignación en red por `numero_tanque`)** / Producto (info) / Conc. lógico (editable) / Aspiración (editable) / `id_manguera_externo` (editable text); tanques huérfanos (visibles sin manguera asociada) listados al final como aviso. **Identificación cross-TPV:** surtidor por `numero` (estable entre BDs), manguera por par `(numero_surtidor, numero_manguera)`, tanque destino por `numero` con resolución de `id_tanque` local en cada TPV via subquery — los IDs internos pueden diferir entre TPVs aunque la pista física sea la misma. **Endpoints nuevos:** `GET /api/pista`, `POST /api/pista/surtidor/campo/red`, `POST /api/pista/surtidor/global/red`, `POST /api/pista/manguera/campo/red`, `POST /api/pista/manguera/tanque/red`. **Whitelists:** `_CAMPOS_SURTIDOR_BOOL`, `_CAMPOS_SURTIDOR_INT`, `_CAMPOS_SURTIDOR_GLOBAL_INT`, `_CAMPOS_SURTIDOR_GLOBAL_CHAR`, `_CAMPOS_MANGUERA_INT`, `_CAMPOS_MANGUERA_TEXT`. **UI uniforme:** todas las etiquetas en snake_case coincidiendo con nombres de columnas SQL para que el técnico pueda relacionar con pgAdmin/DBeaver; mini-tarjetas con borde dashed + ✏ como convención visual de "editable"; fondo azul claro `#f4f9ff` en la franja global; confirmación con `confirm()` antes de operaciones globales por su impacto masivo. **Resto de la app sin cambios** respecto a v5.12 (hotfixes incluidos: no-cache en `/api/*` y `/`, "Hacer principal" en TPV desactivado sin principal, pestaña "Propiedades" auto-carga BD al entrar). |
| v5.13 | **Nuevo módulo "⛽ Pista"** — vista de la configuración física de la pista de surtido por TPV + edición en red de campos clave del surtidor + franja de configuración GLOBAL aplicable a todos los surtidores simultáneamente.

**Franja superior "⚙ Configuración global"** (fondo amarillo) — 4 campos que aplican a **TODOS los surtidores** de **TODOS los TPVs** (UPDATE masivo sin WHERE), pensados para configurar la pista de forma uniforme: `aviso_manguera_descolgada`, `id_modo_operacion_surtidor_por_defecto`, `suministros_cola` (int) y `accion_cola_completa` (character(1), A-Z). Endpoint `POST /api/pista/surtidor/global/red` con whitelist `_CAMPOS_SURTIDOR_GLOBAL_INT` / `_CAMPOS_SURTIDOR_GLOBAL_CHAR`. Si los surtidores tienen valores distintos entre sí, el badge muestra `(varía)` en rojo como aviso al técnico. Confirmación obligatoria con `confirm()` antes de aplicar (impacto: todos los surtidores de todos los TPVs).

**Resto de la entrada v5.13:** Endpoint nuevo `GET /api/pista` que devuelve la jerarquía completa en un solo JSON: surtidores → mangueras → tanque → artículo. Cabecera con `ip_concentrador` (DOMS) de la tabla `pista` para verificar a qué concentrador físico apunta el TPV. Por cada **surtidor**: número, concentrador lógico, puerto, flags (`predeterminador`, `auto_autoriza`), más una fila de **5 badges editables** (borde dashed + ✏) que aplican el cambio a **todos los TPVs accesibles** identificando el surtidor por `numero` (estable entre TPVs): `bajo_informatica` (bool, toggle), `puerto_concentrador`, `interface_tipo_general`, `interface_tipo_protocol`, `direccion_fisica_concentrador` (int, editor inline). Endpoint nuevo `POST /api/pista/surtidor/campo/red` con whitelist explícita `_CAMPOS_SURTIDOR_BOOL` + `_CAMPOS_SURTIDOR_INT`, patrón `_aplicar_red()` (ThreadPoolExecutor max_workers=4, mensajes genéricos al cliente, detalle en log local). Por cada **manguera** dentro del surtidor: número, qué `tanque` la alimenta, capacidad, producto (JOIN con `articulo.nombre`), flags (`breakaway`, `aspiracion`) — solo lectura. Si hay tanques visibles sin manguera asociada se listan al final en una tabla "Tanques sin manguera". Selector de TPV para la LECTURA (puedes auditar diferencias entre TPVs); la EDICIÓN aplica en red. Sin edición todavía de mangueras / tanques / pista; se añadirá en versiones siguientes cuando esté claro qué campos tiene sentido tocar. |
| v5.12 (hotfixes) | **3 hotfixes UX/cache post-auditoría**, todos dentro de v5.12 (sin bump de número). **(1)** Botón **"Hacer principal"** ahora aparece también en TPVs DESACTIVADOS cuando no hay ningún principal accesible en la red — antes solo aparecía con `principalCaido`, lo que dejaba al usuario sin salida en setup inicial o tras "Dejar como secundario" sin principal real. **(2)** Pestaña **"Propiedades de integración"** lee la BD automáticamente al entrar — bug heredado de v5.10/v5.11: `irA('propiedades')` solo poblaba el `<select>` sin disparar `cargarProps()`. **(3)** `Cache-Control: no-store` en TODAS las respuestas `/api/*` vía `@app.after_request` — síntoma post-actualización: pestañas Sondas/Impresoras/Propiedades mostraban "✕ No se pudieron leer..." aunque el backend respondía 200 OK; causa: el navegador servía respuestas cacheadas de la versión anterior. Tras instalar v5.12 conviene Ctrl+F5 una vez para limpiar lo cacheado de versiones previas. |
| v5.12 | **Auditoría pre-distribución a técnicos — endurecimiento (estabilidad + seguridad + limpieza).** Sin nuevas funcionalidades visibles; pestañas, botones y flujos siguen igual. **Seguridad:** `conn_tpv()` y `_conn_controlpista()` validan host con `val_host()` antes de abrir conexión (impide leak de password a IPs externas); `/api/sesion-cierre-turno/huerfanos` valida cada IP recibida (evita SSRF); `sess[]` se muta bajo `threading.Lock` (sin mezcla de credenciales bajo doble F5 o varias pestañas); `_update_simple_red(tabla, campo, ...)` añade whitelist explícita (`_TABLAS_PERMITIDAS_RED` + `_CAMPOS_PERMITIDOS_POR_TABLA`) que bloquea SQLi si un futuro caller pasa input no validado; `/api/personal` ya **no devuelve la columna password** (eran las contraseñas de los empleados del TPV); `/api/instalar/verificar-pg` pasa de GET a POST (la contraseña ya no aparece en query string / access logs / historial); mensajes psycopg2 dejan de propagarse al cliente — detalle solo en log local. **Estabilidad:** `statement_timeout=15000` ms en `conn_tpv()` y `_conn_controlpista()` (un UPDATE colgado ya no bloquea al worker indefinidamente); patrón `c=None / try / except / finally c.close()` aplicado a **~30 endpoints y helpers** (`api_get_props`, `api_set_props`, `api_get_impresoras`, `api_set_impresoras`, `api_get_sondas`, `api_get_integrados`, `api_set_mpe_*`, `api_get_personal`, `api_set_personal_*`, `api_get_depositos`, `api_get_totales_*`, `api_get_conf_tpv`, `api_get_estacion`, `api_get_articulos_mpe`, `api_update_articulo_mpe`, `api_huerfanos_sesion_cierre`, `_leer_tpvs_de_bd`, `probar_tpv`, `_leer_pos`, `leer_cp`, `leer_est`, `_ejecutar_en`, `_registrar_tpv_en`, `_job_restore`, ...) — fin de los conn leaks bajo errores intermitentes; `alog` convertido a `collections.deque(maxlen=500)` (bounded sin `pop(0)` O(n)); `app.run(threaded=True)` explícito; `_leer_config`/`_guardar_config` usan `threading.Lock` y escritura atómica (`tmp + os.replace`) — `config.json` ya no se corrompe; **editor de `hibernateCentral.cfg.xml`: backup `.bak` antes de sobrescribir + sanity-check del XML resultante + fallback `utf-8 → cp1252` + reemplazo seguro con `lambda`** (una regex que no matchea o un XML inválido ya no pueden dejar a GARUM sin arrancar = ya no obligan a una visita física al TPV); helpers JS `get()/post()` leen body en errores y propagan `r.error` del backend (el técnico ve `"No se pudo conectar al TPV"` en vez de `"HTTP 500"`); `try/finally` en botones JS (`conectar`, `editarRetiro`, `editarPerfil`, `verificar-pg`...) — los botones ya no quedan deshabilitados para siempre si la red falla; polls fantasma del asistente de Instalación se cancelan al navegar a otra pestaña y en `visibilitychange='hidden'` (flag `_pollInflight` evita avalanchas); `except: pass` (bare) sustituido por `except Exception: pass` en 8 sitios para no tragar `KeyboardInterrupt`/`SystemExit`/`MemoryError`. **Limpieza (~310 líneas eliminadas):** borrados 6 endpoints single-TPV deprecados (sustituidos por `/red` en versiones anteriores) — `POST /api/configuracion_tpv`, `/api/depositos/estacion-bool`, `/api/depositos/forma-pago-tipo`, `/api/totales-tarjetas/campo`, `/api/sondas/campo-red` (predecesor) y `/api/sondas/<id>/campo`; borrados 4 endpoints sin caller (`api_info`, `api_tpvs_count` + helper `_leer_tpvs_configurados`, `api_log`, `api_log_limpiar`); borradas en `index.html` `function reescanear` duplicada (corregía bug latente: el botón "Actualizar" del Panel ahora oculta `opR` como pretende), `function _badgeBool` huérfana y 4 re-imports redundantes de `ThreadPoolExecutor`/`as_completed`. |
| v5.11 | **"Medios de pago" — convención visual de campos editables:** los tres controles editables de cada tarjeta (toggle Activado/Desactivado, badge Factura Sí/No, badge Dev. c/f pago Sí/No) muestran ahora **borde punteado + icono ✏** — la misma convención que se usa en Sondas y Personal. Sin cambios funcionales: el clic sigue guardando en la BD igual. **Fix `UnicodeEncodeError` en Windows (cp1252):** `sys.stdout.reconfigure(utf-8)` al arranque + `try/except` en `log()` para evitar que caracteres como `→` (`→`) rompan las llamadas al backend en consolas con codificación heredada. **Sondas — propagación afinada:** al pulsar "Sí" en el prompt de propagación, `numero_logico_concentrador` solo se replica al mismo `numero_sonda` en los otros TPVs (es único por tanque), mientras que `puerto_concentrador` además actualiza todos los `configuracion_sonda` del TPV actual (compartido entre tanques). Texto del prompt diferenciado según el campo. |
| v5.10 | **"Medios de pago" — activar/desactivar editable:** cada tarjeta de medio de pago tiene ahora un **interruptor** para ponerlo Activado o Desactivado; el cambio se guarda en la BD (`UPDATE mpe SET activado`). Nuevo endpoint `POST /api/integrados/<id_mpe>/activado`. Además se corrige un bug de renderizado (una comilla mal cerrada descuadraba las tarjetas de la pestaña) y cada tarjeta muestra un borde lateral de color según el estado: verde = activo, gris = inactivo. Además, una franja en la cabecera de la pestaña incorpora el interruptor **"Conexión MPE"**, que activa/desactiva el campo `conexion_mpe` de la tabla `configuracion_avanzada` del TPV seleccionado (endpoint `POST /api/conexion_mpe`). |
| v5.9 | **Nuevo botón "Quitar sesión activa" en el Panel de TPVs:** cada tarjeta de TPV añade un botón que borra la sesión de ese TPV (`DELETE FROM sesion_tpv_activo WHERE id_tpv=N`) en **todos los TPVs accesibles, incluido el propio**. Expone como acción independiente el sub-paso que "Anular" ya ejecutaba — limpia la sesión sin desactivar el TPV ni tocar `CopyDirectories`/`pos`. Nuevo endpoint `POST /api/operacion/borrar_sesion` (CSRF + need_conn); reutiliza `_borrar_sesion_tpv`; el `id_tpv` lo envía el frontend (`_ip_a_id_tpv` queda solo de respaldo), válido también para el TPV con IP local `127.0.0.1`. GARUM recrea la sesión automáticamente. Además, el menú lateral **"Integrados"** pasa a llamarse **"Medios de pago"**. Nueva pestaña **"Series"** en el menú lateral — muestra la tabla `serie` de cada TPV (serie, descripción, factura/rectificativa/comisión/propia) con selector de TPV y buscador; endpoint `GET /api/series`. Y los TPVs inaccesibles muestran ahora un mensaje claro **"No se puede conectar con el TPV"** en lugar del error técnico de psycopg2. |
| v5.8 | **Instalador a prueba de antivirus:** `INSTALAR.bat` pasa a hacer solo operaciones de fichero (copiar y extraer). `ARRANCAR.bat` ya **va pre-hecho** en el paquete (`runtime\ARRANCAR.bat`) y el instalador solo lo copia — antes lo *generaba* línea a línea, patrón que los antivirus heurísticos detectan como *dropper* y cortan el proceso a media instalación (quedaba `app\` y `python\` sin `ARRANCAR.bat`). El instalador ya no ejecuta Python ni auto-arranca la app al terminar. Recomendado añadir una exclusión de antivirus para la carpeta de instalación. |
| v5.7 | **Instalador 100% offline — sin conexión a internet:** el paquete incluye Python 3.11.9 embebido con Flask y psycopg2 ya instalados (`runtime\python-embed.zip`, ~14 MB). `INSTALAR.bat` ya no descarga nada de internet: extrae el runtime incluido y verifica las dependencias. Imprescindible para TPVs en redes aisladas sin salida a internet. La instalación baja de 3-5 min a menos de 1 min. |
| v5.6 | **Detección del TPV nuevo en el Panel:**<br>**1)** Fix detección — el botón **"Actualizar"** del Panel ahora **relee la tabla `tpv`** de la BD (función `_releerTpvsDeBD`) y reconstruye la lista, así que **descubre TPVs nuevos sin reconectar**. Antes solo escaneaba la lista congelada al conectar y nunca la ampliaba.<br>**2)** La **Integración** registra el TPV nuevo en la tabla `tpv` del principal (paso 6): inserta su fila con `id_tpv` = nº de puesto, `principal=FALSE` y los flags de hardware copiados de la fila del TPV1. Así el programa lo detecta.<br>**3)** Nuevo campo **"ID TPV externo"** en el paso 1 del asistente — texto manual que 4GL facilita al técnico; se escribe en `tpv.id_tpv_externo` al registrar el TPV. |
| v5.5 | **Reglas de facturación editables y fix de `propia`:**<br>**1)** En el paso "Crear series", tras crearse las series aparece una **tabla editable** de `regla_facturacion`: cada regla (tienda / carburante) tiene un desplegable con las series propias del TPV para corregir manualmente la asignación si el reapuntado automático no acertó. Botón "Guardar reglas" → endpoint `POST /api/instalar/guardar-reglas`.<br>**2)** Fix `propia`: en el TPV nuevo la marca de `serie.propia` se aplica **siempre**. Antes, si la BD restaurada del TPV1 ya contenía las series del puesto, se omitía todo el bloque y las series propias del TPV quedaban en `propia=FALSE`. Ahora: las existentes → `propia=FALSE` y las 14 del puesto → `propia=TRUE`, existan o no (funciona en instalación nueva y en reinstalación). |
| v5.4 | **Refinamientos de series y estación:**<br>**1)** En "Cambiar tipo de estación", la serie de carburante comisionista se detecta automáticamente **por cada TPV** mediante `factura=TRUE, rectificativa=FALSE, comision=TRUE, propia=TRUE` — se elimina el desplegable manual. La tabla de estado añade columna "Serie comisionista (propia)". Si un TPV tiene 0 o varias candidatas, se omite con aviso.<br>**2)** En el módulo de Instalación, paso "Crear series": tras crear las series del TPV nuevo, se reapunta su `regla_facturacion` a sus series propias — fila `tienda` → serie "Factura" propia, fila `carburante` → serie "Factura Comisionista" propia. Solo cambia `id_serie`, mantiene la estructura.<br>**3)** Fix: el recuadro "Acción manual — Fichero Hibernate" de la pantalla de resultado ya no aparece cuando el fichero `hibernateCentral.cfg.xml` se edita automáticamente; solo se muestra si no se encuentra el fichero. |
| v5.3 | **Nuevo módulo "Cambiar tipo de estación"** — pestaña para cambiar la estación entre **Firme** y **Comisionista** en todos los TPVs accesibles. Lee el estado de la red (tipo actual, nº de carburantes, estado de `regla_facturacion`), el técnico elige el destino y, si es Comisionista, confirma la serie de carburante en un desplegable. El cambio actualiza por cada TPV, en una transacción: **1)** `articulo.comision` de los carburantes (`asignable_tanque=TRUE AND carburante=TRUE`) → TRUE/FALSE; **2)** `estacion.tipo_estacion` → `'C'`/`'F'`; **3)** `regla_facturacion` reestructurada (Firme = 1 fila tienda+carburante; Comisionista = 2 filas, carburante con serie comisionista separada). Un TPV sin `regla_facturacion` con `tienda=TRUE` se omite con aviso. Endpoints `GET /api/estacion/estado-red` y `POST /api/estacion/cambiar-tipo`. |
| v5.2 | **Módulo Instalación TPV ampliado:**<br>**1) Paso "Crear series"** — nuevo paso del asistente que crea las 14 series de facturación del nuevo puesto en TPV1 (`propio=FALSE`) y en el equipo local (`propio=TRUE`, marcando antes las existentes como `propio=FALSE`). Campos configurables N.º de puesto y ID estación. Endpoint `POST /api/instalar/crear-series`.<br>**2) `pos_version_id_local` automático** — al integrar, se actualiza `controlpista.local_config.pos_version_id_local` a `10 + N.º puesto`.<br>**3) Edición automática de `hibernateCentral.cfg.xml`** — el asistente reescribe la URL JDBC del fichero local apuntando al principal; ya no es una acción manual.<br>**4) Backup + Restore fusionados** — un solo paso con un botón que ejecuta backup de TPV1 y, al terminar, encadena automáticamente el restore. El módulo pasa de 6 a 5 pasos.<br>**5) Sub-pestaña "Borrar informes huérfanos"** en Configuración TPV — identifica y elimina registros de `sesion_cierre_turno` sin sesión activa en `sesion_tpv_activo`. Endpoint `POST /api/sesion-cierre-turno/huerfanos`. |
| v5.1 | **Nuevo módulo "Instalación TPV"** — asistente para integrar un TPV recién instalado como secundario: backup de las BDs `tpv` y `controlpista` de TPV1 vía `pg_dump`, restore local vía `pg_restore`, y configuración de la integración en la red. Procesamiento asíncrono por jobs con logs en tiempo real. Endpoints `verificar-pg`, `iniciar-backup`, `iniciar-restore`, `progreso/<id>`, `secundario`. |
| v5.0 | **Salto de versión mayor — cuatro frentes a la vez:**<br>**1) Nueva paleta visual — azules claros, diseño moderno** (estilo Linear / Stripe / Supabase). Sustituida la paleta beige + teal por slate + blue: fondo `#F1F5F9`, acento principal `#2563EB`, bordes slate, sombras con tinte azul. Modo oscuro reescrito con tonos slate-blue (`#0B1220`). Cabecera de tarjeta de sondas y panel de logs adaptados.<br>**2) Nuevo módulo "📂 Restaurar backup"** — botón en el header (junto al de Backup) que parsea el `.txt` generado por la app, muestra una vista previa por TPV (claves de `propiedad`, `ip_server`, filas de `pos`) con badges de accesibilidad, y tras una checklist obligatoria aplica los UPDATEs por TPV. Salta TPVs marcados `[INACCESIBLE]` o caídos ahora. Endpoint `POST /api/restaurar_backup` (CSRF + need_conn). Solo toca las 16 claves whitelist de `propiedad`, `local_config.ip_server` y `pos.online`; nunca `sesion_tpv_activo` ni columnas fuera del alcance.<br>**3) Instalador multi-ruta** — `INSTALAR.bat` ofrece menú: `[1] C:\GarumTPV` (por defecto), `[2] C:\GARUMTOOLS\GarumTPV` (subcarpeta dentro de GARUMTOOLS), `[3]` ruta personalizada. Toda la instalación (carpetas, `ARRANCAR.bat`, acceso directo, mensajes) se adapta a la ruta elegida.<br>**4) Optimización responsive 1024×768** — media queries en cuatro breakpoints (`1280 / 1100 / 1024 / 1024×800`) que reducen sidebar (228 → 200 → 180 → 170 px), topbar (52 → 42 px), padding del contenido, tarjetas TPV (`minmax` 300 → 230 px), grid de sondas a 1 columna en ≤ 1024 px, modales 92 vw y escala tipográfica. Botones, formularios e indicadores se compactan. Sin breaking en pantallas grandes.<br>**5) Fix detección "anulado de la red"** — un TPV inaccesible ya no muestra el botón "Anular de la red" si su `pos.online=FALSE` y ningún TPV accesible le apunta en `CopyDirectories`. La tarjeta muestra "○ Anulado (sin red)". Cuando recupera red entra automáticamente en "○ Desactivado" con el botón "Reintegrar como secundario", aunque su BD local conserve `CopyDirectories`. |
| v1.0 | Primera versión funcional con modo demo |
| v1.1 | Seguridad: validación de IPs, token CSRF, lista blanca de claves |
| v1.2 | Corrección: localhost permitido, mensajes de error visibles |
| v1.3 | Corrección: error de sintaxis JS, página de diagnóstico |
| v1.4 | Escaneo automático de TPVs, contraseña reutilizada en todos |
| v1.5 | SQL generado con valores exactos verificados contra la instalación real |
| v1.6 | Anular solo actualiza TPVs activos (no el averiado) |
| v2.0 | Rediseño UX completo: nav por tabs, acciones en tarjetas, checklist previa, panel resultado inline, aviso hibernate visual y copiable, selector de IP |
| v2.1 | Detección automática del rol real leyendo `BackupDirectoriesBOS`. Propiedades en formato vertical. |
| v2.2 | Corrección crítica: todos los campos de todos los TPVs se actualizan al cambiar principal. Versión en header. |
| v2.3 | Flujo para principal caído: "Hacer principal" en secundarios cuando el principal está inaccesible. |
| v2.4 | Avisos hibernate completos en todas las operaciones. |
| v2.5 | Botón "Reintegrar como secundario". Pestaña "Ajustes" para editar IPs. |
| v2.6 | Integración completa con BD `controlpista`: `ip_server` y `pos.online` automáticos. |
| v2.7 | Botón "💾 Backup config". |
| v2.8 | Corrección `sesion_tpv_activo`: `DELETE WHERE id_tpv=N` en lugar de borrar toda la tabla. |
| v2.9 | Corrección lógica: no se borra `sesion_tpv_activo` al reintegrar. Detección de discrepancias en `CopyDirectories`. Rediseño visual paleta 4GL. |
| v3.0 | Nueva pestaña
| v3.1 | Carga dinámica de TPVs desde tabla `tpv` de la BD al conectar. Config persistente en `config.json` (última IP usada, TPVs personalizados). Diagnóstico integrado en pantalla de login. Limpieza de código muerto (demo, J). Header renombrado a "Integración TPVs GARUM". Tab renombrado a "Propiedades integración TPVs". Backup oculto hasta conectar. |
| v3.2 | Soporte correcto para instalaciones de un único TPV
| v3.3 | Validación del config.json
| v3.4 | Nueva pestaña "🖨 Impresoras"
| v3.5 | Impresoras: los campos
| v3.6 | Corrección guión largo en desplegable Control Pista (\x2014). Aviso local en pestaña Impresoras. Pestaña Actividad eliminada. Validación sessionStorage con detección de datos corruptos. |
| v3.20 | Artículos MPE: JOIN con tabla `articulo` para mostrar el nombre del artículo. Nueva columna "Nombre artículo" junto a ID Art. El buscador también filtra por nombre. |
| v4.4 | Artículos MPE: edición inline de codigo_mpe. Botón "✏ Editar" en cada fila abre desplegable con los 31 productos del diccionario + campo manual. Guarda en BD (UPDATE articulo_mpe SET codigo_mpe, update_date=NOW(), update_user='garum_tpv_mgr'). Nuevo endpoint POST /api/articulos_mpe/<id>. |
| v4.3 | Tipografía: cambiado a Inter (Google Fonts) para display y cuerpo. Eliminadas fuentes Boska y Satoshi (Fontshare). Estilo más limpio y neutro, adecuado para herramienta de mantenimiento. |
| v4.2 | Fix Artículos MPE: MPE_LABELS y _artData movidos al inicio del script (variables globales) para evitar undefined por errores de ejecución previos. |
| v4.1 | Fix Artículos MPE: poblarSelArt usaba variable inexistente _tpvsConocidos — corregido para usar el array global tpvs con fallback a IP de sesión, igual que el resto de pestañas. |
| v4.0 | Rediseño completo UI — sistema Nexus: sidebar colapsable, paleta beige+teal, fuentes Boska+Satoshi (Fontshare), escala tipográfica fluida con clamp(), modo oscuro con toggle persistente (localStorage), skeleton/empty states. Sidebar oculto en login, visible solo tras conectar. Salto de versión mayor por rediseño completo. |
| v3.20 | Rediseño completo UI — sistema Nexus: sidebar colapsable, paleta beige+teal, fuentes Boska+Satoshi (Fontshare), escala tipográfica fluida con clamp(), modo oscuro con toggle persistente (localStorage), estados skeleton y empty states. Eliminada barra de tabs horizontal. |
| v3.19 | Artículos MPE: añadido diccionario de 31 códigos MPE → etiqueta de producto (EFITEC 95, DIESEL e+, ADBLUE, AUTOGAS, GNL, etc.). Nueva columna "Producto" en la tabla. El buscador también filtra por nombre de producto. |
| v3.18 | Nueva pestaña "📦 Artículos MPE": muestra la tabla `articulo_mpe` (BD tpv) con selector de TPV, buscador en tiempo real y tabla con columnas ID Art., ID MPE, Código MPE, Clase, Precio, Última actualización y Usuario. Solo lectura. |
| v3.17 | Sondas: eliminado badge "Fugas OFF/ON" de la cabecera de cada tarjeta. Conc. lógico y Puerto conc. ahora aparecen como badges directamente visibles en la cabecera (sin necesidad de abrir el desplegable Configuración sonda). |
| v3.16 | Fix Guardar en BD (Configuración TPV): botón pasa el contexto correctamente, mensaje verde de éxito y rojo de error inline, botón deshabilitado durante el guardado. |
| v3.15 | Header: título cambiado de "Integración TPVs GARUM" a "Mantenimiento Garum". |
| v3.14 | Header: nombre y tipo de estación leídos de la tabla `estacion` (tipo C=Comisionista, F=Firme), visibles tras conectar. Endpoint `/api/estacion`. Se oculta al desconectar. |
| v3.13 | Sondas: eliminado subtítulo técnico de la cabecera de la pestaña. |
| v3.12 | Sondas: corrección visual de cabecera — badge "Tanque XX" blanco con texto marino, badge "Fugas OFF" visible en fondo oscuro, badges de nivel crítico/bajo con colores propios, subtítulo pista más legible (opacidad .80). |
| v3.11 | Corrección etiqueta "Habilitar forma de pago Efectivo" (eliminado dos puntos). |
| v3.10 | Fix sondas: filtro de tanques sin sonda activa (id_configuracion_sonda IS NOT NULL), título siempre "Tanque XX" con nombre sonda como subtítulo. Fix pestaña Configuración TPV: funciones JS poblarSelConfTPV y cargarConfTPV no existían — implementadas con toggle para habilitar_forma_pago_efectivo. |
| v3.9 | Nueva pestaña "🔍 Sondas": visualización gráfica de tanques con SVG animado (nivel, agua, escala 25/50/75%), KPIs de medición/libre/temperatura, fila de métricas secundarias, config plegable. JOIN de tablas tanque + configuracion_sonda + sonda. Solo lectura. |
| v3.8 | (versión anterior — sin cambios documentados) |
| v3.7 | Auditoría de seguridad completa: rollback en todas las funciones de BD (_borrar_sesion, _actualizar_controlpista, _set_pos_online). @need_conn en endpoints de log y config/tpvs. Eliminación de funciones muertas JS (demo, limpiarLog, J). |
| v3.6 | Corrección: desplegables de TPV en pestañas Impresoras y Configuración ahora muestran la IP de sesión (127.0.0.1) cuando ningún TPV es accesible por red. |
| v3.6 | Impresoras: campo "Puerto impresora" también con desplegable de puertos Windows (USB, TCP/IP, LPT, COM) detectados via PowerShell/wmic, ordenados por tipo. Opción "Escribir manualmente" siempre disponible. | "Nombre impresora ticket" y "Ruta impresora facturas" muestran un desplegable con las impresoras instaladas en Windows (via PowerShell/wmic). Si no se detectan, permite escribir manualmente. Opción "Escribir manualmente..." siempre disponible. |: lee y edita la tabla `configuracion_impresion` de cada TPV. 5 campos editables (nombre impresora, ruta facturas, driver, puerto, formato T/4). El resto de campos en modo solo lectura. | al cargar: si los TPVs guardados tienen formato incorrecto se ignoran y se cargan de la BD. Corrección del botón Backup (ID incorrecto). Robustez en lectura de controlpista durante el backup. |: `CopyDirectories=''` es válido y el TPV se muestra como "Integrado". Aviso explicativo al intentar anular el único TPV principal. Pantalla Ajustes muestra TPVs reales de la BD con indicador de estado y aviso si la IP difiere de la calculada. | "🖧 Control Pista"
| v3.1 | La app lee la tabla `tpv` de la BD al conectar para cargar solo los TPVs realmente configurados en la instalación. Si hay 2 TPVs muestra 2, si hay 4 muestra 4. No asume siempre 4 TPVs. |: ver y modificar `ip_server` y `pos` en tiempo real. Botón "Dejar como secundario" para resolver conflictos de principal cuando un TPV vuelve de avería. Detección visual de conflicto de principal (badge rojo + aviso ámbar). Eliminada operación "Preparar TPV con IP temporal" — el reenganche se gestiona directamente con la IP definitiva. |
