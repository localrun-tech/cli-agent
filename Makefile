.DEFAULT_GOAL := help

help:
	@echo "LocalRun Agent - Build Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make build      Compile TypeScript"
	@echo "  make pack       Build standalone binaries (arm64 + x64)"
	@echo "  make dev        Link for development"
	@echo "  make clean      Remove build artifacts"
	@echo ""

install:
	cd macos && npm install

build:
	cd macos && npm run build

pack: build
	cd macos && npx oclif pack tarballs --targets darwin-arm64,darwin-x64

dev: build
	cd macos && npm link

clean:
	cd macos && rm -rf dist tmp node_modules *.tgz *.tar.gz *.tar.xz oclif.manifest.json
