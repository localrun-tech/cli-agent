.DEFAULT_GOAL := help

help:
	@echo "LocalRun Agent - Build Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make build-mac  Compile TypeScript"
	@echo "  make pack       Build standalone binaries (arm64 + x64)"
	@echo "  make dev        Link for development"
	@echo "  make clean      Remove build artifacts"
	@echo ""

macos-install:
	cd macos && npm install

macos-build:
	cd macos && npm run build

macos-pack: macos-build
	cd macos && npx oclif pack tarballs --targets darwin-arm64,darwin-x64

macos-dev: macos-build
	cd macos && npm link

macos-clean:
	cd macos && rm -rf dist tmp node_modules *.tgz *.tar.gz *.tar.xz oclif.manifest.json
