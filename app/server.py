"""
GARUM TPV Manager - Backend v8.0
==================================
v8.0:   AUTO-ACTUALIZACION desde la nube 4GL. Cambio mayor que cierra el
        flujo de distribucion: ya no hay que descargar e instalar a mano.

        Nuevo modulo "🔄 Actualizar" (en sidebar):
          - Al login, check automatico silencioso contra
            https://4gl.fortiddns.com:1604/descargas/version_manager.txt
            (fichero ligero 1 KB con la version actual). Si la version
            remota > APP_VERSION local → badge en sidebar + banner en Panel.
          - Boton "▶ Descargar e instalar" en la pestaña Actualizar.
          - Al pulsarlo: descarga el ZIP de distribucion completo (~40 MB),
            lo descomprime en C:\\GARUMTOOLS\\Update\\, localiza el
            Setup-vX.exe interno, lo ejecuta como proceso DESACOPLADO
            (DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP), y cierra la
            app via os._exit(0) tras 5 s (suficiente para que el setup
            haya iniciado pero antes de que intente sobrescribir ficheros).

        Constante nueva APP_VERSION="8.0" — fuente unica de verdad para
        version. Sidebar la lee dinamicamente via /api/app-info, asi los
        futuros bumps solo requieren cambiar esa constante.

        Helper extraido _descargar_url_a_fichero(url, dest, timeout, ua):
        descarga atomica (.tmp + replace) con fallback SSL no-verify.
        Usado por api_setup_garum_descargar y api_actualizar_aplicar.

        3 endpoints nuevos:
          GET  /api/app-info         — devuelve {version, name} (publico)
          GET  /api/actualizar/check — compara version local vs remota
          POST /api/actualizar/aplicar — descarga ZIP + descomprime + lanza
                                          setup desacoplado + sys.exit(0)

        Casos defensivos:
          - Sin red al login → check falla silencioso, sin badge ni error.
          - Local >= remota → sin badge (no avisar update si no procede).
          - Setup.exe no encontrado en el ZIP → error claro, no se cierra.
          - Doble clic en "Aplicar" → flag _actualizando previene race.
          - URL no responde → mensaje neutro, no expone detalle tecnico.

v7.6:   Nuevo PASO 0 "Descargar instaladores" en Reintegrar TPV + Nuevo TPV.
        Bloque <details> colapsable al principio de ambos modulos que:
          1. Descarga https://4gl.fortiddns.com:1604/descargas/Setup-GARUM.zip
             a C:\\GARUMTOOLS\\Setup-GARUM.zip (escritura atomica .tmp+replace,
             fallback SSL no-verify si el cert de FortiDDNS falla).
          2. Descomprime automaticamente a C:\\GARUMTOOLS\\Setup-GARUM\\
             (zipfile + defensa zip-slip). Limpia carpeta destino antes.
          3. Muestra al tecnico el path destino + "ejecuta BBDD, Java, GARUM".
        Endpoints: GET /api/setup-garum/info, POST /api/setup-garum/descargar.
        El bloque HTML esta duplicado en page-reintegrar y page-instalacion
        pero usa clases en vez de IDs para que la misma funcion JS controle
        ambas instancias sin colisiones de getElementById.

v7.5:   Nuevos modulos y mejoras de UX sobre v7.4, todos compatibles.
        16 cambios acumulados desde v7.4:

        SERIES — REDISENO COMPLETO DEL MODULO
        --------------------------------------
        1. Sub-tab "✏ Marcar descripciones": añade el sufijo (N) al campo
           serie.descripcion de las series propias=TRUE. Convencion del
           cliente: el N entre parentesis identifica al TPV propietario.
           Idempotente (no duplica si ya esta marcado). RTRIM antes de
           concatenar para evitar espacios feos ("X (1)" → "X(1)").
        2. Sub-tab "🗺 Mapa Series → TPV" (NUEVA, default): vista de red
           consolidada. Escanea en paralelo todos los TPVs accesibles y
           muestra las series propias de cada uno con badges informativos
           segun las booleanas de schema (factura/simplificada/no_venta/
           rectificativa/comision/credito/contado/externo/firma/AEAT).
           Detecta automaticamente conflictos (misma serie marcada como
           propia en varios TPVs — sintoma de mala configuracion).
        3. Sub-tab "📋 Ver series" ELIMINADA: el Mapa Series → TPV cubre
           su funcion con vista de red en vez de single-TPV.
        4. Endpoint /api/series/marcar/global: marcado avanzado en 2
           fases. Fase 1 descubre propietarios escaneando toda la red;
           fase 2 en cada TPV marca CADA serie (propias Y ajenas) con
           el (N) del propietario REAL. Idempotencia conservadora:
           respeta cualquier (N) preexistente sin machacarlo.
        5. /api/series/marcar/global acepta body {dry_run:bool}: si
           True hace SELECT sin UPDATE, devuelve hasta 5 ejemplos por
           TPV (antes/despues). Usado por el preview previo en UI.
        6. UI flujo unificado: un solo boton "🔭 Previsualizar marcado
           global" → resumen visual con DRY RUN banner + tabla por TPV
           con ejemplos → boton "✓ Aplicar cambios" cuando el tecnico
           ha revisado. Reemplaza dos botones previos (TODA la red /
           marcado global) que confundian.

        REINTEGRAR TPV
        ---------------
        7. Permite reintegrar el propio TPV1 (rango 1..9, antes 2..9).
           Caso real: TPV1 cayo y se reinstala desde el TPV que tomo
           el rol de principal. Frontend + backend actualizados.
        8. Auto-deteccion del principal vivo en la red (no asume TPV1).
           Lee propiedad.BackupDirectoriesBOS de cada TPV: si NO empieza
           por '//' (comentado), ese TPV es principal real. La columna
           tpv.principal=TRUE NO sirve para esto porque en cada BD
           identifica al propio TPV (autoreferencia local).
        9. Campos renombrados a lenguaje mas directo:
              "IP del TPV principal / origen" → "IP del TPV a clonar"
              "IP local de este TPV"          → "IP local de este equipo"
           Hints reescritos sin jerga tecnica.

        USUARIO SISTEMA
        ---------------
       10. Mensaje claro cuando la pwd no cumple la politica de Windows
           local: detecta InvalidPasswordException de PowerShell y
           emite instrucciones especificas ("Abre secpol.msc → Directiva
           de contrasenas → deshabilita Complejidad + Longitud minima").
           Antes mostraba el error tecnico crudo.

        UX GENERAL
        ----------
       11. Paleta visual mas calida (paper-like #F6F5F1). Sidebar y
           topbar comparten el fondo crema — solo las tarjetas son
           blancas (estilo Notion/iA Writer). Reduce fatiga visual
           en sesiones largas.
       12. Textos descriptivos cortados a 1-2 lineas en sub-tabs de
           Series. Los tecnicos no leen parrafos largos.

        FIXES INTERNOS
        --------------
       13. Typo sess.get("pwd") → sess.get("password") en 4 endpoints
           nuevos que rompian con "fe_sendauth: no password supplied".
       14. /api/series/marcar/red: quitado filtro `tpv.accesible` (se
           desactualiza entre escaneos) y delegado al try/except del
           connect. Frontend usa claves nativas del backend para que
           rellenarOvRed las pinte directamente; nuevo campo `info`
           opcional para mostrar detalles de exito.
       15. /api/series/mapa-red: SELECT corregido (no existe la columna
           `ticket` en schema serie; reemplazado por las booleanas
           reales credito/contado/no_venta/sistema_venta_externo/
           firma_digital/envio_fiscal).
       16. Otros pulidos: banner v7.4 → v7.5 en sidebar; algunos
           tooltips reescritos.

v7.4:   Mejoras de UX y reorganizacion sobre v7.3, todos compatibles.
        12 cambios acumulados desde v7.3:

        1. USUARIO SISTEMA — comportamiento real "solo crea si no existe":
           si el usuario ya existe NO se toca (ni pwd, ni grupo, ni flags).
           Textos UI alineados ("Crear si no existe", no "Crear/actualizar").
        2. USUARIO SISTEMA — fix descripcion de 49→38 caracteres (limite
           PowerShell -Description = 48). Antes daba error al crear.
        3. USUARIO SISTEMA — UI rediseñada con tarjetas por paso (estados
           pending / running / done / skipped / error), stagger animation.

        4. COMBUSTIBLES (antes "Articulos") — sidebar renombrado y pagina
           con titulo "⛽ Combustibles". El concepto "Articulo MPE" sigue
           usandose para la tabla articulo_mpe (otro modulo).
        5. COMBUSTIBLES — columna Comision (booleana) ahora EDITABLE en la
           sub-tab "Ver". Cada cambio se aplica en RED a todos los TPVs
           accesibles via /api/articulos/comision/red (DELETE+UPDATE
           parametrizado por codigo).
        6. COMBUSTIBLES — nueva columna codigo_concentrador (read-only)
           mostrando el codigo numerico del articulo en el concentrador.
        7. COMBUSTIBLES — imagenes cc_<codigo_concentrador>.png al lado
           del nombre del articulo en AMBAS sub-tabs (Ver e Impuestos).
           Endpoint /api/combustibles/imagen/<N> sirve los PNGs desde
           C:\\GARUM\\images\\carburante\\imagenes_surtidor. Si el fichero
           no existe, onerror del <img> lo oculta (degradacion graceful).

        8. PISTA — la tabla de mangueras (sub-tab Surtidores) muestra
           tambien la imagen cc_<codigo_concentrador>.png en la columna
           Producto, junto al nombre del articulo asociado al tanque.

        9. MEDIOS DE PAGO — "Articulos MPE" eliminado del sidebar y
           movido como sub-tab dentro del modulo "Medios de pago". Ambos
           sub-tabs (mpe + articulo_mpe) comparten cabecera con grupos de
           acciones (search + selector TPV + Leer BD) que se intercambian
           segun el sub-tab activo. Compatibilidad: irA('articulos') sigue
           redirigiendo al sub-tab Articulos.

       10. REINTEGRAR TPV — plan en vivo rediseñado como step-cards
           (mismo patron visual que Usuario sistema): cada paso es una
           tarjeta con icono + texto + estado, animacion de transicion.
       11. REINTEGRAR TPV — aviso "Para TPVs que ya estaban en la red"
           movido al inicio del modulo (antes estaba enterrado bajo la
           detection card).

v7.3:   Mejoras y nuevos modulos sobre v7.2, todos compatibles. Cambios:

        NUEVO MODULO "🔐 Usuario sistema" (integrado en Reintegrar TPV)
        ----------------------------------------------------------------
        Crea (o actualiza) un usuario local de Windows admin que se usa
        para que TODOS los TPVs de la red compartan credenciales SMB e
        identidad para servicios Windows. Datos hardcoded:
          Usuario: integracion4gl
          Password: ni4GL101212 (no caduca, cuenta no expira)
          Grupo: Administradores (via SID built-in S-1-5-32-544 → funciona
                                  en Windows en cualquier idioma)

        Implementacion: PowerShell con Get-LocalUser / New-LocalUser /
        Set-LocalUser + Add-LocalGroupMember. Idempotente — si ya existe,
        actualiza contraseña + flags + grupo sin borrar nada.

        2 endpoints nuevos:
          GET  /api/usuario-sistema/info   - devuelve el nombre del user (sin pwd)
          POST /api/usuario-sistema/crear  - ejecuta el script PS local

        UI: como seccion <details> colapsable "PASO PREVIO" al INICIO del
        modulo Reintegrar TPV (no como modulo aparte). Asi el tecnico ve
        que es lo primero que hay que hacer antes de pulsar el boton rojo.

        INTEGRACION SMB EN REINTEGRAR (paso 6 del job)
        -----------------------------------------------
        El robocopy de \\\\IP\\C$\\GARUM ahora va precedido de un `net use`
        explicito con las credenciales integracion4gl/ni4GL101212. Esto
        permite que el robocopy funcione AUNQUE el usuario Windows actual
        del TPV destino no exista en el principal — la condicion es que
        el user integracion4gl exista en el principal (precisamente lo que
        el modulo "Usuario sistema" ejecutado allí garantiza).

        Flujo: net use /delete (cleanup) → net use con /user → robocopy →
        net use /delete (cleanup final en finally).

        NUEVO MODULO "📅 Series" → sub-tab "↑ Importar números"
        --------------------------------------------------------
        La pestaña Series ahora tiene 2 sub-tabs:
          - "📋 Ver series" (vista original, sin cambios)
          - "↑ Importar números" (NUEVO)
        El tecnico sube un fichero XML con la lista de series y el contador
        (serie.numero) que debe tener cada una. Tras un Reintegrar TPV los
        contadores quedan con los valores del backup origen; el cliente o
        gestoria facilita el XML con los numeros reales en produccion.

        Flujo:
          1. Seleccionar fichero (FileReader en navegador)
          2. POST /api/series/numero/preview → devuelve diff con accion
             (actualizar / sin_cambio / no_existe) y vista previa con
             codigo de colores (verde / gris / rojo).
          3. POST /api/series/numero/aplicar → UPDATE atomico al TPV local
             SOLO (127.0.0.1), modal ovRed con resultado por serie.

        Parser XML flexible — acepta varios formatos:
          <serie codigo="B01021" numero="4523"/>
          <serie><codigo>B01021</codigo><numero>4523</numero></serie>
          <item><nombre>B01021</nombre><contador>4523</contador></item>

        Defensivo contra XXE (usa xml.etree.ElementTree stdlib).

        MEJORAS EN REINTEGRAR TPV
        --------------------------
        - Paso 3 (serie.propia) ahora marca por DESCRIPCION primero
          (LIKE '%(N)%' en serie.descripcion), con fallback al regex de
          4 chars sobre serie.codigo si no encuentra nada. Convencion del
          cliente: el campo descripcion contiene "(N)" donde N es el TPV.
        - Si el step 6 (copia C:\\GARUM) falla, se SALTA el step 7
          (hibernate) con aviso claro de que ambos pasos deben hacerse
          manualmente. Evita editar un hibernateCentral.cfg.xml inexistente
          tras una copia fallida.
        - Modal de progreso en vivo durante la copia (ovCopia): se abre
          automaticamente al entrar el step 6 en running, muestra spinner,
          contador de tiempo MM:SS, ultima linea del log. Robocopy stream
          via subprocess.Popen (linea a linea) en lugar de subprocess.run.
        - Helper "Copiar C:\\GARUM" acortado a una linea simple.

v7.2:   Mejoras y nuevos modulos sobre v7.1, todos compatibles. Cambios:

        NUEVO MODULO "📋 Artículos"
        ----------------------------
        Pestaña con dos sub-tabs para gestionar los articulos de carburante:
          - "📋 Ver artículos": tabla read-only de articulos asignables a tanque
            con flag carburante. Columnas: ID, Código, Nombre, Comisión,
            Impuesto (porcentaje + nombre).
          - "💶 Impuestos": editor visual del impuesto de cada articulo.
            Click en el badge actual abre modal ovImpuesto con cards en
            grid 3 columnas (porcentaje grande + nombre + id). El cambio
            se aplica en RED a todos los TPVs accesibles via DELETE+INSERT
            atomico en `articulo_impuesto`.

        Schema: tabla intermedia articulo_impuesto(id_articulo, id_impuesto)
        + master impuesto(id_impuesto, nombre, clase, cantidad, ...).

        3 endpoints nuevos:
          GET  /api/articulos_carburante      — JOIN articulo + articulo_impuesto + impuesto
          GET  /api/tipos_impuesto            — SELECT * FROM impuesto
          POST /api/articulos/tipo_impuesto/red — DELETE+INSERT en red por codigo

        OTROS CAMBIOS EN v7.2
        ---------------------
        ConfTPV — nuevo toggle:
          - borrar_display_surtidor_sin_suministros (configuracion_estacion)
          - api_get_conf_tpv ahora lee de DOS tablas (configuracion_tpv +
            configuracion_estacion) y fusiona resultado.
          - /api/configuracion_tpv/red despacha a la tabla correcta segun
            el campo (whitelist _CAMPOS_CONFTPV vs _CAMPOS_ESTACION_DESDE_TPV).

        Panel — fix critico:
          - Boton "Dejar como secundario" tenia HTML mal formado: los " "
            literales en el onclick rompian el atributo y el click no
            ejecutaba la funcion. Fix: usar &quot; (entidad HTML) +
            escape con H(). El boton ya funciona en escenario de conflicto
            de principal (2 TPVs con principal=TRUE simultaneamente).

        Reintegrar TPV — mas robusto + nuevo paso:
          - pg_restore: cambio de "--clean --if-exists" a DROP+CREATE atomico
            (terminar sesiones + DROP DATABASE + CREATE DATABASE + pg_restore
            sin flags conflictivos). Funciona en mas versiones de pg_restore.
          - Nuevo paso 6 del plan: copia recursiva de C:\\GARUM del principal
            (\\\\IP\\C$\\GARUM) a la unidad C local via robocopy.
            Opcional via checkbox "Copiar C:\\GARUM del principal" (default ON).
            Util cuando se reinstala Windows en el TPV destino.
          - Hibernate pasa a paso 7. Bucle de pasos: range(1, 8).
          - Salvaguardas: si ip_origen es localhost se skippea la copia; si
            robocopy timeout o no encontrado, paso 6 queda en "error" pero
            el job entero NO se marca como error (el resto fue OK).

v7.1:   Nuevo modulo "🔄 Reintegrar TPV" para reintegrar un TPV que YA estaba
        en la red (BD corrupta / Windows reinstalado / equipo nuevo con el
        mismo rol). Reusa el ~70% del flujo de "Nuevo TPV" pero salta los pasos
        que solo aplican a un puesto nuevo. Operacion 100% local — solo lee
        del TPV1 via pg_dump, ningun otro TPV se toca.

        MODULO REINTEGRAR (nuevo en v7.1)
        ----------------------------------
        Helpers nuevos:
          - _detectar_num_tpv_local() / _detectar_ip_local() — auto-detectan
            el nº de TPV (1..9) y la IP local del PC en el rango 10.0.0.10X.
          - _job_step(job, n, status) — marca el estado de cada paso del plan
            para que el frontend lo refleje en vivo (pending/running/done/
            error/skipped). Generico para futuros jobs paso-a-paso.

        2 endpoints nuevos:
          GET  /api/reintegrar/info   (pre-vuelo: devuelve detección + sugeridos)
          POST /api/reintegrar/iniciar (body: {password, num_tpv?, ip_origen?,
                                        ip_local?, editar_hibernate?})
          Reutiliza /api/instalar/progreso/<job_id> para el polling (ya existia
          para el modulo Nuevo TPV; ahora devuelve tambien job["steps"]).

        Flujo del job (_job_reintegrar, 4 fases / 6 pasos del plan):
          1. pg_dump TPV1 (tpv + controlpista)            → step 1
          2. pg_restore a 127.0.0.1 (--clean --if-exists) → step 2
          3. Ajustes BD `tpv` local:
             - serie.propia=TRUE para el patron del TPV   → step 3
             - regla_facturacion tienda + carburante      → step 3
             - tpv.principal=FALSE / TRUE este puesto     → step 4
          4. Ajustes BD `controlpista` local:
             - local_config.ip = IP local del TPV         → step 5
             - local_config.pos_version_id_local=10+num   → step 5
          5. Editar C:\\GARUM\\hibernateCentral.cfg.xml    → step 6 (opcional)

        Lo que NO toca (a diferencia de Nuevo TPV):
          - Tabla `tpv` del principal (el TPV ya está registrado).
          - Tabla `pos` (las filas ya existen).
          - `propiedad.CopyDirectories` del resto de TPVs (lo gestiona el
            flujo "Hacer principal" / "Reintegrar como secundario" del Panel
            — separamos responsabilidades).

        UI minimalista (sin wizard de 5 pasos):
          - 3 inputs editables con auto-fill: TPV a reintegrar (1..9),
            IP del TPV principal/origen (10.0.0.101 por defecto),
            IP local de este TPV (auto = 10.0.0.10{num_tpv}).
          - Checkbox "Editar hibernate automáticamente" (ON por defecto).
          - Plan en vivo: los 6 pasos se van tachando con ✓/⏳/✕/⊘ + animación.
          - Log técnico colapsable (cerrado en éxito, auto-abierto en error).
          - Tarjeta de resultado: banner verde/ámbar/rojo según estado, resumen
            tabular, próximo paso destacado, botón "Nueva operación".
          - Persistencia en sessionStorage: si el técnico refresca o cambia
            de pestaña durante el job, al volver se recupera el polling.

        Defensa multi-nivel:
          - Validación cliente y servidor (formato IPv4 + whitelist _REDES).
          - val_host() reusado para ip_origen e ip_local.
          - num_tpv obligatorio en [1,9] (v7.x+: incluye TPV1 para el caso
            real de TPV1 caido reintegrado desde otro principal vivo).
          - 404 detect en polling: si el backend purga el job, se cancela
            el timer y se limpia sessionStorage (evita polls fantasma).
          - irA() y visibilitychange limpian reiState._pollTimer.
          - Hibernate edit con backup .bak + escritura atómica + re.subn
            para detectar "URL JDBC no encontrada" vs "ya apuntaba bien".

v7.0:   Salto mayor por integracion del modulo "Clientes" (👥) desde el
        proyecto independiente `tpv-clientes` (Electron + Express). Ahora
        toda la gestion de clientes / vehiculos / tarjetas / asociaciones
        cliente-tarjeta-vehiculo se hace dentro de garum_tpv_manager — un
        solo instalador para el tecnico.

        MODULO CLIENTES (nuevo en v7.0)
        --------------------------------
        4 sub-tabs internas con selector de TPV propio (igual que
        Sondas/Impresoras/Pista):
          - 👤 Clientes: alta/edicion con modal de 3 sub-tabs
            (Datos / Direcciones / Asociaciones)
          - 🚗 Vehiculos: alta/edicion de matriculas
          - 💳 Tarjetas: alta/edicion con PAN/PIN/fechas/bloqueada/lista_negra
          - 🔗 Asociaciones cliente-tarjeta-vehiculo: toggle "mostrar
            eliminadas", baja con fecha opcional, restore

        21 endpoints nuevos (todos con @need_conn + @csrf en escrituras +
        patron c=None/try/finally + mensajes genericos al cliente):
          GET    /api/clientes (?search)
          GET    /api/clientes/<id>     (cliente + direcciones + asociaciones)
          POST   /api/clientes
          PUT    /api/clientes/<id>
          GET    /api/cliente-tipos
          GET    /api/vehiculos (?search)
          POST   /api/vehiculos
          PUT    /api/vehiculos/<id>
          GET    /api/tarjetas (?search)
          POST   /api/tarjetas
          PUT    /api/tarjetas/<id>
          GET    /api/tarjeta-tipos
          GET    /api/asociaciones (?search, ?show_deleted)
          GET    /api/asociaciones/<id>
          POST   /api/asociaciones      (valida duplicados activos)
          PUT    /api/asociaciones/<id> (idem)
          DELETE /api/asociaciones/<id> (soft delete con fecha_baja opcional)
          PATCH  /api/asociaciones/<id>/restore
          GET    /api/provincias
          POST   /api/clientes/<id>/direcciones
          PUT    /api/direcciones/<id>

        Helper interno `_cli_conn()` resuelve host_tpv automaticamente del
        request: args > body JSON > sess['host']. Permite operar contra
        cualquier TPV sin tocar el codigo de cada endpoint.

        NO portado del proyecto original tpv-clientes:
          /api/config* (garum tiene su propio login).
          Sidebar oscuro y topbar de Electron (sustituidos por el sidebar
          de garum). setInterval(checkConnection) cada 30s. Indicador de
          conexion. Seccion `#sec-config`. Carga de provincias en la UI
          (el endpoint sigue disponible para uso futuro).

        OTROS CAMBIOS EN v7.0 (acumulados desde v6.0)
        ----------------------------------------------
        Pista:
          - DOMS IP (pista.ip_concentrador) editable en red con val_host()
            POST /api/pista/doms/ip/red
          - Pestañas internas en cabecera del modulo: Surtidores / Productos / EPT
            GET /api/pista/productos -> SELECT * FROM articulo WHERE asignable_tanque
            GET /api/pista/ept -> SELECT * FROM ept
          - Layout compacto para 1024x768 (mini-tarjetas + tabla overflow-x)
          - accion_cola_completa: desplegable estricto A/B en lugar de input texto

        Impresoras rediseñadas:
          - Sin duplicacion de inputs (eliminado patron <select>+<input> apilado)
          - Detecta si el TPV es el local: en local muestra <select> con impresoras
            de Windows + opcion "manual"; en remoto solo input texto con aviso
          - Pre-validacion de tipos en backend (fix del 500 en /api/impresoras)
          - log() ahora con flush=True (logs aparecen inmediatamente)

        Articulos MPE:
          - Quitadas columnas Precio / Actualizacion / Usuario (no relevantes)
          - Clase editable: toggle vacio <-> 'R' (nuevo endpoint
            POST /api/articulos_mpe/<id>/clase)

        Personal:
          - Boton "Ver claves" funciona de nuevo (era un regresion de v5.12):
            nuevo endpoint GET /api/personal/passwords bajo demanda. El GET
            /api/personal normal sigue sin devolver passwords por seguridad.

        Instalador:
          - Ruta por defecto: C:\\GARUMTOOLS\\GarumTPV (antes C:\\GarumTPV)
          - NO pregunta donde instalar — va directo a esa ruta (eliminada la
            pagina "Directory" del asistente NSIS y el menu del .bat)
          - .nsi con SetShellVarContext all para que el .lnk del Escritorio
            aparezca para todos los usuarios (no solo para el admin que ejecuto
            con UAC)

        Distribucion:
          - sync-to-onedrive.bat (robocopy /E /XO) copia v7.x a OneDrive como
            backup acumulativo. Se ejecuta automaticamente tras cada bump.

v6.0:   Salto mayor de version por incorporacion del modulo "Pista" (⛽) y
        toda la infraestructura de edicion en red asociada. Sin cambios
        funcionales en el resto de la app — solo se anade una pestana nueva
        en la sidebar y se mantienen los modulos anteriores intactos.

        FUNCIONALIDAD DEL MODULO PISTA
        -----------------------------
        Lectura (selector por TPV):
          GET /api/pista — devuelve la jerarquia completa en un JSON:
            * Cabecera DOMS (pista.ip_concentrador, nombre, tipo_concentrador)
            * Lista de surtidores con sus mangueras anidadas
            * Por cada manguera: tanque al que apunta + producto (JOIN articulo)
            * Lista de tanques disponibles del TPV (para el selector de cambio)
            * Lista de tanques huerfanos (visibles sin manguera asociada)

        Edicion individual por surtidor (POST /api/pista/surtidor/campo/red):
          Aplica a UN surtidor concreto en TODOS los TPVs accesibles,
          identificandolo por `numero` (estable entre TPVs).
          Whitelist _CAMPOS_SURTIDOR_BOOL / _CAMPOS_SURTIDOR_INT:
            * bajo_informatica (bool)
            * numero_logico_concentrador, puerto_concentrador,
              direccion_fisica_concentrador, interface_tipo_general,
              interface_tipo_protocol (int)

        Edicion GLOBAL de todos los surtidores (POST /api/pista/surtidor/global/red):
          UPDATE masivo sin WHERE — afecta a TODOS los surtidores del TPV,
          replicado en todos los TPVs accesibles. Indicador "(varía)" en
          la UI cuando los surtidores tienen valores distintos entre si.
          Whitelist _CAMPOS_SURTIDOR_GLOBAL_INT / _CAMPOS_SURTIDOR_GLOBAL_CHAR:
            * aviso_manguera_descolgada, alarma_manguera_descolgada,
              id_modo_operacion_surtidor_por_defecto, suministros_cola (int)
            * accion_cola_completa (character(1) A-Z)

        Edicion de mangueras (POST /api/pista/manguera/campo/red):
          Aplica a UNA manguera concreta en TODOS los TPVs, identificandola
          por el par (numero_surtidor, numero_manguera).
          Whitelist:
            * numero_logico_concentrador, aspiracion (int)
            * id_manguera_externo (text, max 256 chars)

        Reasignar tanque de manguera (POST /api/pista/manguera/tanque/red):
          Cambia que tanque alimenta a una manguera. El tanque destino se
          identifica por `numero` (estable entre TPVs); cada TPV resuelve
          su `id_tanque` local via subquery.

        UI:
          * Pestana "⛽ Pista" en la sidebar (entre Sondas y Personal)
          * Franja superior fondo azul claro con los 5 campos GLOBALES
            (mini-tarjetas grandes con etiqueta + valor en mono)
          * Lista de surtidores con cabeceras CLICKABLES — animacion suave
            con grid-template-rows 0fr <-> 1fr (transicion .28s ease)
          * Al desplegar surtidor: campos editables individuales + boton
            "Ver mangueras" (segundo nivel colapsable independiente)
          * Tabla de mangueras: 6 columnas — Manguera, Tanque (selector),
            Producto (info), Conc. lógico, Aspiración, id_manguera_externo
          * Etiquetas snake_case coincidentes con nombres de columnas SQL

v5.13:  Nuevo modulo "Pista" (⛽) — vista de la configuracion fisica de la
        pista de surtido. Muestra la jerarquia surtidores -> mangueras ->
        tanques -> articulos en una vista anidada por TPV. Cabecera con
        DOMS IP (pista.ip_concentrador). Endpoint nuevo GET /api/pista.

        Edicion en red (aplica a TODOS los TPVs accesibles) de 5 campos del
        surtidor: bajo_informatica (bool), puerto_concentrador,
        interface_tipo_general, interface_tipo_protocol y
        direccion_fisica_concentrador (int). Identificacion del surtidor por
        `numero` (estable entre TPVs). Whitelist explicita en
        _CAMPOS_SURTIDOR_BOOL / _CAMPOS_SURTIDOR_INT. Endpoint
        POST /api/pista/surtidor/campo/red. UI: badges editables (borde
        dashed + ✏) bajo la cabecera de cada tarjeta de surtidor.

        Franja superior con 4 campos GLOBALES — aplican a TODOS los
        surtidores de TODOS los TPVs (UPDATE sin WHERE):
        aviso_manguera_descolgada, id_modo_operacion_surtidor_por_defecto,
        suministros_cola (int) y accion_cola_completa (character(1)).
        Endpoint POST /api/pista/surtidor/global/red. Whitelist en
        _CAMPOS_SURTIDOR_GLOBAL_INT / _CAMPOS_SURTIDOR_GLOBAL_CHAR.
        Confirmacion previa con confirm() antes de aplicar. Si los
        surtidores ya tienen valores distintos, el badge muestra "(varía)"
        en rojo como aviso.

        Sin cambios funcionales en el resto de la app.

v5.12 (hotfixes):
  - Fix UX: el boton "Hacer principal" aparece tambien en TPVs DESACTIVADOS
    cuando NO hay ningun principal accesible en la red (caso del setup
    inicial o tras una operacion "Dejar como secundario" sin principal real).
    Antes solo aparecia con `principalCaido`, lo que dejaba al usuario sin
    salida si todos los TPVs quedaban en rol secundario/desconocido.
  - Fix UX: la pestana "Propiedades de integracion" ahora lee la BD
    automaticamente al entrar (antes la pestana se quedaba vacia hasta
    pulsar manualmente "Leer BD"). Bug heredado de v5.10/v5.11 corregido
    anadiendo cargarProps() tras poblarSelProp() en irA('propiedades').
  - Fix: Cache-Control: no-store en TODAS las respuestas /api/* via
    @app.after_request. Sintoma observado: tras actualizar la version,
    pestanas como Sondas / Impresoras / Propiedades mostraban "✕ No se
    pudieron leer..." aunque el backend respondia 200 OK. Causa: el
    navegador servia respuestas /api/... cacheadas de la version anterior
    (cuando alguna query fallaba). Solucion: forzar no-store en todas las
    rutas /api/* — los datos son volatiles y nunca deben cachearse.

v5.12:  Auditoria pre-distribucion a tecnicos (estabilidad + seguridad +
        limpieza). Sin nuevas funcionalidades visibles: la pestana, los
        endpoints actuales y los flujos siguen iguales. Esta release endurece
        la app para que aguante uso intensivo en campo sin filtrar credenciales,
        bloquear el pool de conexiones, ni dejar el UI inutilizable tras un
        error de red.

  Seguridad
  ---------
  - conn_tpv() y _conn_controlpista() validan host con val_host() antes de
    abrir conexion (defensa en profundidad contra leak de password a IPs
    arbitrarias).
  - /api/sesion-cierre-turno/huerfanos valida cada IP recibida con val_host()
    antes de usarla -- evita SSRF aunque un cliente envie hosts externos.
  - sess (dict global con credenciales) ahora se muta SIEMPRE bajo
    threading.Lock -- no se mezclan credenciales entre threads con doble F5
    o varias pestanas abiertas a la vez.
  - _update_simple_red(tabla, campo, ...) refuerza con whitelist explicita
    (_TABLAS_PERMITIDAS_RED + _CAMPOS_PERMITIDOS_POR_TABLA): si un futuro
    caller pasa un nombre no listado, lanza ValueError antes de tocar la BD.
  - /api/personal ya NO devuelve la columna password (era la contrasena de
    los empleados del TPV; no debe salir de la BD).
  - /api/instalar/verificar-pg pasa de GET a POST: la contrasena de postgres
    ya no aparece en query string (URL/access logs/historial del navegador).
  - Mensajes psycopg2 dejan de propagarse al cliente; el detalle queda en el
    log local (donde el tecnico lo necesita) y el cliente recibe un mensaje
    generico ("No se pudo actualizar la BD", etc.).

  Estabilidad
  -----------
  - statement_timeout=15000 ms en conn_tpv() y _conn_controlpista(): un
    UPDATE colgado contra un TPV con BD bloqueada YA NO bloquea al worker
    indefinidamente; el ThreadPool no se agota.
  - Patron c=None / try / except / finally c.close() aplicado a ~30
    endpoints y helpers (api_get_props, api_set_props, api_get_impresoras,
    api_set_impresoras, api_get_sondas, api_get_integrados, api_set_mpe_*,
    api_get_personal, api_set_personal_*, api_get_depositos, api_get_totales_*,
    api_get_conf_tpv, api_get_estacion, api_get_articulos_mpe,
    api_update_articulo_mpe, api_huerfanos_sesion_cierre, _leer_tpvs_de_bd,
    probar_tpv, _leer_pos, leer_cp, leer_est, _ejecutar_en, _registrar_tpv_en,
    _job_restore, ...). Ya no hay conn leaks bajo errores intermitentes de BD.
  - alog convertido a collections.deque(maxlen=500): bounded sin pop(0) O(n).
  - app.run(threaded=True) explicito.
  - _leer_config/_guardar_config usan threading.Lock y escritura atomica
    (tmp + os.replace) -- config.json ya no se corrompe bajo concurrencia.
  - Editor de hibernateCentral.cfg.xml: backup .bak antes de sobrescribir,
    sanity-check del XML resultante, fallback utf-8 -> cp1252, reemplazo
    seguro con lambda (no se interpretan \\1, \\g en el replacement string).
    Una regex que no matchea o un XML invalido YA NO pueden romper GARUM.
  - Helpers JS get()/post() leen el body en errores y propagan r.error del
    backend: el tecnico ve "No se pudo conectar al TPV" en vez de "HTTP 500".
  - try/finally en botones JS (conectar, editarRetiro, editarPerfil,
    verificar-pg, ...) -- ya no quedan disabled para siempre si la red falla.
  - Polls fantasmas del asistente de instalacion se cancelan al navegar a
    otra pestana y en visibilitychange='hidden'. Flag _pollInflight evita
    avalanchas si una request anterior aun no respondio.
  - except: pass (bare) sustituido por except Exception: pass en 8 sitios
    para no tragar KeyboardInterrupt / SystemExit / MemoryError.

  Limpieza (~310 lineas eliminadas)
  ---------------------------------
  - Borrados 6 endpoints single-TPV deprecados (sustituidos por /red en
    versiones anteriores): POST /api/configuracion_tpv, /api/depositos/*,
    /api/totales-tarjetas/campo, /api/sondas/campo-red (predecesor) y
    /api/sondas/<id>/campo. El frontend solo usaba ya los /red.
  - Borrados 4 endpoints sin caller (api_info, api_tpvs_count, api_log,
    api_log_limpiar) y su helper _leer_tpvs_configurados.
  - Borradas en index.html: function reescanear duplicada (corregia bug
    latente: el boton "Actualizar" del Panel ahora oculta opR como pretende),
    function _badgeBool huerfana y 4 re-imports redundantes de
    ThreadPoolExecutor/as_completed.

v5.11:
  - "Medios de pago": borde punteado + icono edicion (pencil) en los tres
    controles editables de cada tarjeta (boolToggle Factura/Dev.c/f pago y
    el interruptor Activado/Desactivado), igual que los badges de Sondas.
  - Fix UnicodeEncodeError en Windows (cp1252): sys.stdout.reconfigure(utf-8)
    al arranque + try/except en log() para evitar que caracteres como la
    flecha derecha (u2192) rompan las llamadas al backend.
  - Sondas: al pulsar "Si" en el prompt de propagacion, numero_logico_concentrador
    solo se replica al mismo numero_sonda en otros TPVs (es unico por tanque);
    puerto_concentrador ademas actualiza todos los configuracion_sonda del
    TPV actual (todos los tanques). Texto del prompt diferenciado por campo.
  - "Medios de pago": borde punteado + icono edicion (pencil) en los tres
    controles editables de cada tarjeta (boolToggle Factura/Dev.c/f pago y
    el interruptor Activado/Desactivado), igual que los badges de Sondas.
  - Fix UnicodeEncodeError en Windows (cp1252): sys.stdout.reconfigure(utf-8)
    al arranque + try/except en log() para evitar que caracteres como la
    flecha derecha (u2192) rompan las llamadas al backend.
  - Sondas: al pulsar "Si" en el prompt de propagacion, numero_logico_concentrador
    solo se replica al mismo numero_sonda en otros TPVs (es unico por tanque);
    puerto_concentrador ademas actualiza todos los configuracion_sonda del
    TPV actual (todos los tanques). Texto del prompt diferenciado por campo.

v5.10:
  - "Medios de pago": interruptor para activar/desactivar cada medio de pago,
    guardado en la BD. POST /api/integrados/<id_mpe>/activado (UPDATE mpe.activado).
  - "Medios de pago": interruptor "Conexion MPE" en la cabecera de la pestana
    que activa/desactiva configuracion_avanzada.conexion_mpe. POST /api/conexion_mpe.
  - Arreglo de _renderIntegrados: las tarjetas se descuadraban por una comilla
    mal cerrada en un badge; ademas borde lateral de color por estado.

v5.9:
  - Nuevo boton "Quitar sesion activa" en el Panel de TPVs: cada tarjeta
    anade un boton que borra la sesion de ese TPV (sesion_tpv_activo) en
    todos los TPVs accesibles, incluido el propio.
    POST /api/operacion/borrar_sesion -- reutiliza _borrar_sesion_tpv.
  - Nueva pestana "Series": muestra la tabla serie de cada TPV.
    GET /api/series -- serie, descripcion, factura/rectificativa/comision/propia.
  - Menu "Integrados" renombrado a "Medios de pago".
  - Los TPVs inaccesibles muestran "No se puede conectar con el TPV" en vez
    del error tecnico de psycopg2.

v5.8:
  - Instalador a prueba de antivirus: INSTALAR.bat solo copia y extrae
    ficheros. ARRANCAR.bat va pre-hecho en el paquete y el instalador lo
    copia (antes lo generaba por script, patron que el antivirus corta).
    Ya no se ejecuta Python ni se auto-arranca la app al terminar.

v5.7:
  - Instalador offline: el paquete incluye Python 3.11 embebido con Flask y
    psycopg2 ya instalados. INSTALAR.bat ya no descarga nada de internet;
    extrae el runtime incluido. Imprescindible para TPVs en redes aisladas.

v5.6:
  - Fix deteccion: el boton "Actualizar" del Panel ahora relee la tabla tpv
    (_releerTpvsDeBD) y descubre TPVs nuevos sin necesidad de reconectar.
  - Integracion: registra el TPV nuevo en la tabla tpv del principal para que
    el programa lo detecte. Flags de hardware copiados del TPV1.
  - Nuevo campo "ID TPV externo" en el paso 1 — se escribe en tpv.id_tpv_externo.

v5.5:
  - Crear series: tabla editable de regla_facturacion tras crear las series —
    un desplegable por regla (tienda / carburante) para cambiar la serie a mano.
    POST /api/instalar/guardar-reglas -- aplica los cambios manuales.
  - Fix propia: en el TPV nuevo la marca de propia se aplica SIEMPRE (antes se
    omitia si las series ya existian tras el restore, dejandolas en propia=FALSE).
    Existentes -> propia=FALSE; las 14 del puesto -> propia=TRUE.

v5.4:
  - Tipo de estacion: la serie comisionista se detecta por TPV con propia=TRUE
    (sin desplegable). Cada TPV apunta su regla_facturacion a su propia serie.
  - Instalacion / Crear series: tras crear las series del TPV nuevo, reapunta
    su regla_facturacion a sus series propias (tienda y carburante).
  - Fix: el aviso "Accion manual - Fichero Hibernate" ya no aparece cuando el
    fichero se edita automaticamente; solo si no se encuentra.

v5.3:
  - Nuevo modulo "Tipo de estacion": cambia la estacion entre Firme (F) y
    Comisionista (C) en todos los TPVs accesibles.
    GET  /api/estacion/estado-red    -- tipo, carburantes, series por TPV
    POST /api/estacion/cambiar-tipo  -- aplica el cambio en 3 tablas
    Por TPV: articulo.comision de carburantes, estacion.tipo_estacion y
    reestructura regla_facturacion (Firme 1 fila / Comisionista 2 filas).

v5.2:
  - Instalacion TPV: paso "Crear series" del nuevo puesto en TPV1 y local.
    POST /api/instalar/crear-series   -- crea las 14 series (propio FALSE/TRUE)
  - Instalacion TPV: pos_version_id_local automatico (10 + num_puesto).
  - Instalacion TPV: edicion automatica de C:\\GARUM\\hibernateCentral.cfg.xml.
  - Instalacion TPV: pasos Backup y Restore fusionados en una pantalla.
  - Configuracion TPV: sub-pestaña "Borrar informes huerfanos".
    POST /api/sesion-cierre-turno/huerfanos -- identifica/elimina huerfanos

v5.1:
  - Nuevo modulo Instalacion TPV: asistente para integrar un TPV recien
    instalado como secundario en una red GARUM existente.
    GET  /api/instalar/verificar-pg   -- verifica pg_dump + conexion origen
    POST /api/instalar/iniciar-backup -- lanza pg_dump en hilo, devuelve job_id
    POST /api/instalar/iniciar-restore-- lanza pg_restore en hilo, devuelve job_id
    GET  /api/instalar/progreso/<id>  -- polling de logs y estado
    POST /api/instalar/secundario     -- configura integracion (16 claves, ip_server, pos)

v5.0 / v1.6:
  - Anular TPV: actualiza los TPVs ACTIVOS (no el averiado)
  - Aviso hibernate: solo cuando cambia el principal
  - Anular secundario: NO requiere cambio de hibernate
  - Cambiar principal: aviso con instrucciones exactas de hibernate
"""

import os, sys

# Forzar UTF-8 en stdout/stderr para evitar UnicodeEncodeError en Windows (cp1252)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass  # stdout no es TextIOWrapper (sin consola, frozen, etc.)

if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

_LIBS = os.path.join(_BASE, "libs")
if os.path.isdir(_LIBS) and _LIBS not in sys.path:
    sys.path.insert(0, _LIBS)
    _pg = os.path.join(_LIBS, "psycopg2_binary.libs")
    if os.path.isdir(_pg):
        os.environ["PATH"] = _pg + os.pathsep + os.environ.get("PATH", "")

import re, subprocess
import secrets, ipaddress, threading, webbrowser, json
from datetime import datetime
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, send_from_directory, send_file, abort

# ── Fichero de configuración persistente ──────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(_BASE), "config.json")
_config_lock = threading.Lock()    # protege _leer_config/_guardar_config

def _leer_config() -> dict:
    """Lee la configuración persistente del fichero config.json."""
    with _config_lock:
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            # Loguear el detalle pero no romper la app si el fichero esta corrupto.
            try:
                print(f"WARN leer config.json: {e}")
            except Exception:
                pass
        return {}

def _guardar_config(datos: dict):
    """Guarda la configuración persistente en config.json (atomico)."""
    with _config_lock:
        try:
            # Releer y mergear DENTRO del lock para no perder updates concurrentes.
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
            cfg.update(datos)
            # Escribir a tmp + os.replace = escritura atomica en Windows/Linux.
            tmp = CONFIG_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
            os.replace(tmp, CONFIG_FILE)
        except Exception as e:
            try:
                print(f"WARN no se pudo guardar config.json: {e}")
            except Exception:
                pass

try:
    import psycopg2, psycopg2.extras, psycopg2.sql
    PSYCOPG2_OK = True
except ImportError:
    PSYCOPG2_OK = False

PORT = 5050
HOST = "127.0.0.1"
TEMPLATE_DIR = os.path.join(_BASE, "templates")
STATIC_DIR   = os.path.join(_BASE, "static")
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

TPVS_CONOCIDOS = [
    {"id": 1, "nombre": "TPV 1", "ip": "10.0.0.101", "rol": "principal"},
    {"id": 2, "nombre": "TPV 2", "ip": "10.0.0.102", "rol": "secundario"},
    {"id": 3, "nombre": "TPV 3", "ip": "10.0.0.103", "rol": "secundario"},
    {"id": 4, "nombre": "TPV 4", "ip": "10.0.0.104", "rol": "secundario"},
]
IPS_CONOCIDAS = [t["ip"] for t in TPVS_CONOCIDOS]

# Valores fijos verificados contra datos reales de la instalacion
V_INPUT_DIR      = "C:/integracion/XADInput"
V_INPUT_DIR_COPY = "C:/integracion/XADExport"
V_ERROR_DIR      = "C:/integracion/XADError"
V_BACKUP_MAESTRO = "C:/integracion/XADBackup/maestros/"
V_BACKUP_TRANS   = "C:/integracion/XADBackup/transacciones/"
V_BOS_PRINCIPAL  = "C:/integracion/4GLExport"
V_MAESTROS_PRINC = "C:/integracion/XADBackup/maestros_principal"


def _copy_dirs_principal(mi_ip, ips_activas):
    """Principal: apunta a todos los demas CON barra final."""
    otros = [ip for ip in ips_activas if ip != mi_ip]
    return ";".join([f"//{ip}/c/integracion/XADInput/" for ip in otros])


def _copy_dirs_secundario(mi_ip, ips_activas):
    """Secundario: apunta a todos los demas SIN barra final."""
    otros = [ip for ip in ips_activas if ip != mi_ip]
    return ";".join([f"//{ip}/c/integracion/XADInput" for ip in otros])


def _aviso_hibernate_cambio_principal(
        nuevo_principal_ip,
        otros_ips,
        ip_principal_anterior="10.0.0.101",
        tpvs_inaccesibles=None):
    """
    Genera instrucciones exactas para editar hibernateCentral.cfg.xml
    cuando cambia el TPV principal.

    Ficheros confirmados en la instalacion:
      hibernate.cfg.xml        -> localhost:5432/tpv  (NUNCA CAMBIA en ningun TPV)
      hibernateCentral.cfg.xml -> localhost en principal, IP_PRINCIPAL en secundarios

    tpvs_inaccesibles: lista de IPs de TPVs que estaban caidos durante la operacion.
      Se marcan con aviso especial para que el tecnico sepa que tiene que ir fisicamente.
    """
    if tpvs_inaccesibles is None:
        tpvs_inaccesibles = []

    lineas = []
    lineas.append("=" * 60)
    lineas.append("ACCION MANUAL REQUERIDA — FICHERO HIBERNATE")
    lineas.append("=" * 60)
    lineas.append("")
    lineas.append("Fichero a editar en CADA TPV:")
    lineas.append("  C:\\GARUM\\hibernateCentral.cfg.xml")
    lineas.append("")
    lineas.append("IMPORTANTE: hibernate.cfg.xml (sin Central) NO se toca nunca.")
    lineas.append("")

    # Nuevo principal
    caido_np = nuevo_principal_ip in tpvs_inaccesibles
    lineas.append(f"[{nuevo_principal_ip}] NUEVO PRINCIPAL" +
                  (" ⚠ ESTABA CAIDO — editar cuando arranque" if caido_np else ""))
    lineas.append(f"  Buscar:    jdbc:postgresql://{ip_principal_anterior}:5432/tpv")
    lineas.append(f"  Sustituir: jdbc:postgresql://localhost:5432/tpv")
    lineas.append("")

    # Secundarios
    for ip in otros_ips:
        caido = ip in tpvs_inaccesibles
        lineas.append(f"[{ip}] secundario" +
                      (" ⚠ ESTABA CAIDO — editar cuando arranque" if caido else ""))
        lineas.append(f"  Buscar:    jdbc:postgresql://{ip_principal_anterior}:5432/tpv")
        lineas.append(f"  Sustituir: jdbc:postgresql://{nuevo_principal_ip}:5432/tpv")
        lineas.append("")

    if tpvs_inaccesibles:
        lineas.append("-" * 60)
        lineas.append("TPVs que estaban caidos y necesitan edicion manual cuando arranquen:")
        for ip in tpvs_inaccesibles:
            lineas.append(f"  - {ip}")
        lineas.append("")

    lineas.append("Tras editar TODOS los ficheros: reiniciar GARUM en cada TPV.")
    return "\n".join(lineas)


# Seguridad
_REDES = [ipaddress.ip_network("10.0.0.0/24"), ipaddress.ip_network("127.0.0.0/8")]
_CSRF  = secrets.token_hex(32)
_MAX_V = 512


# v5.12 hotfix: forzar no-cache en TODAS las respuestas del backend.
# Sin esto, navegadores antiguos (o tras un cambio de versión) podían servir
# respuestas cacheadas de /api/... y mostrar errores fantasma "✕ No se pudieron
# leer..." aunque el backend ya respondiera 200 OK.
#
# v5.13: ampliado tambien a la ruta raiz "/" y a "/diagnostico" — si el
# usuario actualiza la app (p.ej. v5.12 -> v5.13), el navegador puede tener
# `index.html` cacheado de la version anterior y ejecutar JS obsoleto que
# referencia variables/endpoints que ya no existen (sintoma: "Error interno.
# Recarga la pagina." al pulsar Conectar, sin que llegue ningun POST al log).
# La app vive en localhost y todo es volatil -- nunca cachear nada.
@app.after_request
def _no_cache(resp):
    p = request.path
    if p.startswith("/api/") or p == "/" or p.startswith("/diagnostico"):
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"]        = "no-cache"
        resp.headers["Expires"]       = "0"
    return resp

CLAVES = frozenset({
    "InputDirectory", "InputDirectoryCopy", "BackupDirectoriesBOS",
    "CopyDirectories", "CopyDirectoriesMaestros", "ErrorDirectory",
    "BackupDirectoryMaestro", "BackupDirectoryMaestroMovidosTpvPrincipal",
    "BackupDirectoryTransaccion", "activarDemonioCopia", "activarDemonioError",
    "activarDemonioIntegracion", "procesarMaestros", "procesarTransacciones",
    "tiempoCopia", "tiempoError",
})

sess = {}
_sess_lock = threading.Lock()      # protege mutaciones sobre `sess`
from collections import deque
alog = deque(maxlen=500)
_instalar_jobs = {}   # job_id → {type, status, logs, ficheros, error, done}
_instalar_jobs_lock = threading.Lock()  # purga de jobs antiguos
_INSTALAR_JOBS_TTL = 3600  # segundos: jobs done > 1h se purgan al crear nuevo


def log(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    alog.append({"ts": ts, "msg": msg, "level": level})
    try:
        # flush=True para que los logs aparezcan inmediatamente cuando stdout
        # esta capturado por un pipe (sin buffering por bloques de 4096 bytes).
        print(f"[{ts}][{level.upper()}] {msg}", flush=True)
    except UnicodeEncodeError:
        safe = msg.encode("ascii", errors="replace").decode("ascii")
        print(f"[{ts}][{level.upper()}] {safe}", flush=True)


def val_host(host):
    if not host or not isinstance(host, str):
        raise ValueError("Host vacio o invalido")
    host = host.strip()
    if len(host) > 15:
        raise ValueError("Host demasiado largo")
    try:
        ip = ipaddress.ip_address(host)
    except Exception:
        raise ValueError(f"IP no valida: {host}")
    if not any(ip in r for r in _REDES):
        raise ValueError(f"IP fuera de rango permitido: {host}")
    return host


def val_port(p):
    try:
        p = int(p)
    except Exception:
        raise ValueError("Puerto no numerico")
    if not (1024 <= p <= 65535):
        raise ValueError("Puerto fuera de rango")
    return p


def csrf(f):
    @wraps(f)
    def d(*a, **k):
        t = request.headers.get("X-CSRF-Token", "")
        if not secrets.compare_digest(t, _CSRF):
            return jsonify({"ok": False, "error": "Token invalido"}), 403
        return f(*a, **k)
    return d


def need_conn(f):
    @wraps(f)
    def d(*a, **k):
        if not sess:
            return jsonify({"ok": False, "error": "Sin conexion activa"}), 401
        return f(*a, **k)
    return d


def conn_tpv(host):
    # Defensa en profundidad: validar el host antes de abrir conexion para
    # impedir que un endpoint mal validado envie sess["password"] a un host
    # externo arbitrario.
    host = val_host(host)
    return psycopg2.connect(
        host=host,
        port=int(sess.get("port", 5432)),
        dbname=sess["dbname"],
        user=sess["user"],
        password=sess["password"],
        connect_timeout=4,
        # statement_timeout protege contra UPDATEs colgados (BD bloqueada,
        # locks largos): el thread del pool no queda esperando indefinidamente.
        options="-c search_path=public -c statement_timeout=15000",
    )


def _leer_tpvs_de_bd(host: str) -> list:
    """
    Lee la tabla 'tpv' de la BD para obtener los TPVs configurados.
    Devuelve lista de dicts con id_tpv, nombre e ip calculada.
    La IP se calcula como 10.0.0.(100 + id_tpv).
    Solo necesitamos id_tpv y nombre — el campo principal se ignora.
    """
    if not PSYCOPG2_OK:
        return []
    c = None
    try:
        c = psycopg2.connect(
            host=host,
            port=int(sess.get("port", 5432)),
            dbname=sess["dbname"],
            user=sess["user"],
            password=sess["password"],
            connect_timeout=4,
        )
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id_tpv, nombre FROM tpv ORDER BY id_tpv")
        rows = cur.fetchall()
        resultado = []
        for r in rows:
            id_tpv = int(r["id_tpv"])
            ip = f"10.0.0.{100 + id_tpv}"
            resultado.append({
                "id":     id_tpv,
                "nombre": r["nombre"] or f"TPV {id_tpv}",
                "ip":     ip,
                "rol":    "desconocido",
            })
        for t in resultado:
            log(f"TPV leido: id={t['id']} nombre='{t['nombre']}' ip={t['ip']}", "info")
        return resultado
    except Exception as e:
        log(f"WARN leer tabla tpv: {str(e).split(chr(10))[0]}", "warn")
        return []
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _extraer_ips_copy_dirs(cd: str) -> list:
    """
    Extrae las IPs que aparecen en CopyDirectories.
    Formato: //10.0.0.102/c/integracion/XADInput/;//10.0.0.103/...
    Devuelve lista de IPs: ["10.0.0.102", "10.0.0.103"]
    """
    if not cd or not cd.strip():
        return []
    ips = []
    for parte in cd.split(";"):
        parte = parte.strip()
        if parte.startswith("//"):
            # Extraer la IP: //10.0.0.102/c/...
            sin_barras = parte[2:]  # quitar //
            ip = sin_barras.split("/")[0]
            if ip and ip not in ips:
                ips.append(ip)
    return ips


def probar_tpv(tpv):
    """
    Comprueba el estado real de un TPV leyendo su tabla propiedad.
    Detecta el rol real (principal/secundario) leyendo BackupDirectoriesBOS.
    Extrae las IPs de CopyDirectories para detectar discrepancias de configuracion.
    """
    r = {**tpv, "accesible": False, "integrado": False,
         "estado": "desconocido", "error": None,
         "ips_en_copy_dirs": [],   # IPs a las que apunta este TPV
         "ips_faltantes": []}      # IPs que debería tener pero no tiene
    if not PSYCOPG2_OK or sess.get("demo"):
        r["estado"] = "demo"
        return r
    c = None
    try:
        c = conn_tpv(tpv["ip"])
        cur = c.cursor()
        cur.execute(
            "SELECT clave, valor FROM propiedad "
            "WHERE clave IN ('CopyDirectories', 'BackupDirectoriesBOS')"
        )
        rows = {row[0]: row[1] for row in cur.fetchall()}

        cd  = rows.get("CopyDirectories", "")
        bos = rows.get("BackupDirectoriesBOS", "")

        r["accesible"] = True

        # Detectar rol real primero (necesario para saber si es el único TPV)
        es_principal = bool(bos and not bos.strip().startswith("//"))
        r["rol"] = "principal" if es_principal else "secundario"

        # Un TPV está integrado si:
        # - Tiene CopyDirectories con contenido (caso normal con varios TPVs), O
        # - Es el principal Y CopyDirectories está vacío (caso de único TPV en instalación)
        cd_vacio = not cd or not cd.strip() or cd.strip() == "''"
        es_unico = len(TPVS_CONOCIDOS) == 1
        r["integrado"] = (not cd_vacio) or (es_principal and es_unico)
        r["estado"]    = "activo" if r["integrado"] else "desactivado"

        # Extraer IPs a las que apunta este TPV en CopyDirectories
        ips_en_cd = _extraer_ips_copy_dirs(cd)
        r["ips_en_copy_dirs"] = ips_en_cd

        # Calcular IPs que DEBERÍA tener pero NO tiene
        # (todos los TPVs conocidos excepto él mismo)
        if r["integrado"]:
            todas_ips = [t["ip"] for t in TPVS_CONOCIDOS if t["ip"] != tpv["ip"]]
            r["ips_faltantes"] = [ip for ip in todas_ips if ip not in ips_en_cd]

    except Exception:
        r["estado"] = "inaccesible"
        r["error"] = "No se puede conectar con el TPV"
    finally:
        if c:
            try: c.close()
            except Exception: pass
    return r


def _ip_a_id_tpv(ip: str) -> int:
    """
    Convierte la IP de un TPV a su id_tpv entero.
    Convenio de la instalacion: ultimo octeto - 100
      10.0.0.101 → 1
      10.0.0.102 → 2
      10.0.0.103 → 3
      10.0.0.104 → 4
    """
    try:
        return int(ip.split(".")[-1]) - 100
    except Exception:
        return -1


def _conn_controlpista(host_tpv: str):
    """Abre conexión a la BD controlpista del TPV indicado."""
    host_tpv = val_host(host_tpv)
    return psycopg2.connect(
        host=host_tpv,
        port=int(sess.get("port", 5432)),
        dbname="controlpista",
        user=sess["user"],
        password=sess["password"],
        connect_timeout=4,
        options="-c search_path=public -c statement_timeout=15000",
    )


def _borrar_sesion_tpv(host_tpv: str, id_tpv: int) -> dict:
    """
    Borra la sesion activa de un TPV concreto en la tabla sesion_tpv_activo.
    Solo borra la fila del id_tpv indicado, no toda la tabla.

    host_tpv: TPV donde se ejecuta el DELETE (puede ser cualquier TPV accesible)
    id_tpv:   numero entero del TPV cuya sesion se quiere borrar (1=TPV1, 2=TPV2...)
    """
    if sess.get("demo"):
        log(f"[DEMO] DELETE sesion_tpv_activo WHERE id_tpv={id_tpv} en {host_tpv}", "ok")
        return {"ok": True, "demo": True}
    c = None
    try:
        c = conn_tpv(host_tpv)
        c.autocommit = False
        cur = c.cursor()
        cur.execute(
            "DELETE FROM sesion_tpv_activo WHERE id_tpv=%s",
            (id_tpv,)
        )
        borradas = cur.rowcount
        c.commit()
        if borradas > 0:
            log(f"sesion_tpv_activo: borrada sesion id_tpv={id_tpv} en {host_tpv}", "ok")
        else:
            log(f"sesion_tpv_activo: no habia sesion id_tpv={id_tpv} en {host_tpv}", "info")
        return {"ok": True, "borradas": borradas}
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN sesion {host_tpv}: {msg}", "warn")
        return {"ok": False, "error": msg}
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _actualizar_controlpista(host_tpv: str, ip_nuevo_principal: str) -> dict:
    """
    Actualiza ip_server en local_config de la BD controlpista del TPV indicado.
    Se llama cuando cambia el principal.
    NO toca el campo 'ip' (IP local del propio TPV).
    """
    if sess.get("demo"):
        log(f"[DEMO] controlpista {host_tpv}: ip_server={ip_nuevo_principal}", "ok")
        return {"ok": True, "demo": True}
    c = None
    try:
        c = _conn_controlpista(host_tpv)
        c.autocommit = False
        cur = c.cursor()
        cur.execute("UPDATE local_config SET ip_server=%s", (ip_nuevo_principal,))
        afectadas = cur.rowcount
        c.commit()
        log(f"controlpista {host_tpv}: ip_server={ip_nuevo_principal} ({afectadas} fila)", "ok")
        return {"ok": True, "afectadas": afectadas}
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN controlpista {host_tpv}: {msg}", "warn")
        return {"ok": False, "error": msg}
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _set_pos_online(host_controlpista: str, ip_tpv: str, online: bool) -> dict:
    """
    Actualiza el campo online en la tabla pos de la BD controlpista.
    host_controlpista: TPV donde está la BD controlpista que queremos modificar.
    ip_tpv: IP del TPV cuyo estado online queremos cambiar (clave PK de la tabla pos).
    online: True = TPV activo, False = TPV caído/anulado.

    Se llama en TODOS los TPVs accesibles para que todos tengan
    la tabla pos sincronizada con el estado real.
    """
    if sess.get("demo"):
        estado = "online" if online else "offline"
        log(f"[DEMO] pos en {host_controlpista}: {ip_tpv}={estado}", "ok")
        return {"ok": True, "demo": True}
    c = None
    try:
        c = _conn_controlpista(host_controlpista)
        c.autocommit = False
        cur = c.cursor()
        cur.execute(
            "UPDATE pos SET online=%s WHERE ip=%s",
            (online, ip_tpv)
        )
        afectadas = cur.rowcount
        c.commit()
        estado = "TRUE" if online else "FALSE"
        log(f"pos en {host_controlpista}: {ip_tpv} online={estado} ({afectadas} fila)", "ok")
        return {"ok": True, "afectadas": afectadas}
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN pos {host_controlpista}: {msg}", "warn")
        return {"ok": False, "error": msg}
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _leer_pos(host_tpv: str) -> list:
    """
    Lee la tabla pos de la BD controlpista del TPV indicado.
    Devuelve lista de dicts con ip, preference, online.
    """
    if sess.get("demo"):
        return [
            {"ip": "10.0.0.101", "preference": 1, "online": True},
            {"ip": "10.0.0.102", "preference": 2, "online": True},
            {"ip": "10.0.0.103", "preference": 3, "online": True},
            {"ip": "10.0.0.104", "preference": 4, "online": True},
        ]
    c = None
    try:
        c = _conn_controlpista(host_tpv)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT ip, preference, online FROM pos ORDER BY preference")
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    except Exception as e:
        log(f"WARN leer pos {host_tpv}: {str(e).split(chr(10))[0]}", "warn")
        return []
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _run(host, sqls, desc):
    if sess.get("demo"):
        log(f"[DEMO] {desc}", "ok")
        return {"ok": True, "demo": True, "msg": desc}
    c = None
    try:
        c = conn_tpv(host)
        c.autocommit = False
        cur = c.cursor()
        for sql, params in sqls:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
        c.commit()
        log(desc, "ok")
        return {"ok": True, "msg": desc}
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"ERROR {host}: {msg}", "error")
        return {"ok": False, "error": f"{host}: {msg}"}
    finally:
        if c:
            try: c.close()
            except Exception: pass


# =============================================================================
# RUTAS
# =============================================================================

@app.route("/")
def index():
    return send_from_directory(TEMPLATE_DIR, "index.html")


@app.route("/diagnostico")
def diagnostico():
    return send_from_directory(TEMPLATE_DIR, "diagnostico.html")


@app.route("/api/csrf-token")
def api_csrf():
    return jsonify({"token": _CSRF})


@app.route("/api/config")
def api_config():
    """Devuelve la configuración guardada (último host usado, etc.)."""
    cfg = _leer_config()
    # Validar tpvs_custom antes de devolverlos
    tpvs_raw = cfg.get("tpvs_custom", [])
    tpvs_valid = []
    for t in tpvs_raw:
        try:
            ip = t.get("ip", "")
            nombre = t.get("nombre", "")
            id_t = t.get("id", 0)
            # Validar IP formato correcto y nombre sin caracteres extraños
            if (re.match(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", ip)
                    and isinstance(nombre, str) and len(nombre) > 0 and len(nombre) < 50
                    and isinstance(id_t, int)):
                tpvs_valid.append(t)
        except Exception:
            pass
    return jsonify({
        "ultimo_host": cfg.get("ultimo_host", ""),
        "ultimo_port": cfg.get("ultimo_port", "5432"),
        "ultimo_db":   cfg.get("ultimo_db",   "tpv"),
        "ultimo_user": cfg.get("ultimo_user", "postgres"),
        "tpvs_custom": tpvs_valid,
    })


@app.route("/api/config/tpvs", methods=["POST"])
@csrf
@need_conn
def api_guardar_tpvs():
    """Guarda la configuración personalizada de TPVs en config.json."""
    data = request.json or {}
    tpvs_custom = data.get("tpvs", [])
    if not isinstance(tpvs_custom, list) or len(tpvs_custom) > 20:
        return jsonify({"ok": False, "error": "Datos inválidos"}), 400
    # Validar IPs
    for t in tpvs_custom:
        try:
            val_host(t.get("ip", ""))
        except ValueError as e:
            return jsonify({"ok": False, "error": str(e)}), 400
    _guardar_config({"tpvs_custom": tpvs_custom})
    log(f"Configuración de TPVs guardada en config.json", "ok")
    return jsonify({"ok": True})


@app.route("/api/conexion/estado")
def api_estado():
    if not sess:
        return jsonify({"conectado": False})
    return jsonify({
        "conectado": True,
        "host":   sess.get("host"),
        "dbname": sess.get("dbname"),
        "user":   sess.get("user"),
        "demo":   sess.get("demo", False),
    })


@app.route("/api/conectar", methods=["POST"])
@csrf
def api_conectar():
    global sess
    data = request.json or {}
    host = data.get("host", "").strip()
    pw   = data.get("password", "")
    if not host or not pw:
        return jsonify({"ok": False, "error": "Faltan host o contrasena"}), 400
    try:
        host = val_host(host)
        port = val_port(data.get("port", "5432"))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    db   = data.get("dbname", "tpv").strip()
    user = data.get("user", "postgres").strip()
    if not PSYCOPG2_OK:
        with _sess_lock:
            sess = {"host": host, "port": port, "dbname": db,
                    "user": user, "password": "***", "demo": True}
        log("MODO DEMO", "warn")
        return jsonify({"ok": True, "demo": True, "msg": "Modo demo activo"})
    try:
        c = psycopg2.connect(host=host, port=port, dbname=db,
                             user=user, password=pw, connect_timeout=5)
        c.close()
        # Mutacion atomica de `sess` bajo lock para evitar mezcla de credenciales
        # entre threads (doble F5, dos pestanas abiertas a la vez, etc.).
        with _sess_lock:
            sess = {"host": host, "port": port, "dbname": db,
                    "user": user, "password": pw, "demo": False}
        # Guardar la IP de conexión en config.json para próximas sesiones
        _guardar_config({"ultimo_host": host, "ultimo_port": port,
                         "ultimo_db": db, "ultimo_user": user})
        log(f"Conectado a {host}:{port}/{db} como {user}", "ok")
        return jsonify({"ok": True, "demo": False,
                        "msg": f"Conectado a {host}:{port}/{db}"})
    except Exception as e:
        # No exponer el detalle de psycopg2 (schemas, columnas) al cliente.
        msg = str(e).split("\n")[0]
        log(f"Error conexion: {msg}", "error")
        return jsonify({"ok": False, "error": "No se pudo conectar a la BD. Revise host/usuario/contrasena."}), 400


@app.route("/api/desconectar", methods=["POST"])
@csrf
def api_desconectar():
    global sess
    with _sess_lock:
        sess = {}
    log("Sesion cerrada", "info")
    return jsonify({"ok": True})


@app.route("/api/tpvs/configurados")
@need_conn
def api_tpvs_configurados():
    """
    Lee la tabla tpv de la BD y devuelve los TPVs configurados.
    Se llama al conectar para cargar dinamicamente los TPVs reales
    en lugar de asumir siempre 4.
    """
    global TPVS_CONOCIDOS, IPS_CONOCIDAS  # declarar al inicio de la función

    host = sess.get("host", "")
    if not host:
        return jsonify({"ok": False, "error": "Sin host de conexion"}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "tpvs": TPVS_CONOCIDOS})

    tpvs_bd = _leer_tpvs_de_bd(host)
    if not tpvs_bd:
        log("Fallback a TPVs por defecto", "warn")
        return jsonify({"ok": True, "fallback": True, "tpvs": TPVS_CONOCIDOS})

    # Si el usuario conectó con una IP distinta a la calculada para ese TPV
    # (ej: conectó con 127.0.0.1 en lugar de 10.0.0.101),
    # sustituir la IP del TPV que coincida con la IP de sesión
    for t in tpvs_bd:
        ip_calculada = t["ip"]
        if ip_calculada == host:
            break  # ya coincide, no hay que cambiar nada
    else:
        # La IP de sesión no coincide con ninguna IP calculada
        # → el usuario conectó con una IP alternativa (127.0.0.1, IP temporal...)
        # Sustituir la IP del primer TPV por la IP de sesión
        if tpvs_bd:
            log(f"IP de sesión {host} sustituye a {tpvs_bd[0]['ip']} para el escaneo", "info")
            tpvs_bd[0]["ip"] = host
            _guardar_config({"ip_override_tpv1": host})

    # Actualizar TPVS_CONOCIDOS e IPS_CONOCIDAS para las operaciones
    TPVS_CONOCIDOS = tpvs_bd
    IPS_CONOCIDAS  = [t["ip"] for t in tpvs_bd]

    return jsonify({"ok": True, "tpvs": tpvs_bd})


@app.route("/api/tpvs/escanear")
@need_conn
def api_escanear():
    res = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(probar_tpv, t): t for t in TPVS_CONOCIDOS}
        for f in as_completed(futs):
            try:
                res.append(f.result())
            except Exception as e:
                t = futs[f]
                res.append({**t, "accesible": False,
                            "estado": "error", "error": str(e)})
    res.sort(key=lambda x: x["id"])
    ok = sum(1 for r in res if r["accesible"])
    log(f"Escaneo: {ok}/4 TPVs accesibles", "info")
    return jsonify({"ok": True, "tpvs": res})


@app.route("/api/series")
@need_conn
def api_series():
    """Lista las series de facturacion (tabla serie) de un TPV."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "series": []})
    c = None
    try:
        c   = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id_serie, serie, descripcion, factura, "
                    "rectificativa, comision, propia "
                    "FROM serie ORDER BY id_serie")
        rows = cur.fetchall()
        log(f"Series leidas de {host} ({len(rows)} registros)", "ok")
        return jsonify({"ok": True, "demo": False,
                        "series": [dict(r) for r in rows]})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_series {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer las series"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _parsear_xml_numeros_serie(xml_text):
    """Parsea un XML con pares serie->numero aceptando varios formatos comunes:
       <series>
         <serie codigo="B01021" numero="4523"/>           Formato A: atributos
         <serie><codigo>...</codigo><numero>...</numero></serie>  Formato B: hijos
         <item><serie>...</serie><numero>...</numero></item>      Formato C: alias
       </series>
    Busca recursivamente nodos que tengan AMBOS un codigo/serie y un numero.
    Devuelve [{serie: str, numero: int}].
    Levanta ValueError con mensaje claro si el XML es invalido o no contiene
    ningun par identificable.
    NOTA seguridad: xml.etree.ElementTree NO expande entidades externas (XXE),
    aceptamos el contenido del fichero subido por el tecnico sin riesgo."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ValueError(f"XML mal formado: {e}")
    items = []
    visto = set()  # evitar duplicados por nodos solapados
    for el in root.iter():
        # 1) Probar como atributos del propio elemento
        codigo = el.get("codigo") or el.get("serie") or el.get("nombre")
        numero = el.get("numero") or el.get("contador") or el.get("siguiente")
        # 2) Si no hay atributos validos, probar como hijos del elemento
        if codigo is None or numero is None:
            codigo = (el.findtext("codigo") or el.findtext("serie")
                      or el.findtext("nombre"))
            numero = (el.findtext("numero") or el.findtext("contador")
                      or el.findtext("siguiente"))
        if codigo and numero is not None:
            try:
                serie_str = str(codigo).strip()
                numero_int = int(str(numero).strip())
                if serie_str and (serie_str, numero_int) not in visto:
                    visto.add((serie_str, numero_int))
                    items.append({"serie": serie_str, "numero": numero_int})
            except (ValueError, TypeError):
                # Ignorar entradas con numero no parseable
                pass
    if not items:
        raise ValueError("No se han encontrado pares serie+numero en el XML")
    return items


@app.route("/api/series/numero/preview", methods=["POST"])
@csrf
@need_conn
def api_series_numero_preview():
    """Parsea el XML y devuelve la lista de cambios SIN aplicar.
    Cada item devuelve: serie, numero_xml, numero_actual, accion.
    accion es uno de:
      - 'actualizar' (numero_actual != numero_xml)
      - 'sin_cambio' (ya coincide)
      - 'no_existe' (la serie del XML no existe en la BD local)
    """
    data = request.json or {}
    xml_text = str(data.get("xml_text", ""))
    if not xml_text.strip():
        return jsonify({"ok": False, "error": "Fichero XML vacio"}), 400
    try:
        entradas = _parsear_xml_numeros_serie(xml_text)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "items": [
            {**e, "numero_xml": e["numero"], "numero_actual": 1, "accion": "actualizar"}
            for e in entradas
        ], "total": len(entradas)})

    c = None
    try:
        c = conn_tpv("127.0.0.1")  # SIEMPRE la BD local en este flujo
        cur = c.cursor()
        codigos = list({e["serie"] for e in entradas})
        cur.execute("SELECT serie, numero FROM serie WHERE serie = ANY(%s)",
                    (codigos,))
        actuales = {row[0]: row[1] for row in cur.fetchall()}
        items = []
        for e in entradas:
            actual = actuales.get(e["serie"])
            if actual is None:
                accion = "no_existe"
            elif int(actual) == e["numero"]:
                accion = "sin_cambio"
            else:
                accion = "actualizar"
            items.append({
                "serie": e["serie"],
                "numero_xml": e["numero"],
                "numero_actual": int(actual) if actual is not None else None,
                "accion": accion,
            })
        log(f"[series numero preview] {len(items)} items procesados", "ok")
        return jsonify({"ok": True, "items": items, "total": len(items)})
    except Exception as ex:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(ex).split("\n")[0]
        log(f"WARN api_series_numero_preview: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo leer la BD local"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/series/numero/aplicar", methods=["POST"])
@csrf
@need_conn
def api_series_numero_aplicar():
    """Aplica los contadores serie.numero al TPV local (127.0.0.1).
    Body: {items: [{serie: str, numero: int}, ...]}
    UPDATE atomico en una transaccion. Si algun UPDATE falla, se loguea pero el
    resto siguen — al final se hace commit con los que SI funcionaron.
    Devuelve: {ok, actualizadas, no_encontradas, errores}."""
    data = request.json or {}
    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        return jsonify({"ok": False, "error": "Sin items a aplicar"}), 400

    # Validacion previa de formato (defensa)
    for it in items:
        if not isinstance(it, dict):
            return jsonify({"ok": False, "error": "Formato items invalido"}), 400
        try:
            int(it.get("numero"))
        except (ValueError, TypeError):
            return jsonify({"ok": False,
                            "error": f"numero invalido en serie {it.get('serie')}"}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
                        "actualizadas": items, "no_encontradas": [], "errores": []})

    c = None
    actualizadas, no_encontradas, errores = [], [], []
    try:
        c = conn_tpv("127.0.0.1")  # SIEMPRE la BD local en este flujo
        c.autocommit = False
        cur = c.cursor()
        for it in items:
            serie = str(it.get("serie", "")).strip()
            numero = int(it.get("numero"))
            if not serie:
                continue
            try:
                cur.execute("UPDATE serie SET numero = %s WHERE serie = %s",
                            (numero, serie))
                if cur.rowcount == 1:
                    actualizadas.append({"serie": serie, "numero": numero})
                elif cur.rowcount == 0:
                    no_encontradas.append(serie)
                else:
                    errores.append({"serie": serie,
                                    "error": f"{cur.rowcount} filas afectadas (esperaba 1)"})
            except Exception as e_row:
                errores.append({"serie": serie,
                                "error": str(e_row).split("\n")[0]})
        c.commit()
        log(f"[series numero aplicar] local: ok={len(actualizadas)}, "
            f"no_encontradas={len(no_encontradas)}, errores={len(errores)}", "ok")
        return jsonify({"ok": len(errores) == 0,
                        "actualizadas": actualizadas,
                        "no_encontradas": no_encontradas,
                        "errores": errores})
    except Exception as ex:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(ex).split("\n")[0]
        log(f"WARN api_series_numero_aplicar: {msg}", "warn")
        return jsonify({"ok": False,
                        "error": "No se pudo aplicar al TPV local"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ─────────────────────────────────────────────────────────────────────────────
# MARCAR DESCRIPCIONES DE SERIES PROPIAS con (N) — script SQL del cliente:
#   UPDATE serie SET descripcion = descripcion || '(' || N || ')'
#   WHERE propia = TRUE
# donde N son los digitos extraidos de `tpv.nombre` del TPV principal.
# Idempotente: las series cuya descripcion ya contiene "(N)" se respetan.
# Solo afecta al TPV LOCAL (127.0.0.1) — coherente con el resto de Series.
# ─────────────────────────────────────────────────────────────────────────────


def _extraer_num_de_nombre(nombre):
    """Extrae los digitos de `nombre` (p.ej. 'TPV 2' -> '2', 'POS-12' -> '12').
    Mimetiza el REGEXP_REPLACE del script SQL del cliente.
    Devuelve string ('1', '12', ...) o None si no hay digitos."""
    if not nombre:
        return None
    digits = "".join(ch for ch in str(nombre) if ch.isdigit())
    return digits if digits else None


@app.route("/api/series/marcar/preview")
@need_conn
def api_series_marcar_preview():
    """Devuelve qué series propias se actualizarían y con qué descripción nueva.
    Returns: {ok, num_tpv_principal, tpv_principal_nombre, items: [{serie,
              descripcion_actual, descripcion_nueva, accion}], total}
    Accion ∈ {actualizar, ya_marcada}.
    """
    c = None
    try:
        c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="tpv",
                             user="postgres", password=sess.get("password", ""),
                             connect_timeout=5)
        cur = c.cursor()
        # 1) Encontrar el TPV principal y extraer N de su nombre
        cur.execute("SELECT id_tpv, nombre FROM tpv "
                    "WHERE principal = TRUE LIMIT 1")
        row = cur.fetchone()
        if not row:
            return jsonify({"ok": False,
                            "error": "No hay ningún TPV con principal=TRUE en la BD local"}), 400
        id_tpv_principal, nombre_principal = row
        num = _extraer_num_de_nombre(nombre_principal)
        if num is None:
            # Fallback: usar id_tpv como número (caso BD vieja sin nombre)
            num = str(id_tpv_principal)
        marcador = f"({num})"

        # 2) Listar series con propia=TRUE y calcular accion para cada una
        cur.execute("SELECT serie, COALESCE(descripcion, '') AS descripcion "
                    "FROM serie WHERE propia = TRUE ORDER BY serie")
        items = []
        for serie, descripcion in cur.fetchall():
            if marcador in (descripcion or ""):
                accion = "ya_marcada"
                nueva  = descripcion
            else:
                accion = "actualizar"
                # rstrip elimina espacios al final del original ANTES de concatenar
                # — evita resultados feos como "Factura Simplificada (1)" (con
                # espacio antes del parentesis). El espacio interno se respeta.
                nueva  = (descripcion or "").rstrip() + marcador
            items.append({
                "serie": serie,
                "descripcion_actual": descripcion or "",
                "descripcion_nueva": nueva,
                "accion": accion,
            })
        return jsonify({
            "ok": True,
            "num_tpv_principal": int(num) if num.isdigit() else num,
            "tpv_principal_nombre": nombre_principal or "",
            "items": items,
            "total": len(items),
        })
    except Exception as ex:
        msg = str(ex).split("\n")[0]
        log(f"WARN api_series_marcar_preview: {msg}", "warn")
        return jsonify({"ok": False,
                        "error": "No se pudo leer la BD local"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/series/marcar/aplicar", methods=["POST"])
@csrf
@need_conn
def api_series_marcar_aplicar():
    """Aplica los UPDATEs al TPV LOCAL (127.0.0.1). Body: {items: [{serie,
    descripcion_nueva}, ...]}. Returns: {ok, actualizadas, no_encontradas, errores}.
    """
    data = request.json or {}
    items = data.get("items", [])
    if not isinstance(items, list) or not items:
        return jsonify({"ok": False, "error": "Sin items a aplicar"}), 400
    # Defensa: cada item debe ser dict con serie+descripcion_nueva
    for it in items:
        if not isinstance(it, dict) or not it.get("serie"):
            return jsonify({"ok": False, "error": "Formato de items invalido"}), 400

    c = None
    actualizadas, no_encontradas, errores = [], [], []
    try:
        c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="tpv",
                             user="postgres", password=sess.get("password", ""),
                             connect_timeout=5)
        c.autocommit = False
        cur = c.cursor()
        for it in items:
            serie = str(it.get("serie", "")).strip()
            nueva = it.get("descripcion_nueva", "")
            if nueva is None:
                nueva = ""
            if not serie:
                continue
            try:
                # Solo actualizar si sigue siendo propia=TRUE — defensa frente
                # a cambios concurrentes entre preview y aplicar.
                cur.execute("UPDATE serie SET descripcion = %s "
                            "WHERE serie = %s AND propia = TRUE",
                            (nueva, serie))
                if cur.rowcount == 1:
                    actualizadas.append({"serie": serie, "descripcion_nueva": nueva})
                elif cur.rowcount == 0:
                    no_encontradas.append(serie)
                else:
                    errores.append({"serie": serie,
                                    "error": f"{cur.rowcount} filas afectadas"})
            except Exception as e_row:
                errores.append({"serie": serie,
                                "error": str(e_row).split("\n")[0]})
        c.commit()
        log(f"[series marcar] aplicado al local: ok={len(actualizadas)}, "
            f"no_encontradas={len(no_encontradas)}, errores={len(errores)}",
            "ok")
        return jsonify({"ok": len(errores) == 0,
                        "actualizadas": actualizadas,
                        "no_encontradas": no_encontradas,
                        "errores": errores})
    except Exception as ex:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(ex).split("\n")[0]
        log(f"WARN api_series_marcar_aplicar: {msg}", "warn")
        return jsonify({"ok": False,
                        "error": "No se pudo aplicar al TPV local"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/series/marcar/red", methods=["POST"])
@csrf
@need_conn
def api_series_marcar_red():
    """Aplica el marcado de descripciones en TODOS los TPVs accesibles en
    paralelo. En cada TPV: localiza el row de tpv.principal=TRUE (que en
    cada TPV identifica al propio TPV — la fila principal se replica a
    nivel local con el id_tpv de cada uno), extrae los digitos del nombre y
    actualiza serie.descripcion de las series con propia=TRUE que no tengan
    ya el marcador (N).

    Idempotente: en cada TPV se respetan las series ya marcadas.
    """
    if sess.get("demo"):
        resultados = [{"host": t["ip"], "nombre": t["nombre"], "ok": True,
                       "marcador": "(1)", "actualizadas": 0, "ya_marcadas": 14}
                      for t in TPVS_CONOCIDOS]
        return jsonify({"ok": True, "demo": True, "total": len(resultados),
                        "ok_count": len(resultados), "fail_count": 0,
                        "resultados": resultados})

    pwd = sess.get("password", "")

    def _apply_one(tpv):
        # Patron estandar de los otros /red: NO filtrar por tpv.accesible
        # (puede estar desactualizado entre escaneos). Confiamos en el
        # try/except: si no se puede conectar, el error queda en el resultado.
        host = tpv["ip"]
        nombre_tpv = tpv.get("nombre", host)
        c = None
        try:
            c = psycopg2.connect(host=host, port=5432, dbname="tpv",
                                 user="postgres", password=pwd,
                                 connect_timeout=5)
            c.autocommit = False
            cur = c.cursor()
            # 1) Localizar el principal y extraer digitos del nombre
            cur.execute("SELECT id_tpv, nombre FROM tpv "
                        "WHERE principal = TRUE LIMIT 1")
            row = cur.fetchone()
            if not row:
                return {"host": host, "nombre": nombre_tpv, "ok": False,
                        "error": "Sin TPV con principal=TRUE en su BD"}
            id_tpv_p, nombre_p = row
            num = _extraer_num_de_nombre(nombre_p) or str(id_tpv_p)
            marcador = f"({num})"

            # 2) Contar las que YA estan marcadas (para reporting)
            cur.execute("SELECT COUNT(*) FROM serie "
                        "WHERE propia = TRUE AND descripcion LIKE %s",
                        (f"%{marcador}%",))
            ya_marcadas = int(cur.fetchone()[0] or 0)

            # 3) Actualizar las que no tienen el marcador.
            # RTRIM al original ANTES de concatenar para evitar espacios feos
            # al final ("Factura Simplificada (1)" → "Factura Simplificada(1)").
            cur.execute(
                "UPDATE serie "
                "SET descripcion = RTRIM(COALESCE(descripcion, '')) || %s "
                "WHERE propia = TRUE "
                "  AND (descripcion IS NULL OR descripcion NOT LIKE %s)",
                (marcador, f"%{marcador}%"))
            actualizadas = cur.rowcount
            c.commit()

            return {"host": host, "nombre": nombre_tpv, "ok": True,
                    "marcador": marcador,
                    "actualizadas": int(actualizadas),
                    "ya_marcadas": ya_marcadas}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            return {"host": host, "nombre": nombre_tpv, "ok": False,
                    "error": str(e).split("\n")[0]}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    with ThreadPoolExecutor(max_workers=4) as ex:
        resultados = list(ex.map(_apply_one, TPVS_CONOCIDOS))
    ok_count = sum(1 for r in resultados if r.get("ok"))
    fail_count = len(resultados) - ok_count
    log(f"[series marcar /red] ok={ok_count} fail={fail_count}",
        "ok" if fail_count == 0 else "warn")
    return jsonify({"ok": fail_count == 0,
                    "total": len(resultados),
                    "ok_count": ok_count,
                    "fail_count": fail_count,
                    "resultados": resultados})


@app.route("/api/series/marcar/global", methods=["POST"])
@csrf
@need_conn
def api_series_marcar_global():
    """Marca CADA serie en cada BD con (N) del propietario REAL — incluyendo
    series ajenas que cada TPV tiene en su tabla pero pertenecen a otro.

    Body opcional: {dry_run: bool} — si True, NO ejecuta UPDATEs (cuenta
    pero no toca BD). Util para preview previo a la accion real.

    Diferencia con /api/series/marcar/red:
      - /red: cada TPV marca SOLO sus propia=TRUE con SU propio (N).
      - /global: descubre el mapa de propietarios escaneando toda la red,
        y luego en cada TPV marca CADA serie (propia o ajena) con el (N)
        del propietario real. Las huerfanas (sin propietario en la red) se
        dejan sin tocar.

    Idempotencia conservadora: si la descripcion ya contiene cualquier
    "(N)" actualmente, NO se toca — asume que el usuario sabe lo que hace.
    Si NO tiene marcador, se aplica el del propietario.

    Returns: {ok, dry_run, fase1:{propietarios, conflictos}, fase2:[{host,
              nombre, ok, actualizadas, ya_marcadas, sin_propietario, error?}]}
    """
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "dry_run": False,
                        "fase1": {"propietarios": {}, "conflictos": []},
                        "fase2": []})

    data = request.json or {}
    dry_run = bool(data.get("dry_run", False))

    pwd = sess.get("password", "")
    if not pwd:
        return jsonify({"ok": False, "error": "Sin pwd en sesion"}), 401

    # ── FASE 1: descubrir propietarios ───────────────────────────────────
    # Por cada TPV vivo: leer sus series propia=TRUE + identidad.
    def _descubrir(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = psycopg2.connect(host=host, port=5432, dbname="tpv",
                                 user="postgres", password=pwd,
                                 connect_timeout=5)
            cur = c.cursor()
            # Identidad local: id_tpv del row principal=TRUE
            cur.execute("SELECT id_tpv, nombre FROM tpv "
                        "WHERE principal = TRUE LIMIT 1")
            row = cur.fetchone()
            if not row:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": "Sin tpv.principal=TRUE en su BD",
                        "num_tpv": None, "propias": []}
            id_tpv_local, nombre_local = int(row[0]), row[1]
            num_str = _extraer_num_de_nombre(nombre_local) or str(id_tpv_local)
            # Series propias
            cur.execute("SELECT serie FROM serie "
                        "WHERE propia = TRUE AND serie IS NOT NULL")
            propias = [r[0] for r in cur.fetchall()]
            return {"host": host, "nombre": nombre, "ok": True,
                    "num_tpv": id_tpv_local, "num_str": num_str,
                    "propias": propias}
        except Exception as e:
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": str(e).split("\n")[0],
                    "num_tpv": None, "propias": []}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    with ThreadPoolExecutor(max_workers=4) as ex:
        descubrimientos = list(ex.map(_descubrir, TPVS_CONOCIDOS))

    # Construir mapping codigo_serie → (num_tpv, num_str). En caso de
    # conflicto (mismo codigo como propia en >1 TPV), preferimos el de
    # menor id_tpv (consistente con la heuristica de /red).
    propietarios = {}        # codigo → (num_tpv, num_str)
    conflictos_por_serie = {}  # codigo → [num_tpv, ...]
    for d in descubrimientos:
        if not d.get("ok"):
            continue
        n = d["num_tpv"]
        for codigo in d.get("propias", []):
            if codigo in propietarios:
                conflictos_por_serie.setdefault(
                    codigo, [propietarios[codigo][0]]).append(n)
                # Prefiere el menor id_tpv (sustituye si entrante es menor)
                if n < propietarios[codigo][0]:
                    propietarios[codigo] = (n, d["num_str"])
            else:
                propietarios[codigo] = (n, d["num_str"])
    conflictos = [
        {"serie": k, "tpvs": sorted(set(v)),
         "elegido": propietarios[k][0]}
        for k, v in conflictos_por_serie.items()
    ]

    # ── FASE 2: aplicar marcadores en cada TPV en paralelo ───────────────
    # Por cada serie en su tabla: si tiene propietario en el mapping y
    # NO tiene ya un (N) en su descripcion, marcarla con el (N) del
    # propietario. Si ya tiene (cualquier) (N), respetar.
    def _aplicar(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        # ¿Este TPV respondió en la fase 1? Si no, no podemos saber su
        # id_tpv local — pero podemos seguir aplicando (no necesitamos
        # el id local para esta fase, solo el mapping global).
        c = None
        try:
            c = psycopg2.connect(host=host, port=5432, dbname="tpv",
                                 user="postgres", password=pwd,
                                 connect_timeout=5)
            c.autocommit = False
            cur = c.cursor()
            # Listar todas las series de este TPV
            cur.execute("SELECT id_serie, serie, COALESCE(descripcion,'') "
                        "FROM serie ORDER BY id_serie")
            filas = cur.fetchall()
            actualizadas, ya_marcadas, sin_propietario = 0, 0, 0
            errores_serie = []
            # Sample de las primeras 5 actualizaciones para que el preview
            # las muestre — util para que el tecnico vea exactamente que
            # se va a tocar antes de pulsar "Aplicar".
            ejemplos = []
            # Regex para detectar cualquier (N) ya presente — \(\d+\)
            import re
            ya_marcador = re.compile(r"\(\d+\)")
            for id_s, codigo, desc in filas:
                if not codigo or codigo not in propietarios:
                    sin_propietario += 1
                    continue
                if ya_marcador.search(desc or ""):
                    ya_marcadas += 1
                    continue
                marcador = f"({propietarios[codigo][1]})"
                nueva = (desc or "").rstrip() + marcador
                if len(ejemplos) < 5:
                    ejemplos.append({
                        "id_serie": int(id_s), "serie": codigo,
                        "antes": desc or "", "despues": nueva,
                        "marcador": marcador,
                    })
                if dry_run:
                    actualizadas += 1
                    continue
                try:
                    cur.execute("UPDATE serie SET descripcion = %s "
                                "WHERE id_serie = %s",
                                (nueva, id_s))
                    if cur.rowcount == 1:
                        actualizadas += 1
                    else:
                        errores_serie.append(f"id={id_s}: rowcount={cur.rowcount}")
                except Exception as eu:
                    errores_serie.append(f"id={id_s}: {str(eu).split(chr(10))[0]}")
            if dry_run:
                # Ningún cambio queda en la BD — rollback explicito por higiene
                try: c.rollback()
                except Exception: pass
            else:
                c.commit()
            return {"host": host, "nombre": nombre, "ok": True,
                    "actualizadas": actualizadas,
                    "ya_marcadas": ya_marcadas,
                    "sin_propietario": sin_propietario,
                    "errores_serie": errores_serie[:10],
                    "ejemplos": ejemplos}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": str(e).split("\n")[0]}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    with ThreadPoolExecutor(max_workers=4) as ex:
        fase2 = list(ex.map(_aplicar, TPVS_CONOCIDOS))

    ok_count = sum(1 for r in fase2 if r.get("ok"))
    log(f"[series marcar /global{' DRY' if dry_run else ''}] "
        f"propietarios={len(propietarios)} conflictos={len(conflictos)} "
        f"fase2_ok={ok_count}/{len(fase2)}",
        "ok" if ok_count == len(fase2) else "warn")

    return jsonify({
        "ok": ok_count == len(fase2),
        "dry_run": dry_run,
        "fase1": {
            "propietarios": {k: {"num_tpv": v[0], "num_str": v[1]}
                             for k, v in propietarios.items()},
            "total_propietarios": len(propietarios),
            "conflictos": conflictos,
        },
        "fase2": fase2,
        "ok_count": ok_count,
        "fail_count": len(fase2) - ok_count,
        "total": len(fase2),
    })


@app.route("/api/series/mapa-red")
@need_conn
def api_series_mapa_red():
    """Vista consolidada de la red: para cada TPV accesible devuelve sus
    series propia=TRUE + su identidad (id_tpv/nombre via tpv.principal=TRUE
    local) en paralelo. Util para ver de un vistazo qué id_serie/serie
    pertenece a qué TPV en toda la estacion.

    Detecta conflictos: codigos de serie marcados como propia en varios
    TPVs simultaneamente (sintoma de mala configuracion).

    Returns: {ok, tpvs: [{ip, nombre, num_tpv, ok, total_propias,
              series:[{id_serie, serie, descripcion, factura,...}], error?}],
              conflictos: [{serie, owners:[{ip,nombre,num_tpv}]}]}
    """
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "tpvs": [], "conflictos": []})

    pwd = sess.get("password", "")

    def _scan_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = psycopg2.connect(host=host, port=5432, dbname="tpv",
                                 user="postgres", password=pwd,
                                 connect_timeout=5)
            cur = c.cursor()
            # 1) Identidad: en cada BD, tpv.principal=TRUE es la fila propia
            cur.execute("SELECT id_tpv, nombre FROM tpv "
                        "WHERE principal = TRUE LIMIT 1")
            row = cur.fetchone()
            if row:
                id_tpv_local, nombre_local = row
            else:
                id_tpv_local, nombre_local = None, None
            # 2) Series propias del TPV. Schema completo conocido (CREATE TABLE
            # publico): factura, credito, contado, rectificativa, comision,
            # no_venta, sistema_venta_externo, firma_digital, envio_fiscal,
            # desglosa_impuesto, ... Usamos los booleanos relevantes para
            # clasificar la serie en la UI.
            cur.execute(
                "SELECT id_serie, serie, COALESCE(descripcion,'') AS descripcion,"
                "       factura, rectificativa, comision, credito, contado,"
                "       no_venta, sistema_venta_externo, firma_digital, envio_fiscal "
                "FROM serie WHERE propia = TRUE "
                "ORDER BY id_serie")
            series = []
            for r in cur.fetchall():
                series.append({
                    "id_serie":              int(r[0]),
                    "serie":                 r[1] or "",
                    "descripcion":           r[2] or "",
                    "factura":               bool(r[3]),
                    "rectificativa":         bool(r[4]),
                    "comision":              bool(r[5]),
                    "credito":               bool(r[6]),
                    "contado":               bool(r[7]),
                    "no_venta":              bool(r[8]),
                    "sistema_venta_externo": bool(r[9]),
                    "firma_digital":         bool(r[10]),
                    "envio_fiscal":          bool(r[11]),
                })
            return {"ip": host, "nombre": nombre, "ok": True,
                    "num_tpv": id_tpv_local, "nombre_local": nombre_local,
                    "total_propias": len(series), "series": series}
        except Exception as e:
            return {"ip": host, "nombre": nombre, "ok": False,
                    "error": str(e).split("\n")[0],
                    "num_tpv": None, "total_propias": 0, "series": []}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    with ThreadPoolExecutor(max_workers=4) as ex:
        resultados = list(ex.map(_scan_one, TPVS_CONOCIDOS))

    # Detectar conflictos: codigos `serie` marcados como propia en >1 TPV
    serie_owners = {}
    for tpv_res in resultados:
        if not tpv_res.get("ok"):
            continue
        for s in tpv_res["series"]:
            key = s["serie"]
            if not key:
                continue
            serie_owners.setdefault(key, []).append({
                "ip": tpv_res["ip"],
                "nombre": tpv_res["nombre"],
                "num_tpv": tpv_res.get("num_tpv"),
                "id_serie": s["id_serie"],
            })
    conflictos = [
        {"serie": k, "owners": v}
        for k, v in sorted(serie_owners.items())
        if len(v) > 1
    ]

    ok_count = sum(1 for r in resultados if r.get("ok"))
    return jsonify({
        "ok": True,
        "total_tpvs": len(resultados),
        "ok_count": ok_count,
        "fail_count": len(resultados) - ok_count,
        "tpvs": resultados,
        "conflictos": conflictos,
    })


@app.route("/api/propiedades")
@need_conn
def api_get_props():
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "propiedades": _demo(host)})
    c = None
    try:
        c   = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cl  = list(CLAVES)
        ph  = ",".join(["%s"] * len(cl))
        cur.execute(
            f"SELECT clave, valor FROM propiedad WHERE clave IN ({ph}) ORDER BY clave", cl)
        rows = cur.fetchall()
        log(f"Props leidas de {host} ({len(rows)} registros)", "ok")
        return jsonify({"ok": True, "demo": False,
                        "propiedades": {r["clave"]: r["valor"] for r in rows}})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_props {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer las propiedades"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/propiedades", methods=["POST"])
@csrf
@need_conn
def api_set_props():
    data = request.json or {}
    try:
        host = val_host(data.get("host_tpv", sess.get("host", "")))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    upd = data.get("updates", {})
    if not upd:
        return jsonify({"ok": False, "error": "Sin cambios"}), 400
    if not isinstance(upd, dict) or len(upd) > 20:
        return jsonify({"ok": False, "error": "Updates invalido"}), 400
    bad = set(upd.keys()) - CLAVES
    if bad:
        return jsonify({"ok": False,
                        "error": f"Claves no permitidas: {sorted(bad)}"}), 400
    for k, v in upd.items():
        if not isinstance(v, str) or len(v) > _MAX_V:
            return jsonify({"ok": False, "error": f"Valor invalido para {k}"}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "afectadas": len(upd)})
    c = None
    try:
        c = conn_tpv(host)
        c.autocommit = False
        cur = c.cursor()
        n = 0
        for k, v in upd.items():
            cur.execute("UPDATE propiedad SET valor=%s WHERE clave=%s", (v, k))
            n += cur.rowcount
        c.commit()
        log(f"Actualizado {host}: {', '.join(sorted(upd.keys()))}", "ok")
        return jsonify({"ok": True, "afectadas": n})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_props {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# =============================================================================
# OPERACIONES DE INTEGRACION
# =============================================================================

@app.route("/api/operacion/anular", methods=["POST"])
@csrf
@need_conn
def api_anular():
    """
    Anula un TPV averiado (su BD puede ser inaccesible).
    NO toca la BD del TPV anulado.
    Actualiza los CopyDirectories de todos los TPVs ACTIVOS
    eliminando la IP del TPV anulado de sus rutas.

    Si el TPV anulado era el PRINCIPAL, devuelve aviso_hibernate
    con instrucciones exactas para editar hibernateCentral.cfg.xml.
    """
    data = request.json or {}
    try:
        host_anulado = val_host(data.get("host_tpv", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    nombre_anulado = str(data.get("nombre", host_anulado))[:64]
    era_principal  = data.get("era_principal", False)

    # IPs que siguen activas (todos excepto el anulado)
    ips_activas_raw = data.get("ips_activas", [])
    ips_activas = []
    for ip in ips_activas_raw:
        try:
            ips_activas.append(val_host(ip))
        except Exception:
            pass

    if not ips_activas:
        return jsonify({"ok": False,
                        "error": "No hay TPVs activos a los que aplicar el cambio"}), 400

    # Determinar qué TPV es el principal entre los activos
    ip_principal = None
    for t in TPVS_CONOCIDOS:
        if t["ip"] in ips_activas and t["rol"] == "principal":
            ip_principal = t["ip"]
            break
    if not ip_principal:
        ip_principal = ips_activas[0]  # fallback: el primero activo

    errores = []
    exitos  = []

    # id_tpv del TPV anulado (para borrar su sesion en cada TPV accesible)
    id_tpv_anulado = _ip_a_id_tpv(host_anulado)

    for ip_activa in ips_activas:
        es_principal = (ip_activa == ip_principal)

        if es_principal:
            cd = _copy_dirs_principal(ip_activa, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectoriesMaestros")),
            ]
        else:
            cd = _copy_dirs_secundario(ip_activa, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
            ]

        r = _run(ip_activa, sqls,
                 f"Actualizado {ip_activa}: CopyDirectories sin {host_anulado}")
        # Borrar sesion del TPV anulado en este TPV accesible
        if id_tpv_anulado > 0:
            _borrar_sesion_tpv(ip_activa, id_tpv_anulado)
        if r["ok"]:
            exitos.append(ip_activa)
        else:
            errores.append(f"{ip_activa}: {r.get('error','?')}")

    # ── Actualizar tabla pos: online=False para el TPV anulado ──────────────────
    # Se actualiza en TODOS los TPVs accesibles para sincronizar su tabla pos
    for ip_activa in ips_activas:
        r_pos = _set_pos_online(ip_activa, host_anulado, False)
        if not r_pos["ok"] and not r_pos.get("demo"):
            errores.append(f"{ip_activa} (pos): {r_pos.get('error','?')}")

    log(f"ANULADO {nombre_anulado} ({host_anulado}) — "
        f"Actualizados: {exitos}, Errores: {errores}", "ok" if not errores else "warn")

    # Aviso hibernate — solo si el anulado era el principal
    aviso_hibernate = None
    if era_principal:
        # NO asumimos quién será el nuevo principal — el técnico lo decidirá
        # Solo avisamos que hay que editar hibernate DESPUÉS de elegir el nuevo principal
        aviso_hibernate = (
            f"=" * 60 + "\n"
            f"ACCION MANUAL REQUERIDA — FICHERO HIBERNATE\n"
            f"=" * 60 + "\n"
            f"\n"
            f"Has anulado {host_anulado} que era el PRINCIPAL.\n"
            f"\n"
            f"PASO 1 — En la app: pulsa 'Hacer principal' en el TPV\n"
            f"         que quieras designar como nuevo principal.\n"
            f"         La app actualizara la BD de todos los TPVs.\n"
            f"\n"
            f"PASO 2 — Editar en CADA TPV accesible:\n"
            f"         C:\\GARUM\\hibernateCentral.cfg.xml\n"
            f"\n"
            f"         Cuando sepas el nuevo principal (ej: 10.0.0.102):\n"
            f"         En el nuevo principal:\n"
            f"           Sustituir: jdbc:postgresql://localhost:5432/tpv\n"
            f"         En cada secundario:\n"
            f"           Sustituir: jdbc:postgresql://10.0.0.102:5432/tpv\n"
            f"\n"
            f"         (La operacion 'Hacer principal' te dara las instrucciones exactas)\n"
            f"\n"
            f"PASO 3 — Reiniciar GARUM en todos los TPVs.\n"
            f"\n"
            f"IMPORTANTE: hibernate.cfg.xml (sin Central) NO se toca nunca."
        )

    return jsonify({
        "ok": len(errores) == 0,
        "exitos": exitos,
        "errores": errores,
        "aviso_hibernate": aviso_hibernate,
        "msg": (f"TPV {nombre_anulado} anulado. "
                f"Actualizados {len(exitos)} TPVs." +
                (" Ver aviso hibernate." if aviso_hibernate else ""))
    })


@app.route("/api/operacion/borrar_sesion", methods=["POST"])
@csrf
@need_conn
def api_borrar_sesion():
    """
    Quita la sesion activa de un TPV en la tabla sesion_tpv_activo.
    Ejecuta DELETE WHERE id_tpv=N en todos los TPVs de ips_destino
    (los accesibles, incluido el propio TPV si esta accesible).
    No toca CopyDirectories ni pos: solo limpia la sesion.
    """
    data = request.json or {}
    try:
        host = val_host(data.get("host_tpv", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    nombre = str(data.get("nombre", host))[:64]

    # TPVs donde ejecutar el DELETE (los accesibles que manda el frontend)
    ips_destino = []
    for ip in data.get("ips_destino", []):
        try:
            ips_destino.append(val_host(ip))
        except Exception:
            pass

    if not ips_destino:
        return jsonify({"ok": False,
                        "error": "No hay TPVs accesibles donde quitar la sesion"}), 400

    # id_tpv real del TPV: lo envia el frontend (t.id); si no llega, se deriva de la IP
    id_tpv = data.get("id_tpv")
    try:
        id_tpv = int(id_tpv)
    except (TypeError, ValueError):
        id_tpv = _ip_a_id_tpv(host)
    if id_tpv <= 0:
        return jsonify({"ok": False,
                        "error": f"id_tpv no valido para {nombre}"}), 400

    exitos  = []
    errores = []
    total_borradas = 0
    for ip_destino in ips_destino:
        r = _borrar_sesion_tpv(ip_destino, id_tpv)
        if r["ok"]:
            exitos.append(ip_destino)
            total_borradas += r.get("borradas", 0)
        else:
            errores.append(f"{ip_destino}: {r.get('error', '?')}")

    log(f"Sesion id_tpv={id_tpv} ({nombre}) quitada en {len(exitos)} TPV(s), "
        f"{total_borradas} fila(s)", "ok" if not errores else "warn")

    return jsonify({
        "ok": len(errores) == 0,
        "exitos": exitos,
        "errores": errores,
        "msg": (f"Sesion de {nombre} quitada de {len(exitos)} TPV(s). "
                f"{total_borradas} fila(s) eliminada(s) de sesion_tpv_activo.")
    })


@app.route("/api/operacion/activar_secundario", methods=["POST"])
@csrf
@need_conn
def api_act_sec():
    """
    Reactiva un TPV reparado como secundario.
    Actualiza su propia BD Y recalcula los CopyDirectories
    de todos los demas TPVs para incluirle.
    No requiere cambio de hibernate (solo el principal lo necesita).
    """
    data = request.json or {}
    try:
        host = val_host(data.get("host_tpv", ""))
        host_principal = val_host(data.get("host_principal", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    nombre = str(data.get("nombre", host))[:64]

    # IPs que estaran activas tras la reactivacion (incluye el que se activa)
    ips_activas_raw = data.get("ips_activas", IPS_CONOCIDAS)
    ips_activas = []
    for ip in ips_activas_raw:
        try:
            ips_activas.append(val_host(ip))
        except Exception:
            pass
    if host not in ips_activas:
        ips_activas.append(host)
    if not ips_activas:
        ips_activas = IPS_CONOCIDAS

    errores = []
    exitos  = []

    # 1. Configurar el TPV reactivado como secundario
    cd_nuevo = _copy_dirs_secundario(host, ips_activas)
    bos = f"//{host_principal}/c/integracion/4GLExport"
    sqls_nuevo = [
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR,      "InputDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR_COPY, "InputDirectoryCopy")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd_nuevo,         "CopyDirectories")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (bos,              "BackupDirectoriesBOS")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "CopyDirectoriesMaestros")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "BackupDirectoryMaestroMovidosTpvPrincipal")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_ERROR_DIR,      "ErrorDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_MAESTRO, "BackupDirectoryMaestro")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_TRANS,   "BackupDirectoryTransaccion")),
    ]
    r = _run(host, sqls_nuevo, f"Configurado {nombre} como secundario")
    if r["ok"]:
        exitos.append(host)
    else:
        errores.append(f"{host}: {r.get('error','?')}")

    # 2. Actualizar CopyDirectories en los demas TPVs para incluir al reactivado
    for ip_otro in ips_activas:
        if ip_otro == host:
            continue
        es_principal = (ip_otro == host_principal)
        if es_principal:
            cd = _copy_dirs_principal(ip_otro, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectoriesMaestros")),
            ]
        else:
            cd = _copy_dirs_secundario(ip_otro, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
            ]
        r2 = _run(ip_otro, sqls,
                  f"Actualizado {ip_otro}: incluido {host} en CopyDirectories")
        if r2["ok"]:
            exitos.append(ip_otro)
        else:
            errores.append(f"{ip_otro}: {r2.get('error','?')}")

    # sesion_tpv_activo NO se toca al reintegrar:
    # GARUM creará automáticamente la sesión de este TPV cuando arranque.

    # ── Actualizar controlpista del TPV reactivado ──────────────────────────────
    # ip_server debe apuntar al principal actual
    r_cp = _actualizar_controlpista(host, host_principal)
    if not r_cp["ok"] and not r_cp.get("demo"):
        errores.append(f"{host} (controlpista): {r_cp.get('error','?')}")

    # ── Actualizar tabla pos: online=True para el TPV reactivado ─────────────
    # Se sincroniza en TODOS los TPVs accesibles (incluido el reactivado)
    for ip_sync in ips_activas:
        r_pos = _set_pos_online(ip_sync, host, True)
        if not r_pos["ok"] and not r_pos.get("demo"):
            errores.append(f"{ip_sync} (pos): {r_pos.get('error','?')}")

    log(f"ACTIVADO {nombre} como secundario. Exitos: {exitos}, Errores: {errores}",
        "ok" if not errores else "warn")

    # Aviso hibernate para el TPV reactivado:
    # Su hibernateCentral.cfg.xml puede apuntar a localhost (si era principal antes)
    # o a una IP de principal antigua. Hay que actualizarlo para apuntar al principal actual.
    aviso_hib_sec = (
        f"=" * 60 + "\n"
        f"ACCION MANUAL EN {host} — FICHERO HIBERNATE\n"
        f"=" * 60 + "\n"
        f"\n"
        f"Editar en {host}:\n"
        f"  C:\\GARUM\\hibernateCentral.cfg.xml\n"
        f"\n"
        f"  Verificar que contiene:\n"
        f"    jdbc:postgresql://{host_principal}:5432/tpv\n"
        f"\n"
        f"  Si contiene localhost o una IP diferente, sustituir por:\n"
        f"    jdbc:postgresql://{host_principal}:5432/tpv\n"
        f"\n"
        f"IMPORTANTE: hibernate.cfg.xml (sin Central) NO se toca nunca.\n"
        f"\n"
        f"Tras editar: reiniciar GARUM en {host}."
    )

    return jsonify({
        "ok": len(errores) == 0,
        "exitos": exitos,
        "errores": errores,
        "aviso_hibernate": aviso_hib_sec,
        "msg": (f"{nombre} activado como secundario. "
                f"Actualizados {len(exitos)} TPVs. Ver aviso hibernate.")
    })


@app.route("/api/operacion/activar_principal", methods=["POST"])
@csrf
@need_conn
def api_act_pri():
    """
    Convierte un TPV en el nuevo principal. Actualiza la BD de TODOS
    los TPVs activos — incluyendo el ex-principal que pasa a secundario.

    Ejemplo: TPV4 era principal, TPV2 pasa a principal.
      - TPV2: BackupDirectoriesBOS=local, CopyDirectories->101,103,104, CopyDirectoriesMaestros activo
      - TPV4: BackupDirectoriesBOS=//TPV2/..., CopyDirectories->101,102,103, CopyDirectoriesMaestros=''
      - TPV1: BackupDirectoriesBOS=//TPV2/..., CopyDirectories->102,103,104 (sin cambio de CopyDirs si ya apuntaba a todos)
      - TPV3: BackupDirectoriesBOS=//TPV2/..., CopyDirectories->101,102,104

    El aviso hibernate indica qué fichero editar en cada TPV.
    """
    data = request.json or {}
    try:
        host_nuevo = val_host(data.get("host_tpv", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    nombre = str(data.get("nombre", host_nuevo))[:64]

    ips_activas_raw = data.get("ips_activas", IPS_CONOCIDAS)
    ips_activas = []
    for ip in ips_activas_raw:
        try:
            ips_activas.append(val_host(ip))
        except Exception:
            pass
    if not ips_activas:
        ips_activas = IPS_CONOCIDAS

    # IP del principal anterior (para el aviso hibernate)
    # Lo detectamos buscando quien tiene BackupDirectoriesBOS local entre los activos
    ip_principal_anterior = data.get("ip_principal_anterior", "")
    if ip_principal_anterior:
        try:
            ip_principal_anterior = val_host(ip_principal_anterior)
        except Exception:
            ip_principal_anterior = ""

    errores = []
    exitos  = []

    # ── PASO 1: Configurar el NUEVO PRINCIPAL ────────────────────────────────
    # CopyDirectories y CopyDirectoriesMaestros: todos los demás CON barra final
    cd_nuevo = _copy_dirs_principal(host_nuevo, ips_activas)
    sqls_principal = [
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR,      "InputDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR_COPY, "InputDirectoryCopy")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BOS_PRINCIPAL,  "BackupDirectoriesBOS")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd_nuevo,         "CopyDirectories")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd_nuevo,         "CopyDirectoriesMaestros")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_MAESTROS_PRINC, "BackupDirectoryMaestroMovidosTpvPrincipal")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_ERROR_DIR,      "ErrorDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_MAESTRO, "BackupDirectoryMaestro")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_TRANS,   "BackupDirectoryTransaccion")),
    ]
    r = _run(host_nuevo, sqls_principal, f"[PRINCIPAL] {nombre} ({host_nuevo}) configurado como principal")
    if r["ok"]:
        exitos.append(host_nuevo)
    else:
        errores.append(f"{host_nuevo}: {r.get('error','?')}")

    # ── PASO 2: Configurar TODOS LOS SECUNDARIOS (incluido el ex-principal) ──
    # BackupDirectoriesBOS: apuntar al nuevo principal
    # CopyDirectories: todos los demás SIN barra final
    # CopyDirectoriesMaestros: vacío
    # BackupDirectoryMaestroMovidosTpvPrincipal: vacío
    bos_sec = f"//{host_nuevo}/c/integracion/4GLExport"

    for ip_sec in ips_activas:
        if ip_sec == host_nuevo:
            continue  # ya configurado arriba

        cd_sec = _copy_dirs_secundario(ip_sec, ips_activas)
        nombre_sec = next((t["nombre"] for t in TPVS_CONOCIDOS if t["ip"] == ip_sec), ip_sec)

        sqls_sec = [
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR,      "InputDirectory")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR_COPY, "InputDirectoryCopy")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (bos_sec,          "BackupDirectoriesBOS")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd_sec,           "CopyDirectories")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "CopyDirectoriesMaestros")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "BackupDirectoryMaestroMovidosTpvPrincipal")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_ERROR_DIR,      "ErrorDirectory")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_MAESTRO, "BackupDirectoryMaestro")),
            ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_TRANS,   "BackupDirectoryTransaccion")),
        ]
        r2 = _run(ip_sec, sqls_sec,
                  f"[SECUNDARIO] {nombre_sec} ({ip_sec}) -> nuevo principal {host_nuevo}")
        if r2["ok"]:
            exitos.append(ip_sec)
        else:
            errores.append(f"{ip_sec}: {r2.get('error','?')}")

    # ── PASO 3: Actualizar BD controlpista en TODOS los TPVs accesibles ─────────
    # 3a. ip_server → nuevo principal en local_config de cada TPV
    # 3b. tabla pos → online=True para los activos, online=False para los inaccesibles
    todos_conocidos = [t["ip"] for t in TPVS_CONOCIDOS]
    ips_inaccesibles_conocidas = [ip for ip in todos_conocidos if ip not in ips_activas]

    for ip_cp in ips_activas:
        # Actualizar ip_server
        r_cp = _actualizar_controlpista(ip_cp, host_nuevo)
        if not r_cp["ok"] and not r_cp.get("demo"):
            errores.append(f"{ip_cp} (controlpista ip_server): {r_cp.get('error','?')}")

        # Marcar como online=True los activos y online=False los caídos en tabla pos
        for ip_pos in ips_activas:
            r_pos = _set_pos_online(ip_cp, ip_pos, True)
            if not r_pos["ok"] and not r_pos.get("demo"):
                errores.append(f"{ip_cp}/pos/{ip_pos}: {r_pos.get('error','?')}")
        for ip_pos in ips_inaccesibles_conocidas:
            r_pos = _set_pos_online(ip_cp, ip_pos, False)
            # No añadir a errores si falla — puede que la fila no exista

    # ── PASO 4: Borrar sesiones correctamente en todos los TPVs ─────────────────
    # Cada TPV accesible borra la sesion de los TPVs que ya no estan activos
    # Los que SI estan activos NO se borran — GARUM los gestiona
    ips_inactivas_en_sesion = [ip for ip in todos_conocidos if ip not in ips_activas]
    for ip_tpv_activo in ips_activas:
        for ip_inactiva in ips_inactivas_en_sesion:
            id_inactivo = _ip_a_id_tpv(ip_inactiva)
            if id_inactivo > 0:
                _borrar_sesion_tpv(ip_tpv_activo, id_inactivo)

    # ── PASO 5: Aviso hibernate ───────────────────────────────────────────────
    # Incluir TPVs conocidos que NO estaban en ips_activas (estaban caídos)
    todos_ips = [t["ip"] for t in TPVS_CONOCIDOS]
    otros_ips = [ip for ip in todos_ips if ip != host_nuevo]
    inaccesibles = [ip for ip in todos_ips if ip not in ips_activas and ip != host_nuevo]

    aviso = _aviso_hibernate_cambio_principal(
        host_nuevo,
        otros_ips,
        ip_principal_anterior=ip_principal_anterior or "10.0.0.101",
        tpvs_inaccesibles=inaccesibles
    )

    log(f"NUEVO PRINCIPAL: {nombre} ({host_nuevo}). "
        f"Actualizados: {exitos}. Errores: {errores}",
        "ok" if not errores else "warn")

    return jsonify({
        "ok": len(errores) == 0,
        "exitos": exitos,
        "errores": errores,
        "aviso_hibernate": aviso,
        "msg": (f"{nombre} es ahora el principal. "
                f"{len(exitos)} TPVs actualizados. Ver instrucciones hibernate.")
    })


@app.route("/api/controlpista/estado")
@need_conn
def api_controlpista_estado():
    """
    Lee el estado completo de controlpista en todos los TPVs en paralelo:
      - local_config.ip_server
      - tabla pos completa
    Devuelve un array con la info de cada TPV conocido.
    """
    def leer_cp(tpv):
        resultado = {
            "id": tpv["id"],
            "nombre": tpv["nombre"],
            "ip": tpv["ip"],
            "accesible": False,
            "ip_server": None,
            "pos": [],
            "error": None
        }
        if sess.get("demo"):
            resultado["accesible"] = True
            resultado["ip_server"] = "10.0.0.101"
            resultado["pos"] = [
                {"ip": "10.0.0.101", "preference": 1, "online": True},
                {"ip": "10.0.0.102", "preference": 2, "online": True},
                {"ip": "10.0.0.103", "preference": 3, "online": True},
                {"ip": "10.0.0.104", "preference": 4, "online": True},
            ]
            return resultado
        c = None
        try:
            c = _conn_controlpista(tpv["ip"])
            cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Leer ip_server de local_config
            cur.execute("SELECT ip_server FROM local_config LIMIT 1")
            row = cur.fetchone()
            resultado["ip_server"] = row["ip_server"] if row else None
            # Leer tabla pos
            cur.execute("SELECT ip, preference, online FROM pos ORDER BY preference")
            resultado["pos"] = [dict(r) for r in cur.fetchall()]
            resultado["accesible"] = True
        except Exception as e:
            msg = str(e).split("\n")[0]
            log(f"WARN leer_cp {tpv['ip']}: {msg}", "warn")
            resultado["error"] = "No se pudo conectar al TPV"
        finally:
            if c:
                try: c.close()
                except Exception: pass
        return resultado

    resultados = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(leer_cp, t): t for t in TPVS_CONOCIDOS}
        for f in as_completed(futs):
            try:
                resultados.append(f.result())
            except Exception as e:
                t = futs[f]
                resultados.append({**t, "accesible": False, "error": str(e)})
    resultados.sort(key=lambda x: x["id"])
    return jsonify({"ok": True, "tpvs": resultados})


@app.route("/api/controlpista/set_ip_server", methods=["POST"])
@csrf
@need_conn
def api_set_ip_server():
    """
    Actualiza manualmente ip_server en la BD controlpista de un TPV concreto.
    Permite control manual independiente de las operaciones de integracion.
    """
    data = request.json or {}
    try:
        host_tpv = val_host(data.get("host_tpv", ""))
        ip_nueva  = val_host(data.get("ip_server", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    nombre = str(data.get("nombre", host_tpv))[:64]
    r = _actualizar_controlpista(host_tpv, ip_nueva)
    if r["ok"]:
        log(f"[MANUAL] ip_server en {nombre} ({host_tpv}) -> {ip_nueva}", "ok")
    return jsonify(r)


@app.route("/api/controlpista/set_pos_online", methods=["POST"])
@csrf
@need_conn
def api_set_pos_online():
    """
    Actualiza manualmente el campo online de un TPV en la tabla pos
    de la BD controlpista del TPV indicado.
    """
    data = request.json or {}
    try:
        host_tpv = val_host(data.get("host_tpv", ""))
        ip_pos   = val_host(data.get("ip_pos", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    online = bool(data.get("online", True))
    nombre = str(data.get("nombre", host_tpv))[:64]
    r = _set_pos_online(host_tpv, ip_pos, online)
    if r["ok"]:
        estado = "TRUE" if online else "FALSE"
        log(f"[MANUAL] pos.online={estado} para {ip_pos} en {nombre} ({host_tpv})", "ok")
    return jsonify(r)


@app.route("/api/controlpista/delete_pos", methods=["POST"])
@csrf
@need_conn
def api_delete_pos():
    """Elimina manualmente una fila de la tabla pos (BD controlpista del TPV)."""
    data = request.json or {}
    try:
        host_tpv = val_host(data.get("host_tpv", ""))
        ip_pos   = val_host(data.get("ip_pos", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    nombre = str(data.get("nombre", host_tpv))[:64]
    if sess.get("demo"):
        log(f"[DEMO] DELETE pos en {host_tpv}: {ip_pos}", "ok")
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = _conn_controlpista(host_tpv)
        c.autocommit = False
        cur = c.cursor()
        cur.execute("DELETE FROM pos WHERE ip=%s", (ip_pos,))
        afectadas = cur.rowcount
        c.commit()
        log(f"[MANUAL] DELETE pos en {nombre} ({host_tpv}): {ip_pos} "
            f"({afectadas} fila/s)", "ok")
        return jsonify({"ok": True, "afectadas": afectadas})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN delete_pos {ip_pos} en {host_tpv}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo eliminar la fila de pos"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/restaurar_backup", methods=["POST"])
@csrf
@need_conn
def api_restaurar_backup():
    """
    Restaura configuracion desde un fichero de backup parseado en el frontend.

    Recibe:
      {
        "tpvs": [
          {
            "ip": "10.0.0.101",
            "propiedades": { "CopyDirectories": "...", ... },   # 16 claves whitelist
            "ip_server":   "10.0.0.101",                         # opcional
            "pos":         [{ "ip": "10.0.0.102", "online": true }, ...]  # opcional
          },
          ...
        ]
      }

    Por cada TPV:
      1) UPDATE propiedad SET valor=%s WHERE clave=%s   (filtrado por CLAVES)
      2) UPDATE local_config SET ip_server=%s
      3) UPDATE pos SET online=%s WHERE ip=%s   (una por fila)

    NO toca: sesion_tpv_activo, pos.preference, pos.ip, local_config.ip,
             ni claves de propiedad fuera de la whitelist.

    Devuelve un resultado por TPV con conteos y warnings.
    """
    data = request.json or {}
    tpvs_in = data.get("tpvs") or []
    if not isinstance(tpvs_in, list) or not tpvs_in:
        return jsonify({"ok": False, "error": "Sin TPVs a restaurar"}), 400

    resultados = []
    for entry in tpvs_in:
        try:
            host = val_host(entry.get("ip", ""))
        except ValueError as e:
            resultados.append({"ip": entry.get("ip"), "ok": False, "error": str(e)})
            continue

        nombre = str(entry.get("nombre", host))[:64]
        r = {"ip": host, "nombre": nombre, "ok": False,
             "propiedades_aplicadas": 0, "ip_server_aplicado": False,
             "pos_aplicadas": 0, "warnings": []}

        # 1) Restaurar propiedad (solo CLAVES whitelist)
        props = entry.get("propiedades") or {}
        if not isinstance(props, dict):
            props = {}
        sqls = []
        for k, v in props.items():
            if k not in CLAVES:
                r["warnings"].append(f"Clave ignorada (fuera de whitelist): {k}")
                continue
            valor = "" if v is None else str(v)
            if len(valor) > _MAX_V:
                r["warnings"].append(f"Valor demasiado largo en {k}, ignorado")
                continue
            sqls.append(("UPDATE propiedad SET valor=%s WHERE clave=%s", (valor, k)))

        if sqls:
            r_run = _run(host, sqls, f"Restaurar propiedad en {nombre} ({len(sqls)} claves)")
            if not r_run.get("ok"):
                r["error"] = r_run.get("error", "Error en propiedad")
                resultados.append(r)
                continue
            r["propiedades_aplicadas"] = len(sqls)

        # 2) Restaurar ip_server en local_config
        ip_srv = entry.get("ip_server")
        if ip_srv:
            try:
                ip_srv = val_host(ip_srv)
                r_cp = _actualizar_controlpista(host, ip_srv)
                if r_cp.get("ok"):
                    r["ip_server_aplicado"] = True
                else:
                    r["warnings"].append(f"ip_server: {r_cp.get('error', 'no aplicado')}")
            except ValueError as e:
                r["warnings"].append(f"ip_server invalido: {e}")

        # 3) Restaurar pos.online por cada fila
        pos_list = entry.get("pos") or []
        if isinstance(pos_list, list):
            for p in pos_list:
                if not isinstance(p, dict):
                    continue
                try:
                    ip_pos = val_host(p.get("ip", ""))
                except ValueError:
                    r["warnings"].append(f"pos.ip invalido, fila ignorada")
                    continue
                online = bool(p.get("online"))
                r_pos = _set_pos_online(host, ip_pos, online)
                if r_pos.get("ok"):
                    r["pos_aplicadas"] += 1
                else:
                    r["warnings"].append(f"pos {ip_pos}: {r_pos.get('error', 'no aplicado')}")

        r["ok"] = True
        resultados.append(r)

    ok_count = sum(1 for x in resultados if x.get("ok"))
    log(f"Restaurar backup: {ok_count}/{len(resultados)} TPVs procesados", "info")
    return jsonify({"ok": True, "resultados": resultados})


@app.route("/api/controlpista/pos")
@need_conn
def api_get_pos():
    """
    Lee la tabla pos de la BD controlpista del TPV indicado.
    Devuelve la lista de TPVs declarados y su estado online.
    """
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    rows = _leer_pos(host)
    return jsonify({"ok": True, "pos": rows, "demo": sess.get("demo", False)})


@app.route("/api/impresoras/windows")
@need_conn
def api_impresoras_windows():
    """
    Lista las impresoras instaladas en Windows usando PowerShell o wmic.
    Solo funciona en Windows — en otros SO devuelve lista vacía.
    """
    impresoras = []
    try:
        # Intentar con PowerShell (Windows 7+)
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-Printer | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, timeout=8,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
        if resultado.returncode == 0:
            impresoras = [l.strip() for l in resultado.stdout.splitlines()
                         if l.strip() and not l.strip().startswith("Name")]
        if not impresoras:
            # Fallback: wmic (Windows XP/7/10)
            resultado2 = subprocess.run(
                ["wmic", "printer", "get", "name"],
                capture_output=True, text=True, timeout=8,
                creationflags=0x08000000
            )
            if resultado2.returncode == 0:
                impresoras = [l.strip() for l in resultado2.stdout.splitlines()
                             if l.strip() and l.strip().lower() != "name"]
    except Exception as e:
        log(f"WARN listar impresoras Windows: {str(e).split(chr(10))[0]}", "warn")

    log(f"Impresoras Windows detectadas: {len(impresoras)}", "info")
    return jsonify({"ok": True, "impresoras": sorted(impresoras)})


@app.route("/api/impresoras/puertos")
@need_conn
def api_puertos_impresora():
    """
    Lista los puertos de impresora instalados en Windows.
    Usa PowerShell Get-PrinterPort o wmic como fallback.
    """
    puertos = []
    try:
        # PowerShell (Windows 7+)
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-PrinterPort | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, timeout=8,
            creationflags=0x08000000
        )
        if resultado.returncode == 0:
            puertos = [l.strip() for l in resultado.stdout.splitlines()
                      if l.strip() and l.strip().lower() != "name"]
        if not puertos:
            # Fallback: wmic
            resultado2 = subprocess.run(
                ["wmic", "printerconfig", "get", "portname"],
                capture_output=True, text=True, timeout=8,
                creationflags=0x08000000
            )
            if resultado2.returncode == 0:
                puertos = [l.strip() for l in resultado2.stdout.splitlines()
                          if l.strip() and l.strip().lower() != "portname"]
    except Exception as e:
        log(f"WARN listar puertos impresora: {str(e).split(chr(10))[0]}", "warn")

    # Ordenar: USB primero, luego TCP/IP, luego el resto
    def orden_puerto(p):
        p = p.upper()
        if p.startswith("USB"): return (0, p)
        if p.startswith("IP_") or p.startswith("TCP"): return (1, p)
        if p.startswith("LPT"): return (2, p)
        if p.startswith("COM"): return (3, p)
        return (4, p)

    puertos = sorted(set(puertos), key=orden_puerto)
    log(f"Puertos impresora Windows detectados: {len(puertos)}", "info")
    return jsonify({"ok": True, "puertos": puertos})


@app.route("/api/impresoras")
@need_conn
def api_get_impresoras():
    """
    Lee la tabla configuracion_impresion del TPV indicado.
    Cada TPV tiene una fila única con su configuración local de impresoras.
    """
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "config": {
            "id_configuracion_impresion": 1,
            "nombre_impresora_ticket_por_defecto": "EPSON TM-T20",
            "ruta_impresora_local_facturas": "C:/impresoras/facturas",
            "nombre_driver_impresora": "EPSON TM-T20 Receipt",
            "puerto_impresora": "USB001",
            "formato_impresion_facturas": "T",
            "impresion_javapos": False,
            "impresion_report": True,
            "fichar_entrada": False,
            "fichar_salida": False,
            "impresion_cambio_precios_programados": False,
            "impresion_ajuste_liquidacion": True,
            "lineas_paginacion_contadores_surtidores": 40,
            "numero_copias_depositos": 1,
            "nuevo_valor_desplazamiento_horizontal_px_reports": 0,
            "nuevo_valor_variacion_fuente_reports": 0,
        }})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM configuracion_impresion LIMIT 1")
        row = cur.fetchone()
        if not row:
            return jsonify({"ok": False, "error": "No hay filas en configuracion_impresion"}), 404
        config = dict(row)
        log(f"configuracion_impresion leida de {host}", "ok")
        return jsonify({"ok": True, "demo": False, "config": config})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_impresoras {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo leer la configuracion de impresion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/impresoras", methods=["POST"])
@csrf
@need_conn
def api_set_impresoras():
    """
    Actualiza los campos editables de configuracion_impresion en el TPV indicado.
    Solo se permiten los 5 campos editables definidos.
    """
    CAMPOS_EDITABLES = frozenset({
        "nombre_impresora_ticket_por_defecto",
        "ruta_impresora_local_facturas",
        "nombre_driver_impresora",
        "puerto_impresora",
        "formato_impresion_facturas",
        "fichar_entrada",
        "fichar_salida",
        "nuevo_valor_desplazamiento_horizontal_px_reports",
        "numero_copias_depositos",
    })
    CAMPOS_BOOL = frozenset({"fichar_entrada", "fichar_salida"})
    CAMPOS_INT  = frozenset({"nuevo_valor_desplazamiento_horizontal_px_reports", "numero_copias_depositos"})
    VALORES_FORMATO = {"T", "4"}

    data = request.json or {}
    try:
        host = val_host(data.get("host_tpv", sess.get("host", "")))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    updates = data.get("updates", {})
    if not updates:
        return jsonify({"ok": False, "error": "Sin cambios"}), 400

    bad = set(updates.keys()) - CAMPOS_EDITABLES
    if bad:
        return jsonify({"ok": False, "error": f"Campos no permitidos: {sorted(bad)}"}), 400

    # Validar y convertir tipos ANTES del UPDATE — evita 500 si el frontend
    # manda strings vacios para campos int o booleanos mal tipados.
    norm = {}
    for campo, valor in updates.items():
        if campo in CAMPOS_BOOL:
            norm[campo] = bool(valor) if isinstance(valor, bool) else str(valor).lower() in ("true","1","si","yes","on")
        elif campo in CAMPOS_INT:
            try:
                norm[campo] = int(str(valor).strip()) if str(valor).strip() != "" else 0
            except (TypeError, ValueError):
                return jsonify({"ok": False, "error": f"{campo} debe ser entero, recibido: {valor!r}"}), 400
        elif campo == "formato_impresion_facturas":
            v = str(valor).strip().upper()
            if v not in VALORES_FORMATO:
                return jsonify({"ok": False, "error": "formato_impresion_facturas debe ser T o 4"}), 400
            norm[campo] = v
        else:
            # campos text — aceptar string (incluso vacio = limpiar campo)
            norm[campo] = str(valor) if valor is not None else ""

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "afectadas": len(norm)})

    c = None
    try:
        c = conn_tpv(host)
        c.autocommit = False
        cur = c.cursor()
        for campo, valor in norm.items():
            cur.execute(
                psycopg2.sql.SQL(
                    "UPDATE configuracion_impresion SET {} = %s"
                ).format(psycopg2.sql.Identifier(campo)),
                (valor,)
            )
        c.commit()
        log(f"configuracion_impresion actualizada en {host}: {list(norm.keys())}", "ok")
        return jsonify({"ok": True, "afectadas": len(norm)})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_impresoras {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la configuracion de impresion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# =============================================================================
# PISTA (v5.13) — vista de configuracion fisica de la pista de surtido
# Jerarquia: surtidor -> manguera -> tanque -> articulo
# Cabecera: ip_concentrador (DOMS) de la tabla pista
# Solo lectura.
# =============================================================================

@app.route("/api/pista")
@need_conn
def api_get_pista():
    """Lee toda la configuracion de la pista del TPV indicado en una sola
    consulta. Devuelve:
      - doms_ip: pista.ip_concentrador (solo informativo)
      - surtidores: lista anidada con sus mangueras y, por cada manguera,
        el tanque al que apunta y el articulo (producto) que ese tanque
        almacena. Ordenado por numero de surtidor y de manguera.
      - tanques_huerfanos: tanques sin manguera asociada (informativo).
    """
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "doms_ip": "10.0.0.50",
            "doms_nombre": "Pista A",
            "doms_tipo": "D",
            "surtidores": [
                {"id_surtidor": 1, "numero": "1",
                 "numero_logico_concentrador": 1, "puerto_concentrador": 21,
                 "predeterminador": False, "auto_autoriza": False,
                 "importe_maximo_prede": 99999.99,
                 "bajo_informatica": True,
                 "interface_tipo_general": 1, "interface_tipo_protocol": 2,
                 "direccion_fisica_concentrador": 1,
                 "aviso_manguera_descolgada": 0,
                 "id_modo_operacion_surtidor_por_defecto": 2,
                 "suministros_cola": 5,
                 "accion_cola_completa": "A",
                 "mangueras": [
                    {"id_manguera": 1, "numero": 1, "aspiracion": 2,
                     "breakaway": False, "numero_logico_concentrador": 1,
                     "id_tanque": 1, "tanque_numero": "T1",
                     "tanque_capacidad": 30000.0,
                     "id_articulo": 1, "articulo_nombre": "Gasolina 95"},
                    {"id_manguera": 2, "numero": 2, "aspiracion": 2,
                     "breakaway": False, "numero_logico_concentrador": 2,
                     "id_tanque": 2, "tanque_numero": "T2",
                     "tanque_capacidad": 50000.0,
                     "id_articulo": 2, "articulo_nombre": "Gasoil B7"},
                 ]},
                {"id_surtidor": 2, "numero": "2",
                 "numero_logico_concentrador": 2, "puerto_concentrador": 21,
                 "predeterminador": False, "auto_autoriza": False,
                 "importe_maximo_prede": 99999.99,
                 "bajo_informatica": True,
                 "interface_tipo_general": 1, "interface_tipo_protocol": 2,
                 "direccion_fisica_concentrador": 2,
                 "aviso_manguera_descolgada": 0,
                 "id_modo_operacion_surtidor_por_defecto": 2,
                 "suministros_cola": 5,
                 "accion_cola_completa": "A",
                 "mangueras": [
                    {"id_manguera": 3, "numero": 1, "aspiracion": 2,
                     "breakaway": False, "numero_logico_concentrador": 3,
                     "id_tanque": 1, "tanque_numero": "T1",
                     "tanque_capacidad": 30000.0,
                     "id_articulo": 1, "articulo_nombre": "Gasolina 95"},
                    {"id_manguera": 4, "numero": 2, "aspiracion": 2,
                     "breakaway": False, "numero_logico_concentrador": 4,
                     "id_tanque": 2, "tanque_numero": "T2",
                     "tanque_capacidad": 50000.0,
                     "id_articulo": 2, "articulo_nombre": "Gasoil B7"},
                 ]},
            ],
            "tanques_huerfanos": [],
        })

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # DOMS (ip_concentrador) — informativo. Cogemos la primera pista; en
        # casi todas las estaciones hay 1 sola.
        cur.execute("""
            SELECT id_pista, nombre, ip_concentrador, tipo_concentrador,
                   numero_concentrador
            FROM pista
            ORDER BY id_pista
            LIMIT 1
        """)
        pista_row = cur.fetchone()
        doms_ip      = pista_row["ip_concentrador"] if pista_row else None
        doms_nombre  = pista_row["nombre"]          if pista_row else None
        doms_tipo    = pista_row["tipo_concentrador"] if pista_row else None

        # Surtidores + mangueras + tanque + articulo en un solo SELECT.
        # LEFT JOIN para no perder surtidores sin mangueras (raro pero posible).
        cur.execute("""
            SELECT
                s.id_surtidor, s.numero AS surtidor_numero,
                s.numero_logico_concentrador AS surt_nlc,
                s.puerto_concentrador AS surt_puerto,
                s.predeterminador, s.auto_autoriza,
                s.importe_maximo_prede,
                s.bajo_informatica,
                s.interface_tipo_general,
                s.interface_tipo_protocol,
                s.direccion_fisica_concentrador,
                s.aviso_manguera_descolgada,
                s.alarma_manguera_descolgada,
                s.id_modo_operacion_surtidor_por_defecto,
                s.suministros_cola,
                s.accion_cola_completa,
                m.id_manguera, m.numero AS manguera_numero,
                m.aspiracion, m.breakaway,
                m.numero_logico_concentrador AS mang_nlc,
                m.id_manguera_externo,
                t.id_tanque, t.numero AS tanque_numero,
                t.capacidad AS tanque_capacidad,
                a.id_articulo, a.nombre AS articulo_nombre,
                a.codigo_concentrador AS articulo_codigo_concentrador
            FROM surtidor s
            LEFT JOIN manguera m ON m.id_surtidor = s.id_surtidor
            LEFT JOIN tanque    t ON t.id_tanque   = m.id_tanque
            LEFT JOIN articulo  a ON a.id_articulo = t.id_articulo
            ORDER BY s.numero, m.numero
        """)
        rows = cur.fetchall()

        # Agrupar mangueras bajo su surtidor
        surtidores_dict = {}
        for r in rows:
            sid = r["id_surtidor"]
            if sid not in surtidores_dict:
                surtidores_dict[sid] = {
                    "id_surtidor": sid,
                    "numero": r["surtidor_numero"],
                    "numero_logico_concentrador": r["surt_nlc"],
                    "puerto_concentrador": r["surt_puerto"],
                    "predeterminador": r["predeterminador"],
                    "auto_autoriza": r["auto_autoriza"],
                    "importe_maximo_prede": float(r["importe_maximo_prede"])
                                            if r["importe_maximo_prede"] is not None else None,
                    "bajo_informatica": r["bajo_informatica"],
                    "interface_tipo_general": r["interface_tipo_general"],
                    "interface_tipo_protocol": r["interface_tipo_protocol"],
                    "direccion_fisica_concentrador": r["direccion_fisica_concentrador"],
                    "aviso_manguera_descolgada": r["aviso_manguera_descolgada"],
                    "alarma_manguera_descolgada": r["alarma_manguera_descolgada"],
                    "id_modo_operacion_surtidor_por_defecto": r["id_modo_operacion_surtidor_por_defecto"],
                    "suministros_cola": r["suministros_cola"],
                    "accion_cola_completa": r["accion_cola_completa"],
                    "mangueras": []
                }
            if r["id_manguera"] is not None:
                surtidores_dict[sid]["mangueras"].append({
                    "id_manguera": r["id_manguera"],
                    "numero": r["manguera_numero"],
                    "aspiracion": r["aspiracion"],
                    "breakaway": r["breakaway"],
                    "numero_logico_concentrador": r["mang_nlc"],
                    "id_manguera_externo": r["id_manguera_externo"],
                    "id_tanque": r["id_tanque"],
                    "tanque_numero": r["tanque_numero"],
                    "tanque_capacidad": float(r["tanque_capacidad"])
                                        if r["tanque_capacidad"] is not None else None,
                    "id_articulo": r["id_articulo"],
                    "articulo_nombre": r["articulo_nombre"],
                    "articulo_codigo_concentrador": r["articulo_codigo_concentrador"],
                })
        surtidores = list(surtidores_dict.values())

        # Lista de TODOS los tanques visibles del TPV — necesaria para el
        # selector de cambio de tanque en cada manguera (v5.13).
        cur.execute("""
            SELECT t.id_tanque, t.numero, t.capacidad,
                   a.id_articulo, a.nombre AS articulo_nombre
            FROM tanque t
            LEFT JOIN articulo a ON a.id_articulo = t.id_articulo
            WHERE t.visible = TRUE
            ORDER BY t.numero
        """)
        tanques_disponibles = []
        for r in cur.fetchall():
            tanques_disponibles.append({
                "id_tanque": r["id_tanque"],
                "numero": r["numero"],
                "capacidad": float(r["capacidad"]) if r["capacidad"] is not None else None,
                "id_articulo": r["id_articulo"],
                "articulo_nombre": r["articulo_nombre"],
            })

        # Tanques huerfanos: subconjunto de los disponibles que ninguna
        # manguera referencia. Util como aviso al tecnico.
        numeros_referenciados = set()
        for sur in surtidores:
            for m in sur["mangueras"]:
                if m.get("tanque_numero"):
                    numeros_referenciados.add(m["tanque_numero"])
        tanques_huerfanos = [t for t in tanques_disponibles
                             if t["numero"] not in numeros_referenciados]

        log(f"Pista leida de {host}: {len(surtidores)} surtidor(es), "
            f"{sum(len(s['mangueras']) for s in surtidores)} manguera(s), "
            f"{len(tanques_disponibles)} tanque(s) visibles, "
            f"{len(tanques_huerfanos)} huerfano(s)", "ok")

        return jsonify({
            "ok": True, "demo": False,
            "doms_ip": doms_ip,
            "doms_nombre": doms_nombre,
            "doms_tipo": doms_tipo,
            "surtidores": surtidores,
            "tanques_disponibles": tanques_disponibles,
            "tanques_huerfanos": tanques_huerfanos,
        })
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_pista {host}: {msg}", "warn")
        return jsonify({"ok": False,
                        "error": "No se pudo leer la configuracion de la pista"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# Campos editables del surtidor (v5.13).
# bool: bajo_informatica
# int: puerto_concentrador, interface_tipo_general, interface_tipo_protocol,
#      direccion_fisica_concentrador
_CAMPOS_SURTIDOR_BOOL = {"bajo_informatica"}
_CAMPOS_SURTIDOR_INT  = {
    "puerto_concentrador",
    "interface_tipo_general",
    "interface_tipo_protocol",
    "direccion_fisica_concentrador",
    "numero_logico_concentrador",
}


@app.route("/api/pista/surtidor/campo/red", methods=["POST"])
@need_conn
@csrf
def api_set_surtidor_campo_red():
    """Aplica un cambio de campo de la tabla `surtidor` a TODOS los TPVs.
    Identifica el surtidor por `numero` (estable entre TPVs); usar id_surtidor
    seria fragil porque los IDs pueden diferir entre BDs.
    Whitelist explicita en _CAMPOS_SURTIDOR_BOOL / _CAMPOS_SURTIDOR_INT."""
    data = request.json or {}
    campo = data.get("campo", "")
    if campo not in (_CAMPOS_SURTIDOR_BOOL | _CAMPOS_SURTIDOR_INT):
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400

    if campo in _CAMPOS_SURTIDOR_BOOL:
        valor = bool(data.get("valor"))
    else:
        try:
            valor = int(data.get("valor"))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": f"{campo} debe ser entero"}), 400

    numero_surtidor = data.get("numero_surtidor")
    if numero_surtidor is None or str(numero_surtidor).strip() == "":
        return jsonify({"ok": False, "error": "numero_surtidor requerido"}), 400
    numero_str = str(numero_surtidor).strip()

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            # surtidor.numero es text — comparamos como string.
            cur.execute(
                f"UPDATE surtidor SET {campo} = %s, "
                f"update_date = NOW(), update_user = 'garum_tpv_mgr' "
                f"WHERE numero = %s",
                (valor, numero_str))
            n = cur.rowcount
            c.commit()
            if n == 0:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"Surtidor {numero_str} no existe en este TPV"}
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_set_surtidor_campo_red {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] surtidor.{campo}={valor} numero={numero_str}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


# Campos globales del surtidor (v5.13) — aplican a TODOS los surtidores de
# TODOS los TPVs (UPDATE sin WHERE). Pensados para configurar la pista de
# forma uniforme cuando todos los surtidores deben compartir el mismo valor.
_CAMPOS_SURTIDOR_GLOBAL_INT = {
    "aviso_manguera_descolgada",
    "alarma_manguera_descolgada",
    "id_modo_operacion_surtidor_por_defecto",
    "suministros_cola",
}
_CAMPOS_SURTIDOR_GLOBAL_CHAR = {"accion_cola_completa"}


@app.route("/api/pista/surtidor/global/red", methods=["POST"])
@need_conn
@csrf
def api_set_surtidor_global_red():
    """Aplica un cambio en `surtidor.<campo>` SIN WHERE — afecta a TODOS los
    surtidores de cada TPV. Pensado para campos que comparten todos los
    surtidores de la estacion (config global de pista).

    Whitelist explicita: _CAMPOS_SURTIDOR_GLOBAL_INT (int) y
    _CAMPOS_SURTIDOR_GLOBAL_CHAR (character(1) alfabetico mayusculo).
    """
    data = request.json or {}
    campo = data.get("campo", "")
    es_int  = campo in _CAMPOS_SURTIDOR_GLOBAL_INT
    es_char = campo in _CAMPOS_SURTIDOR_GLOBAL_CHAR
    if not (es_int or es_char):
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400

    if es_int:
        try:
            valor = int(data.get("valor"))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": f"{campo} debe ser entero"}), 400
    else:
        # accion_cola_completa: SOLO 'A' o 'B' (es un enum corto, no A-Z).
        v = str(data.get("valor", "")).strip().upper()
        if campo == "accion_cola_completa":
            if v not in ("A", "B"):
                return jsonify({"ok": False,
                                "error": "accion_cola_completa solo admite 'A' o 'B'"}), 400
        else:
            if len(v) != 1 or not v.isalpha():
                return jsonify({"ok": False,
                                "error": "Debe ser un solo caracter alfabetico (A-Z)"}), 400
        valor = v

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            # UPDATE masivo: todos los surtidores del TPV reciben el mismo valor.
            cur.execute(
                f"UPDATE surtidor SET {campo} = %s, "
                f"update_date = NOW(), update_user = 'garum_tpv_mgr'",
                (valor,))
            n = cur.rowcount
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_set_surtidor_global_red {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED-GLOBAL] surtidor.{campo}={valor}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


# Campos editables de la manguera (v5.13).
# Identificacion: par (numero_surtidor, numero_manguera) — la combinacion es
# estable entre TPVs porque la pista fisica es la misma.
_CAMPOS_MANGUERA_INT = {
    "numero_logico_concentrador",
    "aspiracion",
}
_CAMPOS_MANGUERA_TEXT = {
    "id_manguera_externo",
}


@app.route("/api/pista/manguera/campo/red", methods=["POST"])
@need_conn
@csrf
def api_set_manguera_campo_red():
    """Aplica un cambio de campo de la tabla `manguera` a TODOS los TPVs.
    Identifica la manguera por el par (numero_surtidor, numero_manguera);
    los IDs internos (id_manguera, id_surtidor) pueden diferir entre BDs."""
    data = request.json or {}
    campo = data.get("campo", "")
    es_int  = campo in _CAMPOS_MANGUERA_INT
    es_text = campo in _CAMPOS_MANGUERA_TEXT
    if not (es_int or es_text):
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400

    if es_int:
        try:
            valor = int(data.get("valor"))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": f"{campo} debe ser entero"}), 400
    else:
        valor = str(data.get("valor", ""))
        if len(valor) > 256:
            return jsonify({"ok": False, "error": f"{campo}: texto demasiado largo (max 256)"}), 400

    numero_surtidor = data.get("numero_surtidor")
    numero_manguera = data.get("numero_manguera")
    if numero_surtidor is None or str(numero_surtidor).strip() == "":
        return jsonify({"ok": False, "error": "numero_surtidor requerido"}), 400
    if numero_manguera is None:
        return jsonify({"ok": False, "error": "numero_manguera requerido"}), 400
    numero_surtidor_str = str(numero_surtidor).strip()
    try:
        numero_manguera_int = int(numero_manguera)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "numero_manguera debe ser entero"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            cur.execute(
                f"UPDATE manguera SET {campo} = %s, "
                f"update_date = NOW(), update_user = 'garum_tpv_mgr' "
                f"WHERE id_surtidor = (SELECT id_surtidor FROM surtidor WHERE numero = %s) "
                f"  AND numero = %s",
                (valor, numero_surtidor_str, numero_manguera_int))
            n = cur.rowcount
            c.commit()
            if n == 0:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"Manguera surtidor={numero_surtidor_str} num={numero_manguera_int} no existe"}
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_set_manguera_campo_red {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] manguera.{campo}={valor} surtidor={numero_surtidor_str} num={numero_manguera_int}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/pista/manguera/tanque/red", methods=["POST"])
@need_conn
@csrf
def api_set_manguera_tanque_red():
    """Reasigna el tanque de una manguera en TODOS los TPVs accesibles.
    Identifica manguera por (numero_surtidor, numero_manguera) y tanque
    destino por su `numero`. En cada TPV resuelve el id_tanque local via
    subquery — el ID puede diferir entre BDs aunque el numero del tanque
    sea estable."""
    data = request.json or {}
    numero_surtidor = data.get("numero_surtidor")
    numero_manguera = data.get("numero_manguera")
    numero_tanque   = data.get("numero_tanque")
    if numero_surtidor is None or str(numero_surtidor).strip() == "":
        return jsonify({"ok": False, "error": "numero_surtidor requerido"}), 400
    if numero_manguera is None:
        return jsonify({"ok": False, "error": "numero_manguera requerido"}), 400
    if numero_tanque is None or str(numero_tanque).strip() == "":
        return jsonify({"ok": False, "error": "numero_tanque requerido"}), 400
    numero_surtidor_str = str(numero_surtidor).strip()
    numero_tanque_str   = str(numero_tanque).strip()
    try:
        numero_manguera_int = int(numero_manguera)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "numero_manguera debe ser entero"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            # Resuelve el id_tanque local (puede diferir entre TPVs).
            cur.execute("SELECT id_tanque FROM tanque WHERE numero = %s AND visible = TRUE",
                        (numero_tanque_str,))
            row = cur.fetchone()
            if not row:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"Tanque {numero_tanque_str} no existe o no es visible"}
            id_tanque_local = row[0]
            cur.execute(
                "UPDATE manguera SET id_tanque = %s, "
                "update_date = NOW(), update_user = 'garum_tpv_mgr' "
                "WHERE id_surtidor = (SELECT id_surtidor FROM surtidor WHERE numero = %s) "
                "  AND numero = %s",
                (id_tanque_local, numero_surtidor_str, numero_manguera_int))
            n = cur.rowcount
            c.commit()
            if n == 0:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"Manguera surtidor={numero_surtidor_str} num={numero_manguera_int} no existe"}
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_set_manguera_tanque_red {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] manguera.id_tanque -> tanque#{numero_tanque_str} "
        f"surtidor={numero_surtidor_str} num={numero_manguera_int}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/pista/doms/ip/red", methods=["POST"])
@need_conn
@csrf
def api_set_pista_doms_ip_red():
    """Cambia la IP del concentrador (DOMS) de la pista en TODOS los TPVs.
    Asume una sola pista por TPV (la mas habitual); en caso de varias,
    actualiza la de menor id_pista.
    Validamos la IP con val_host() — solo se admiten IPs dentro de los
    rangos permitidos (10.0.0.0/24 + 127.0.0.0/8)."""
    data = request.json or {}
    nueva_ip = str(data.get("ip_concentrador", "")).strip()
    try:
        nueva_ip = val_host(nueva_ip)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            cur.execute(
                "UPDATE pista SET ip_concentrador = %s "
                "WHERE id_pista = (SELECT id_pista FROM pista ORDER BY id_pista LIMIT 1)",
                (nueva_ip,))
            n = cur.rowcount
            c.commit()
            if n == 0:
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": "No hay filas en la tabla pista"}
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_set_pista_doms_ip_red {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] pista.ip_concentrador -> {nueva_ip}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/pista/ept")
@need_conn
def api_get_pista_ept():
    """Lee la tabla `ept` (Electronic Payment Terminals) del TPV indicado.
    SELECT * — devuelve todas las columnas. El frontend renderiza una tabla
    generica con cabecera y filas. Solo lectura por ahora."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "columnas": ["id_ept", "numero", "nombre", "ip", "puerto", "activo"],
            "filas": [
                {"id_ept": 1, "numero": "1", "nombre": "Datafono Sala", "ip": "10.0.0.30", "puerto": 5000, "activo": True},
                {"id_ept": 2, "numero": "2", "nombre": "Datafono Pista", "ip": "10.0.0.31", "puerto": 5000, "activo": True},
            ]})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM ept ORDER BY 1")
        rows = cur.fetchall()
        columnas = [d.name for d in cur.description] if cur.description else []
        filas = []
        for r in rows:
            fila = dict(r)
            for k, v in fila.items():
                if hasattr(v, "isoformat"):
                    fila[k] = v.isoformat()
                elif hasattr(v, "__float__") and not isinstance(v, (int, bool)):
                    fila[k] = float(v)
            filas.append(fila)
        log(f"ept leida de {host}: {len(filas)} fila(s)", "ok")
        return jsonify({"ok": True, "demo": False, "columnas": columnas, "filas": filas})
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_pista_ept {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo leer la tabla ept"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/pista/productos")
@need_conn
def api_get_pista_productos():
    """Lee la tabla `articulo` filtrando productos con asignable_tanque=TRUE.
    El esquema de columnas a devolver se concretara cuando el usuario pase
    el schema completo de `articulo`. De momento: SELECT * (igual que ept)
    para que el frontend pueda mostrar todo y luego refinamos columnas."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "columnas": ["id_articulo", "codigo", "nombre", "asignable_tanque", "carburante", "comision"],
            "filas": [
                {"id_articulo": 1, "codigo": "G95", "nombre": "Gasolina 95", "asignable_tanque": True, "carburante": True, "comision": False},
                {"id_articulo": 2, "codigo": "GAS", "nombre": "Gasoil B7",   "asignable_tanque": True, "carburante": True, "comision": False},
            ]})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM articulo WHERE asignable_tanque = TRUE ORDER BY 1")
        rows = cur.fetchall()
        columnas = [d.name for d in cur.description] if cur.description else []
        filas = []
        for r in rows:
            fila = dict(r)
            for k, v in fila.items():
                if hasattr(v, "isoformat"):
                    fila[k] = v.isoformat()
                elif hasattr(v, "__float__") and not isinstance(v, (int, bool)):
                    fila[k] = float(v)
            filas.append(fila)
        log(f"productos (articulo asignable_tanque) leidos de {host}: {len(filas)} fila(s)", "ok")
        return jsonify({"ok": True, "demo": False, "columnas": columnas, "filas": filas})
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_pista_productos {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los productos"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/sondas")
@need_conn
def api_get_sondas():
    """
    Lee las tablas tanque + configuracion_sonda + sonda del TPV indicado.
    Devuelve una lista de tanques visibles con su configuracion de sonda
    y las lecturas actuales (medicion, libre, agua, temperatura...).
    Solo lectura — usa /api/sondas/<id_cs>/campo para modificar.
    """
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "sondas": [
            {
                "id_tanque": 1, "numero": "T1", "capacidad_tanque": 30000,
                "fecha_instalacion": "2020-01-15T00:00:00", "visible": True,
                "id_tanque_externo": "EXT-001",
                "id_configuracion_sonda": 1,
                "nombre_sonda": "Sonda Gasolina 95", "id_pista": 1,
                "numero_logico_concentrador": 1, "puerto_concentrador": 1,
                "deteccion_fugas": True, "volumen_perdida": 5,
                "recuento_estable": 3, "fin_entrega": 10, "ciclo_polling": 60,
                "id_configuracion_sonda_externo": None,
                "id_sonda": 1, "numero_sonda": 1, "tipo_conexion": "A",
                "ultima_actualizacion": "2026-04-30T09:45:00",
                "medicion": 18500, "libre": 11500, "agua": 12,
                "temperatura": 17.3, "precio_medio": 1.659,
                "parcial": 0, "capacidad_sonda": 30000,
            },
            {
                "id_tanque": 2, "numero": "T2", "capacidad_tanque": 50000,
                "fecha_instalacion": "2020-01-15T00:00:00", "visible": True,
                "id_tanque_externo": "EXT-002",
                "id_configuracion_sonda": 2,
                "nombre_sonda": "Sonda Gasoil B7", "id_pista": 2,
                "numero_logico_concentrador": 2, "puerto_concentrador": 2,
                "deteccion_fugas": True, "volumen_perdida": 5,
                "recuento_estable": 3, "fin_entrega": 10, "ciclo_polling": 60,
                "id_configuracion_sonda_externo": None,
                "id_sonda": 2, "numero_sonda": 2, "tipo_conexion": "A",
                "ultima_actualizacion": "2026-04-30T09:45:00",
                "medicion": 41200, "libre": 8800, "agua": 8,
                "temperatura": 16.8, "precio_medio": 1.449,
                "parcial": 0, "capacidad_sonda": 50000,
            },
        ]})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                t.id_tanque,
                t.numero,
                t.capacidad            AS capacidad_tanque,
                t.fecha_instalacion,
                t.visible,
                t.id_tanque_externo,
                cs.id_configuracion_sonda,
                cs.nombre              AS nombre_sonda,
                cs.id_pista,
                cs.numero_logico_concentrador,
                cs.puerto_concentrador,
                cs.deteccion_fugas,
                cs.volumen_perdida,
                cs.recuento_estable,
                cs.fin_entrega,
                cs.ciclo_polling,
                cs.id_configuracion_sonda_externo,
                s.id_sonda,
                s.numero_sonda,
                s.tipo_conexion,
                s.ultima_actualizacion,
                s.medicion,
                s.libre,
                s.agua,
                s.temperatura,
                s.precio_medio,
                s.parcial,
                s.capacidad            AS capacidad_sonda,
                s.update_date
            FROM tanque t
            LEFT JOIN configuracion_sonda cs
                   ON t.id_configuracion_sonda = cs.id_configuracion_sonda
            LEFT JOIN (
                SELECT DISTINCT ON (id_tanque)
                       id_sonda, id_tanque, numero_sonda, tipo_conexion,
                       ultima_actualizacion, medicion, libre, agua,
                       temperatura, precio_medio, parcial, capacidad,
                       update_date
                FROM sonda
                ORDER BY id_tanque, ultima_actualizacion DESC
            ) s ON s.id_tanque = t.id_tanque
            WHERE t.visible = TRUE
              AND t.id_configuracion_sonda IS NOT NULL
              AND s.id_sonda IS NOT NULL
            ORDER BY t.numero
        """)
        rows = []
        for r in cur.fetchall():
            fila = dict(r)
            # Serializar timestamps y Decimal a tipos JSON-compatibles
            for k, v in fila.items():
                if hasattr(v, "isoformat"):
                    fila[k] = v.isoformat()
                elif hasattr(v, "__float__"):
                    fila[k] = float(v)
                # None queda como None → null en JSON
            rows.append(fila)
        log(f"Sondas leidas de {host}: {len(rows)} tanque(s)", "ok")
        return jsonify({"ok": True, "demo": False, "sondas": rows})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_sondas {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer las sondas"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


_CAMPOS_SONDA_INT = {"numero_logico_concentrador", "puerto_concentrador"}


@app.route("/api/sondas/campo/red", methods=["POST"])
@need_conn
@csrf
def api_set_sonda_campo_red_all():
    """Aplica un cambio de campo de configuracion_sonda en TODOS los TPVs.
    - puerto_concentrador: UPDATE en todas las sondas del TPV (un puerto compartido).
    - numero_logico_concentrador: UPDATE solo en la sonda con numero_sonda dado."""
    data = request.get_json(force=True) or {}
    campo = data.get("campo", "")
    if campo not in _CAMPOS_SONDA_INT:
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400
    try:
        valor = int(data.get("valor"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "valor debe ser entero"}), 400
    numero_sonda = data.get("numero_sonda")
    if campo != "puerto_concentrador" and numero_sonda is None:
        return jsonify({"ok": False,
                        "error": f"numero_sonda requerido para {campo}"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            if campo == "puerto_concentrador":
                cur.execute(f"UPDATE configuracion_sonda SET {campo} = %s", (valor,))
            else:
                cur.execute(
                    f"UPDATE configuracion_sonda SET {campo} = %s "
                    f"WHERE id_configuracion_sonda IN ("
                    f"  SELECT t2.id_configuracion_sonda FROM tanque t2 "
                    f"  JOIN sonda s2 ON s2.id_tanque = t2.id_tanque "
                    f"  WHERE s2.numero_sonda = %s "
                    f"  AND t2.id_configuracion_sonda IS NOT NULL"
                    f")",
                    (valor, numero_sonda))
            n = cur.rowcount
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN sondas_red {host} campo={campo}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] sondas.{campo}={valor} numero_sonda={numero_sonda}: "
        f"ok={res['ok_count']}/{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/integrados")
@need_conn
def api_get_integrados():
    """Lee la tabla mpe (integrados) de la BD tpv."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "integrados": [
            {"id_mpe": 1, "codigo": "SE", "nombre": "Solred TMS", "codigo_articulo_generico": "093",
             "factura": True, "numero_tpv": "0", "devolucion_cualquier_forma_pago": True, "activado": True,
             "formas_pago": [
                 {"nombre": "Solred",     "clase": "R", "referencia": "02"},
                 {"nombre": "Repsol Mas", "clase": "C", "referencia": "60"},
             ]},
            {"id_mpe": 2, "codigo": "H6", "nombre": "H24", "codigo_articulo_generico": "121",
             "factura": True, "numero_tpv": "0", "devolucion_cualquier_forma_pago": True, "activado": False,
             "formas_pago": [
                 {"nombre": "H24", "clase": "R", "referencia": "04"},
             ]},
        ], "conexion_mpe": True})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT m.id_mpe,
                   m.codigo,
                   m.nombre,
                   m.codigo_articulo_generico,
                   m.factura,
                   m.numero_tpv,
                   m.devolucion_cualquier_forma_pago,
                   m.activado,
                   fp.id_forma_pago,
                   fp.nombre   AS fp_nombre,
                   fp.clase,
                   fp.referencia
            FROM mpe m
            LEFT JOIN forma_pago fp ON fp.id_mpe = m.id_mpe
                                    AND fp.delete_date IS NULL
            WHERE m.id_mpe IS NOT NULL
            ORDER BY m.id_mpe, fp.nombre
        """)
        rows = cur.fetchall()
        # Leer el flag global de conexion MPE (tabla configuracion_avanzada)
        conexion_mpe = None
        try:
            cur.execute("SELECT conexion_mpe FROM configuracion_avanzada LIMIT 1")
            fila_cfg = cur.fetchone()
            if fila_cfg is not None:
                conexion_mpe = fila_cfg["conexion_mpe"]
        except Exception:
            conexion_mpe = None
        # Agrupar formas de pago bajo cada mpe
        mpe_map = {}
        for r in rows:
            row = dict(r)
            mid = row["id_mpe"]
            if mid not in mpe_map:
                mpe_map[mid] = {
                    "id_mpe":                        row["id_mpe"],
                    "codigo":                        (row["codigo"] or "").strip(),
                    "nombre":                        row["nombre"],
                    "codigo_articulo_generico":      row["codigo_articulo_generico"],
                    "factura":                       row["factura"],
                    "numero_tpv":                    row["numero_tpv"],
                    "devolucion_cualquier_forma_pago": row["devolucion_cualquier_forma_pago"],
                    "activado":                      row["activado"],
                    "formas_pago":                   [],
                }
            if row["fp_nombre"] is not None:
                mpe_map[mid]["formas_pago"].append({
                    "id_forma_pago": row["id_forma_pago"],
                    "nombre":        row["fp_nombre"],
                    "clase":         (row["clase"] or "").strip(),
                    "referencia":    row["referencia"],
                })
        return jsonify({"ok": True, "integrados": list(mpe_map.values()),
                        "conexion_mpe": conexion_mpe})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_integrados {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los medios de pago"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/forma_pago/<int:id_forma_pago>/set_mpe", methods=["POST"])
@need_conn
@csrf
def api_set_mpe_forma_pago(id_forma_pago):
    """Actualiza el id_mpe de una forma de pago."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    id_mpe = data.get("id_mpe")
    if id_mpe is None:
        return jsonify({"ok": False, "error": "id_mpe requerido"}), 400
    try:
        id_mpe = int(id_mpe)
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "id_mpe debe ser entero"}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute(
            "UPDATE forma_pago SET id_mpe = %s WHERE id_forma_pago = %s",
            (id_mpe, id_forma_pago)
        )
        if cur.rowcount == 0:
            return jsonify({"ok": False, "error": f"No existe forma_pago con id {id_forma_pago}"}), 404
        c.commit()
        log(f"forma_pago id={id_forma_pago} → id_mpe={id_mpe}", "ok")
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_mpe_forma_pago: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/personal")
@need_conn
def api_get_personal():
    """Lee la tabla personal de la BD tpv. Password nunca se devuelve en claro."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "perfiles": [
                {"id_perfil_tpv": 1, "descripcion": "Bajo"},
                {"id_perfil_tpv": 2, "descripcion": "Medio"},
                {"id_perfil_tpv": 3, "descripcion": "Alto"},
            ],
            "personal": [
            {"id_personal": 1, "nombre": "Carlos",   "primer_apellido": "García",   "segundo_apellido": "López",
             "nif": "12345678A", "referencia": "15", "importe_retiro": 200.00,
             "nivel_acceso": 3, "id_idioma": 1, "diestro": True, "id_perfil_tpv": 1, "id_personal_externo": "16"},
            {"id_personal": 2, "nombre": "Ana",      "primer_apellido": "Martínez", "segundo_apellido": None,
             "nif": "87654321B", "referencia": "07", "importe_retiro": 100.00,
             "nivel_acceso": 1, "id_idioma": 1, "diestro": True, "id_perfil_tpv": 2, "id_personal_externo": "22"},
        ]})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # NOTA: password NUNCA se devuelve al cliente — es la contrasena del
        # empleado del TPV y nadie debe verla por la API. Si en el futuro
        # se necesita validar password, hacerlo server-side via endpoint propio.
        cur.execute("""
            SELECT id_personal,
                   nombre,
                   primer_apellido,
                   segundo_apellido,
                   nif,
                   referencia,
                   importe_retiro,
                   nivel_acceso,
                   id_idioma,
                   diestro,
                   id_perfil_tpv,
                   id_personal_externo
            FROM personal
            ORDER BY nombre, primer_apellido
        """)
        rows = cur.fetchall()
        # Catálogo de perfiles para el selector
        perfiles = []
        try:
            cur.execute("SELECT id_perfil_tpv, nombre AS descripcion "
                        "FROM perfil_tpv ORDER BY id_perfil_tpv")
            perfiles = [dict(r) for r in cur.fetchall()]
        except Exception as ep:
            log(f"WARN perfil_tpv: {str(ep).split(chr(10))[0]}", "warn")
        personal = []
        for r in rows:
            row = dict(r)
            for k, v in row.items():
                if hasattr(v, "isoformat"):
                    row[k] = v.isoformat()
                elif hasattr(v, "__float__") and not isinstance(v, (int, bool)):
                    row[k] = float(v)
            personal.append(row)
        return jsonify({"ok": True, "personal": personal, "perfiles": perfiles})
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN personal: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo leer la tabla personal"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/personal/passwords")
@need_conn
def api_get_personal_passwords():
    """Devuelve las passwords de los empleados — endpoint dedicado, solo se
    llama bajo accion explicita del tecnico (boton "Ver claves"). El GET
    normal /api/personal NO las devuelve por seguridad. Justificacion: el
    tecnico de mantenimiento necesita poder ver/restablecer la contrasena
    de un empleado que la ha olvidado."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "passwords": {
            "1": "1234",
            "2": "5678",
        }})

    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute("SELECT id_personal, password FROM personal ORDER BY id_personal")
        rows = cur.fetchall()
        passwords = {str(r[0]): (r[1] if r[1] is not None else "") for r in rows}
        log(f"Passwords de personal solicitadas en {host}: {len(passwords)} empleados", "info")
        return jsonify({"ok": True, "passwords": passwords})
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN personal_passwords: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer las passwords"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/personal/<int:id_personal>/perfil", methods=["POST"])
@need_conn
@csrf
def api_set_personal_perfil(id_personal):
    """Actualiza id_perfil_tpv de un empleado."""
    data = request.get_json(force=True) or {}
    try:
        id_perfil = int(data.get("id_perfil_tpv"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "id_perfil_tpv debe ser entero"}), 400
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        # Validar que el perfil existe
        cur.execute("SELECT 1 FROM perfil_tpv WHERE id_perfil_tpv = %s", (id_perfil,))
        if not cur.fetchone():
            return jsonify({"ok": False,
                            "error": f"id_perfil_tpv {id_perfil} no existe"}), 404
        cur.execute(
            "UPDATE personal SET id_perfil_tpv = %s WHERE id_personal = %s",
            (id_perfil, id_personal))
        if cur.rowcount == 0:
            return jsonify({"ok": False,
                            "error": f"No existe personal con id {id_personal}"}), 404
        c.commit()
        log(f"personal id={id_personal} id_perfil_tpv={id_perfil}", "ok")
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_personal_perfil: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/personal/<int:id_personal>/retiro", methods=["POST"])
@need_conn
@csrf
def api_set_personal_retiro(id_personal):
    """Actualiza importe_retiro de un empleado."""
    data = request.get_json(force=True) or {}
    try:
        valor = float(data.get("valor"))
        if valor < 0:
            raise ValueError("negativo")
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "valor debe ser numerico positivo"}), 400
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute(
            "UPDATE personal SET importe_retiro = %s WHERE id_personal = %s",
            (valor, id_personal))
        if cur.rowcount == 0:
            return jsonify({"ok": False, "error": f"No existe personal con id {id_personal}"}), 404
        c.commit()
        log(f"personal id={id_personal} importe_retiro={valor}", "ok")
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_personal_retiro: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/depositos")
@need_conn
def api_get_depositos():
    """Lee configuracion_estacion (booleans de depósito) + forma_pago (tipo_fijo)."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "estacion": {"id_configuracion_estacion": 1,
                         "deposito_seguridad_como_forma_pago": True,
                         "ultimo_retiro_como_forma_pago": False},
            "formas_pago": [
                {"id_forma_pago": 1, "nombre": "Efectivo",               "tipo_fijo": None},
                {"id_forma_pago": 2, "nombre": "Depósito de seguridad",  "tipo_fijo": "D"},
                {"id_forma_pago": 3, "nombre": "Tarjeta",                "tipo_fijo": None},
            ]})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id_configuracion_estacion, "
            "deposito_seguridad_como_forma_pago, ultimo_retiro_como_forma_pago "
            "FROM configuracion_estacion LIMIT 1")
        row = cur.fetchone()
        estacion = dict(row) if row else {}
        cur.execute(
            "SELECT id_forma_pago, nombre, tipo_fijo "
            "FROM forma_pago WHERE delete_date IS NULL "
            "ORDER BY id_forma_pago")
        fps = [dict(r) for r in cur.fetchall()]
        return jsonify({"ok": True, "estacion": estacion, "formas_pago": fps})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_depositos: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los datos de depositos"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


_CAMPOS_ESTACION_DEPOSITO = {"deposito_seguridad_como_forma_pago", "ultimo_retiro_como_forma_pago"}


# ── TOTALES TARJETAS (configuracion_estacion) ─────────────────────
# Los 3 primeros son boolean; el último es character(1) — por defecto 'E'.

_CAMPOS_TOTALES_TARJETAS_BOOL = {
    "pedir_recaudacion_totales",
    "totales_forma_pago_cierre_turno",
    "arqueo_cajon_totales_forma_pago",
}
_CAMPOS_TOTALES_TARJETAS_CHAR = {
    "seleccion_defecto_totales_forma_pago",
}


@app.route("/api/totales-tarjetas")
@need_conn
def api_get_totales_tarjetas():
    """Lee los campos de configuracion_estacion para Totales tarjetas."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
            "estacion": {"id_configuracion_estacion": 1,
                         "pedir_recaudacion_totales": True,
                         "totales_forma_pago_cierre_turno": True,
                         "seleccion_defecto_totales_forma_pago": "E",
                         "arqueo_cajon_totales_forma_pago": True}})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT id_configuracion_estacion, "
            "pedir_recaudacion_totales, totales_forma_pago_cierre_turno, "
            "seleccion_defecto_totales_forma_pago, arqueo_cajon_totales_forma_pago "
            "FROM configuracion_estacion LIMIT 1")
        row = cur.fetchone()
        estacion = dict(row) if row else {}
        # Normalizar el carácter (puede llegar con espacios por ser CHAR(1))
        if "seleccion_defecto_totales_forma_pago" in estacion and estacion["seleccion_defecto_totales_forma_pago"] is not None:
            estacion["seleccion_defecto_totales_forma_pago"] = str(estacion["seleccion_defecto_totales_forma_pago"]).strip()
        return jsonify({"ok": True, "estacion": estacion})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_totales_tarjetas: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los totales de tarjetas"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/configuracion_tpv")
@need_conn
def api_get_conf_tpv():
    """Lee la tabla configuracion_tpv del TPV indicado."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT habilitar_forma_pago_efectivo FROM configuracion_tpv LIMIT 1")
        row = cur.fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Sin datos en configuracion_tpv"}), 404
        config = dict(row)
        # Campos que viven en configuracion_estacion pero pertenecen logicamente
        # a la pestaña "Configuración TPV". Si la tabla esta vacia, no fallamos
        # el endpoint — el campo simplemente no se mostrara.
        try:
            cur.execute("SELECT borrar_display_surtidor_sin_suministros "
                        "FROM configuracion_estacion LIMIT 1")
            row_est = cur.fetchone()
            if row_est:
                config.update(dict(row_est))
        except Exception as e2:
            log(f"WARN api_get_conf_tpv {host} (configuracion_estacion): "
                f"{str(e2).split(chr(10))[0]}", "warn")
        return jsonify({"ok": True, "config": config})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_conf_tpv {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo leer la configuracion del TPV"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# Whitelist de campos editables de configuracion_tpv (extensible)
_CAMPOS_CONFTPV = {
    "habilitar_forma_pago_efectivo",
}
# Whitelist de campos de configuracion_ESTACION expuestos desde el modulo
# "⚙ Configuración TPV" (junto a _CAMPOS_CONFTPV). El campo vive en otra tabla
# pero conceptualmente pertenece a la pestaña "Configuracion TPV".
_CAMPOS_ESTACION_DESDE_TPV = {
    "borrar_display_surtidor_sin_suministros",
}


def _aplicar_red(apply_one):
    """Ejecuta apply_one(tpv_dict) en paralelo sobre TPVS_CONOCIDOS.
    apply_one debe devolver dict con al menos {host, nombre, ok, error?}.
    Devuelve el payload agregado para jsonify."""
    if sess.get("demo"):
        resultados = [{"host": t["ip"], "nombre": t["nombre"], "ok": True}
                      for t in TPVS_CONOCIDOS]
        return {"ok": True, "demo": True, "total": len(resultados),
                "ok_count": len(resultados), "fail_count": 0,
                "resultados": resultados}
    with ThreadPoolExecutor(max_workers=4) as ex:
        resultados = list(ex.map(apply_one, TPVS_CONOCIDOS))
    ok_count = sum(1 for r in resultados if r.get("ok"))
    fail_count = len(resultados) - ok_count
    return {"ok": fail_count == 0, "total": len(resultados),
            "ok_count": ok_count, "fail_count": fail_count,
            "resultados": resultados}


# Whitelist explicita para _update_simple_red (defensa en profundidad).
# Solo se permiten tablas y campos listados aqui. Si anades un caller con un
# campo nuevo, registralo en la whitelist correspondiente.
_TABLAS_PERMITIDAS_RED = {"configuracion_tpv", "configuracion_estacion"}
_CAMPOS_PERMITIDOS_POR_TABLA = {
    "configuracion_tpv": _CAMPOS_CONFTPV,
    "configuracion_estacion": (_CAMPOS_ESTACION_DEPOSITO
                               | _CAMPOS_TOTALES_TARJETAS_BOOL
                               | _CAMPOS_TOTALES_TARJETAS_CHAR
                               | _CAMPOS_ESTACION_DESDE_TPV),
}


def _update_simple_red(tabla, campo, valor):
    """Crea un apply_one que hace UPDATE simple sobre una tabla single-row.

    Defensa en profundidad: aunque los callers pasan literales seguros, validamos
    tabla y campo contra whitelist explicita para evitar SQLi si en el futuro
    alguien anade un caller que reciba `tabla`/`campo` desde request.json.
    """
    if tabla not in _TABLAS_PERMITIDAS_RED:
        raise ValueError(f"Tabla no permitida en _update_simple_red: {tabla}")
    campos_ok = _CAMPOS_PERMITIDOS_POR_TABLA.get(tabla, set())
    if campo not in campos_ok:
        raise ValueError(f"Campo no permitido en {tabla}: {campo}")

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            cur.execute(f"UPDATE {tabla} SET {campo} = %s", (valor,))
            n = cur.rowcount
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN _update_simple_red {tabla}.{campo} {host}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass
    return apply_one


@app.route("/api/configuracion_tpv/red", methods=["POST"])
@csrf
@need_conn
def api_set_conf_tpv_red():
    """Aplica un cambio en TODOS los TPVs. La pestaña "Configuración TPV" expone
    campos de DOS tablas: configuracion_tpv (campo_principal habilitar_forma_*)
    y configuracion_estacion (borrar_display_*). Despachamos a la tabla correcta
    segun el campo recibido, ambos con whitelist explicita."""
    data = request.json or {}
    campo = str(data.get("campo", "")).strip()
    if campo in _CAMPOS_CONFTPV:
        tabla = "configuracion_tpv"
    elif campo in _CAMPOS_ESTACION_DESDE_TPV:
        tabla = "configuracion_estacion"
    else:
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400
    valor = data.get("valor")
    if not isinstance(valor, bool):
        return jsonify({"ok": False, "error": "Valor debe ser boolean"}), 400
    res = _aplicar_red(_update_simple_red(tabla, campo, valor))
    log(f"[RED] {tabla}.{campo}={valor}: ok={res['ok_count']}/"
        f"{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/depositos/estacion-bool/red", methods=["POST"])
@csrf
@need_conn
def api_set_depositos_estacion_bool_red():
    """Aplica un boolean de Depósitos en configuracion_estacion en TODOS los TPVs."""
    data = request.json or {}
    campo = data.get("campo", "")
    if campo not in _CAMPOS_ESTACION_DEPOSITO:
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400
    valor = bool(data.get("valor"))
    res = _aplicar_red(_update_simple_red("configuracion_estacion", campo, valor))
    log(f"[RED] configuracion_estacion.{campo}={valor}: ok={res['ok_count']}/"
        f"{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/depositos/forma-pago-tipo/red", methods=["POST"])
@csrf
@need_conn
def api_set_forma_pago_tipo_red():
    """Aplica el tipo_fijo a una forma_pago en TODOS los TPVs (por id)."""
    data = request.json or {}
    id_fp = data.get("id_forma_pago")
    tipo = str(data.get("tipo_fijo", "")).strip()
    if not isinstance(id_fp, int) or not tipo or len(tipo) > 2:
        return jsonify({"ok": False, "error": "Parámetros inválidos"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            cur.execute(
                "UPDATE forma_pago SET tipo_fijo = %s, update_date = NOW(), "
                "update_user = 'garum_tpv_mgr' WHERE id_forma_pago = %s",
                (tipo, id_fp))
            n = cur.rowcount
            if n == 0:
                c.rollback()
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"id_forma_pago {id_fp} no existe"}
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN forma_pago_tipo_red {host} id_fp={id_fp}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] forma_pago.id={id_fp} tipo_fijo={tipo}: "
        f"ok={res['ok_count']}/{res['total']}", "ok")
    return jsonify(res)


@app.route("/api/totales-tarjetas/campo/red", methods=["POST"])
@csrf
@need_conn
def api_set_totales_tarjetas_red():
    """Aplica un campo de Totales tarjetas en TODOS los TPVs."""
    data = request.json or {}
    campo = data.get("campo", "")
    es_bool = campo in _CAMPOS_TOTALES_TARJETAS_BOOL
    es_char = campo in _CAMPOS_TOTALES_TARJETAS_CHAR
    if not (es_bool or es_char):
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400
    if es_bool:
        valor = bool(data.get("valor"))
    else:
        v = str(data.get("valor", "")).strip().upper()
        if len(v) != 1 or not v.isalpha():
            return jsonify({"ok": False,
                            "error": "Debe ser un solo carácter alfabético (A-Z)"}), 400
        valor = v
    res = _aplicar_red(_update_simple_red("configuracion_estacion", campo, valor))
    log(f"[RED] configuracion_estacion.{campo}={valor}: ok={res['ok_count']}/"
        f"{res['total']}, fail={res['fail_count']}", "ok")
    return jsonify(res)


@app.route("/api/sesion-cierre-turno/huerfanos", methods=["POST"])
@csrf
@need_conn
def api_huerfanos_sesion_cierre():
    """
    Identifica o elimina registros huérfanos en sesion_cierre_turno
    (registros sin sesión activa correspondiente en sesion_tpv_activo).
    Body: { accion: 'identificar'|'eliminar', hosts: ['10.0.0.101', ...] }
    """
    data   = request.get_json() or {}
    accion = data.get("accion", "identificar")
    hosts  = data.get("hosts", [])

    SQL_SEL = """
        SELECT sct.*
        FROM sesion_cierre_turno sct
        WHERE NOT EXISTS (
            SELECT 1 FROM sesion_tpv_activo sta
            WHERE sta.id_tpv = sct.id_tpv
              AND sta.id_sesion = sct.id_sesion
              AND sta.fecha_ultima_activo > now() - interval '5 minutes'
        )
    """
    SQL_DEL = """
        DELETE FROM sesion_cierre_turno sct
        WHERE NOT EXISTS (
            SELECT 1 FROM sesion_tpv_activo sta
            WHERE sta.id_tpv = sct.id_tpv
              AND sta.id_sesion = sct.id_sesion
              AND sta.fecha_ultima_activo > now() - interval '5 minutes'
        )
    """

    resultados = {}
    errores    = []

    for host_raw in hosts:
        # Defensa contra SSRF: validar IP antes de usar credenciales.
        try:
            host = val_host(host_raw)
        except ValueError as e:
            resultados[str(host_raw)] = {"ok": False, "error": str(e)}
            errores.append(f"{host_raw}: {e}")
            continue

        conn = None
        try:
            conn = conn_tpv(host)
            if accion == "identificar":
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(SQL_SEL)
                filas = [dict(r) for r in cur.fetchall()]
                for f in filas:
                    for k, v in f.items():
                        if hasattr(v, "isoformat"):
                            f[k] = v.isoformat()
                resultados[host] = {"ok": True, "count": len(filas), "filas": filas}
            else:
                cur = conn.cursor()
                cur.execute(SQL_DEL)
                eliminados = cur.rowcount
                conn.commit()
                resultados[host] = {"ok": True, "eliminados": eliminados}
        except Exception as ex:
            if conn:
                try: conn.rollback()
                except Exception: pass
            msg = str(ex).split("\n")[0]
            log(f"WARN huerfanos_sesion_cierre {host}: {msg}", "warn")
            resultados[host] = {"ok": False, "error": "No se pudo procesar la operacion en la BD"}
            errores.append(f"{host}: no se pudo procesar")
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    return jsonify({"ok": len(errores) == 0, "accion": accion,
                    "resultados": resultados, "errores": errores})


@app.route("/api/estacion")
@need_conn
def api_get_estacion():
    """Lee el nombre y tipo de la estación de servicio de la tabla estacion."""
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
                        "nombre": "Estación Demo", "tipo_estacion": "C"})
    c = None
    try:
        c = conn_tpv(sess.get("host", ""))
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT nombre, tipo_estacion FROM estacion LIMIT 1")
        row = cur.fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Sin datos en tabla estacion"}), 404
        return jsonify({"ok": True, "nombre": row["nombre"],
                        "tipo_estacion": row["tipo_estacion"]})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_estacion: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los datos de la estacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/estacion/estado-red")
@need_conn
def api_estacion_estado_red():
    """Lee de todos los TPVs conocidos: tipo_estacion, nº de carburantes,
    si existe regla_facturacion con tienda=TRUE y la serie comisionista
    propia del TPV (factura=TRUE, rectificativa=FALSE, comision=TRUE, propia=TRUE)."""
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "tpvs": [
            {"id": 1, "nombre": "TPV 1", "ip": "10.0.0.101", "accesible": True,
             "tipo_estacion": "C", "carburantes": 6, "regla_tienda": True,
             "series": [{"id_serie": 17, "serie": "O1",
                         "descripcion": "Factura Carburante"}], "error": None},
        ]})

    def leer_est(tpv):
        info = {"id": tpv["id"], "nombre": tpv["nombre"], "ip": tpv["ip"],
                "accesible": False, "tipo_estacion": None, "carburantes": 0,
                "regla_tienda": False, "series": [],
                "series_tienda": [], "series_carburante": [],
                "error": None}
        c = None
        try:
            c = conn_tpv(tpv["ip"])
            cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT tipo_estacion FROM estacion LIMIT 1")
            row = cur.fetchone()
            if row and row["tipo_estacion"]:
                info["tipo_estacion"] = row["tipo_estacion"].strip()
            cur.execute("SELECT COUNT(*) AS n FROM articulo "
                        "WHERE asignable_tanque = TRUE AND carburante = TRUE")
            info["carburantes"] = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM regla_facturacion WHERE tienda = TRUE")
            info["regla_tienda"] = cur.fetchone()["n"] > 0
            # Serie comisionista propia del TPV (para el cambio a Comisionista)
            cur.execute("SELECT id_serie, serie, descripcion FROM serie "
                        "WHERE factura = TRUE AND rectificativa = FALSE "
                        "AND comision = TRUE AND propia = TRUE ORDER BY id_serie")
            info["series"] = [dict(r) for r in cur.fetchall()]
            # Serie de la regla tienda
            cur.execute("SELECT s.id_serie, s.serie, s.descripcion "
                        "FROM regla_facturacion rf "
                        "JOIN serie s ON s.id_serie = rf.id_serie "
                        "WHERE rf.tienda = TRUE "
                        "ORDER BY s.id_serie")
            info["series_tienda"] = [dict(r) for r in cur.fetchall()]
            # Serie de la regla carburante (en Firme coincide con tienda; en Comisionista difiere)
            cur.execute("SELECT s.id_serie, s.serie, s.descripcion "
                        "FROM regla_facturacion rf "
                        "JOIN serie s ON s.id_serie = rf.id_serie "
                        "WHERE rf.carburante = TRUE "
                        "ORDER BY s.id_serie")
            info["series_carburante"] = [dict(r) for r in cur.fetchall()]
            info["accesible"] = True
        except Exception as e:
            msg = str(e).split("\n")[0]
            log(f"WARN leer_est {tpv['ip']}: {msg}", "warn")
            info["error"] = "No se pudieron leer los datos"
        finally:
            if c:
                try: c.close()
                except Exception: pass
        return info

    with ThreadPoolExecutor(max_workers=4) as ex:
        tpvs = list(ex.map(leer_est, TPVS_CONOCIDOS))
    return jsonify({"ok": True, "tpvs": tpvs})


@app.route("/api/estacion/cambiar-tipo", methods=["POST"])
@csrf
@need_conn
def api_estacion_cambiar_tipo():
    """Cambia el tipo de estación (F = Firme / C = Comisionista) en los TPVs
    indicados. Por cada TPV: actualiza articulo.comision de los carburantes,
    estacion.tipo_estacion y reestructura regla_facturacion.
    Si tipo=C y existe mpe.codigo='S8' (Solred V8), también pone mpe.factura=TRUE."""
    data  = request.get_json() or {}
    tipo  = str(data.get("tipo", "")).strip().upper()
    hosts = data.get("hosts", [])

    if tipo not in ("F", "C"):
        return jsonify({"ok": False, "error": "Tipo inválido (debe ser F o C)"}), 400

    comision_bool = (tipo == "C")
    resultados = {}
    errores    = []

    for host_raw in hosts:
        try:
            host = val_host(host_raw)
        except ValueError:
            errores.append(f"{host_raw}: IP inválida")
            continue

        conn = None
        try:
            conn = conn_tpv(host)
            conn.autocommit = False
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM regla_facturacion WHERE tienda = TRUE")
            if cur.fetchone()[0] == 0:
                conn.rollback()
                resultados[host] = {"ok": False,
                                    "error": "Sin regla_facturacion tienda=TRUE — TPV omitido"}
                errores.append(f"{host}: sin regla tienda")
                continue

            # 1. articulo — comision de los carburantes (no el AdBlue: carburante=FALSE)
            cur.execute("UPDATE articulo SET comision = %s "
                        "WHERE asignable_tanque = TRUE AND carburante = TRUE",
                        (comision_bool,))
            n_art = cur.rowcount

            # 2. estacion
            cur.execute("UPDATE estacion SET tipo_estacion = %s", (tipo,))

            # 3. regla_facturacion
            serie_info = None
            if tipo == "F":
                cur.execute("UPDATE regla_facturacion SET carburante = TRUE "
                            "WHERE tienda = TRUE")
                cur.execute("DELETE FROM regla_facturacion "
                            "WHERE tienda = FALSE AND carburante = TRUE")
                regla = (f"regla tienda → carburante=TRUE; "
                         f"{cur.rowcount} regla(s) carburante eliminada(s)")
            else:
                # Serie comisionista propia de ESTE TPV
                cur.execute("SELECT id_serie, serie FROM serie "
                            "WHERE factura = TRUE AND rectificativa = FALSE "
                            "AND comision = TRUE AND propia = TRUE")
                filas = cur.fetchall()
                if len(filas) == 0:
                    raise Exception("sin serie comisionista propia "
                                    "(factura=T, rectificativa=F, comision=T, propia=T)")
                if len(filas) > 1:
                    raise Exception(f"{len(filas)} series comisionista propias — "
                                    "ambiguo, revisar manualmente")
                id_serie_com, serie_com = filas[0]
                cur.execute("UPDATE regla_facturacion SET carburante = FALSE "
                            "WHERE tienda = TRUE")
                cur.execute("DELETE FROM regla_facturacion "
                            "WHERE tienda = FALSE AND carburante = TRUE")
                cur.execute(
                    "INSERT INTO regla_facturacion "
                    "(id_regla_facturacion, id_serie, tienda, carburante) "
                    "VALUES ((SELECT COALESCE(MAX(id_regla_facturacion), 0) + 1 "
                    "FROM regla_facturacion), %s, FALSE, TRUE)", (id_serie_com,))
                regla = f"regla tienda → carburante=FALSE; regla carburante → serie {serie_com}"
                # Leer todas las series disponibles para mostrar en el frontend
                cur.execute("SELECT id_serie, serie, descripcion FROM serie "
                            "WHERE factura = TRUE AND rectificativa = FALSE "
                            "ORDER BY id_serie")
                serie_info = {
                    "id_serie": id_serie_com,
                    "serie": serie_com,
                    "disponibles": [{"id_serie": r[0], "serie": r[1],
                                     "descripcion": r[2] or ""} for r in cur.fetchall()],
                }

            # 4. mpe — Solred V8 (codigo='S8') debe facturar en Comisionista
            mpe_s8 = None
            if tipo == "C":
                cur.execute("UPDATE mpe SET factura = TRUE "
                            "WHERE codigo = 'S8' AND (factura IS NULL OR factura = FALSE)")
                n_mpe = cur.rowcount
                # Detectar si existe la fila S8 aunque ya estuviera a TRUE
                cur.execute("SELECT COUNT(*) FROM mpe WHERE codigo = 'S8'")
                n_total = cur.fetchone()[0]
                if n_total == 0:
                    mpe_s8 = {"existe": False, "actualizado": 0}
                else:
                    mpe_s8 = {"existe": True, "actualizado": n_mpe}

            conn.commit()
            res_tpv = {"ok": True, "tipo": tipo, "carburantes": n_art, "regla": regla}
            if serie_info:
                res_tpv["serie_asignada"] = {"id_serie": serie_info["id_serie"],
                                             "serie":    serie_info["serie"]}
                res_tpv["series_disponibles"] = serie_info["disponibles"]
            if mpe_s8 is not None:
                res_tpv["mpe_s8"] = mpe_s8
            resultados[host] = res_tpv
        except Exception as e:
            if conn:
                try: conn.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN api_estacion_cambiar_tipo {host}: {msg}", "warn")
            resultados[host] = {"ok": False, "error": "No se pudo cambiar el tipo de estacion"}
            errores.append(f"{host}: no se pudo cambiar el tipo")
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    return jsonify({"ok": len(errores) == 0, "tipo": tipo,
                    "resultados": resultados, "errores": errores})


@app.route("/api/estacion/serie-carburante", methods=["POST"])
@need_conn
@csrf
def api_set_serie_carburante():
    """Cambia la serie asignada a regla_facturacion (tienda=FALSE, carburante=TRUE)."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    id_serie = data.get("id_serie")
    if not isinstance(id_serie, int):
        return jsonify({"ok": False, "error": "id_serie debe ser entero"}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute("UPDATE regla_facturacion SET id_serie = %s "
                    "WHERE tienda = FALSE AND carburante = TRUE", (id_serie,))
        if cur.rowcount == 0:
            return jsonify({"ok": False,
                            "error": "No existe regla_facturacion carburante para actualizar"}), 404
        c.commit()
        log(f"regla_facturacion carburante → id_serie={id_serie}", "ok")
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_serie_carburante: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/integrados/<int:id_mpe>/activado", methods=["POST"])
@need_conn
@csrf
def api_set_mpe_activado(id_mpe):
    """Activa o desactiva un medio de pago (campo mpe.activado)."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    activado = bool(data.get("activado"))

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "activado": activado})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute("UPDATE mpe SET activado = %s WHERE id_mpe = %s",
                    (activado, id_mpe))
        if cur.rowcount == 0:
            return jsonify({"ok": False,
                            "error": f"No existe mpe con id {id_mpe}"}), 404
        c.commit()
        log(f"mpe id={id_mpe} -> activado={activado}", "ok")
        return jsonify({"ok": True, "activado": activado})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_mpe_activado: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


_CAMPOS_MPE_BOOL = {"factura", "devolucion_cualquier_forma_pago"}


@app.route("/api/integrados/<int:id_mpe>/campo", methods=["POST"])
@need_conn
@csrf
def api_set_mpe_campo(id_mpe):
    """Actualiza un campo booleano de mpe (factura, devolucion_cualquier_forma_pago)."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    campo = data.get("campo", "")
    if campo not in _CAMPOS_MPE_BOOL:
        return jsonify({"ok": False, "error": f"Campo no permitido: {campo}"}), 400
    valor = bool(data.get("valor"))
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, campo: valor})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute(f"UPDATE mpe SET {campo} = %s WHERE id_mpe = %s", (valor, id_mpe))
        if cur.rowcount == 0:
            return jsonify({"ok": False, "error": f"No existe mpe con id {id_mpe}"}), 404
        c.commit()
        log(f"mpe id={id_mpe} -> {campo}={valor}", "ok")
        return jsonify({"ok": True, campo: valor})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_mpe_campo {campo}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/conexion_mpe", methods=["POST"])
@need_conn
@csrf
def api_set_conexion_mpe():
    """Activa o desactiva la conexion MPE global (configuracion_avanzada.conexion_mpe)."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    activado = bool(data.get("activado"))

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "activado": activado})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute("UPDATE configuracion_avanzada SET conexion_mpe = %s",
                    (activado,))
        if cur.rowcount == 0:
            return jsonify({"ok": False,
                            "error": "La tabla configuracion_avanzada no tiene filas"}), 404
        c.commit()
        log(f"configuracion_avanzada.conexion_mpe -> {activado}", "ok")
        return jsonify({"ok": True, "activado": activado})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_set_conexion_mpe: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/articulos_mpe")
@need_conn
def api_get_articulos_mpe():
    """Lee la tabla articulo_mpe de la BD tpv. Solo lectura."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "articulos": [
            {"id_articulo": 1, "id_mpe": 1, "codigo_mpe": "GASOIL001", "clase": "G",
             "update_date": "2026-04-01T10:00:00", "update_user": "admin", "precio": 1.459},
            {"id_articulo": 2, "id_mpe": 1, "codigo_mpe": "SP95001",   "clase": "G",
             "update_date": "2026-04-01T10:00:00", "update_user": "admin", "precio": 1.659},
        ]})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT am.id_articulo, am.id_mpe, am.codigo_mpe, am.clase,
                   am.update_date, am.update_user, am.precio,
                   a.nombre AS nombre_articulo
            FROM articulo_mpe am
            LEFT JOIN articulo a ON a.id_articulo = am.id_articulo
            ORDER BY am.id_mpe, am.id_articulo
        """)
        rows = cur.fetchall()
        articulos = []
        for r in rows:
            row = dict(r)
            if row.get("update_date"):
                row["update_date"] = row["update_date"].isoformat()
            if row.get("precio") is not None:
                row["precio"] = float(row["precio"])
            articulos.append(row)
        return jsonify({"ok": True, "articulos": articulos})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_articulos_mpe: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los articulos MPE"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/articulos_mpe/<int:id_articulo>", methods=["POST"])
@need_conn
@csrf
def api_update_articulo_mpe(id_articulo):
    """Actualiza codigo_mpe (y opcionalmente precio/clase) en articulo_mpe."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    codigo_mpe = data.get("codigo_mpe")
    if codigo_mpe is None:
        return jsonify({"ok": False, "error": "codigo_mpe requerido"}), 400
    codigo_mpe = str(codigo_mpe).strip()
    if not codigo_mpe:
        return jsonify({"ok": False, "error": "codigo_mpe no puede estar vacío"}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        cur.execute("""
            UPDATE articulo_mpe
            SET codigo_mpe = %s,
                update_date = NOW(),
                update_user = 'garum_tpv_mgr'
            WHERE id_articulo = %s
        """, (codigo_mpe, id_articulo))
        if cur.rowcount == 0:
            return jsonify({"ok": False, "error": f"No existe articulo_mpe con id {id_articulo}"}), 404
        c.commit()
        log(f"articulo_mpe id={id_articulo} → codigo_mpe='{codigo_mpe}'", "ok")
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_update_articulo_mpe: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/articulos_mpe/<int:id_articulo>/clase", methods=["POST"])
@need_conn
@csrf
def api_update_articulo_mpe_clase(id_articulo):
    """Actualiza solo el campo `clase` de articulo_mpe. Valores permitidos:
    '' (vacio/sin asignar) o 'R'. Aplica al TPV indicado en host_tpv."""
    data = request.get_json(force=True) or {}
    host_raw = data.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    clase = data.get("clase", "")
    if clase is None:
        clase = ""
    clase = str(clase).strip().upper()
    if clase not in ("", "R"):
        return jsonify({"ok": False, "error": "clase solo puede ser vacio o 'R'"}), 400

    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor()
        # Guardamos NULL si esta vacio, 'R' si es 'R'.
        valor_bd = clase if clase else None
        cur.execute("""
            UPDATE articulo_mpe
            SET clase = %s,
                update_date = NOW(),
                update_user = 'garum_tpv_mgr'
            WHERE id_articulo = %s
        """, (valor_bd, id_articulo))
        if cur.rowcount == 0:
            return jsonify({"ok": False, "error": f"No existe articulo_mpe con id {id_articulo}"}), 404
        c.commit()
        log(f"articulo_mpe id={id_articulo} → clase={valor_bd!r}", "ok")
        return jsonify({"ok": True, "clase": clase})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_update_articulo_mpe_clase: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudo actualizar la BD"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# =============================================================================
# ARTICULOS — Vista de carburantes + edicion del impuesto en red
# =============================================================================
# La pestaña "📋 Artículos" expone los articulos asignables a tanque que son
# carburantes (asignable_tanque=TRUE AND carburante=TRUE). Dos sub-tabs:
#   - Ver articulos: lectura del TPV seleccionado.
#   - Impuestos: dropdown editable de id_impuesto que se aplica en RED a todos
#     los TPVs accesibles (cada articulo se identifica por su `codigo` en lugar
#     de id_articulo porque los ids pueden diferir entre TPVs).
#
# Schema relevante:
#   articulo            (id_articulo PK, codigo, nombre, asignable_tanque, carburante, ...)
#   articulo_impuesto   (id_articulo FK, id_impuesto FK) — relacion N-a-N
#   impuesto            (id_impuesto PK, descripcion, ...) — master de tipos


@app.route("/api/articulos_carburante")
@need_conn
def api_get_articulos_carburante():
    """Lee `articulo` filtrando carburantes asignables a tanque. JOIN con
    articulo_impuesto + impuesto para mostrar descripcion del impuesto actual."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "articulos": [
            {"id_articulo": 1, "codigo": "G95", "nombre": "Gasolina 95",
             "comision": False, "codigo_concentrador": 1, "id_impuesto": 1,
             "nombre_impuesto": "IVA General", "cantidad_impuesto": 21.00,
             "clase_impuesto": "I"},
            {"id_articulo": 2, "codigo": "GAS", "nombre": "Gasoil B7",
             "comision": False, "codigo_concentrador": 2, "id_impuesto": 1,
             "nombre_impuesto": "IVA General", "cantidad_impuesto": 21.00,
             "clase_impuesto": "I"},
        ]})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # En la mayoria de instalaciones cada articulo tiene 1 fila en
        # articulo_impuesto. Si tuviera varias (caso teorico de la N-a-N), el
        # frontend mostrara el primero alfabeticamente por nombre.
        # Schema real de impuesto: id_impuesto, nombre, clase, cantidad, ...
        cur.execute("""
            SELECT a.id_articulo, a.codigo, a.nombre, a.comision,
                   a.codigo_concentrador,
                   ai.id_impuesto,
                   i.nombre   AS nombre_impuesto,
                   i.cantidad AS cantidad_impuesto,
                   i.clase    AS clase_impuesto
            FROM articulo a
            LEFT JOIN articulo_impuesto ai ON ai.id_articulo = a.id_articulo
            LEFT JOIN impuesto i ON i.id_impuesto = ai.id_impuesto
            WHERE a.asignable_tanque = TRUE AND a.carburante = TRUE
            ORDER BY a.codigo, a.id_articulo
        """)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            # cantidad es numeric → convertir a float para JSON
            if d.get("cantidad_impuesto") is not None:
                d["cantidad_impuesto"] = float(d["cantidad_impuesto"])
            rows.append(d)
        return jsonify({"ok": True, "articulos": rows})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_articulos_carburante {host}: {msg}", "warn")
        return jsonify({"ok": False,
                        "error": "No se pudieron leer los articulos de carburante"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/tipos_impuesto")
@need_conn
def api_get_tipos_impuesto():
    """Lee la tabla `impuesto` entera (master de tipos para el desplegable)."""
    host_raw = request.args.get("host_tpv", sess.get("host", ""))
    try:
        host = val_host(host_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "tipos": [
            {"id_impuesto": 1, "nombre": "IVA General",   "clase": "I", "cantidad": 21.00},
            {"id_impuesto": 2, "nombre": "IVA Reducido",  "clase": "I", "cantidad": 10.00},
            {"id_impuesto": 3, "nombre": "IVA Superreducido","clase": "I","cantidad":  4.00},
        ]})
    c = None
    try:
        c = conn_tpv(host)
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Solo los campos relevantes para el desplegable. update_date/update_user
        # se omiten para no inflar la respuesta.
        cur.execute("SELECT id_impuesto, nombre, clase, cantidad, id_impuesto_externo "
                    "FROM impuesto ORDER BY clase, cantidad, id_impuesto")
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            if d.get("cantidad") is not None:
                d["cantidad"] = float(d["cantidad"])
            rows.append(d)
        return jsonify({"ok": True, "tipos": rows})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_get_tipos_impuesto {host}: {msg}", "warn")
        return jsonify({"ok": False, "error": "No se pudieron leer los tipos de impuesto"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/articulos/tipo_impuesto/red", methods=["POST"])
@csrf
@need_conn
def api_set_articulo_tipo_impuesto_red():
    """Actualiza el impuesto del articulo en TODOS los TPVs accesibles.
    Identifica el articulo por `codigo` (estable entre BDs).
    Estrategia: DELETE + INSERT dentro de una transaccion (reemplaza el impuesto
    actual; si por error habia varias filas las consolidamos a una).
    Body: {codigo: str, id_impuesto: int}"""
    data = request.json or {}
    codigo = str(data.get("codigo", "")).strip()
    # Soportar tanto "id_impuesto" como "id_tipo_impuesto" en el body por compat
    # con clientes antiguos del frontend que enviaban la clave vieja.
    id_imp = data.get("id_impuesto", data.get("id_tipo_impuesto"))
    if not codigo:
        return jsonify({"ok": False, "error": "codigo requerido"}), 400
    if not isinstance(id_imp, int):
        try:
            id_imp = int(id_imp)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "id_impuesto debe ser entero"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            # 1) Validar que el id_impuesto existe en este TPV.
            cur.execute("SELECT 1 FROM impuesto WHERE id_impuesto = %s", (id_imp,))
            if cur.fetchone() is None:
                c.rollback()
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"id_impuesto {id_imp} no existe en este TPV"}
            # 2) Localizar el id_articulo local por codigo + filtros defensivos.
            cur.execute(
                "SELECT id_articulo FROM articulo "
                "WHERE codigo = %s AND asignable_tanque = TRUE AND carburante = TRUE",
                (codigo,))
            row = cur.fetchone()
            if row is None:
                c.rollback()
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"articulo con codigo={codigo} no encontrado"}
            id_articulo_local = row[0]
            # 3) Reemplazo atomico: borrar filas previas e insertar la nueva.
            cur.execute("DELETE FROM articulo_impuesto WHERE id_articulo = %s",
                        (id_articulo_local,))
            n_del = cur.rowcount
            cur.execute("INSERT INTO articulo_impuesto (id_articulo, id_impuesto) "
                        "VALUES (%s, %s)", (id_articulo_local, id_imp))
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True,
                    "id_articulo_local": id_articulo_local,
                    "filas_borradas": n_del, "filas_insertadas": 1}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN articulo_impuesto_red {host} codigo={codigo}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] articulo_impuesto({codigo})=>id_impuesto={id_imp}: "
        f"ok={res['ok_count']}/{res['total']}", "ok")
    return jsonify(res)


@app.route("/api/articulos/comision/red", methods=["POST"])
@csrf
@need_conn
def api_set_articulo_comision_red():
    """Actualiza el flag articulo.comision en TODOS los TPVs accesibles.
    Identifica el articulo por `codigo` (estable entre BDs).
    Body: {codigo: str, valor: bool}
    Defensa: filtro adicional asignable_tanque=TRUE AND carburante=TRUE
    para que el UPDATE NO afecte accidentalmente a articulos no-carburante."""
    data = request.json or {}
    codigo = str(data.get("codigo", "")).strip()
    valor = data.get("valor")
    if not codigo:
        return jsonify({"ok": False, "error": "codigo requerido"}), 400
    if not isinstance(valor, bool):
        return jsonify({"ok": False, "error": "valor debe ser boolean"}), 400

    def apply_one(tpv):
        host = tpv["ip"]
        nombre = tpv.get("nombre", host)
        c = None
        try:
            c = conn_tpv(host)
            c.autocommit = False
            cur = c.cursor()
            cur.execute(
                "UPDATE articulo SET comision = %s "
                "WHERE codigo = %s AND asignable_tanque = TRUE AND carburante = TRUE",
                (valor, codigo))
            n = cur.rowcount
            if n == 0:
                c.rollback()
                return {"host": host, "nombre": nombre, "ok": False,
                        "error": f"articulo con codigo={codigo} no encontrado"}
            c.commit()
            return {"host": host, "nombre": nombre, "ok": True, "filas": n}
        except Exception as e:
            if c:
                try: c.rollback()
                except Exception: pass
            msg = str(e).split("\n")[0]
            log(f"WARN articulo_comision_red {host} codigo={codigo}: {msg}", "warn")
            return {"host": host, "nombre": nombre, "ok": False,
                    "error": "No se pudo actualizar la BD"}
        finally:
            if c:
                try: c.close()
                except Exception: pass

    res = _aplicar_red(apply_one)
    log(f"[RED] articulo_comision({codigo})={valor}: "
        f"ok={res['ok_count']}/{res['total']}", "ok")
    return jsonify(res)


# Carpeta LOCAL del TPV donde estan las imagenes de los surtidores.
# Los ficheros se llaman cc_<codigo_concentrador>.png (convenccion GARUM).
_IMG_CARBURANTE_DIR = r"C:\GARUM\images\carburante\imagenes_surtidor"


@app.route("/api/combustibles/imagen/<int:codigo>")
@need_conn
def api_combustibles_imagen(codigo):
    """Sirve la imagen del combustible asociada por codigo_concentrador.
    Convencion GARUM: ficheros 'cc_<N>.png' en C:\\GARUM\\images\\carburante\\
    imagenes_surtidor. Si no encuentra .png, prueba .jpg/.jpeg/.gif/.bmp.
    Devuelve 404 si no existe (el frontend usa onerror para esconder el img).
    Defensa: validar rango del codigo + abspath dentro del directorio base
    (impide path traversal aunque codigo viene como int de la URL — defensa
    en profundidad)."""
    if codigo < 0 or codigo > 99999:
        abort(400)
    base = _IMG_CARBURANTE_DIR
    if not os.path.isdir(base):
        # Si la carpeta GARUM no existe en este equipo (p. ej. dev), 404 limpio.
        abort(404)
    base_abs = os.path.abspath(base)
    for ext in ("png", "jpg", "jpeg", "gif", "bmp"):
        candidato = os.path.join(base, f"cc_{codigo}.{ext}")
        cand_abs = os.path.abspath(candidato)
        # Defensa en profundidad — el path resuelto debe estar dentro del directorio base
        if not cand_abs.startswith(base_abs):
            continue
        if os.path.isfile(cand_abs):
            return send_file(cand_abs)
    abort(404)


# =============================================================================
# INSTALACION — Backup + Restore + Integración de nuevo TPV secundario
# =============================================================================

_BACKUP_DIR = r"C:\GarumTPV\backups"
_PG_VERS    = ["9.5","9.6","10","11","12","13","14","15","16"]
_INST_DBS   = ["tpv", "controlpista"]


def _find_pg_bin(tool):
    """Busca pg_dump.exe / pg_restore.exe en rutas estándar de PostgreSQL en Windows."""
    for ver in _PG_VERS:
        p = rf"C:\Program Files\PostgreSQL\{ver}\bin\{tool}.exe"
        if os.path.exists(p):
            return p
    import shutil
    return shutil.which(tool)


def _job_log(job, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    job["logs"].append(f"[{ts}] {msg}")


def _job_step(job, n, status):
    """Marca el estado de un paso del plan para que el frontend lo refleje en vivo.
    Estados: 'running' (en curso), 'done' (completado), 'error', 'skipped'.
    Solo se usa en jobs que tengan un plan paso a paso (p.ej. reintegrar)."""
    if "steps" not in job:
        job["steps"] = {}
    job["steps"][str(n)] = status


def _run_pg_cmd(job, cmd, password):
    """Ejecuta pg_dump/pg_restore capturando stderr línea a línea."""
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    flags = 0x08000000 if sys.platform == "win32" else 0   # CREATE_NO_WINDOW
    try:
        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True,
            env=env,
            creationflags=flags,
        )
        for line in proc.stderr:
            line = line.strip()
            if line:
                _job_log(job, line)
        proc.wait()
        return proc.returncode
    except FileNotFoundError:
        _job_log(job, f"ERROR: ejecutable no encontrado — {cmd[0]}")
        return -1
    except Exception as e:
        _job_log(job, f"ERROR: {e}")
        return -1


def _job_backup(job_id, pg_dump, ip_origen, password):
    """Hilo que ejecuta pg_dump de _INST_DBS contra ip_origen."""
    job = _instalar_jobs[job_id]
    os.makedirs(_BACKUP_DIR, exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    _job_log(job, f"Conectando a {ip_origen}...")
    for db in _INST_DBS:
        filename = f"{db}_{ts_str}.backup"
        filepath = os.path.join(_BACKUP_DIR, filename)
        _job_log(job, f"► Backup BD '{db}' → {filename}")

        cmd = [
            pg_dump, "-h", ip_origen, "-p", "5432", "-U", "postgres",
            "-d", db, "-F", "c", "-v", "-f", filepath,
        ]
        rc = _run_pg_cmd(job, cmd, password)

        if rc != 0:
            _job_log(job, f"✗ pg_dump falló en '{db}' (código {rc})")
            job["error"]  = f"pg_dump falló en BD '{db}' (código {rc})"
            job["status"] = "error"
            job["done"]   = True
            return

        size_mb = os.path.getsize(filepath) / (1024*1024) if os.path.exists(filepath) else 0
        _job_log(job, f"✓ '{db}' completado → {filename} ({size_mb:.1f} MB)")
        job["ficheros"][db] = filepath

    _job_log(job, "✓ Backup completado.")
    job["status"] = "ok"
    job["done"]   = True


def _job_restore(job_id, pg_restore, password, ficheros):
    """Hilo que ejecuta pg_restore sobre 127.0.0.1."""
    job = _instalar_jobs[job_id]
    _job_log(job, "Iniciando restore en este equipo (127.0.0.1)...")

    for db, filepath in ficheros.items():
        _job_log(job, f"► Restaurando BD '{db}' desde {os.path.basename(filepath)}...")

        # Conectar a postgres (BD de mantenimiento) para gestionar la BD destino
        existe = False   # default: tratar como nueva si falla la comprobación
        c = None
        try:
            c = psycopg2.connect(
                host="127.0.0.1", port=5432, dbname="postgres",
                user="postgres", password=password, connect_timeout=5,
            )
            c.autocommit = True
            cur = c.cursor()

            # Comprobar si la BD existe
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db,))
            existe = cur.fetchone() is not None

            if not existe:
                _job_log(job, f"  BD '{db}' no existe — creando...")
                cur.execute(f'CREATE DATABASE "{db}" ENCODING \'UTF8\'')
                _job_log(job, f"  BD '{db}' creada correctamente")
            else:
                # Terminar conexiones activas antes de limpiar
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname=%s AND pid<>pg_backend_pid()", (db,)
                )
                n = cur.rowcount
                if n > 0:
                    _job_log(job, f"  Conexiones activas cerradas: {n}")
        except Exception as e:
            _job_log(job, f"  Aviso al preparar BD: {str(e).split(chr(10))[0]}")
        finally:
            if c:
                try: c.close()
                except Exception: pass

        # pg_restore: si la BD es nueva no usamos --clean; si ya existía sí
        cmd = [
            pg_restore, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres",
            "-d", db, "-v", filepath,
        ]
        if existe:
            cmd += ["--clean", "--if-exists"]
        rc = _run_pg_cmd(job, cmd, password)

        if rc != 0:
            _job_log(job, f"✗ pg_restore falló en '{db}' (código {rc})")
            job["error"]  = f"pg_restore falló en BD '{db}' (código {rc})"
            job["status"] = "error"
            job["done"]   = True
            return

        _job_log(job, f"✓ BD '{db}' restaurada correctamente")

    _job_log(job, "✓ Restore completado.")
    job["status"] = "ok"
    job["done"]   = True


@app.route("/api/instalar/verificar-pg", methods=["POST"])
@csrf
@need_conn
def api_instalar_verificar_pg():
    """Verifica que pg_dump.exe existe y que hay conexión al host origen.

    Convertido a POST en v5.12 para no exponer la contrasena en query string
    (los GET con password aparecen en access logs, historial del navegador y
    en cualquier proxy intermedio).
    """
    data     = request.json or {}
    ip_raw   = data.get("ip", "")
    password = data.get("password", "")
    try:
        ip = val_host(ip_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    pg_dump = _find_pg_bin("pg_dump")
    if not pg_dump:
        return jsonify({
            "ok":    False,
            "error": "pg_dump.exe no encontrado. "
                     "¿PostgreSQL 9.5 instalado en este equipo (TPV2)?",
        })

    if sess.get("demo"):
        return jsonify({"ok": True, "pg_dump": pg_dump, "demo": True})

    c = None
    try:
        c = psycopg2.connect(
            host=ip, port=5432, dbname="postgres",
            user="postgres", password=password, connect_timeout=6,
        )
    except Exception as e:
        # No incluir el detalle psycopg2 al cliente — el log local guarda
        # el motivo real para el tecnico.
        msg = str(e).split("\n")[0]
        log(f"WARN verificar-pg origen={ip}: {msg}", "warn")
        return jsonify({
            "ok":     False,
            "error":  "No se pudo conectar al host origen. Revise IP/contrasena de postgres.",
            "pg_dump": pg_dump,
        })
    finally:
        if c:
            try: c.close()
            except Exception: pass

    log(f"Verificacion instalacion OK: pg_dump={pg_dump}, origen={ip}", "ok")
    return jsonify({"ok": True, "pg_dump": pg_dump})


@app.route("/api/instalar/iniciar-backup", methods=["POST"])
@csrf
@need_conn
def api_instalar_iniciar_backup():
    """Lanza el backup de TPV1 en un hilo. Devuelve job_id para polling."""
    data     = request.json or {}
    ip_raw   = data.get("ip_origen", "")
    password = data.get("password", "")
    try:
        ip = val_host(ip_raw)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    pg_dump = _find_pg_bin("pg_dump")
    if not pg_dump:
        return jsonify({"ok": False, "error": "pg_dump.exe no encontrado"}), 400

    job_id = secrets.token_hex(8)
    _instalar_jobs[job_id] = {
        "type": "backup", "status": "running",
        "logs": [], "ficheros": {}, "error": None, "done": False,
    }
    threading.Thread(
        target=_job_backup,
        args=(job_id, pg_dump, ip, password),
        daemon=True,
    ).start()

    log(f"Backup iniciado → {ip} (job {job_id})", "info")
    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/instalar/iniciar-restore", methods=["POST"])
@csrf
@need_conn
def api_instalar_iniciar_restore():
    """Lanza el restore sobre 127.0.0.1 usando los ficheros del backup."""
    data          = request.json or {}
    password      = data.get("password", "")
    job_backup_id = data.get("job_backup_id", "")

    backup_job = _instalar_jobs.get(job_backup_id, {})
    if backup_job.get("status") != "ok" or not backup_job.get("ficheros"):
        return jsonify({"ok": False, "error": "Backup no disponible o con errores"}), 400

    pg_restore = _find_pg_bin("pg_restore")
    if not pg_restore:
        return jsonify({"ok": False, "error": "pg_restore.exe no encontrado"}), 400

    job_id = secrets.token_hex(8)
    _instalar_jobs[job_id] = {
        "type": "restore", "status": "running",
        "logs": [], "ficheros": {}, "error": None, "done": False,
    }
    threading.Thread(
        target=_job_restore,
        args=(job_id, pg_restore, password, backup_job["ficheros"]),
        daemon=True,
    ).start()

    log(f"Restore iniciado (job {job_id})", "info")
    return jsonify({"ok": True, "job_id": job_id})


@app.route("/api/instalar/progreso/<job_id>")
@need_conn
def api_instalar_progreso(job_id):
    """Devuelve estado + logs de un job de backup o restore."""
    job = _instalar_jobs.get(job_id)
    if not job:
        return jsonify({"ok": False, "error": "Job no encontrado"}), 404
    return jsonify({
        "ok":      True,
        "status":  job["status"],
        "logs":    job["logs"],
        "done":    job["done"],
        "ficheros": {db: os.path.basename(p)
                     for db, p in job.get("ficheros", {}).items()},
        "error":   job.get("error") or "",
        # steps: dict {numero_paso: 'running'|'done'|'error'|'skipped'} — solo
        # poblado en jobs con plan paso a paso (reintegrar). El frontend lo lee
        # para ir tachando los pasos del plan en vivo.
        "steps":   job.get("steps", {}),
    })


@app.route("/api/instalar/crear-series", methods=["POST"])
@csrf
@need_conn
def api_instalar_crear_series():
    """Crea las 14 series del nuevo puesto en TPV1 (propio=FALSE) y en este equipo
    (propio=TRUE). En el equipo nuevo reapunta ademas regla_facturacion a sus
    series propias."""
    data        = request.get_json() or {}
    password    = data.get("password", "")
    ip_origen   = data.get("ip_origen", "10.0.0.101")
    num_puesto  = str(data.get("num_puesto",  "2")).strip()
    id_estacion = str(data.get("id_estacion", "2")).strip()

    if not num_puesto.isdigit() or not (1 <= int(num_puesto) <= 9):
        return jsonify({"ok": False, "logs": [],
                        "errores": ["Número de puesto inválido (debe ser 1-9)"]}), 400
    if not id_estacion.isdigit() or not (1 <= int(id_estacion) <= 9):
        return jsonify({"ok": False, "logs": [],
                        "errores": ["ID estación inválido (debe ser 1-9)"]}), 400

    logs    = []
    errores = []
    p = num_puesto   # var_serieTpv   — digit-only, safe to embed
    e = id_estacion  # var_idestacion — digit-only, safe to embed
    patron = f"%0{e}{p}"

    def _sql_series(propio_bool):
        propio_sql  = "TRUE" if propio_bool else "FALSE"
        return f"""
DO $$
<<bloque_series>>
DECLARE
  var_propio     BOOLEAN := {propio_sql};
  var_serieTpv   text    := '{p}';
  var_idestacion text    := '{e}';
BEGIN
  INSERT INTO serie (serie, factura, numero, credito, rectificativa, comision,
      numero_impresiones_automaticas, descripcion,
      update_date, update_user, contado, desglosa_impuesto,
      reinicio_numeracion_cambio_ejercicio, id_serie_report, numero_inicial,
      no_venta, propia, firma_digital, sistema_venta_externo, envio_fiscal) VALUES
  ('B0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,FALSE,FALSE,1,'Factura Simplificada TPV'||var_serieTpv,'2018-01-30 08:40:47.091','TPV '||var_serieTpv,FALSE,TRUE, TRUE,1,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('L0'||var_idestacion||var_serieTpv,TRUE ,1,FALSE,FALSE,FALSE,1,'Factura TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,TRUE, TRUE,4,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('N0'||var_idestacion||var_serieTpv,TRUE ,1,FALSE,FALSE,TRUE ,1,'Factura Comisionista TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,TRUE, TRUE,4,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('C0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,TRUE ,FALSE,1,'Rectificativa Factura Simplificada TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,TRUE, TRUE,1,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('M0'||var_idestacion||var_serieTpv,TRUE ,1,FALSE,TRUE ,FALSE,1,'Factura Rectificativa TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,TRUE, TRUE,4,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('O0'||var_idestacion||var_serieTpv,TRUE ,1,FALSE,TRUE ,TRUE ,1,'Rectificativa factura Comisionista TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,TRUE, TRUE,4,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('D0'||var_idestacion||var_serieTpv,FALSE,1,TRUE ,FALSE,FALSE,1,'Albarán crédito TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,5,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('E0'||var_idestacion||var_serieTpv,FALSE,1,TRUE ,TRUE ,FALSE,1,'Rectificativa albarán crédito TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,5,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('F0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,FALSE,FALSE,1,'Albarán contado TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,TRUE ,FALSE,TRUE,3,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('G0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,TRUE ,FALSE,1,'Rectificativa albarán contado TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,TRUE ,FALSE,TRUE,3,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('H0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,FALSE,TRUE ,1,'Venta por cuenta de terceros TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,2,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('I0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,TRUE ,TRUE ,1,'Rectificativa Venta por cuenta de terceros TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,2,1,FALSE,var_propio,FALSE,FALSE,FALSE),
  ('J0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,FALSE,FALSE,1,'No Venta TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,2,1,TRUE ,var_propio,FALSE,FALSE,FALSE),
  ('K0'||var_idestacion||var_serieTpv,FALSE,1,FALSE,TRUE ,FALSE,1,'No Venta Rectificativa TPV'||var_serieTpv,'2018-01-30 08:41:02.319','TPV '||var_serieTpv,FALSE,FALSE,TRUE,2,1,TRUE ,var_propio,FALSE,FALSE,FALSE);

  UPDATE serie
  SET    id_serie_externo = id_serie::text
  WHERE  id_serie_externo IS NULL;
END bloque_series $$;
"""

    def _reapuntar_reglas(host, cur):
        """En el TPV nuevo, reapunta cada fila de regla_facturacion a la serie
        propia equivalente del propio TPV (propia=TRUE). Solo cambia id_serie,
        no toca la estructura (Firme 1 fila / Comisionista 2 filas)."""
        logs.append(f"[{host}] Reapuntando regla_facturacion a las series propias del TPV...")
        cur.execute("SELECT id_serie, serie FROM serie "
                    "WHERE factura=TRUE AND rectificativa=FALSE "
                    "AND comision=FALSE AND propia=TRUE")
        tienda = cur.fetchall()
        cur.execute("SELECT id_serie, serie FROM serie "
                    "WHERE factura=TRUE AND rectificativa=FALSE "
                    "AND comision=TRUE AND propia=TRUE")
        comis = cur.fetchall()

        # Fila(s) tienda → serie 'Factura' propia
        if len(tienda) == 1:
            cur.execute("UPDATE regla_facturacion SET id_serie=%s WHERE tienda=TRUE",
                        (tienda[0][0],))
            logs.append(f"[{host}] regla_facturacion tienda → serie {tienda[0][1]} "
                        f"({cur.rowcount} fila/s)")
        elif len(tienda) == 0:
            logs.append(f"[{host}] ⚠ Sin serie tienda propia — regla tienda sin reapuntar.")
        else:
            logs.append(f"[{host}] ⚠ {len(tienda)} series tienda propias — "
                        f"regla tienda sin reapuntar (ambiguo).")

        # Fila carburante → serie comisionista propia (solo si la estacion es comisionista)
        cur.execute("SELECT COUNT(*) FROM regla_facturacion "
                    "WHERE tienda=FALSE AND carburante=TRUE")
        if cur.fetchone()[0] > 0:
            if len(comis) == 1:
                cur.execute("UPDATE regla_facturacion SET id_serie=%s "
                            "WHERE tienda=FALSE AND carburante=TRUE", (comis[0][0],))
                logs.append(f"[{host}] regla_facturacion carburante → serie {comis[0][1]} "
                            f"({cur.rowcount} fila/s)")
            elif len(comis) == 0:
                logs.append(f"[{host}] ⚠ Sin serie comisionista propia — "
                            f"regla carburante sin reapuntar.")
            else:
                logs.append(f"[{host}] ⚠ {len(comis)} series comisionista propias — "
                            f"regla carburante sin reapuntar (ambiguo).")

    def _ejecutar_en(host, propio_bool):
        etiqueta = f"{host} ({'propio=TRUE' if propio_bool else 'propio=FALSE'})"
        conn = None
        try:
            conn = psycopg2.connect(
                host=host, port=5432, dbname="tpv",
                user="postgres", password=password, connect_timeout=5
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM serie WHERE serie LIKE %s", (patron,))
            ya = cur.fetchone()[0]

            if propio_bool:
                # TPV nuevo: SIEMPRE deja propia correcto, existan o no las series.
                # 1) Todas las series existentes (heredadas del TPV1) → propia=FALSE
                cur.execute("UPDATE serie SET propia = FALSE WHERE propia = TRUE")
                logs.append(f"[{host}] Series existentes → propia=FALSE ({cur.rowcount} fila/s)")
                # 2) Las 14 del puesto: crear (propia=TRUE) o, si ya existen, marcarlas
                if ya:
                    cur.execute("UPDATE serie SET propia = TRUE WHERE serie LIKE %s", (patron,))
                    logs.append(f"[{host}] Las {ya} series del puesto ya existían → "
                                f"propia=TRUE ({cur.rowcount} fila/s)")
                else:
                    logs.append(f"[{host}] Creando 14 series (idEstacion={e}, puesto={p}, propia=TRUE)...")
                    cur.execute(_sql_series(True))
                    cur.execute("SELECT COUNT(*) FROM serie WHERE serie LIKE %s", (patron,))
                    logs.append(f"[{host}] ✓ {cur.fetchone()[0]} series creadas correctamente.")
                # 3) Reapuntar regla_facturacion a las series propias del TPV nuevo
                _reapuntar_reglas(host, cur)
            else:
                # TPV1 principal: crea las 14 del puesto con propia=FALSE si no existen
                if ya:
                    logs.append(f"[{host}] ⚠ Ya existen {ya} serie(s) con sufijo {e}{p} — se omite.")
                else:
                    logs.append(f"[{host}] Creando 14 series (idEstacion={e}, puesto={p}, propia=FALSE)...")
                    cur.execute(_sql_series(False))
                    cur.execute("SELECT COUNT(*) FROM serie WHERE serie LIKE %s", (patron,))
                    logs.append(f"[{host}] ✓ {cur.fetchone()[0]} series creadas correctamente.")

            cur.close()
        except Exception as ex:
            msg = str(ex).split("\n")[0]
            logs.append(f"[{host}] ✗ Error: {msg}")
            errores.append(f"{etiqueta}: {msg}")
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    # TPV1 principal — propio = FALSE
    logs.append(f"── TPV1 principal ({ip_origen}) ──────────────")
    _ejecutar_en(ip_origen, False)

    # Este equipo (TPV2) — propio = TRUE
    logs.append(f"── Este equipo / TPV secundario (127.0.0.1) ──")
    _ejecutar_en("127.0.0.1", True)

    # Estado de regla_facturacion del TPV nuevo (para la tabla editable)
    reglas, series_disp = [], []
    c = None
    try:
        c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="tpv",
                             user="postgres", password=password, connect_timeout=5)
        cur = c.cursor()
        cur.execute("SELECT rf.id_regla_facturacion, rf.tienda, rf.carburante, "
                    "rf.id_serie, s.serie, s.descripcion "
                    "FROM regla_facturacion rf "
                    "LEFT JOIN serie s ON s.id_serie = rf.id_serie "
                    "ORDER BY rf.id_regla_facturacion")
        for idrf, tienda, carb, ids, ser, desc in cur.fetchall():
            tipo = "tienda" if tienda else ("carburante" if carb else "otra")
            reglas.append({"id_regla_facturacion": idrf, "tipo": tipo,
                           "id_serie": ids, "serie": ser, "descripcion": desc})
        cur.execute("SELECT id_serie, serie, descripcion FROM serie "
                    "WHERE propia = TRUE ORDER BY serie")
        series_disp = [{"id_serie": r[0], "serie": r[1], "descripcion": r[2]}
                       for r in cur.fetchall()]
    except Exception as ex:
        logs.append(f"[127.0.0.1] Aviso leyendo regla_facturacion: "
                    f"{str(ex).split(chr(10))[0]}")
    finally:
        if c:
            try: c.close()
            except Exception: pass

    return jsonify({"ok": len(errores) == 0, "logs": logs, "errores": errores,
                    "reglas": reglas, "series_disponibles": series_disp})


@app.route("/api/instalar/guardar-reglas", methods=["POST"])
@csrf
@need_conn
def api_instalar_guardar_reglas():
    """Aplica cambios manuales de id_serie en regla_facturacion del TPV
    nuevo (127.0.0.1)."""
    data     = request.get_json() or {}
    password = data.get("password", "")
    cambios  = data.get("reglas", [])

    logs, errores = [], []
    conn = None
    try:
        conn = psycopg2.connect(host="127.0.0.1", port=5432, dbname="tpv",
                                user="postgres", password=password, connect_timeout=5)
        conn.autocommit = False
        cur = conn.cursor()
        for c in cambios:
            try:
                idrf = int(c.get("id_regla_facturacion"))
                ids  = int(c.get("id_serie"))
            except (TypeError, ValueError):
                continue
            cur.execute("SELECT serie FROM serie WHERE id_serie = %s", (ids,))
            row = cur.fetchone()
            if not row:
                errores.append(f"serie {ids} no existe")
                continue
            cur.execute("UPDATE regla_facturacion SET id_serie = %s "
                        "WHERE id_regla_facturacion = %s", (ids, idrf))
            logs.append(f"regla #{idrf} → serie {row[0]} ({cur.rowcount} fila/s)")
        conn.commit()
    except Exception as ex:
        if conn:
            try: conn.rollback()
            except Exception: pass
        errores.append(str(ex).split("\n")[0])
    finally:
        if conn:
            try: conn.close()
            except Exception: pass

    return jsonify({"ok": len(errores) == 0, "logs": logs, "errores": errores})


@app.route("/api/instalar/secundario", methods=["POST"])
@csrf
@need_conn
def api_instalar_secundario():
    """
    Integra un TPV recien instalado como secundario en la red existente.

    Pasos:
      1. Configura propiedad del nuevo TPV como secundario (UPDATE de 16 claves)
      2. Actualiza controlpista.local_config.ip_server en el nuevo TPV
      3. Sincroniza controlpista.pos en el nuevo TPV para todos los activos
      4. Actualiza CopyDirectories en todos los TPVs existentes accesibles
      5. Asegura fila del nuevo TPV en controlpista.pos de los demas TPVs
      6. Registra el TPV nuevo en la tabla tpv del principal y del propio TPV
         (en cada BD, principal=TRUE solo para su propia fila)
      7. Edita hibernateCentral.cfg.xml en local

    NO toca: sesion_tpv_activo
    """
    data = request.json or {}
    try:
        nueva_ip    = val_host(data.get("nueva_ip", ""))
        ip_principal = val_host(data.get("ip_principal", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    ips_activas_raw = data.get("ips_activas", [])
    ips_activas = []
    for ip in ips_activas_raw:
        try:
            ips_activas.append(val_host(ip))
        except Exception:
            pass
    if nueva_ip not in ips_activas:
        ips_activas.append(nueva_ip)
    if not ips_activas:
        return jsonify({"ok": False, "error": "Sin IPs activas definidas"}), 400

    nombre_nuevo = next(
        (t["nombre"] for t in TPVS_CONOCIDOS if t["ip"] == nueva_ip), nueva_ip
    )

    errores = []
    exitos  = []

    if sess.get("demo"):
        return jsonify({
            "ok": True, "demo": True,
            "exitos": [f"{nueva_ip} (demo)"],
            "errores": [],
            "aviso_hibernate": f"[DEMO] Editar hibernateCentral.cfg.xml en {nueva_ip}",
            "msg": f"[DEMO] {nombre_nuevo} configurado como secundario.",
        })

    # ── 1. Configurar el nuevo TPV como secundario en propiedad ────────────────
    cd_nuevo  = _copy_dirs_secundario(nueva_ip, ips_activas)
    bos_nuevo = f"//{ip_principal}/c/integracion/4GLExport"

    sqls_nuevo = [
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR,      "InputDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_INPUT_DIR_COPY, "InputDirectoryCopy")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (bos_nuevo,        "BackupDirectoriesBOS")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd_nuevo,         "CopyDirectories")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "CopyDirectoriesMaestros")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("",               "BackupDirectoryMaestroMovidosTpvPrincipal")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_ERROR_DIR,      "ErrorDirectory")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_MAESTRO, "BackupDirectoryMaestro")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", (V_BACKUP_TRANS,   "BackupDirectoryTransaccion")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("1",              "activarDemonioCopia")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("1",              "activarDemonioError")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("1",              "activarDemonioIntegracion")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("1",              "procesarMaestros")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("1",              "procesarTransacciones")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("0",              "tiempoCopia")),
        ("UPDATE propiedad SET valor=%s WHERE clave=%s", ("300",            "tiempoError")),
    ]
    r1 = _run(nueva_ip, sqls_nuevo,
              f"[INSTALACION] {nombre_nuevo} propiedad configurada como secundario")
    if r1["ok"]:
        exitos.append(f"{nueva_ip} — propiedad (16 claves)")
    else:
        errores.append(f"{nueva_ip} propiedad: {r1.get('error','?')}")

    # ── 2. Actualizar controlpista del nuevo TPV — ip_server → principal ───────
    r2 = _actualizar_controlpista(nueva_ip, ip_principal)
    if r2["ok"]:
        exitos.append(f"{nueva_ip} — controlpista.ip_server → {ip_principal}")
    else:
        errores.append(f"{nueva_ip} controlpista ip_server: {r2.get('error','?')}")

    # ── 2b. Actualizar pos_version_id_local = 10 + num_puesto ─────────────────
    c_cp = None
    try:
        num_puesto_int = int(data.get("num_puesto", 2))
        if not (1 <= num_puesto_int <= 9):
            raise ValueError("fuera de rango 1-9")
        pos_ver_local = 10 + num_puesto_int
        c_cp = _conn_controlpista(nueva_ip)
        c_cp.autocommit = False
        cur_cp = c_cp.cursor()
        cur_cp.execute("UPDATE local_config SET pos_version_id_local = %s", (pos_ver_local,))
        c_cp.commit()
        exitos.append(f"{nueva_ip} — controlpista.pos_version_id_local → {pos_ver_local}")
    except Exception as ex:
        if c_cp:
            try: c_cp.rollback()
            except Exception: pass
        errores.append(f"{nueva_ip} controlpista pos_version_id_local: {str(ex).split(chr(10))[0]}")
    finally:
        if c_cp:
            try: c_cp.close()
            except Exception: pass

    # ── 3. Sincronizar pos en el nuevo TPV para todos los activos ──────────────
    for ip_pos in ips_activas:
        r_pos = _set_pos_online(nueva_ip, ip_pos, True)
        if not r_pos["ok"] and not r_pos.get("demo"):
            errores.append(f"{nueva_ip} pos/{ip_pos}: {r_pos.get('error','?')}")
    exitos.append(f"{nueva_ip} — pos.online=TRUE para {len(ips_activas)} TPVs")

    # ── 4. Actualizar CopyDirectories en los TPVs existentes ──────────────────
    for ip_otro in ips_activas:
        if ip_otro == nueva_ip:
            continue
        es_principal = (ip_otro == ip_principal)
        nom_otro = next(
            (t["nombre"] for t in TPVS_CONOCIDOS if t["ip"] == ip_otro), ip_otro
        )
        if es_principal:
            cd = _copy_dirs_principal(ip_otro, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectoriesMaestros")),
            ]
        else:
            cd = _copy_dirs_secundario(ip_otro, ips_activas)
            sqls = [
                ("UPDATE propiedad SET valor=%s WHERE clave=%s", (cd, "CopyDirectories")),
            ]
        r4 = _run(ip_otro, sqls,
                  f"[INSTALACION] {nom_otro} CopyDirectories actualizado con {nueva_ip}")
        if r4["ok"]:
            exitos.append(f"{ip_otro} — CopyDirectories actualizado")
        else:
            errores.append(f"{ip_otro} CopyDirectories: {r4.get('error','?')}")

        # ── 5. Asegurar fila del nuevo TPV en pos de cada TPV existente ─────
        r_pos2 = _set_pos_online(ip_otro, nueva_ip, True)
        if r_pos2["ok"]:
            pass  # UPDATE ok
        else:
            # UPDATE afecto 0 filas — intentar INSERT
            c_ins = None
            try:
                c_ins = _conn_controlpista(ip_otro)
                c_ins.autocommit = False
                cur_ins = c_ins.cursor()
                pref = _ip_a_id_tpv(nueva_ip)
                cur_ins.execute(
                    "INSERT INTO pos (ip, preference, online) VALUES (%s, %s, TRUE) "
                    "ON CONFLICT (ip) DO UPDATE SET online=TRUE",
                    (nueva_ip, pref)
                )
                c_ins.commit()
                log(f"pos INSERT {nueva_ip} en {ip_otro}", "ok")
            except Exception as e_ins:
                if c_ins:
                    try: c_ins.rollback()
                    except Exception: pass
                errores.append(
                    f"{ip_otro} pos INSERT {nueva_ip}: "
                    f"{str(e_ins).split(chr(10))[0]}"
                )
            finally:
                if c_ins:
                    try: c_ins.close()
                    except Exception: pass

    # ── 6. Registrar el TPV nuevo en la tabla tpv (en cada BD su propio principal) ─
    num_puesto_int = int(data.get("num_puesto", 2))
    id_tpv_ext     = (str(data.get("id_tpv_externo") or "")).strip() or None

    def _registrar_tpv_en(host, es_propio):
        """Asegura la fila del TPV nuevo en la tabla tpv de `host`.
        es_propio=True  (BD del propio TPV nuevo): su fila principal=TRUE, resto FALSE.
        es_propio=False (BD del principal):        su fila principal=FALSE, no toca el resto."""
        conn = None
        try:
            conn = conn_tpv(host)
            conn.autocommit = False
            cur = conn.cursor()
            if es_propio:
                cur.execute("UPDATE tpv SET principal = FALSE")
            cur.execute("SELECT 1 FROM tpv WHERE id_tpv = %s", (num_puesto_int,))
            if cur.fetchone() is not None:
                cur.execute("UPDATE tpv SET principal = %s WHERE id_tpv = %s",
                            (es_propio, num_puesto_int))
                accion = "ya registrado"
            else:
                cur.execute(
                    "INSERT INTO tpv (id_tpv, nombre, lector_codigo_barras, teclado_auxiliar, "
                    "impresora_ticket, impresora_facturas, visor_cliente, trabaja_offline, "
                    "id_tpv_externo, update_date, update_user, principal) "
                    "SELECT %s, %s, lector_codigo_barras, teclado_auxiliar, impresora_ticket, "
                    "impresora_facturas, visor_cliente, trabaja_offline, %s, NOW(), %s, %s "
                    "FROM tpv ORDER BY id_tpv LIMIT 1",
                    (num_puesto_int, f"TPV {num_puesto_int}", id_tpv_ext,
                     f"TPV {num_puesto_int}", es_propio))
                if not cur.rowcount:
                    raise Exception("tabla tpv vacía — sin fila de TPV1 para copiar")
                accion = "registrado"
            conn.commit()
            exitos.append(f"{host} — tabla tpv: TPV {num_puesto_int} {accion} "
                          f"(principal={'TRUE' if es_propio else 'FALSE'})")
        except Exception as ex:
            if conn:
                try: conn.rollback()
                except Exception: pass
            errores.append(f"{host} tabla tpv: {str(ex).split(chr(10))[0]}")
        finally:
            if conn:
                try: conn.close()
                except Exception: pass

    _registrar_tpv_en(ip_principal, False)   # BD del principal: TPV nuevo → principal=FALSE
    _registrar_tpv_en(nueva_ip,     True)    # BD del TPV nuevo: su fila → principal=TRUE, resto FALSE

    # ── 7. Editar hibernateCentral.cfg.xml en local ────────────────────────────
    # Si la regex falla y produce XML invalido, GARUM no arranca = visita
    # fisica al TPV. Por eso copiamos a .bak ANTES de escribir y validamos
    # que el resultado sigue siendo un XML balanceado (al menos tiene < y >).
    import shutil
    _HIB_PATH = r"C:\GARUM\hibernateCentral.cfg.xml"
    _HIB_BAK  = _HIB_PATH + ".bak"
    aviso_hib = None
    try:
        # Intentar utf-8; fallback a cp1252 si el fichero legacy usa esa codificacion.
        _xml = None
        for _enc in ("utf-8", "cp1252"):
            try:
                with open(_HIB_PATH, "r", encoding=_enc) as _f:
                    _xml = _f.read()
                _xml_enc = _enc
                break
            except UnicodeDecodeError:
                continue
        if _xml is None:
            raise UnicodeDecodeError("hibernate", b"", 0, 1, "no se pudo leer ni en utf-8 ni cp1252")

        # Reemplazo seguro con funcion lambda: ip_principal puede contener
        # caracteres que re.sub interpretaria en el replacement string (\1, \g<>).
        _xml_nuevo = re.sub(
            r'(<property name="hibernate\.connection\.url">jdbc:postgresql://)[^<]+(</property>)',
            lambda m: m.group(1) + ip_principal + ":5432/tpv" + m.group(2),
            _xml
        )
        if _xml_nuevo == _xml:
            exitos.append(f"hibernateCentral.cfg.xml — URL ya apuntaba a {ip_principal}, sin cambios")
        else:
            # Validacion minima: el XML resultante debe seguir teniendo el
            # tag property que acabamos de modificar, y conservar tamano similar.
            if "hibernate.connection.url" not in _xml_nuevo \
               or abs(len(_xml_nuevo) - len(_xml)) > 200:
                raise ValueError("Resultado XML invalido tras sustitucion (sanity check)")
            # Backup antes de sobrescribir.
            try:
                shutil.copy2(_HIB_PATH, _HIB_BAK)
            except Exception as _ex_bak:
                log(f"WARN no se pudo crear backup hibernate: {_ex_bak}", "warn")
            # Escritura atomica: tmp + replace.
            _tmp = _HIB_PATH + ".tmp"
            with open(_tmp, "w", encoding=_xml_enc) as _f:
                _f.write(_xml_nuevo)
            os.replace(_tmp, _HIB_PATH)
            exitos.append(f"hibernateCentral.cfg.xml — URL actualizada → {ip_principal}:5432/tpv (backup: {_HIB_BAK})")
    except FileNotFoundError:
        errores.append(f"hibernateCentral.cfg.xml no encontrado en {_HIB_PATH}")
        aviso_hib = (
            f"ATENCION: No se encontro {_HIB_PATH}\n"
            f"Editar manualmente y poner:\n"
            f"  jdbc:postgresql://{ip_principal}:5432/tpv\n"
            f"Reiniciar GARUM tras editar."
        )
    except Exception as ex:
        errores.append(f"hibernateCentral.cfg.xml: {str(ex).split(chr(10))[0]}")

    log(
        f"INSTALACION {nombre_nuevo} ({nueva_ip}) como secundario "
        f"→ principal {ip_principal}. "
        f"Exitos: {len(exitos)}, Errores: {len(errores)}",
        "ok" if not errores else "warn"
    )

    return jsonify({
        "ok":              len(errores) == 0,
        "exitos":          exitos,
        "errores":         errores,
        "aviso_hibernate": aviso_hib,
        "msg": (
            f"{nombre_nuevo} integrado como secundario. "
            f"{len(exitos)} operaciones completadas."
            + (" Con errores — ver detalle." if errores else "")
        ),
    })


def _demo(host):
    base = {
        "InputDirectory": V_INPUT_DIR, "InputDirectoryCopy": V_INPUT_DIR_COPY,
        "ErrorDirectory": V_ERROR_DIR, "BackupDirectoryMaestro": V_BACKUP_MAESTRO,
        "BackupDirectoryTransaccion": V_BACKUP_TRANS,
        "activarDemonioCopia": "1", "activarDemonioError": "0",
        "activarDemonioIntegracion": "1", "procesarMaestros": "1",
        "procesarTransacciones": "1", "tiempoCopia": "0", "tiempoError": "300",
    }
    if host == "10.0.0.101":
        cd = _copy_dirs_principal(host, IPS_CONOCIDAS)
        base.update({"BackupDirectoriesBOS": V_BOS_PRINCIPAL,
                     "CopyDirectories": cd, "CopyDirectoriesMaestros": cd,
                     "BackupDirectoryMaestroMovidosTpvPrincipal": V_MAESTROS_PRINC})
    else:
        cd = _copy_dirs_secundario(host, IPS_CONOCIDAS)
        base.update({"BackupDirectoriesBOS": "//10.0.0.101/c/integracion/4GLExport",
                     "CopyDirectories": cd, "CopyDirectoriesMaestros": "",
                     "BackupDirectoryMaestroMovidosTpvPrincipal": ""})
    return base


# =============================================================================
# REINTEGRAR TPV (v7.x)
# =============================================================================
# Modulo paralelo a "Nuevo TPV" pero SIN wizard ni preguntas.
# Caso: el TPV ya estaba funcionando, se ha corrompido/reinstalado/cambiado
# de equipo, y solo queremos clonar la BD del TPV1 encima + ajustar:
#   - serie.propia: TRUE solo en las series del propio TPV (X = num_puesto)
#   - regla_facturacion: tienda y carburante apuntando a series propias
#   - tpv.principal: TRUE solo en el id_tpv del propio TPV
#   - controlpista.local_config.pos_version_id_local = 10 + num_puesto
#   - C:\GARUM\hibernateCentral.cfg.xml: URL apuntando al principal
#
# NO crea series, NO inserta filas en `tpv` ni `pos`, NO toca CopyDirectories.
# El nº de TPV se detecta de la IP local del PC (10.0.0.10X -> X-100).
# =============================================================================

_REINT_IP_PRINCIPAL = "10.0.0.101"   # convencion GARUM: TPV1 = principal habitual


def _detectar_num_tpv_local():
    """Detecta el numero de TPV (1-9) mirando la IP local del PC.
    Si el equipo tiene una IP en 10.0.0.101..10.0.0.109, devuelve 1..9.
    Si no, devuelve None. No hace red — solo consulta interfaces locales."""
    import socket
    ips_locales = set()
    try:
        # Metodo 1: gethostbyname_ex (a veces devuelve todas las IPs)
        try:
            _h, _a, ips = socket.gethostbyname_ex(socket.gethostname())
            for ip in ips:
                ips_locales.add(ip)
        except Exception:
            pass
        # Metodo 2: getaddrinfo (mas fiable en Windows)
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None):
                ip = info[4][0]
                if ip and "." in ip:
                    ips_locales.add(ip)
        except Exception:
            pass
    except Exception:
        return None

    # Orden determinista (sorted) por si el equipo tiene varias IPs en 10.0.0.10X
    # (raro pero posible con dual NIC). Sin sorted el orden del set es no-determinista.
    for ip in sorted(ips_locales):
        # Patron 10.0.0.10X con X en 1-9
        partes = ip.split(".")
        if len(partes) == 4 and partes[0]=="10" and partes[1]=="0" and partes[2]=="0":
            try:
                ult = int(partes[3])
                if 101 <= ult <= 109:
                    return ult - 100
            except ValueError:
                continue
    return None


def _detectar_ip_local():
    """Devuelve la IP local 10.0.0.10X si la encuentra, o cadena vacia."""
    import socket
    ips = set()
    try:
        _h, _a, lst = socket.gethostbyname_ex(socket.gethostname())
        ips.update(lst)
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ips.add(info[4][0])
    except Exception:
        pass
    for ip in sorted(ips):  # orden determinista por si hay dual NIC
        partes = ip.split(".")
        if len(partes)==4 and partes[0]=="10" and partes[1]=="0" and partes[2]=="0":
            try:
                ult = int(partes[3])
                if 101 <= ult <= 109:
                    return ip
            except ValueError:
                pass
    return ""


def _detectar_principal_red(num_tpv_local=None, password=None):
    """Escanea la red GARUM (10.0.0.101..10.0.0.109) buscando el TPV vivo que
    EJERCE como principal/master. Util para Reintegrar cuando el TPV1 cayo y
    otro TPV ha tomado el rol: en ese caso clonamos desde ese otro, no desde
    10.0.0.101.

    IMPORTANTE — convencion GARUM (line 6027 de este archivo):
      "En cada BD, principal=TRUE solo para su propia fila"
    Es decir, `tpv.principal=TRUE` en cada BD identifica al PROPIO TPV (su
    autoidentificacion), NO al master de la red. Por eso NO sirve para
    saber quien es el master vivo: cada TPV reportaria a si mismo.

    Lo que SI sirve (ver probar_tpv() linea 994): el campo `BackupDirectoriesBOS`
    de la tabla `propiedad`. Si NO empieza por '//' (comentado) → ese TPV
    es PRINCIPAL real. Los secundarios tienen `//...` (BOS comentado).

    Devuelve: dict {ip, num_tpv, ok:bool, motivo:str}.
      - ok=True con ip/num_tpv si encontramos al principal vivo
      - ok=False con motivo explicativo si nadie responde como principal

    Conexion en paralelo (ThreadPoolExecutor) con timeout 2s.

    Args:
      num_tpv_local: si se indica, excluimos esa IP del escaneo (el local
        no puede ser el origen — si estamos en TPV2 reintegrando, no vale
        clonar de TPV2 a TPV2).
      password: pwd de postgres. Si es None usa sess['password'].
    """
    pwd = password if password is not None else sess.get("password", "")
    if not pwd:
        return {"ok": False, "motivo": "Sin pwd en sesion para escanear"}

    candidatos = []
    for n in range(1, 10):
        if num_tpv_local is not None and n == num_tpv_local:
            continue   # nos saltamos a nosotros mismos
        candidatos.append((n, f"10.0.0.10{n}"))

    def _probar(n_ip):
        """Devuelve (num_tpv_local_segun_su_BD, ip) si responde como principal,
        None si no. La n_ip que pasamos por defecto se usa solo si no podemos
        leer el id_tpv de su propia BD (caso defensivo)."""
        n, ip = n_ip
        c = None
        try:
            c = psycopg2.connect(host=ip, port=5432, dbname="tpv",
                                  user="postgres", password=pwd,
                                  connect_timeout=2)
            cur = c.cursor()
            # 1) ¿Es este TPV principal? Lo decide BackupDirectoriesBOS.
            #    Si esta vacio o empieza por '//' → es secundario, NO master.
            cur.execute("SELECT valor FROM propiedad "
                        "WHERE clave = 'BackupDirectoriesBOS' LIMIT 1")
            row = cur.fetchone()
            bos = (row[0] if row else "") or ""
            es_principal = bool(bos.strip()) and not bos.strip().startswith("//")
            if not es_principal:
                return None
            # 2) Es principal — leemos su id_tpv local (principal=TRUE en su
            #    BD identifica su propia fila, asi que aqui SI vale).
            cur.execute("SELECT id_tpv FROM tpv WHERE principal = TRUE LIMIT 1")
            row2 = cur.fetchone()
            id_tpv = int(row2[0]) if row2 else n
            return (id_tpv, ip)
        except Exception:
            return None
        finally:
            if c:
                try: c.close()
                except Exception: pass

    encontrados = []
    with ThreadPoolExecutor(max_workers=min(9, len(candidatos))) as ex:
        futuros = {ex.submit(_probar, c): c for c in candidatos}
        for fut in as_completed(futuros):
            res = fut.result()
            if res:
                encontrados.append(res)

    if not encontrados:
        return {"ok": False, "motivo": (
            "Ningun TPV vivo en la red tiene BackupDirectoriesBOS activo "
            "(todos son secundarios o no responden)")}
    # Si por mala configuracion de red hay varios "principales", preferimos
    # el de menor id_tpv (mas estable y previsible).
    encontrados.sort(key=lambda r: r[0])
    id_tpv, ip = encontrados[0]
    return {"ok": True, "ip": ip, "num_tpv": id_tpv,
            "motivo": f"TPV {id_tpv} ({ip}) es el principal vivo (BOS activo)"}


@app.route("/api/reintegrar/info")
@need_conn
def api_reintegrar_info():
    """Pre-vuelo del modulo Reintegrar: devuelve qué TPV se va a reintegrar
    detectándolo automáticamente de la IP local del PC + buscando cuál es
    el principal vivo en la red (puede no ser el TPV1 si éste cayó)."""
    num_tpv = _detectar_num_tpv_local()
    ip_local = _detectar_ip_local()
    # Escanea la red para localizar el principal real (puede no ser TPV1).
    # Si falla la deteccion (red caida, otros TPVs apagados, etc.) caemos a
    # _REINT_IP_PRINCIPAL como antes. Coste: ~2s en LAN tipica.
    principal = _detectar_principal_red(num_tpv_local=num_tpv)
    ip_principal_red = principal["ip"]    if principal.get("ok") else _REINT_IP_PRINCIPAL
    num_principal_red = principal["num_tpv"] if principal.get("ok") else 1
    principal_motivo  = principal.get("motivo", "")
    # Caso A: IP local fuera del rango GARUM — auto-detect falla.
    # Devolvemos defaults sugeridos para que el frontend pre-rellene los inputs
    # manuales (num_tpv=2, ip_origen=<principal detectado o 10.0.0.101>).
    if num_tpv is None:
        return jsonify({
            "ok": True,
            "listo": False,
            "motivo": ("No se ha detectado una IP local en el rango 10.0.0.101..10.0.0.109. "
                       "Configura el destino manualmente abajo."),
            "ip_local": ip_local or "(desconocida)",
            "num_tpv": None,
            "num_tpv_sugerido": 2,
            "ip_origen_sugerida": ip_principal_red,
            "principal_detectado": principal,
        })
    # Caso B: TPV1 detectado. Este modulo no aplica directamente si TPV1 SIGUE
    # siendo el principal vivo (TPV1 seria la fuente, no destino). Pero si TPV1
    # esta caido y otro TPV es principal, entonces tiene sentido reintegrar el
    # TPV1 desde ese otro — caso real al recuperar tras una caida del 1.
    if num_tpv == 1:
        # Si el principal detectado NO es el 1, tiene sentido reintegrar.
        if principal.get("ok") and num_principal_red != 1:
            return jsonify({
                "ok": True,
                "listo": True,
                "num_tpv": 1,
                "ip_local": ip_local,
                "ip_principal": ip_principal_red,
                "ip_origen": ip_principal_red,
                "es_tpv1": True,
                "principal_caido": True,
                "motivo": (f"TPV1 detectado pero el principal vivo es TPV {num_principal_red} "
                           f"({ip_principal_red}). Reintegrando TPV1 desde ese."),
                "num_tpv_sugerido": 1,
                "ip_origen_sugerida": ip_principal_red,
                "principal_detectado": principal,
            })
        # Caso original: TPV1 vivo y principal — no aplica reintegrar.
        return jsonify({
            "ok": True,
            "listo": False,
            "es_tpv1": True,
            "num_tpv": 1,
            "ip_local": ip_local,
            "motivo": "Detectado TPV1 — fuente habitual del clonado. Si vas a reinstalar TPV1 mantén el 1; en caso normal indica el nº destino 2..9.",
            "num_tpv_sugerido": 2,
            "ip_origen_sugerida": ip_local or ip_principal_red,
            "principal_detectado": principal,
        })
    # Caso C: TPV 2..9 detectado, listo para reintegrar.
    # ip_origen viene del escaneo de red — puede ser el TPV1 (caso normal) o
    # cualquier otro TPV vivo que haya tomado el rol de principal.
    ip_principal = ip_principal_red
    ip_origen = ip_principal_red
    return jsonify({
        "ok": True,
        "listo": True,
        "num_tpv": num_tpv,
        "ip_local": ip_local,
        "ip_principal": ip_principal,
        "ip_origen": ip_origen,
        "es_tpv1": False,
        # Mismos valores como "sugeridos" para que el frontend solo lea una clave.
        "num_tpv_sugerido": num_tpv,
        "ip_origen_sugerida": ip_origen,
        "principal_detectado": principal,
    })


def _job_reintegrar(job_id, password, num_tpv, ip_origen, ip_principal,
                    editar_hibernate=True, ip_local=None, copiar_garum=True):
    """Hilo que ejecuta el flujo completo de reintegracion:
    1. pg_dump del TPV1 (BDs tpv y controlpista)
    2. pg_restore en 127.0.0.1
    3. Ajustes post-restore: serie.propia, regla_facturacion, tpv.principal,
       controlpista.local_config.ip + pos_version_id_local
    4. (Opcional) Copia recursiva de C:\\GARUM del principal a este equipo
       via \\\\IP\\C$\\GARUM con robocopy. Si copiar_garum=False, se omite.
    5. (Opcional) Edicion de C:\\GARUM\\hibernateCentral.cfg.xml apuntando al
       principal. Si editar_hibernate=False, se omite (manual).
    ip_local: la IP local de este TPV (default 10.0.0.10{num_tpv}). Se escribe
              en controlpista.local_config.ip para que el TPV se identifique
              correctamente en la red (no queda como la del TPV1 tras el restore).
    """
    if ip_local is None:
        ip_local = f"10.0.0.10{num_tpv}"
    job = _instalar_jobs[job_id]

    # Inicializa los 7 pasos del plan como "pending" (no aparecen aun marcados).
    # El frontend lee job["steps"] cada poll y va tachando.
    for _n in range(1, 8):
        _job_step(job, _n, "pending")

    # ── 1. BACKUP TPV1 ────────────────────────────────────────────
    _job_step(job, 1, "running")
    pg_dump = _find_pg_bin("pg_dump")
    if not pg_dump:
        _job_log(job, "✗ ERROR: no se encuentra pg_dump.exe en este equipo.")
        _job_step(job, 1, "error")
        job["error"] = "pg_dump no encontrado"
        job["status"] = "error"; job["done"] = True
        return
    pg_restore = _find_pg_bin("pg_restore")
    if not pg_restore:
        _job_log(job, "✗ ERROR: no se encuentra pg_restore.exe en este equipo.")
        # pg_restore corresponde conceptualmente al paso 2 del plan, no al 1.
        _job_step(job, 2, "error")
        job["error"] = "pg_restore no encontrado"
        job["status"] = "error"; job["done"] = True
        return

    _job_log(job, f"═══ FASE 1/4: Backup BD del TPV1 ({ip_origen}) ═══")
    os.makedirs(_BACKUP_DIR, exist_ok=True)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    ficheros = {}
    for db in _INST_DBS:
        filename = f"{db}_{ts_str}.backup"
        filepath = os.path.join(_BACKUP_DIR, filename)
        _job_log(job, f"► pg_dump '{db}' -> {filename}")
        cmd = [pg_dump, "-h", ip_origen, "-p", "5432", "-U", "postgres",
               "-d", db, "-F", "c", "-v", "-f", filepath]
        rc = _run_pg_cmd(job, cmd, password)
        if rc != 0:
            _job_log(job, f"✗ pg_dump fallo en '{db}' (codigo {rc})")
            _job_step(job, 1, "error")
            job["error"] = f"pg_dump fallo en '{db}'"
            job["status"] = "error"; job["done"] = True
            return
        size_mb = os.path.getsize(filepath) / (1024*1024) if os.path.exists(filepath) else 0
        _job_log(job, f"✓ '{db}' OK ({size_mb:.1f} MB)")
        ficheros[db] = filepath
        job["ficheros"][db] = filepath
    _job_step(job, 1, "done")

    # ── 2. RESTORE LOCAL ──────────────────────────────────────────
    _job_log(job, "")
    _job_step(job, 2, "running")
    _job_log(job, "═══ FASE 2/4: Restore en este equipo (127.0.0.1) ═══")
    for db, filepath in ficheros.items():
        _job_log(job, f"► pg_restore '{db}' desde {os.path.basename(filepath)}")
        # Estrategia: si la BD ya existe la BORRAMOS y la RECREAMOS limpia. Asi
        # pg_restore corre sobre BD vacia y no necesita --clean/--if-exists (que
        # en algunas versiones de pg_restore daban "demasiados argumentos" segun
        # el orden en que se pasaban los flags vs. el filename). Esto es mas
        # robusto y coincide con el caso de uso de Reintegrar: machacar la BD
        # local con el contenido de TPV1.
        c = None
        try:
            c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="postgres",
                                 user="postgres", password=password, connect_timeout=5)
            c.autocommit = True
            cur = c.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db,))
            existe = cur.fetchone() is not None
            if existe:
                # Terminamos sesiones activas (si quedaba GARUM abierto, etc.)
                cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                            "WHERE datname=%s AND pid<>pg_backend_pid()", (db,))
                n = cur.rowcount
                if n > 0:
                    _job_log(job, f"  Conexiones activas cerradas: {n}")
                _job_log(job, f"  BD '{db}' existe — borrando para recrear limpia...")
                cur.execute(f'DROP DATABASE "{db}"')
                _job_log(job, f"  ✓ BD '{db}' borrada")
            else:
                _job_log(job, f"  BD '{db}' no existe — se creara desde cero.")
            _job_log(job, f"  Creando BD '{db}' vacia...")
            cur.execute(f'CREATE DATABASE "{db}" ENCODING \'UTF8\'')
            _job_log(job, f"  ✓ BD '{db}' creada")
        except Exception as e:
            msg = str(e).split("\n")[0]
            _job_log(job, f"  ✗ Error preparando BD '{db}': {msg}")
            _job_step(job, 2, "error")
            job["error"] = f"No se pudo preparar BD '{db}': {msg}"
            job["status"] = "error"; job["done"] = True
            return
        finally:
            if c:
                try: c.close()
                except Exception: pass

        # pg_restore sobre BD recien creada (vacia): sin --clean/--if-exists.
        cmd = [pg_restore, "-h", "127.0.0.1", "-p", "5432", "-U", "postgres",
               "-d", db, "-v", filepath]
        rc = _run_pg_cmd(job, cmd, password)
        if rc != 0:
            _job_log(job, f"✗ pg_restore fallo en '{db}' (codigo {rc})")
            _job_step(job, 2, "error")
            job["error"] = f"pg_restore fallo en '{db}'"
            job["status"] = "error"; job["done"] = True
            return
        _job_log(job, f"✓ '{db}' restaurada OK")
    _job_step(job, 2, "done")

    # ── 3. AJUSTES EN BD `tpv` LOCAL ──────────────────────────────
    # FASE 3 contiene 3 sub-pasos del plan: (3) serie+regla, (4) tpv.principal, (5) pos_version.
    _job_log(job, "")
    _job_step(job, 3, "running")
    _job_log(job, "═══ FASE 3/4: Ajustes en este TPV (id={}) ═══".format(num_tpv))

    c = None
    try:
        c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="tpv",
                             user="postgres", password=password, connect_timeout=5)
        c.autocommit = False
        cur = c.cursor()

        # 3a/3b. Marcar series propia=TRUE — metodo principal: por DESCRIPCION.
        # Convencion del cliente: el campo `serie.descripcion` contiene un marcador
        # `(N)` donde N es el numero de TPV (1..9). Ejemplo:
        #   "Factura Simplificada (2) — adicional" -> serie del TPV 2.
        # LIKE '%(N)%' es seguro: `(20)` no contiene la substring `(2)` (no van
        # parentesis consecutivos al 2), asi que no hay falsos positivos.
        patron_desc = f"%({num_tpv})%"
        _job_log(job, f"  Marcando propia=TRUE por descripcion LIKE '{patron_desc}'...")

        # Limpiar todas las marcas previas (clean slate)
        cur.execute("UPDATE serie SET propia = FALSE WHERE propia = TRUE")
        _job_log(job, f"  serie.propia=FALSE en {cur.rowcount} fila(s) (limpieza previa)")

        # Marcar las que contengan el marcador en descripcion
        cur.execute("UPDATE serie SET propia = TRUE WHERE descripcion LIKE %s",
                    (patron_desc,))
        n_propias = cur.rowcount

        if n_propias > 0:
            _job_log(job, f"  ✓ serie.propia=TRUE en {n_propias} fila(s) — por descripcion '({num_tpv})'")
        else:
            # FALLBACK: metodo antiguo de regex sobre `serie` (4 chars).
            # Util en BDs viejas donde las descripciones no llevan el marcador.
            _job_log(job, f"  ⚠ Ninguna descripcion contiene '({num_tpv})'. "
                          f"Probando metodo antiguo (regex 4 chars sobre `serie`)...")
            cur.execute("""
                SELECT substring(serie, 3, 1) AS id_est
                FROM serie WHERE serie ~ '^[A-Z]0[0-9][0-9]$'
                GROUP BY id_est ORDER BY COUNT(*) DESC LIMIT 1
            """)
            row = cur.fetchone()
            id_estacion = row[0] if row else "1"
            patron_serie = f"_0{id_estacion}{num_tpv}"
            cur.execute("UPDATE serie SET propia = TRUE WHERE serie LIKE %s",
                        (patron_serie,))
            n_propias = cur.rowcount
            _job_log(job, f"  serie.propia=TRUE en {n_propias} fila(s) por patron '{patron_serie}'")
            if n_propias == 0:
                _job_log(job, f"  ⚠⚠ Ningun metodo encontro series propias del TPV {num_tpv}.")
                _job_log(job, f"     Revisa: ¿tus descripciones llevan '({num_tpv})'? "
                              f"¿O tus codigos de serie cumplen el patron [A-Z]0X{num_tpv}?")

        # 3c. Reapuntar regla_facturacion a las series propias
        cur.execute("SELECT id_serie, serie FROM serie "
                    "WHERE factura=TRUE AND rectificativa=FALSE "
                    "AND comision=FALSE AND propia=TRUE")
        tienda_filas = cur.fetchall()
        cur.execute("SELECT id_serie, serie FROM serie "
                    "WHERE factura=TRUE AND rectificativa=FALSE "
                    "AND comision=TRUE AND propia=TRUE")
        comis_filas = cur.fetchall()

        if len(tienda_filas) == 1:
            cur.execute("UPDATE regla_facturacion SET id_serie=%s WHERE tienda=TRUE",
                        (tienda_filas[0][0],))
            _job_log(job, f"  regla_facturacion tienda -> serie {tienda_filas[0][1]} ({cur.rowcount} fila/s)")
        elif len(tienda_filas) == 0:
            _job_log(job, f"  ⚠ Sin serie tienda propia — regla tienda sin reapuntar")
        else:
            _job_log(job, f"  ⚠ {len(tienda_filas)} series tienda propias — regla tienda sin reapuntar")

        cur.execute("SELECT COUNT(*) FROM regla_facturacion WHERE tienda=FALSE AND carburante=TRUE")
        if cur.fetchone()[0] > 0:
            if len(comis_filas) == 1:
                cur.execute("UPDATE regla_facturacion SET id_serie=%s "
                            "WHERE tienda=FALSE AND carburante=TRUE", (comis_filas[0][0],))
                _job_log(job, f"  regla_facturacion carburante -> serie {comis_filas[0][1]} ({cur.rowcount} fila/s)")
            elif len(comis_filas) == 0:
                _job_log(job, "  ⚠ Sin serie comisionista propia — regla carburante sin reapuntar")
            else:
                _job_log(job, f"  ⚠ {len(comis_filas)} series comisionista propias — regla carburante sin reapuntar")
        # Paso 3 del plan (serie.propia + regla_facturacion) terminado
        _job_step(job, 3, "done")

        # 3d. tpv.principal: limpiar todo y poner TRUE solo en el id_tpv del propio TPV
        _job_step(job, 4, "running")
        cur.execute("UPDATE tpv SET principal = FALSE")
        _job_log(job, f"  tpv.principal=FALSE en {cur.rowcount} fila(s)")
        cur.execute("UPDATE tpv SET principal = TRUE WHERE id_tpv = %s", (num_tpv,))
        n_pri = cur.rowcount
        if n_pri == 1:
            _job_log(job, f"  tpv.principal=TRUE en id_tpv={num_tpv}")
        elif n_pri == 0:
            _job_log(job, f"  ⚠ No existe fila tpv con id_tpv={num_tpv} (no se ha marcado principal)")
        else:
            _job_log(job, f"  ⚠ {n_pri} filas tpv con id_tpv={num_tpv} (raro)")

        c.commit()
        _job_log(job, "  ✓ BD 'tpv' actualizada")
        # Paso 4 del plan (tpv.principal) terminado
        _job_step(job, 4, "done")
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        _job_log(job, f"  ✗ Error en BD 'tpv': {msg}")
        # Marca como error el paso que estaba en curso (3 o 4); el frontend
        # los pintará en rojo segun lo que tuvieran antes.
        if job.get("steps", {}).get("4") == "running":
            _job_step(job, 4, "error")
        else:
            _job_step(job, 3, "error")
        job["error"] = f"Error en BD tpv: {msg}"
        job["status"] = "error"; job["done"] = True
        return
    finally:
        if c:
            try: c.close()
            except Exception: pass

    # 3e. controlpista.local_config.pos_version_id_local (paso 5 del plan)
    _job_step(job, 5, "running")
    c = None
    try:
        c = psycopg2.connect(host="127.0.0.1", port=5432, dbname="controlpista",
                             user="postgres", password=password, connect_timeout=5)
        c.autocommit = False
        cur = c.cursor()
        pos_ver_local = 10 + num_tpv
        cur.execute("UPDATE local_config SET pos_version_id_local = %s", (pos_ver_local,))
        _job_log(job, f"  controlpista.local_config.pos_version_id_local = {pos_ver_local} ({cur.rowcount} fila/s)")
        # local_config.ip: la IP propia de este TPV. Tras el restore queda con la
        # del TPV1 (10.0.0.101) — la corregimos a la IP local indicada.
        cur.execute("UPDATE local_config SET ip = %s", (ip_local,))
        _job_log(job, f"  controlpista.local_config.ip = {ip_local} ({cur.rowcount} fila/s)")
        c.commit()
        _job_log(job, "  ✓ BD 'controlpista' actualizada")
        _job_step(job, 5, "done")
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        _job_log(job, f"  ✗ Error en BD 'controlpista': {msg}")
        _job_step(job, 5, "error")
        job["error"] = f"Error en BD controlpista: {msg}"
        job["status"] = "error"; job["done"] = True
        return
    finally:
        if c:
            try: c.close()
            except Exception: pass

    # ── 4. COPIA DE C:\GARUM DEL PRINCIPAL (opcional) — paso 6 del plan ────────
    # Copia recursiva via Windows admin share \\IP\C$\GARUM -> C:\GARUM local.
    # Util cuando se reinstala Windows en el TPV y hay que repoblar la carpeta
    # GARUM completa (jars, configs, scripts, etc.) desde el principal.
    _job_log(job, "")
    if not copiar_garum:
        _job_step(job, 6, "skipped")
        _job_log(job, "═══ FASE 4/5: Copia de C:\\GARUM OMITIDA (modo manual) ═══")
        _job_log(job, f"  ℹ Copia manualmente la carpeta C:\\GARUM del principal ({ip_origen})")
        _job_log(job, f"     a la C:\\GARUM de este equipo si lo necesitas.")
    else:
        _job_step(job, 6, "running")
        _job_log(job, f"═══ FASE 4/5: Copiar C:\\GARUM del principal ({ip_origen}) ═══")
        # Seguridad/sanidad: no tiene sentido copiar de uno mismo.
        if ip_origen in ("127.0.0.1", "localhost"):
            _job_log(job, "  ⚠ ip_origen es localhost — no se puede copiar de uno mismo. Omitido.")
            _job_step(job, 6, "skipped")
        else:
            _src = f"\\\\{ip_origen}\\C$\\GARUM"
            _dst = r"C:\GARUM"
            _share = f"\\\\{ip_origen}\\C$"   # el recurso para autenticar via net use
            _job_log(job, f"  Origen: {_src}")
            _job_log(job, f"  Destino: {_dst}")
            flags_rc = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW

            # PASO previo: autenticar la sesion SMB con el usuario integracion4gl.
            # Asi robocopy puede acceder a \\IP\C$ aunque el usuario Windows actual
            # del TPV destino no exista en el principal o no tenga admin alli.
            # Limpiamos primero cualquier conexion previa al share (silenciosamente),
            # luego abrimos con credenciales explicitas.
            try:
                subprocess.run(["net", "use", _share, "/delete"],
                               capture_output=True, text=True, timeout=10,
                               creationflags=flags_rc)
            except Exception:
                pass  # ignoramos errores — solo cleanup defensivo
            _job_log(job, f"  Autenticando como '{_USYS_USER}' contra {_share}...")
            try:
                _r_netuse = subprocess.run(
                    ["net", "use", _share, "/user:" + _USYS_USER, _USYS_PWD],
                    capture_output=True, text=True, timeout=15,
                    creationflags=flags_rc,
                )
                if _r_netuse.returncode != 0:
                    _err_brief = (_r_netuse.stderr or _r_netuse.stdout or "").strip().split("\n")[-1][:200]
                    _job_log(job, f"  ✗ net use fallo: {_err_brief}")
                    _job_log(job, f"  → Comprueba que el usuario '{_USYS_USER}' existe en {ip_origen}")
                    _job_log(job, f"    (modulo 🔐 Usuario sistema, ejecutado en el PRINCIPAL).")
                    _job_step(job, 6, "error")
                    # No intentamos el robocopy si la autenticacion fallo.
                    raise RuntimeError("net use fallo")
                _job_log(job, f"  ✓ Sesion SMB autenticada como '{_USYS_USER}'")
            except subprocess.TimeoutExpired:
                _job_log(job, "  ✗ net use timeout — ¿el principal responde?")
                _job_step(job, 6, "error")
                raise
            except RuntimeError:
                # ya logueado y marcado
                raise

            try:
                # robocopy es robusto en Windows: maneja ficheros en uso, reintentos,
                # paths largos, etc. Codigos 0-7 = exito (con o sin copias), 8+ = error.
                # /E       — copiar subdirectorios (incluye vacios)
                # /COPY:DAT— copiar Data + Atributos + Timestamps (sin ACLs)
                # /R:1 /W:2 — un reintento, esperar 2s entre cada uno
                # SIN /NFL — queremos los nombres de ficheros para que el frontend
                # los muestre en vivo. Mantenemos /NDL /NJH /NJS /NC /NS /NP para
                # no inflar mas la salida.
                cmd_rc = [
                    "robocopy", _src, _dst,
                    "/E", "/COPY:DAT", "/R:1", "/W:2",
                    "/NDL", "/NJH", "/NJS", "/NC", "/NS", "/NP",
                ]
                # Streaming: lanzamos robocopy con Popen y leemos stdout linea a
                # linea. Cada linea se agrega al job log para que el frontend
                # muestre la copia en vivo en el modal ovCopia.
                proc = subprocess.Popen(
                    cmd_rc, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, creationflags=flags_rc, bufsize=1,
                )
                _ficheros_copiados = 0
                for line in proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    _ficheros_copiados += 1
                    # Para evitar que el log se infle con miles de lineas en una
                    # copia grande, registramos cada linea pero comprimimos las
                    # rutas dejando solo el nombre relativo a C:\GARUM.
                    short = line.replace(_src + "\\", "").replace(_dst + "\\", "")
                    _job_log(job, f"  {short[:160]}")
                try:
                    proc.wait(timeout=600)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    _job_log(job, "  ✗ robocopy timeout (>10 min) — comprueba la red.")
                    _job_step(job, 6, "error")
                    raise
                rc_robo = proc.returncode
                # Tipico robocopy: 0=nada que copiar, 1=copiados OK, 2=extras detectados,
                # 3=copiados+extras, 4=mismatches, 5..7=combinaciones. 8+ = fallo real.
                if rc_robo < 8:
                    _job_log(job, f"  ✓ Copia completada — {_ficheros_copiados} entradas (robocopy exit={rc_robo})")
                    _job_step(job, 6, "done")
                else:
                    _job_log(job, f"  ✗ robocopy fallo (exit={rc_robo})")
                    _job_log(job, f"  Verifica permisos: ¿este usuario es admin en {ip_origen}?")
                    _job_step(job, 6, "error")
                    # NO marcamos error global — el resto del proceso fue OK.
            except subprocess.TimeoutExpired:
                # Ya logueado dentro del try; aqui solo evitamos doble log.
                pass
            except FileNotFoundError:
                _job_log(job, "  ✗ robocopy.exe no encontrado en este equipo (¿Windows muy antiguo?)")
                _job_step(job, 6, "error")
            except RuntimeError:
                # net use fallo — ya logueado y marcado el step 6 como error.
                pass
            except Exception as e:
                msg = str(e).split("\n")[0]
                _job_log(job, f"  ✗ Error inesperado copiando C:\\GARUM: {msg}")
                _job_step(job, 6, "error")
            finally:
                # Cleanup: cerrar la conexion SMB autenticada para no dejar la
                # sesion del usuario integracion4gl colgada en la maquina.
                try:
                    subprocess.run(["net", "use", _share, "/delete"],
                                   capture_output=True, text=True, timeout=10,
                                   creationflags=flags_rc)
                except Exception:
                    pass  # cleanup defensivo — no afecta al resultado del job

    # ── 5. EDITAR hibernateCentral.cfg.xml (opcional) — paso 7 del plan ────────
    # Si la copia de C:\GARUM (step 6) fallo y el usuario habia pedido la copia,
    # el fichero hibernateCentral.cfg.xml puede no existir aun (o estar obsoleto
    # de una instalacion previa). Saltar el editor con aviso explicito de que
    # hay que hacer AMBOS pasos manualmente — evita editar un XML inexistente y
    # deja al tecnico instrucciones claras.
    copia_garum_fallo = (copiar_garum
                        and job.get("steps", {}).get("6") == "error")
    _job_log(job, "")
    if copia_garum_fallo and editar_hibernate:
        _job_step(job, 7, "skipped")
        _job_log(job, "═══ FASE 5/5: Edicion de hibernate OMITIDA (la copia de C:\\GARUM fallo) ═══")
        _job_log(job, "  ⚠ Como la copia de C:\\GARUM fallo en el paso 6,")
        _job_log(job, "    hibernateCentral.cfg.xml puede no existir en este equipo")
        _job_log(job, "    o estar obsoleto. NO se va a editar automaticamente para")
        _job_log(job, "    evitar dejar un fichero corrupto.")
        _job_log(job, "  → Realiza AMBOS pasos manualmente:")
        _job_log(job, f"     1) Copia la carpeta C:\\GARUM del principal ({ip_origen})")
        _job_log(job, "        a la unidad C de este equipo (Explorador o robocopy).")
        _job_log(job, f"     2) Edita C:\\GARUM\\hibernateCentral.cfg.xml y pon la URL JDBC:")
        _job_log(job, f"          jdbc:postgresql://{ip_principal}:5432/tpv")
    elif not editar_hibernate:
        _job_step(job, 7, "skipped")
        _job_log(job, "═══ FASE 5/5: Edicion de hibernateCentral.cfg.xml OMITIDA (modo manual) ═══")
        _job_log(job, f"  ℹ Edita manualmente C:\\GARUM\\hibernateCentral.cfg.xml y pon:")
        _job_log(job, f"      jdbc:postgresql://{ip_principal}:5432/tpv")
    else:
        _job_step(job, 7, "running")
        _job_log(job, "═══ FASE 5/5: Editar hibernateCentral.cfg.xml ═══")
        import shutil
        _HIB_PATH = r"C:\GARUM\hibernateCentral.cfg.xml"
        _HIB_BAK  = _HIB_PATH + ".bak"
        try:
            _xml = None
            for _enc in ("utf-8", "cp1252"):
                try:
                    with open(_HIB_PATH, "r", encoding=_enc) as _f:
                        _xml = _f.read()
                    _xml_enc = _enc
                    break
                except UnicodeDecodeError:
                    continue
            if _xml is None:
                raise ValueError("no se pudo leer en utf-8 ni cp1252")

            # Usamos re.subn para distinguir "ya apuntaba ahí" (n>=1, sin cambios)
            # de "URL JDBC no encontrada" (n==0, fichero con otro formato).
            _xml_nuevo, _n_match = re.subn(
                r'(<property name="hibernate\.connection\.url">jdbc:postgresql://)[^<]+(</property>)',
                lambda m: m.group(1) + ip_principal + ":5432/tpv" + m.group(2),
                _xml
            )
            if _n_match == 0:
                _job_log(job, f"  ⚠ No se encontro la URL JDBC en {_HIB_PATH} — editar manualmente y poner:")
                _job_log(job, f"      jdbc:postgresql://{ip_principal}:5432/tpv")
                _job_step(job, 7, "error")
                # salimos del try; el finally del FASE 5 se ejecutará igualmente
                # (no marcamos error global — el resto del proceso fue OK).
                raise ValueError("URL JDBC no encontrada en el XML")
            elif _xml_nuevo == _xml:
                _job_log(job, f"  hibernateCentral.cfg.xml ya apuntaba a {ip_principal}, sin cambios")
            else:
                if "hibernate.connection.url" not in _xml_nuevo \
                   or abs(len(_xml_nuevo) - len(_xml)) > 200:
                    raise ValueError("Resultado XML invalido tras sustitucion")
                try:
                    shutil.copy2(_HIB_PATH, _HIB_BAK)
                    _job_log(job, f"  Backup creado: {_HIB_BAK}")
                except Exception as _ex_bak:
                    _job_log(job, f"  ⚠ No se pudo crear backup hibernate: {_ex_bak}")
                _tmp = _HIB_PATH + ".tmp"
                with open(_tmp, "w", encoding=_xml_enc) as _f:
                    _f.write(_xml_nuevo)
                os.replace(_tmp, _HIB_PATH)
                _job_log(job, f"  ✓ URL actualizada -> jdbc:postgresql://{ip_principal}:5432/tpv")
            # Edicion exitosa: paso 7 "done".
            _job_step(job, 7, "done")
        except FileNotFoundError:
            _job_log(job, f"  ⚠ {_HIB_PATH} no encontrado — editar manualmente y poner:")
            _job_log(job, f"      jdbc:postgresql://{ip_principal}:5432/tpv")
            # No marcamos error total — pero el paso queda como "error" para
            # que el tecnico vea que hay que actuar manualmente.
            _job_step(job, 7, "error")
        except Exception as e:
            _job_log(job, f"  ⚠ Error editando hibernate: {str(e).split(chr(10))[0]}")
            # No marcamos error total — el resto del proceso fue exitoso
            _job_step(job, 7, "error")

    # ── FIN ────────────────────────────────────────────────────────
    _job_log(job, "")
    _job_log(job, "═══ REINTEGRACION COMPLETADA ═══")
    if editar_hibernate:
        _job_log(job, f"TPV {num_tpv} listo. Reinicia GARUM para aplicar los cambios de hibernate.")
    else:
        _job_log(job, f"TPV {num_tpv} listo. Recuerda editar hibernateCentral.cfg.xml manualmente y reiniciar GARUM.")
    job["status"] = "ok"
    job["done"]   = True


@app.route("/api/reintegrar/iniciar", methods=["POST"])
@csrf
@need_conn
def api_reintegrar_iniciar():
    """Lanza el job de reintegracion en hilo. Devuelve job_id.
    El frontend polea /api/instalar/progreso/<job_id> (mismo polling
    que usa el modulo Nuevo TPV)."""
    data = request.json or {}
    password = data.get("password", "")
    if not password:
        return jsonify({"ok": False, "error": "Contrasena requerida"}), 400

    # Overrides opcionales desde el frontend. Si vienen, ganan a la auto-deteccion.
    num_tpv_override = data.get("num_tpv")
    ip_origen_override = (data.get("ip_origen") or "").strip()
    ip_local_override  = (data.get("ip_local")  or "").strip()
    # Opcion para que el tecnico edite hibernateCentral.cfg.xml manualmente.
    # Default True (mismo comportamiento que antes). Acepta bool o str ("false"/"0").
    _eh = data.get("editar_hibernate", True)
    if isinstance(_eh, str):
        editar_hibernate = _eh.strip().lower() not in ("false", "0", "no", "off", "")
    else:
        editar_hibernate = bool(_eh)
    # Opcion para copiar la carpeta C:\GARUM del principal a este equipo via
    # \\IP\C$\GARUM. Default True. Mismo parsing que editar_hibernate.
    _cg = data.get("copiar_garum", True)
    if isinstance(_cg, str):
        copiar_garum = _cg.strip().lower() not in ("false", "0", "no", "off", "")
    else:
        copiar_garum = bool(_cg)

    # 1) num_tpv: override > auto-detect. Rango [1, 9].
    # Antes era [2, 9] bajo la asuncion de que TPV1 SIEMPRE es la fuente. Pero
    # hay un caso real en el que necesitamos reintegrar TPV1: cuando el propio
    # TPV1 muere y otro TPV (que tomo el rol de principal) es la fuente.
    if num_tpv_override is not None and num_tpv_override != "":
        try:
            num_tpv = int(num_tpv_override)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "num_tpv invalido (no es entero)"}), 400
    else:
        num_tpv = _detectar_num_tpv_local()
        if num_tpv is None:
            return jsonify({"ok": False,
                            "error": ("No se ha detectado IP local en 10.0.0.101..10.0.0.109. "
                                      "Indica el nº de TPV manualmente.")}), 400
    if not (1 <= num_tpv <= 9):
        return jsonify({"ok": False,
                        "error": "num_tpv debe estar entre 1 y 9."}), 400

    # 2) ip_origen: override > default _REINT_IP_PRINCIPAL.
    # Reusa val_host() (linea 604): valida formato IPv4 + whitelist _REDES.
    if ip_origen_override:
        try:
            ip_origen = val_host(ip_origen_override)
        except ValueError as e:
            return jsonify({"ok": False, "error": f"IP origen invalida: {e}"}), 400
    else:
        ip_origen = _REINT_IP_PRINCIPAL
    ip_principal = ip_origen   # mismo host (TPV1 = principal = fuente del clonado)

    # 3) ip_local: override > default 10.0.0.10{num_tpv}. Es la IP que se escribira
    # en controlpista.local_config.ip para identificar a este TPV en la red.
    if ip_local_override:
        try:
            ip_local = val_host(ip_local_override)
        except ValueError as e:
            return jsonify({"ok": False, "error": f"IP local invalida: {e}"}), 400
    else:
        ip_local = f"10.0.0.10{num_tpv}"

    job_id = secrets.token_hex(8)
    with _instalar_jobs_lock:
        _instalar_jobs[job_id] = {
            "type": "reintegrar",
            "status": "running",
            "logs": [],
            "ficheros": {},
            "error": "",
            "done": False,
            "created_at": datetime.now().isoformat(),
        }
    threading.Thread(
        target=_job_reintegrar,
        args=(job_id, password, num_tpv, ip_origen, ip_principal, editar_hibernate, ip_local, copiar_garum),
        daemon=True,
    ).start()
    log(f"[reintegrar] job {job_id} lanzado: num_tpv={num_tpv}, principal={ip_principal}, "
        f"ip_local={ip_local}, editar_hibernate={editar_hibernate}, copiar_garum={copiar_garum}", "info")
    return jsonify({"ok": True, "job_id": job_id, "num_tpv": num_tpv, "ip_local": ip_local,
                    "editar_hibernate": editar_hibernate, "copiar_garum": copiar_garum})


# =============================================================================
# USUARIO SISTEMA (v7.x) — crea usuario Windows local hardcoded
# =============================================================================
# Crea (o actualiza) un usuario local de Windows con privilegios de Admin y
# contraseña que no caduca. El mismo usuario+pwd en todos los TPVs permite que
# se vean entre si via SMB (\\IP\C$\GARUM) y se use para un servicio Windows.
#
# La operacion es SIEMPRE sobre el TPV local (la maquina donde corre la app).
# Idempotente: si el usuario ya existe, actualiza la pwd + flag + grupo sin
# fallar. El grupo Administradores se resuelve via SID built-in (S-1-5-32-544)
# para funcionar tanto en Windows en español ("Administradores") como ingles
# ("Administrators").

_USYS_USER = "integracion4gl"
_USYS_PWD  = "ni4GL101212"


def _crear_usuario_windows_local():
    """Ejecuta PowerShell con 3 pasos estructurados (check, create, group).
    Estrategia: si el usuario YA EXISTE, NO se hace nada — la operacion es
    "asegurar que existe", no "asegurar que tiene esta pwd y este grupo".
    Devuelve dict {ok, resumen, resultado, pasos: [{id, estado, mensaje}]}.
    Solo Windows."""
    if sys.platform != "win32":
        return {"ok": False, "resumen": "Solo funciona en Windows",
                "resultado": "no_windows",
                "pasos": [
                    {"id": "check",  "estado": "error", "mensaje": "Sistema no Windows"},
                    {"id": "create", "estado": "pending", "mensaje": ""},
                    {"id": "group",  "estado": "pending", "mensaje": ""},
                ]}
    # El script emite lineas estructuradas STEP<n>:<id>:<estado>:<mensaje>
    # que el backend parsea y devuelve al frontend para renderizar tarjetas.
    # Si el usuario YA existe → check=done, create=skipped, group=skipped (no
    # se toca nada). Si NO existe → se procede con create y group.
    script = (
        "$ErrorActionPreference = 'Stop'\n"
        "$user = '" + _USYS_USER + "'\n"
        "$pwd  = ConvertTo-SecureString '" + _USYS_PWD + "' -AsPlainText -Force\n"
        "# Paso 1: comprobar si el usuario ya existe\n"
        "$existing = Get-LocalUser -Name $user -ErrorAction SilentlyContinue\n"
        "if ($existing) {\n"
        "  Write-Output ('STEP1:check:done:Usuario \"' + $user + '\" ya existe en este equipo')\n"
        "  Write-Output ('STEP2:create:skipped:No es necesario crear (ya existe)')\n"
        "  Write-Output ('STEP3:group:skipped:No se toca el grupo (usuario ya existe)')\n"
        "  Write-Output 'RESULT:exists'\n"
        "} else {\n"
        "  Write-Output ('STEP1:check:done:Usuario \"' + $user + '\" NO existe — procediendo a crearlo')\n"
        "  # Paso 2: crear el usuario\n"
        "  try {\n"
        "    New-LocalUser -Name $user -Password $pwd -PasswordNeverExpires:$true "
        "-AccountNeverExpires -FullName 'Integracion 4GL' "
        # ojo: -Description tiene limite duro de 48 caracteres (PowerShell).
        "-Description 'Usuario tecnico integracion TPVs GARUM' | Out-Null\n"
        "    Write-Output ('STEP2:create:done:Usuario creado con PasswordNeverExpires + AccountNeverExpires')\n"
        "  } catch {\n"
        # Mensaje amigable cuando la politica local de pwd rechaza la contrasena.
        # InvalidPasswordException la lanza New-LocalUser cuando la directiva de
        # seguridad local (secpol.msc) exige mas complejidad / longitud que la
        # del password hardcoded. La pwd no la podemos cambiar porque tiene que
        # ser identica en todos los TPVs (SMB cross-host).
        "    $exType = $_.Exception.GetType().FullName\n"
        "    if ($exType -match 'InvalidPasswordException' -or "
        "        $_.Exception.Message -match 'complej|complex|policy|directiva|policia') {\n"
        "      $msg = 'La politica de Windows de este equipo rechaza la contrasena. " \
                  "Abre secpol.msc -> Directivas de cuenta -> Directiva de contrasenas y " \
                  "deshabilita Complejidad + baja Longitud minima a 0. Reintenta.'\n"
        "      Write-Output ('STEP2:create:error:' + $msg)\n"
        "    } else {\n"
        "      Write-Output ('STEP2:create:error:' + $_.Exception.Message)\n"
        "    }\n"
        "    Write-Output 'STEP3:group:pending:No se ha intentado (paso anterior fallo)'\n"
        "    Write-Output 'RESULT:error'\n"
        "    return\n"
        "  }\n"
        "  # Paso 3: añadir al grupo Administradores (SID built-in, idioma-agnostico)\n"
        "  $adminGroup = (Get-LocalGroup -SID 'S-1-5-32-544').Name\n"
        "  try {\n"
        "    Add-LocalGroupMember -Group $adminGroup -Member $user -ErrorAction Stop\n"
        "    Write-Output ('STEP3:group:done:Anadido al grupo ' + $adminGroup)\n"
        "    Write-Output 'RESULT:created'\n"
        "  } catch {\n"
        "    if ($_.FullyQualifiedErrorId -like '*MemberExists*' -or "
        "        $_.Exception.Message -match 'ya es miembro|already a member') {\n"
        "      Write-Output ('STEP3:group:done:Ya pertenecia al grupo ' + $adminGroup)\n"
        "      Write-Output 'RESULT:created'\n"
        "    } else {\n"
        "      Write-Output ('STEP3:group:error:' + $_.Exception.Message)\n"
        "      Write-Output 'RESULT:partial'\n"
        "    }\n"
        "  }\n"
        "}\n"
    )
    # Pasos por defecto (placeholders por si PowerShell falla y no emite todos)
    pasos_default = [
        {"id": "check",  "estado": "pending", "mensaje": ""},
        {"id": "create", "estado": "pending", "mensaje": ""},
        {"id": "group",  "estado": "pending", "mensaje": ""},
    ]
    try:
        flags = 0x08000000  # CREATE_NO_WINDOW
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=30, creationflags=flags
        )
    except subprocess.TimeoutExpired:
        pasos_default[0] = {"id": "check", "estado": "error", "mensaje": "Timeout PowerShell (>30s)"}
        return {"ok": False, "resumen": "PowerShell timeout (>30s)",
                "resultado": "timeout", "user": _USYS_USER, "pasos": pasos_default}
    except FileNotFoundError:
        pasos_default[0] = {"id": "check", "estado": "error", "mensaje": "powershell.exe no encontrado"}
        return {"ok": False, "resumen": "PowerShell no encontrado",
                "resultado": "no_powershell", "user": _USYS_USER, "pasos": pasos_default}
    except Exception as e:
        pasos_default[0] = {"id": "check", "estado": "error",
                            "mensaje": str(e).split("\n")[0][:150]}
        return {"ok": False, "resumen": "Error inesperado lanzando PowerShell",
                "resultado": "exception", "user": _USYS_USER, "pasos": pasos_default}

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    lineas = [l for l in stdout.splitlines() if l.strip()]

    # Parser de las lineas STEP<n>:<id>:<estado>:<mensaje>
    pasos_map = {"check": None, "create": None, "group": None}
    resultado = "desconocido"
    for l in lineas:
        if l.startswith("RESULT:"):
            resultado = l.split(":", 1)[1]
            continue
        if l.startswith("STEP"):
            # Formato: STEP1:check:done:Usuario "X" ya existe...
            partes = l.split(":", 3)
            if len(partes) >= 4:
                _step_n, pid, estado, mensaje = partes
                if pid in pasos_map:
                    pasos_map[pid] = {"id": pid, "estado": estado, "mensaje": mensaje}

    pasos = []
    for pid in ("check", "create", "group"):
        if pasos_map[pid]:
            pasos.append(pasos_map[pid])
        else:
            pasos.append({"id": pid, "estado": "pending", "mensaje": "Sin info de PowerShell"})

    # Si PowerShell devolvio error y no tenemos ningun STEP, reportar el stderr.
    if proc.returncode != 0 and resultado == "desconocido":
        log(f"[usuario-sistema] PowerShell exit={proc.returncode} stderr={stderr[:500]}", "warn")
        msg_err = (stderr.split("\n")[0] if stderr else "Error desconocido")[:200]
        pasos[0] = {"id": "check", "estado": "error", "mensaje": msg_err}
        return {"ok": False, "resumen": "PowerShell devolvio error",
                "resultado": "error", "user": _USYS_USER, "pasos": pasos}

    # Determinar resumen segun resultado
    if resultado == "exists":
        resumen, ok = "El usuario ya existia — no se ha tocado nada", True
    elif resultado == "created":
        resumen, ok = "Usuario creado y anadido al grupo Administradores", True
    elif resultado == "partial":
        resumen, ok = "Usuario creado pero hubo problema con el grupo", False
    elif resultado == "error":
        resumen, ok = "Fallo creando el usuario", False
    else:
        resumen, ok = "Operacion completada con resultado indeterminado", False

    log(f"[usuario-sistema] {_USYS_USER}: resultado={resultado}", "ok" if ok else "warn")
    return {"ok": ok, "resumen": resumen, "resultado": resultado,
            "user": _USYS_USER, "pasos": pasos}


# ─────────────────────────────────────────────────────────────────────────────
# VERSION Y CONSTANTES GLOBALES — APP_VERSION es la fuente unica de verdad
# para la version. El docstring, el sidebar HTML, el User-Agent y los
# endpoints /api/app-info y /api/actualizar/check la leen de aqui. Bumpar
# solo este valor (+ los .bat / NSI / docs) en el siguiente release.
# ─────────────────────────────────────────────────────────────────────────────

APP_VERSION = "8.0"
APP_NAME    = "GARUM TPV Manager"
_USER_AGENT = f"GARUM-TPV-Manager/{APP_VERSION}"

# Lock global para evitar doble click en "Aplicar actualizacion" (no es 100%
# robusto entre procesos, pero esta app corre como instancia unica). Threading
# nativo basta — Flask en threaded=True puede tener varios requests en vuelo.
_actualizando_lock = threading.Lock()
_actualizando_en_curso = False


def _descargar_url_a_fichero(url, dest_path, timeout=600, user_agent=None):
    """Descarga url → dest_path con escritura atomica (.tmp + replace).
    Fallback SSL no-verify si el primer intento con verificacion falla
    (algunos clientes tienen cert FortiDDNS auto-firmado).

    Lanza RuntimeError si la descarga acaba pero el fichero esta vacio.
    Lanza otras excepciones (URLError, OSError) sin envolverlas — el caller
    decide como reportarlas.
    """
    import urllib.request, ssl, shutil
    tmp_path = dest_path + ".tmp"
    ua = user_agent or _USER_AGENT

    def _do(ctx):
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            with open(tmp_path, "wb") as f:
                shutil.copyfileobj(resp, f, length=64 * 1024)

    try:
        _do(ssl.create_default_context())
    except ssl.SSLError as ssl_err:
        log(f"[descarga] SSL verify fallo ({ssl_err}); reintentando sin verify",
            "warn")
        _do(ssl._create_unverified_context())

    if not os.path.isfile(tmp_path) or os.path.getsize(tmp_path) == 0:
        try:
            if os.path.isfile(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise RuntimeError("La descarga termino pero el fichero esta vacio")
    os.replace(tmp_path, dest_path)
    return os.path.getsize(dest_path)


def _comparar_versiones(local, remota):
    """Compara strings tipo '8.0' vs '8.1.3' devolviendo -1, 0 o 1.
    Tolera espacios, prefijo 'v', diferentes longitudes (8.0 < 8.0.1)."""
    def _parse(s):
        s = (s or "").strip().lstrip("vV")
        return tuple(int(p) for p in s.split(".") if p.isdigit())
    a, b = _parse(local), _parse(remota)
    if a < b: return -1
    if a > b: return 1
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# SETUP-GARUM (PASO 0): descarga del ZIP con los instaladores (BBDD + Java +
# GARUM) desde la nube 4GL. Usado al principio de Reintegrar TPV y Nuevo TPV.
# Endpoint sincrono: bloquea hasta que termine la descarga. Si el ZIP fuera
# muy grande convendria pasar a job async, pero para los tamanos actuales
# (<= 300 MB tipico) la respuesta tarda 30-90 s y el frontend muestra spinner.
# ─────────────────────────────────────────────────────────────────────────────

_SETUP_GARUM_URL     = "https://4gl.fortiddns.com:1604/descargas/Setup-GARUM.zip"
_SETUP_GARUM_DIR     = r"C:\GARUMTOOLS"
_SETUP_GARUM_PATH    = r"C:\GARUMTOOLS\Setup-GARUM.zip"
_SETUP_GARUM_EXTRACT = r"C:\GARUMTOOLS\Setup-GARUM"


@app.route("/api/setup-garum/info")
@need_conn
def api_setup_garum_info():
    """Estado del ZIP local — para que el frontend sepa si ya esta descargado."""
    existe = os.path.isfile(_SETUP_GARUM_PATH)
    size = os.path.getsize(_SETUP_GARUM_PATH) if existe else 0
    try:
        mtime = (os.path.getmtime(_SETUP_GARUM_PATH) if existe else 0)
    except Exception:
        mtime = 0
    return jsonify({"ok": True, "url": _SETUP_GARUM_URL,
                    "path": _SETUP_GARUM_PATH,
                    "existe": existe, "size": int(size),
                    "mtime": int(mtime)})


@app.route("/api/setup-garum/descargar", methods=["POST"])
@csrf
@need_conn
def api_setup_garum_descargar():
    """Descarga Setup-GARUM.zip desde la URL fija de 4GL y lo DESCOMPRIME
    en C:\\GARUMTOOLS\\Setup-GARUM\\ — listo para que el tecnico ejecute
    los instaladores directamente sin paso manual de descompresion.

    Returns: {ok, zip_path, extract_dir, size_mb, files_count, unzip_ok}
    """
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True,
                        "zip_path": _SETUP_GARUM_PATH,
                        "extract_dir": _SETUP_GARUM_EXTRACT,
                        "size_mb": 0.0, "files_count": 0, "unzip_ok": True})
    import shutil, zipfile
    try:
        os.makedirs(_SETUP_GARUM_DIR, exist_ok=True)
        log(f"[setup-garum] Descargando {_SETUP_GARUM_URL} → {_SETUP_GARUM_PATH}", "info")
        # Helper compartido (v8.0): escritura atomica + fallback SSL no-verify.
        size = _descargar_url_a_fichero(_SETUP_GARUM_URL, _SETUP_GARUM_PATH,
                                        timeout=600)
        size_mb = round(size / 1024 / 1024, 1)
        log(f"[setup-garum] OK descarga — {size_mb} MB", "ok")

        # ── Descompresion automatica ──────────────────────────────────
        # Limpia la carpeta de extraccion anterior (si existe) — evita
        # mezclar restos de instalaciones previas. Es seguro porque la
        # carpeta es exclusiva (C:\GARUMTOOLS\Setup-GARUM\).
        unzip_ok = False
        files_count = 0
        try:
            if os.path.isdir(_SETUP_GARUM_EXTRACT):
                shutil.rmtree(_SETUP_GARUM_EXTRACT, ignore_errors=True)
            os.makedirs(_SETUP_GARUM_EXTRACT, exist_ok=True)
            with zipfile.ZipFile(_SETUP_GARUM_PATH, "r") as zf:
                # Defensa contra path traversal (zip slip): rechazamos
                # entradas cuyo path resuelto se sale del directorio destino.
                base_abs = os.path.abspath(_SETUP_GARUM_EXTRACT)
                for member in zf.infolist():
                    member_path = os.path.abspath(os.path.join(base_abs, member.filename))
                    if not member_path.startswith(base_abs + os.sep) and member_path != base_abs:
                        raise RuntimeError(f"Zip slip detectado: {member.filename}")
                zf.extractall(_SETUP_GARUM_EXTRACT)
                files_count = len(zf.namelist())
            unzip_ok = True
            log(f"[setup-garum] OK descomprimido — {files_count} ficheros en {_SETUP_GARUM_EXTRACT}", "ok")
        except Exception as e_unzip:
            msg = str(e_unzip).split("\n")[0]
            log(f"[setup-garum] WARN no se pudo descomprimir: {msg}", "warn")
            # El ZIP esta descargado correctamente — el tecnico puede descomprimirlo a mano.

        return jsonify({"ok": True,
                        "zip_path": _SETUP_GARUM_PATH,
                        "extract_dir": _SETUP_GARUM_EXTRACT,
                        "size": int(size), "size_mb": size_mb,
                        "unzip_ok": unzip_ok,
                        "files_count": files_count})
    except Exception as e:
        try:
            if os.path.isfile(_SETUP_GARUM_PATH + ".tmp"):
                os.remove(_SETUP_GARUM_PATH + ".tmp")
        except Exception:
            pass
        msg = str(e).split("\n")[0]
        log(f"[setup-garum] ERROR: {msg}", "error")
        return jsonify({"ok": False, "error": msg}), 500


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-ACTUALIZACION (v8.0): la app consulta version_manager.txt en la nube,
# compara con APP_VERSION local, y si la remota es mayor permite descargar
# el ZIP de distribucion completo, descomprimirlo, lanzar el Setup.exe como
# proceso desacoplado, y cerrarse para que el setup pueda sobrescribir los
# ficheros sin conflictos. Bandera global _actualizando_en_curso previene
# que un doble click dispare 2 descargas/relanzamientos en paralelo.
# ─────────────────────────────────────────────────────────────────────────────

_UPDATE_VERSION_URL = "https://4gl.fortiddns.com:1604/descargas/version_manager.txt"
_UPDATE_ZIP_URL     = "https://4gl.fortiddns.com:1604/descargas/GARUM_TPV_Manager_v7.4_distribucion.zip"
_UPDATE_DIR         = r"C:\GARUMTOOLS\Update"
_UPDATE_ZIP_PATH    = r"C:\GARUMTOOLS\Update\update.zip"


@app.route("/api/app-info")
def api_app_info():
    """Devuelve metadata basica de la app (publico, sin @need_conn).
    Lo usa el frontend para inyectar la version en el sidebar y para
    el modulo de auto-actualizacion."""
    return jsonify({"ok": True, "version": APP_VERSION, "name": APP_NAME})


@app.route("/api/actualizar/check")
@need_conn
def api_actualizar_check():
    """Consulta la nube 4GL para saber si hay una version mas reciente.
    Defensa: ante cualquier error (sin red, URL caida, version_manager.txt
    mal formado) NO devuelve 500. Devuelve hay_actualizacion=false con un
    motivo informativo. La idea es que el frontend pueda hacer este check
    silenciosamente al login sin mostrar errores al tecnico.

    Returns {ok:True, version_local, version_remota, hay_actualizacion,
             zip_url, comprobado_en, motivo?}
    """
    import urllib.request, ssl, datetime

    def _ahora_iso():
        return datetime.datetime.now().replace(microsecond=0).isoformat()

    version_remota = None
    motivo = None
    try:
        # Descargar version_manager.txt (~10 bytes) — sin escribir a disco.
        # Reusamos el patron SSL + fallback no-verify del helper.
        req = urllib.request.Request(_UPDATE_VERSION_URL,
                                      headers={"User-Agent": _USER_AGENT})

        def _leer(ctx):
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                return resp.read(256).decode("utf-8", errors="ignore").strip()

        try:
            version_remota = _leer(ssl.create_default_context())
        except ssl.SSLError:
            version_remota = _leer(ssl._create_unverified_context())
    except Exception as e:
        msg = str(e).split("\n")[0][:200]
        log(f"[actualizar/check] No se pudo consultar la nube: {msg}", "warn")
        motivo = "No se pudo consultar la nube"

    if not version_remota:
        return jsonify({
            "ok": True,
            "version_local": APP_VERSION,
            "version_remota": None,
            "hay_actualizacion": False,
            "zip_url": _UPDATE_ZIP_URL,
            "comprobado_en": _ahora_iso(),
            "motivo": motivo or "Sin version remota leible",
        })

    cmp_ = _comparar_versiones(APP_VERSION, version_remota)
    hay = (cmp_ < 0)
    log(f"[actualizar/check] local={APP_VERSION} remota={version_remota} "
        f"hay_update={hay}", "info")
    return jsonify({
        "ok": True,
        "version_local": APP_VERSION,
        "version_remota": version_remota,
        "hay_actualizacion": hay,
        "zip_url": _UPDATE_ZIP_URL,
        "comprobado_en": _ahora_iso(),
    })


@app.route("/api/actualizar/aplicar", methods=["POST"])
@csrf
@need_conn
def api_actualizar_aplicar():
    """Descarga el ZIP de distribucion, lo descomprime en C:\\GARUMTOOLS\\Update\\,
    localiza el Setup-vX.exe interno y lo lanza como proceso DESACOPLADO. Tras
    5 s la app se cierra via os._exit(0) para que el setup pueda sobrescribir
    los ficheros sin tener Flask bloqueandolos.

    Returns {ok, version_a_instalar, setup_path, segundos_para_cerrar}
    """
    global _actualizando_en_curso
    if sess.get("demo"):
        return jsonify({"ok": True, "demo": True, "setup_path": "<demo>",
                        "version_a_instalar": "demo",
                        "segundos_para_cerrar": 5})

    # Defensa anti-race: solo una actualizacion concurrente.
    with _actualizando_lock:
        if _actualizando_en_curso:
            return jsonify({"ok": False, "ya_en_curso": True,
                            "error": "Hay una actualizacion en curso"}), 409
        _actualizando_en_curso = True

    import shutil, zipfile, glob, subprocess
    try:
        # Re-check de version (defensa anti-race entre check y aplicar)
        try:
            r_check = api_actualizar_check()
            data = r_check.get_json() if hasattr(r_check, "get_json") else {}
            if not data.get("hay_actualizacion"):
                # No hay update — abortamos por higiene.
                with _actualizando_lock:
                    _actualizando_en_curso = False
                return jsonify({"ok": False,
                                "error": "No hay una version nueva en la nube"}), 400
            version_remota = data.get("version_remota") or "?"
        except Exception:
            # Si el re-check falla, seguimos igual (la descarga del ZIP
            # confirmara el estado real).
            version_remota = "?"

        os.makedirs(_UPDATE_DIR, exist_ok=True)
        log(f"[actualizar/aplicar] Descargando ZIP desde {_UPDATE_ZIP_URL}",
            "info")
        size = _descargar_url_a_fichero(_UPDATE_ZIP_URL, _UPDATE_ZIP_PATH,
                                        timeout=600)
        size_mb = round(size / 1024 / 1024, 1)
        log(f"[actualizar/aplicar] OK descarga — {size_mb} MB", "ok")

        # ── Descompresion en _UPDATE_DIR ──────────────────────────────
        # Limpia ficheros viejos de updates anteriores (mantiene el .zip
        # recien descargado pero borra el resto).
        for p in glob.glob(os.path.join(_UPDATE_DIR, "*")):
            if os.path.abspath(p) == os.path.abspath(_UPDATE_ZIP_PATH):
                continue
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.remove(p)
            except Exception:
                pass

        with zipfile.ZipFile(_UPDATE_ZIP_PATH, "r") as zf:
            base_abs = os.path.abspath(_UPDATE_DIR)
            for member in zf.infolist():
                member_path = os.path.abspath(
                    os.path.join(base_abs, member.filename))
                if (not member_path.startswith(base_abs + os.sep)
                        and member_path != base_abs):
                    raise RuntimeError(f"Zip slip detectado: {member.filename}")
            zf.extractall(_UPDATE_DIR)
        log(f"[actualizar/aplicar] OK descomprimido en {_UPDATE_DIR}", "ok")

        # ── Localizar Setup-vX.exe dentro del ZIP descomprimido ───────
        candidatos = glob.glob(os.path.join(
            _UPDATE_DIR, "**", "GARUM_TPV_Manager_Setup_v*.exe"), recursive=True)
        if not candidatos:
            with _actualizando_lock:
                _actualizando_en_curso = False
            return jsonify({"ok": False,
                            "error": ("ZIP descargado pero no se encontro "
                                      "GARUM_TPV_Manager_Setup_v*.exe dentro. "
                                      "Descomprime manualmente y ejecutalo.")}), 500
        setup_exe = candidatos[0]
        log(f"[actualizar/aplicar] Setup localizado: {setup_exe}", "info")

        # ── Lanzar setup como proceso desacoplado ──────────────────────
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        try:
            subprocess.Popen([setup_exe], creationflags=flags, close_fds=True)
            log(f"[actualizar/aplicar] Setup lanzado en proceso desacoplado",
                "ok")
        except Exception as e_pop:
            with _actualizando_lock:
                _actualizando_en_curso = False
            msg = str(e_pop).split("\n")[0]
            return jsonify({"ok": False,
                            "error": f"No se pudo lanzar el setup: {msg}"}), 500

        # ── Programar cierre de la app en 5 s ──────────────────────────
        # Tiempo suficiente para que el setup haya arrancado pero antes
        # de que intente sobrescribir los ficheros que Flask tiene abiertos.
        def _suicidar():
            log(f"[actualizar/aplicar] os._exit(0) — cerrando para liberar "
                f"ficheros al setup", "warn")
            os._exit(0)

        threading.Timer(5.0, _suicidar).start()

        return jsonify({"ok": True,
                        "version_a_instalar": version_remota,
                        "setup_path": setup_exe,
                        "segundos_para_cerrar": 5,
                        "size_mb": size_mb})
    except Exception as e:
        with _actualizando_lock:
            _actualizando_en_curso = False
        msg = str(e).split("\n")[0]
        log(f"[actualizar/aplicar] ERROR: {msg}", "error")
        return jsonify({"ok": False, "error": msg}), 500


@app.route("/api/usuario-sistema/info")
@need_conn
def api_usuario_sistema_info():
    """Devuelve metadata sobre el usuario sistema (sin la contraseña).
    Util para que el frontend muestre el nombre antes de pulsar el boton."""
    return jsonify({"ok": True, "user": _USYS_USER,
                    "descripcion": "Usuario admin local para integracion entre TPVs GARUM."})


@app.route("/api/usuario-sistema/crear", methods=["POST"])
@csrf
@need_conn
def api_usuario_sistema_crear():
    """Crea el usuario sistema en el Windows LOCAL del TPV donde corre la app
    SI no existe ya. Si ya existe, NO se toca nada (ni contraseña, ni grupo,
    ni flags). Sin parametros — usuario y pwd estan hardcoded en el server."""
    if sess.get("demo"):
        return jsonify({
            "ok": True, "demo": True,
            "resumen": "[DEMO] Usuario integracion4gl creado",
            "resultado": "created", "user": _USYS_USER,
            "pasos": [
                {"id": "check",  "estado": "done",
                 "mensaje": "Usuario \"integracion4gl\" NO existe — procediendo a crearlo"},
                {"id": "create", "estado": "done",
                 "mensaje": "Usuario creado con PasswordNeverExpires + AccountNeverExpires"},
                {"id": "group",  "estado": "done",
                 "mensaje": "Anadido al grupo Administradores"},
            ],
        })
    return jsonify(_crear_usuario_windows_local())


# =============================================================================
# CLIENTES (v6.x - portado de tpv-clientes / gestion-clientes-garum v1.1.0)
# =============================================================================
# Gestion de clientes, vehiculos, tarjetas y asociaciones cliente-tarjeta-vehiculo.
# Comparte la misma BD `tpv` que el resto de garum_tpv_manager.
# Tablas: cliente, cliente_direccion, cliente_tipo, vehiculo, tarjeta,
#         tarjeta_tipo, cliente_tarjeta_vehiculo, provincia.
# Conexion: usa sess["host"] (el TPV al que el tecnico se conecto en login).
# Soft delete: cliente_tarjeta_vehiculo.delete_date IS NULL = activa.
# =============================================================================

def _cli_conn():
    """Devuelve una conexion a la BD `tpv` del TPV indicado por el cliente.
    Resuelve `host_tpv` en este orden:
      1. ?host_tpv= en query string (para GETs)
      2. host_tpv en el body JSON (para POST/PUT/DELETE/PATCH)
      3. sess['host'] como fallback (el TPV del login)
    `conn_tpv(host)` valida internamente con val_host()."""
    host_raw = request.args.get("host_tpv")
    if not host_raw and request.is_json:
        try:
            data = request.get_json(silent=True, cache=True) or {}
            host_raw = data.get("host_tpv")
        except Exception:
            pass
    if not host_raw:
        host_raw = sess.get("host", "")
    return conn_tpv(host_raw)


@app.route("/api/clientes")
@need_conn
def api_cli_get_clientes():
    """Lista clientes con tipo + direccion de facturacion + provincia.
    ?search filtra por nombre/nif/referencia."""
    search = request.args.get("search", "").strip()
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = """
            SELECT c.*, ct.nombre AS tipo_nombre, ct.referencia AS tipo_ref,
                   cd.direccion, cd.poblacion, cd.codigo_postal, cd.telefono, cd.movil,
                   cd.id_cliente_direccion, cd.id_provincia, p.nombre AS provincia_nombre
            FROM cliente c
            JOIN cliente_tipo ct ON c.id_cliente_tipo = ct.id_cliente_tipo
            LEFT JOIN cliente_direccion cd ON c.id_cliente = cd.id_cliente AND cd.facturacion = true
            LEFT JOIN provincia p ON cd.id_provincia = p.id_provincia
            WHERE c.delete_date IS NULL
        """
        params = []
        if search:
            sql += " AND (c.nombre ILIKE %s OR c.nif ILIKE %s OR c.referencia ILIKE %s)"
            pat = f"%{search}%"
            params = [pat, pat, pat]
        sql += " ORDER BY c.nombre"
        cur.execute(sql, params)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
                elif hasattr(v, "__float__") and not isinstance(v, (int, bool)):
                    d[k] = float(v)
            rows.append(d)
        return jsonify(rows)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_clientes: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer los clientes"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/clientes/<int:id_cliente>")
@need_conn
def api_cli_get_cliente_detalle(id_cliente):
    """Detalle de un cliente con su tipo + direcciones + asociaciones (con
    tarjeta/vehiculo resueltos por JOIN)."""
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT c.*, ct.nombre AS tipo_nombre
            FROM cliente c
            JOIN cliente_tipo ct ON c.id_cliente_tipo = ct.id_cliente_tipo
            WHERE c.id_cliente = %s
        """, (id_cliente,))
        cliente_row = cur.fetchone()
        if not cliente_row:
            return jsonify({"error": "Cliente no encontrado"}), 404

        cur.execute("""
            SELECT cd.*, p.nombre AS provincia_nombre
            FROM cliente_direccion cd
            LEFT JOIN provincia p ON cd.id_provincia = p.id_provincia
            WHERE cd.id_cliente = %s
            ORDER BY cd.facturacion DESC
        """, (id_cliente,))
        direcciones = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT ctv.*,
                   t.pan, t.fecha_alta, t.fecha_caducidad, t.bloqueada,
                   t.lista_negra AS tarjeta_lista_negra,
                   tt.nombre AS tarjeta_tipo_nombre, tt.id_tarjeta_tipo,
                   v.matricula
            FROM cliente_tarjeta_vehiculo ctv
            LEFT JOIN tarjeta t ON ctv.id_tarjeta = t.id_tarjeta
            LEFT JOIN tarjeta_tipo tt ON t.id_tarjeta_tipo = tt.id_tarjeta_tipo
            LEFT JOIN vehiculo v ON ctv.id_vehiculo = v.id_vehiculo
            WHERE ctv.id_cliente = %s AND ctv.delete_date IS NULL
            ORDER BY ctv.update_date DESC
        """, (id_cliente,))
        asociaciones = [dict(r) for r in cur.fetchall()]

        # Serializar fechas/decimals en todas las estructuras
        def _ser(rows):
            for d in rows:
                for k, v in d.items():
                    if hasattr(v, "isoformat"):
                        d[k] = v.isoformat()
                    elif hasattr(v, "__float__") and not isinstance(v, (int, bool)):
                        d[k] = float(v)
            return rows
        cliente = dict(cliente_row)
        _ser([cliente])
        _ser(direcciones)
        _ser(asociaciones)

        cliente["direcciones"]  = direcciones
        cliente["asociaciones"] = asociaciones
        return jsonify(cliente)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_cliente_detalle: {msg}", "warn")
        return jsonify({"error": "No se pudo leer el cliente"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/clientes", methods=["POST"])
@need_conn
@csrf
def api_cli_post_cliente():
    """Crea un cliente. Devuelve id_cliente."""
    data = request.json or {}
    referencia      = data.get("referencia")
    nombre          = data.get("nombre")
    nif             = data.get("nif")
    id_cliente_tipo = data.get("id_cliente_tipo")
    email           = data.get("email")
    aviso           = data.get("aviso")
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            INSERT INTO cliente (referencia, nombre, nif, id_cliente_tipo, email, aviso,
                                 lista_negra, update_date, update_user)
            VALUES (%s, %s, %s, %s, %s, %s, false, NOW(), 'APP')
            RETURNING id_cliente
        """, (referencia, nombre, nif, id_cliente_tipo, email, aviso))
        new_id = cur.fetchone()[0]
        c.commit()
        log(f"cliente creado id={new_id} nombre={nombre!r}", "ok")
        return jsonify({"id_cliente": new_id})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_post_cliente: {msg}", "warn")
        return jsonify({"error": "No se pudo crear el cliente"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/clientes/<int:id_cliente>", methods=["PUT"])
@need_conn
@csrf
def api_cli_put_cliente(id_cliente):
    """Actualiza campos del cliente (nombre, nif, tipo, email, aviso, lista_negra)."""
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            UPDATE cliente
            SET nombre=%s, nif=%s, id_cliente_tipo=%s, email=%s,
                aviso=%s, lista_negra=%s,
                update_date=NOW(), update_user='APP'
            WHERE id_cliente=%s
        """, (
            data.get("nombre"),
            data.get("nif"),
            data.get("id_cliente_tipo"),
            data.get("email"),
            data.get("aviso"),
            bool(data.get("lista_negra")),
            id_cliente,
        ))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_put_cliente: {msg}", "warn")
        return jsonify({"error": "No se pudo actualizar el cliente"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/cliente-tipos")
@need_conn
def api_cli_get_cliente_tipos():
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM cliente_tipo ORDER BY nombre")
        return jsonify([dict(r) for r in cur.fetchall()])
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_cliente_tipos: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer los tipos de cliente"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ── VEHICULOS ────────────────────────────────────────────────────────────────

@app.route("/api/vehiculos")
@need_conn
def api_cli_get_vehiculos():
    search = request.args.get("search", "").strip()
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = "SELECT * FROM vehiculo WHERE delete_date IS NULL"
        params = []
        if search:
            sql += " AND matricula ILIKE %s"
            params = [f"%{search}%"]
        sql += " ORDER BY matricula"
        cur.execute(sql, params)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            rows.append(d)
        return jsonify(rows)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_vehiculos: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer los vehiculos"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/vehiculos", methods=["POST"])
@need_conn
@csrf
def api_cli_post_vehiculo():
    data = request.json or {}
    matricula = data.get("matricula")
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            INSERT INTO vehiculo (matricula, update_date, update_user)
            VALUES (%s, NOW(), 'APP')
            RETURNING id_vehiculo
        """, (matricula,))
        new_id = cur.fetchone()[0]
        c.commit()
        return jsonify({"id_vehiculo": new_id})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_post_vehiculo: {msg}", "warn")
        return jsonify({"error": "No se pudo crear el vehiculo"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/vehiculos/<int:id_vehiculo>", methods=["PUT"])
@need_conn
@csrf
def api_cli_put_vehiculo(id_vehiculo):
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            UPDATE vehiculo SET matricula=%s, update_date=NOW(), update_user='APP'
            WHERE id_vehiculo=%s
        """, (data.get("matricula"), id_vehiculo))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_put_vehiculo: {msg}", "warn")
        return jsonify({"error": "No se pudo actualizar el vehiculo"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ── TARJETAS ─────────────────────────────────────────────────────────────────

@app.route("/api/tarjetas")
@need_conn
def api_cli_get_tarjetas():
    search = request.args.get("search", "").strip()
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = """
            SELECT t.*, tt.nombre AS tipo_nombre
            FROM tarjeta t
            JOIN tarjeta_tipo tt ON t.id_tarjeta_tipo = tt.id_tarjeta_tipo
            WHERE t.delete_date IS NULL
        """
        params = []
        if search:
            sql += " AND t.pan ILIKE %s"
            params = [f"%{search}%"]
        sql += " ORDER BY t.pan"
        cur.execute(sql, params)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            rows.append(d)
        return jsonify(rows)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_tarjetas: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer las tarjetas"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/tarjeta-tipos")
@need_conn
def api_cli_get_tarjeta_tipos():
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM tarjeta_tipo ORDER BY nombre")
        return jsonify([dict(r) for r in cur.fetchall()])
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_tarjeta_tipos: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer los tipos de tarjeta"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/tarjetas", methods=["POST"])
@need_conn
@csrf
def api_cli_post_tarjeta():
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            INSERT INTO tarjeta (pan, pin, fecha_alta, fecha_caducidad, bloqueada,
                                 lista_negra, id_tarjeta_tipo, update_date, update_user)
            VALUES (%s, %s, COALESCE(%s, NOW()), %s, false, false, %s, NOW(), 'APP')
            RETURNING id_tarjeta
        """, (
            data.get("pan"),
            data.get("pin"),
            data.get("fecha_alta"),
            data.get("fecha_caducidad"),
            data.get("id_tarjeta_tipo"),
        ))
        new_id = cur.fetchone()[0]
        c.commit()
        return jsonify({"id_tarjeta": new_id})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_post_tarjeta: {msg}", "warn")
        return jsonify({"error": "No se pudo crear la tarjeta"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/tarjetas/<int:id_tarjeta>", methods=["PUT"])
@need_conn
@csrf
def api_cli_put_tarjeta(id_tarjeta):
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            UPDATE tarjeta
            SET pan=%s, pin=%s, fecha_caducidad=%s, bloqueada=%s, lista_negra=%s,
                id_tarjeta_tipo=%s, update_date=NOW(), update_user='APP'
            WHERE id_tarjeta=%s
        """, (
            data.get("pan"),
            data.get("pin"),
            data.get("fecha_caducidad"),
            bool(data.get("bloqueada")),
            bool(data.get("lista_negra")),
            data.get("id_tarjeta_tipo"),
            id_tarjeta,
        ))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_put_tarjeta: {msg}", "warn")
        return jsonify({"error": "No se pudo actualizar la tarjeta"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ── ASOCIACIONES (cliente_tarjeta_vehiculo) ──────────────────────────────────

@app.route("/api/asociaciones")
@need_conn
def api_cli_get_asociaciones():
    search        = request.args.get("search", "").strip()
    show_deleted  = request.args.get("show_deleted", "").lower() == "true"
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = """
            SELECT ctv.*,
                   c.nombre AS cliente_nombre, c.nif AS cliente_nif, c.referencia AS cliente_referencia,
                   t.pan, t.fecha_alta AS tarjeta_fecha_alta, t.fecha_caducidad AS tarjeta_fecha_caducidad,
                   t.bloqueada AS tarjeta_bloqueada, t.lista_negra AS tarjeta_lista_negra,
                   tt.nombre AS tarjeta_tipo_nombre,
                   v.matricula
            FROM cliente_tarjeta_vehiculo ctv
            JOIN cliente c ON ctv.id_cliente = c.id_cliente
            LEFT JOIN tarjeta t ON ctv.id_tarjeta = t.id_tarjeta
            LEFT JOIN tarjeta_tipo tt ON t.id_tarjeta_tipo = tt.id_tarjeta_tipo
            LEFT JOIN vehiculo v ON ctv.id_vehiculo = v.id_vehiculo
            WHERE 1=1
        """
        params = []
        if not show_deleted:
            sql += " AND ctv.delete_date IS NULL"
        if search:
            sql += (" AND (c.nombre ILIKE %s OR c.nif ILIKE %s OR c.referencia ILIKE %s "
                    "OR t.pan ILIKE %s OR v.matricula ILIKE %s)")
            pat = f"%{search}%"
            params = [pat, pat, pat, pat, pat]
        sql += " ORDER BY ctv.update_date DESC"
        cur.execute(sql, params)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for k, v in d.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            rows.append(d)
        return jsonify(rows)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_asociaciones: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer las asociaciones"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/asociaciones/<int:id_asoc>")
@need_conn
def api_cli_get_asociacion_detalle(id_asoc):
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT ctv.*,
                   c.nombre AS cliente_nombre, c.nif AS cliente_nif,
                   t.pan, tt.nombre AS tarjeta_tipo_nombre,
                   v.matricula
            FROM cliente_tarjeta_vehiculo ctv
            JOIN cliente c ON ctv.id_cliente = c.id_cliente
            LEFT JOIN tarjeta t ON ctv.id_tarjeta = t.id_tarjeta
            LEFT JOIN tarjeta_tipo tt ON t.id_tarjeta_tipo = tt.id_tarjeta_tipo
            LEFT JOIN vehiculo v ON ctv.id_vehiculo = v.id_vehiculo
            WHERE ctv.id_cliente_tarjeta_vehiculo = %s
        """, (id_asoc,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Asociacion no encontrada"}), 404
        d = dict(row)
        for k, v in d.items():
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        return jsonify(d)
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_asociacion_detalle: {msg}", "warn")
        return jsonify({"error": "No se pudo leer la asociacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/asociaciones", methods=["POST"])
@need_conn
@csrf
def api_cli_post_asociacion():
    data = request.json or {}
    id_cliente  = data.get("id_cliente")
    id_tarjeta  = data.get("id_tarjeta") or None
    id_vehiculo = data.get("id_vehiculo") or None
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        # Validar que la tarjeta/vehiculo no este ya asignada a otro cliente activo
        if id_tarjeta:
            cur.execute("""
                SELECT id_cliente_tarjeta_vehiculo FROM cliente_tarjeta_vehiculo
                WHERE id_tarjeta=%s AND delete_date IS NULL
            """, (id_tarjeta,))
            if cur.fetchone():
                return jsonify({"error": "Esa tarjeta ya esta asignada a otro cliente"}), 400
        if id_vehiculo:
            cur.execute("""
                SELECT id_cliente_tarjeta_vehiculo FROM cliente_tarjeta_vehiculo
                WHERE id_vehiculo=%s AND delete_date IS NULL
            """, (id_vehiculo,))
            if cur.fetchone():
                return jsonify({"error": "Ese vehiculo ya esta asignado a otro cliente"}), 400
        cur.execute("""
            INSERT INTO cliente_tarjeta_vehiculo (id_cliente, id_tarjeta, id_vehiculo,
                                                  update_date, update_user)
            VALUES (%s, %s, %s, NOW(), 'APP')
            RETURNING id_cliente_tarjeta_vehiculo
        """, (id_cliente, id_tarjeta, id_vehiculo))
        new_id = cur.fetchone()[0]
        c.commit()
        return jsonify({"id": new_id})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_post_asociacion: {msg}", "warn")
        return jsonify({"error": "No se pudo crear la asociacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/asociaciones/<int:id_asoc>", methods=["PUT"])
@need_conn
@csrf
def api_cli_put_asociacion(id_asoc):
    data = request.json or {}
    id_cliente  = data.get("id_cliente")
    id_tarjeta  = data.get("id_tarjeta") or None
    id_vehiculo = data.get("id_vehiculo") or None
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        if id_tarjeta:
            cur.execute("""
                SELECT id_cliente_tarjeta_vehiculo FROM cliente_tarjeta_vehiculo
                WHERE id_tarjeta=%s AND delete_date IS NULL
                  AND id_cliente_tarjeta_vehiculo != %s
            """, (id_tarjeta, id_asoc))
            if cur.fetchone():
                return jsonify({"error": "Esa tarjeta ya esta asignada a otro cliente"}), 400
        if id_vehiculo:
            cur.execute("""
                SELECT id_cliente_tarjeta_vehiculo FROM cliente_tarjeta_vehiculo
                WHERE id_vehiculo=%s AND delete_date IS NULL
                  AND id_cliente_tarjeta_vehiculo != %s
            """, (id_vehiculo, id_asoc))
            if cur.fetchone():
                return jsonify({"error": "Ese vehiculo ya esta asignado a otro cliente"}), 400
        cur.execute("""
            UPDATE cliente_tarjeta_vehiculo
            SET id_cliente=%s, id_tarjeta=%s, id_vehiculo=%s,
                update_date=NOW(), update_user='APP'
            WHERE id_cliente_tarjeta_vehiculo=%s
        """, (id_cliente, id_tarjeta, id_vehiculo, id_asoc))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_put_asociacion: {msg}", "warn")
        return jsonify({"error": "No se pudo actualizar la asociacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/asociaciones/<int:id_asoc>", methods=["DELETE"])
@need_conn
@csrf
def api_cli_delete_asociacion(id_asoc):
    """Soft delete: marca delete_date. Acepta `fecha_baja` opcional en el body."""
    data = request.json or {}
    fecha_baja = data.get("fecha_baja")
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        if fecha_baja:
            cur.execute("""
                UPDATE cliente_tarjeta_vehiculo
                SET delete_date=%s, update_user='APP'
                WHERE id_cliente_tarjeta_vehiculo=%s
            """, (fecha_baja, id_asoc))
        else:
            cur.execute("""
                UPDATE cliente_tarjeta_vehiculo
                SET delete_date=NOW(), update_user='APP'
                WHERE id_cliente_tarjeta_vehiculo=%s
            """, (id_asoc,))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_delete_asociacion: {msg}", "warn")
        return jsonify({"error": "No se pudo dar de baja la asociacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/asociaciones/<int:id_asoc>/restore", methods=["PATCH"])
@need_conn
@csrf
def api_cli_restore_asociacion(id_asoc):
    """Reactiva una asociacion previamente borrada (delete_date = NULL)."""
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            UPDATE cliente_tarjeta_vehiculo
            SET delete_date=NULL, update_date=NOW(), update_user='APP'
            WHERE id_cliente_tarjeta_vehiculo=%s
        """, (id_asoc,))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_restore_asociacion: {msg}", "warn")
        return jsonify({"error": "No se pudo restaurar la asociacion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ── PROVINCIAS ───────────────────────────────────────────────────────────────

@app.route("/api/provincias")
@need_conn
def api_cli_get_provincias():
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM provincia ORDER BY nombre")
        return jsonify([dict(r) for r in cur.fetchall()])
    except Exception as e:
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_get_provincias: {msg}", "warn")
        return jsonify({"error": "No se pudieron leer las provincias"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


# ── DIRECCIONES ──────────────────────────────────────────────────────────────

@app.route("/api/clientes/<int:id_cliente>/direcciones", methods=["POST"])
@need_conn
@csrf
def api_cli_post_direccion(id_cliente):
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            INSERT INTO cliente_direccion (id_cliente, direccion, poblacion, codigo_postal,
                                           id_provincia, telefono, movil, facturacion,
                                           update_date, update_user)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'APP')
            RETURNING id_cliente_direccion
        """, (
            id_cliente,
            data.get("direccion"),
            data.get("poblacion"),
            data.get("codigo_postal"),
            data.get("id_provincia"),
            data.get("telefono"),
            data.get("movil"),
            bool(data.get("facturacion")),
        ))
        new_id = cur.fetchone()[0]
        c.commit()
        return jsonify({"id_cliente_direccion": new_id})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_post_direccion: {msg}", "warn")
        return jsonify({"error": "No se pudo crear la direccion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


@app.route("/api/direcciones/<int:id_direccion>", methods=["PUT"])
@need_conn
@csrf
def api_cli_put_direccion(id_direccion):
    data = request.json or {}
    c = None
    try:
        c = _cli_conn()
        cur = c.cursor()
        cur.execute("""
            UPDATE cliente_direccion
            SET direccion=%s, poblacion=%s, codigo_postal=%s, id_provincia=%s,
                telefono=%s, movil=%s, facturacion=%s,
                update_date=NOW(), update_user='APP'
            WHERE id_cliente_direccion=%s
        """, (
            data.get("direccion"),
            data.get("poblacion"),
            data.get("codigo_postal"),
            data.get("id_provincia"),
            data.get("telefono"),
            data.get("movil"),
            bool(data.get("facturacion")),
            id_direccion,
        ))
        c.commit()
        return jsonify({"ok": True})
    except Exception as e:
        if c:
            try: c.rollback()
            except Exception: pass
        msg = str(e).split("\n")[0]
        log(f"WARN api_cli_put_direccion: {msg}", "warn")
        return jsonify({"error": "No se pudo actualizar la direccion"}), 500
    finally:
        if c:
            try: c.close()
            except Exception: pass


def _nav():
    import time; time.sleep(1.3)
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    log(f"GARUM TPV Manager v7.3 en http://{HOST}:{PORT}", "info")
    log(f"psycopg2: {PSYCOPG2_OK}", "info" if PSYCOPG2_OK else "warn")
    threading.Thread(target=_nav, daemon=True).start()
    # threaded=True explicito para no depender de defaults futuros de Flask.
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
