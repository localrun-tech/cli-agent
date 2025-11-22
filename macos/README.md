# LocalRun Agent (OCLIF)

Agente nativo para macOS construido con OCLIF/Node.js. Proporciona acceso local al sistema para el dashboard de LocalRun.

## Instalación Rápida

```bash
npm install
npm run build
npm link  # Instala globalmente en modo desarrollo
```

## Desarrollo

```bash
# Build
npm run build

# Desarrollo (auto-rebuild)
npm run dev

# Lint
npm run lint

# Tests
npm test
```

## Comandos Disponibles

```bash
# Instalar como LaunchAgent (servicio de sistema)
localrun install

# Iniciar servicio
localrun start

# Detener servicio
localrun stop

# Ver estado
localrun status

# Ver logs
localrun logs
localrun logs -f  # Seguir en tiempo real

# Servidor HTTP (usado por LaunchAgent)
localrun serve --port 47777

# Desinstalar
localrun uninstall

# Ayuda
localrun --help
localrun COMMAND --help
```

## Distribución

### Generar binarios para macOS

```bash
# Requiere oclif CLI
npm install -g oclif

# Generar tarball con binarios
npm run pack:tarballs

# Generar instalador .pkg para macOS
npm run pack:macos
```

Los binarios se generan en `dist/` y tarballs en `dist/localrun-agent-v{version}/`.

## Estructura

```
agent/macos/
├── src/
│   ├── commands/        # Comandos CLI (install, start, stop, etc)
│   ├── lib/
│   │   └── system/      # Módulos del sistema (host, ports, docker)
│   └── index.ts
├── bin/                 # Scripts de ejecución
├── dist/                # Código compilado (TypeScript → JS)
└── package.json
```

## API del Servidor

Cuando se ejecuta `localrun serve`, expone una API HTTP:

- `GET /api/ping` - Health check
- `GET /api/host/info` - Información del host
- `GET /api/host/ports` - Puertos abiertos
- `GET /api/host/processes` - Procesos activos
- `GET /api/docker/containers` - Contenedores Docker

Por defecto escucha en `http://127.0.0.1:47777`

## Build Time

- Primera compilación: ~3-5 segundos
- Compilaciones incrementales: ~1-2 segundos
- Build de binarios (oclif pack): ~10-15 segundos

## Ventajas vs Python/PyInstaller

✅ Builds 20-30x más rápidos  
✅ Ecosistema npm maduro  
✅ Binarios más pequeños  
✅ Desarrollo más ágil  
✅ Mejor DX con TypeScript
