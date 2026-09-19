# Contributing to Indian Railway Data

Thank you for your interest in contributing to this open-source Indian Railway dataset! Our goal is to maintain an accurate, comprehensive, and up-to-date repository of stations, schedules, routes, and geographic data.

---

## 🛠️ How You Can Contribute

1. **Station Corrections & Additions**:
   - Add newly inaugurated stations or halts.
   - Update / fix incorrect coordinates (latitude/longitude), zone codes, or state names.
   
2. **Train Schedule & Route Updates**:
   - Add new trains (e.g., new Vande Bharat, Amrit Bharat, or Express services).
   - Update altered train routes, timetable timings, or stoppage changes.

3. **Code Examples & Utilities**:
   - Add useful Python, JavaScript, Go, or R scripts demonstrating route search, graphs, or GIS analysis.
   - Improve existing scripts in the `examples/` directory.

---

## 📋 Contribution Guidelines

### 1. Structure Consistency
- When editing `stations.json` or `trains.json`, ensure the schema and field formats match the existing structure documented in [`README.md`](./README.md).
- Keep JSON formatted with standard 2-space indentation.
- Ensure latitude and longitude coordinates are valid decimal degrees (WGS84).

### 2. Submitting a Pull Request
1. Fork the repository.
2. Create a meaningful branch: `git checkout -b feature/add-new-station` or `git checkout -b fix/train-route-12951`.
3. Test your changes using standard JSON validation (e.g., `python -m json.tool stations.json > /dev/null`).
4. Commit your changes with clear messages: `git commit -m "Update schedule for train 12951"`.
5. Push to your fork: `git push origin feature/add-new-station`.
6. Open a Pull Request on GitHub describing the exact changes made and any official sources (e.g., Indian Railways press releases, NTES, IRCTC).

---

## 🐛 Reporting Issues

If you find discrepancies or outdated information but are unable to submit a PR:
- Open an **Issue** on GitHub with the label `data-correction` or `enhancement`.
- Please provide train numbers or station codes along with verification links/sources.
