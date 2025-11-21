# fandanGO-cryoem-dls

**Diamond Light Source FandanGO Plugin for Cryo-EM Metadata Deposition**

[![Maintained by DLS](https://img.shields.io/badge/maintained%20by-Diamond%20Light%20Source-blue)](https://github.com/DiamondLightSource)
[![Part of FandanGO](https://img.shields.io/badge/part%20of-FandanGO%20ecosystem-green)](https://github.com/orgs/FragmentScreen/repositories)

---

## Repository Status

> **⚠️ Source of Truth**: This repository (`DiamondLightSource/fandanGO-cryoem-dls`) is the **authoritative source** maintained by Diamond Light Source.
>
> **🔄 FragmentScreen Fork**: A mirror/fork exists at `FragmentScreen/fandanGO-cryoem-dls` for ecosystem visibility and discoverability. All development and issue tracking should occur in this repository.

---

## Overview

FandanGO plugin for integrating Diamond Light Source (DLS) cryo-EM metadata from the SmartEM decision system into the ARIA data deposition platform.

This plugin enables the extraction, management, and deposition of cryo-EM experimental metadata from DLS's SmartEM system into ARIA for centralized tracking and sharing within the Fragment Screen / WP4 ecosystem.

### Key Features

- **SmartEM Integration**: Extracts complete hierarchical metadata from DLS's SmartEM API
- **ARIA Deposition**: Submits structured metadata to ARIA with embargo controls
- **Extract → Transform → Load**: Clean architecture for metadata pipeline
- **Facility-Specific**: DLS-maintained plugin following FandanGO facility pattern

### Related Repositories

#### This Project
- **SmartEM Decisions** (DLS): [DiamondLightSource/smartem-decisions](https://github.com/DiamondLightSource/smartem-decisions)
  - Source system for cryo-EM metadata at DLS
  - Provides REST API for metadata extraction

#### FandanGO Ecosystem (FragmentScreen)
- **FandanGO Core**: [FragmentScreen/fandanGO-core](https://github.com/FragmentScreen/fandanGO-core)
  - Plugin framework and CLI foundation
- **FandanGO ARIA**: [FragmentScreen/fandanGO-aria](https://github.com/FragmentScreen/fandanGO-aria)
  - ARIA API client for metadata deposition
- **FandanGO Samples**: [FragmentScreen/Samples](https://github.com/FragmentScreen/Samples)
  - Example metadata formats and templates

#### Similar Facility Plugins
- **CNB Cryo-EM Plugin**: [FragmentScreen/fandanGO-cryoem-cnb](https://github.com/FragmentScreen/fandanGO-cryoem-cnb)
  - CNB-CSIC (Madrid) cryo-EM integration via Scipion
- **CERM NMR Plugin**: [FragmentScreen/fandanGO-nmr-cerm](https://github.com/FragmentScreen/fandanGO-nmr-cerm)
  - CERM (Florence) NMR metadata integration
- **GUF NMR Plugin**: [FragmentScreen/fandanGO-nmr-guf](https://github.com/FragmentScreen/fandanGO-nmr-guf)
  - GUF University (Frankfurt) NMR integration

## Architecture

The plugin follows the **Extract → Transform → Load** pattern:

```
┌─────────────────┐
│ smartem-decisions│  ← DLS data source (REST API)
│   (DLS server)   │
└────────┬─────────┘
         │ HTTP API
         │
    ┌────▼──────────────┐
    │ fandanGO-cryoem-dls│  ← This plugin (client)
    │   (this plugin)    │
    └────┬──────────────┘
         │ HTTP API
         │
┌────────▼─────┐
│     ARIA     │  ← FragmentScreen metadata repository
│   (remote)   │
└──────────────┘
```

**Stages:**
1. **Extract**: Fetch metadata from SmartEM API
   - Acquisitions (sessions)
   - Grids → Grid Squares → Foil Holes → Micrographs
   - Quality metrics and imaging parameters
   - Atlas images and tiles

2. **Transform**: Structure data into ARIA-compatible JSON
   - DLS_CRYOEM schema namespace
   - Hierarchical metadata organization
   - Proper field typing and serialization

3. **Load**: Submit to ARIA with embargo controls
   - Create embargoed data buckets (3-year default)
   - Link to ARIA visit records
   - Store data location references

## Installation

### Prerequisites

- Python 3.8 or higher
- Access to SmartEM API (DLS network or VPN)
- ARIA credentials (from Fragment Screen consortium)
- FandanGO dependencies:
  - `fandanGO-core`
  - `fandanGO-aria`

### Install from Source

```bash
# Clone the repository
git clone https://github.com/DiamondLightSource/fandanGO-cryoem-dls.git
cd fandanGO-cryoem-dls

# Install in development mode
pip install -e .
```

### Configuration

1. **Copy configuration templates:**
   ```bash
   cp config.yaml.template config.yaml
   cp .env.template .env
   ```

2. **Edit `config.yaml`:**
   ```ini
   [DDBB]
   DDBB_PATH = /home/user/FandanGOUserData

   [SMARTEM]
   API_URL = http://smartem-api.diamond.ac.uk:8000
   ```

3. **Edit `.env` with ARIA credentials:**
   ```bash
   ARIA_CONNECTION_USERNAME=your_username
   ARIA_CONNECTION_PASSWORD=your_password
   ARIA_FACILITY_ID=your_facility_id
   ARIA_CLIENT_SECRET=your_client_secret
   ```

   > **Note**: ARIA credentials are provided by the Fragment Screen consortium. Contact the ARIA team for access.

### SmartEM Integration

If `smartem-decisions` is not installed as a package:

```bash
# Add smartem-decisions to PYTHONPATH
export PYTHONPATH=/path/to/smartem-decisions/src:$PYTHONPATH
```

Or install smartem-decisions:
```bash
pip install git+https://github.com/DiamondLightSource/smartem-decisions.git
```

## Usage

### Workflow

#### 1. Extract Metadata from SmartEM

```bash
fandango generate-metadata <project_name> --acquisition-id <acquisition_uuid>
```

**What it does:**
- Connects to SmartEM API
- Fetches complete acquisition hierarchy:
  - Acquisition (session) metadata
  - All grids in the acquisition
  - Grid squares with spatial coordinates
  - Foil holes with quality predictions
  - Micrographs with imaging parameters
  - Atlas images and tiles
- Stores metadata locally in SQLite database

**Example:**
```bash
fandango generate-metadata my_project \
  --acquisition-id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Output:**
```
FandanGO will extract metadata from SmartEM for project my_project...
... connecting to SmartEM API at http://smartem-api.diamond.ac.uk:8000
... extracting metadata for acquisition a1b2c3d4-e5f6-7890-abcd-ef1234567890
... successfully extracted metadata for 5 grids, 127 grid squares
```

#### 2. Send Metadata to ARIA

```bash
fandango send-metadata <project_name> --visit-id <aria_visit_id>
```

**What it does:**
- Retrieves stored metadata from local database
- Authenticates with ARIA
- Creates embargoed data bucket (3-year embargo)
- Creates `DLS_CRYOEM` record with SmartEM metadata
- Links to specified ARIA visit record

**Example:**
```bash
fandango send-metadata my_project --visit-id 12345
```

**Output:**
```
FandanGO will send metadata for my_project project to ARIA...
Successfully sent metadata for project my_project to ARIA!
```

#### 3. View Project Information

```bash
fandango print-project <project_name>
```

Displays all stored information for a project in a formatted table.

### Complete Example Session

```bash
# 1. Extract metadata from SmartEM
fandango generate-metadata dls_session_001 \
  --acquisition-id a1b2c3d4-e5f6-7890-abcd-ef1234567890

# 2. Verify extraction
fandango print-project dls_session_001

# 3. Submit to ARIA
fandango send-metadata dls_session_001 --visit-id 12345

# Success! Metadata is now in ARIA with 3-year embargo
```

## Metadata Structure

The metadata sent to ARIA follows this hierarchical structure:

```json
{
  "acquisition": {
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Session_2024-11-20",
    "start_time": "2024-11-20T10:30:00Z",
    "instrument": {
      "instrument_model": "Titan Krios",
      "instrument_id": "TK-01",
      "computer_name": "epu-workstation-01"
    },
    "storage_path": "/dls/em/data/2024/..."
  },
  "grids": [
    {
      "grid_info": {
        "uuid": "grid-uuid-1",
        "name": "Grid_1",
        "status": "completed"
      },
      "grid_squares": [
        {
          "grid_square_info": {
            "uuid": "gs-uuid-1",
            "gridsquare_id": 1,
            "center_x": 0.5,
            "center_y": 0.5,
            "defocus": -2.0,
            "magnification": 165000,
            "pixel_size": 0.85,
            "detector_name": "Falcon 4i"
          },
          "foil_holes": [
            {
              "foil_hole_info": {
                "uuid": "fh-uuid-1",
                "quality": 0.85,
                "diameter": 1.2
              },
              "micrographs": [
                {
                  "uuid": "mic-uuid-1",
                  "high_res_path": "/dls/em/.../image_001.mrc",
                  "defocus": -2.0,
                  "image_size_x": 4096,
                  "image_size_y": 4096
                }
              ]
            }
          ],
          "quality_prediction": {
            "prediction": 0.75,
            "model_version": "v1.0"
          }
        }
      ],
      "atlas": {
        "uuid": "atlas-uuid-1",
        "name": "Atlas_Grid_1",
        "tiles": [...]
      }
    }
  ]
}
```

See [ARIA_SCHEMA.md](docs/ARIA_SCHEMA.md) for complete ARIA deposition schema documentation.

## Development

### Project Structure

```
fandanGO-cryoem-dls/
├── fandango_dls/
│   ├── __init__.py              # Plugin class definition
│   ├── constants.py             # Action and config constants
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── generate_metadata.py # SmartEM extraction
│   │   ├── send_metadata.py     # ARIA submission
│   │   └── print_project.py     # Display project info
│   ├── db/
│   │   ├── __init__.py
│   │   ├── sqlite.py            # Database connection
│   │   └── sqlite_db.py         # Database operations
│   └── utils/
│       ├── __init__.py
│       └── smartem_client.py    # SmartEM API wrapper
├── setup.py                     # Package configuration
├── requirements.txt             # Python dependencies
├── config.yaml.template         # Configuration template
├── .env.template                # Environment variables template
└── README.md                    # This file
```

### Comparison with Other Plugins

| Aspect | CNB Plugin | DLS Plugin |
|--------|------------|------------|
| **Metadata Source** | Scipion JSON files (pre-generated) | SmartEM REST API (live queries) |
| **Data Storage** | iRODS upload with access tickets | Reference to DLS storage |
| **Metadata Format** | OSCEM JSON standard | SmartEM hierarchical JSON |
| **API Client** | File system reading | SmartEMAPIClient (HTTP) |
| **Actions** | copy-data, generate-metadata, send-metadata | generate-metadata, send-metadata |
| **Schema Type** | `OSCEM` | `DLS_CRYOEM` |

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=fandango_dls tests/
```

## Deployment

The plugin can be deployed:

1. **At DLS alongside SmartEM** - Convenient for local API access
2. **On a dedicated integration server** - Separate from both SmartEM and ARIA
3. **Any location with network access** - Requires connectivity to both APIs

**Requirements:**
- Network access to SmartEM API (DLS network/VPN)
- Network access to ARIA API (internet)
- Python environment with fandanGO installed
- ARIA credentials configured

## Troubleshooting

### SmartEM API Connection Issues

**Error:** `SmartEM client not available`

**Solutions:**
- Ensure `smartem-decisions` is installed or in `PYTHONPATH`
- Check SmartEM API URL in `config.yaml`
- Verify network connectivity to SmartEM API
- Check VPN connection if accessing remotely

### ARIA Authentication Issues

**Error:** `ARIA login failed`

**Solutions:**
- Verify credentials in `.env` file
- Check `ARIA_FACILITY_ID` is set correctly
- Ensure `ARIA_CLIENT_SECRET` is configured
- Contact ARIA team to verify account status

### No Metadata Found

**Error:** `No metadata found for project`

**Solutions:**
- Run `generate-metadata` before `send-metadata`
- Use `print-project` to verify metadata was extracted
- Verify the acquisition UUID exists in SmartEM
- Check SmartEM API is accessible

### Permission Errors

**Error:** Cannot write to database

**Solutions:**
- Check `DDBB_PATH` in `config.yaml` exists
- Verify write permissions to database directory
- Ensure directory is not read-only

## Contributing

Contributions are welcome! This is an open-source project maintained by Diamond Light Source for the Fragment Screen community.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for public functions
- Keep functions focused and testable

## Governance

- **Maintained by**: Diamond Light Source Scientific Software team
- **Primary contact**: scientificsoftware@diamond.ac.uk
- **Issue tracking**: GitHub Issues in this repository
- **Part of**: FragmentScreen FandanGO ecosystem
- **License**: [To be specified]

## Acknowledgments

- **FandanGO Framework**: Fragment Screen consortium
- **SmartEM System**: Diamond Light Source Electron Microscopy team
- **ARIA Platform**: Structural biology data repository
- **Fragment Screen**: European structural biology infrastructure project

## Citation

If you use this plugin in your research, please cite:

```
[Citation to be added]
```

## Links

### This Project
- **Repository**: https://github.com/DiamondLightSource/fandanGO-cryoem-dls
- **Issues**: https://github.com/DiamondLightSource/fandanGO-cryoem-dls/issues
- **SmartEM**: https://github.com/DiamondLightSource/smartem-decisions

### FandanGO Ecosystem
- **FragmentScreen Organization**: https://github.com/orgs/FragmentScreen/repositories
- **FandanGO Core**: https://github.com/FragmentScreen/fandanGO-core
- **FandanGO ARIA**: https://github.com/FragmentScreen/fandanGO-aria
- **ARIA Platform**: https://beta.structuralbiology.eu

### Diamond Light Source
- **DLS GitHub**: https://github.com/DiamondLightSource
- **DLS Website**: https://www.diamond.ac.uk
- **Electron Microscopy**: https://www.diamond.ac.uk/Instruments/Imaging-and-Microscopy/eBIC.html
