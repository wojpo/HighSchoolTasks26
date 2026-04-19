# 🎓 High School Tasks 26

Tasks for the 3rd edition of Hack4Krak CTF!

> [!CAUTION]
> This repository contains **solutions** for CTF tasks!\
> Remember to **never** share this repository with anyone outside the **High School Tasks 26** team!
> 
> *If this leaks, I will hunt you down - and you will be forced to use nothing but Windows, Copilot, and Edge for the rest of your tragically short life.*

## Documentation

You can read about how to configure each task in [STRUCTURE.md](docs/STRUCTURE.md).\
Each task must be properly tested before submission - both manually and by writing automated tests, as described in [TESTING.md](docs/TESTING.md).

And if your name begins with `N` and ends with `orbiros`, and you are responsible for deploying tasks, check out [DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Architecture
- [tasks/](tasks/) - configuration for all tasks
- [config/](config/) - configuration for the specific CTF event
- [toolbox/](toolbox/) - our custom CLI for working with this repository
- [docs/](docs/) - documentation

## Development
*Required only for running Hack4Krak Toolbox*

### 1. Download all required dependencies
```shell
uv sync
```

### 2. Run CLI
```shell
uv run toolbox 
```