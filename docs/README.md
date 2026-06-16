# Forge Senior Project Portfolio

Forge is a Python desktop fitness and health tracking application developed as the Senior Project for CST-451 and CST-452 at Grand Canyon University.

This repository includes the Forge application source code and an internet-facing senior project portfolio website that summarizes the project background, implementation approach, design artifacts, code examples, screenshots, presentation video, supporting documentation, and executable build.

## Live Portfolio Website

The Forge project portfolio is hosted with GitHub Pages:

https://mrspoopyskeltal.github.io/Forge/

## Presentation Video

Final project presentation:

https://www.youtube.com/watch?v=RlTXyfMjoRw

## GitHub Repository

Project repository:

https://github.com/MrSpoopySkeltal/Forge

## Project Overview

Forge was created as a desktop application for tracking personal fitness information. The application allows users to create a profile, calculate health and nutrition metrics, generate macro targets, log strength workouts, review workout history, track cardio activity, estimate calories burned, and manage saved records through a local desktop interface.

The project was built to demonstrate the full senior project lifecycle, including planning, implementation, testing, documentation, final presentation, and public portfolio deployment.

## Main Features

- User profile setup and local profile persistence
- BMI, BMR, and TDEE calculations
- Goal-based macro target recommendations
- Strength workout logging
- Workout history viewing and management
- Progressive overload recommendations based on workout history
- Cardio activity tracking
- MET-based estimated calorie burn using saved profile weight
- Cardio history viewing and management
- Local JSON storage for profile, workout, and cardio data
- Dark-mode desktop interface with rounded-button navigation
- Packaged Windows executable build
- Public senior project portfolio website

## Technology Stack

- Python
- Tkinter
- JSON-based local persistence
- Modular application structure
- GitHub for source control
- GitHub Pages for portfolio hosting
- HTML, CSS, and JavaScript for the portfolio website

## Application Structure

The Forge application is organized into separate modules:

- `main.py` - Application entry point
- `ui.py` - Main graphical user interface and screen navigation
- `models.py` - Data models for user profiles, workout entries, and cardio entries
- `storage.py` - Local JSON save/load logic and record management
- `calculations.py` - BMI, BMR, TDEE, macro target, progressive overload, and cardio calorie calculation logic

This modular structure separates the user interface, data models, storage logic, and calculation logic so that the application is easier to maintain, test, and expand.

## Portfolio Website Contents

The portfolio website is located in the `docs/` folder and includes:

- Project overview and background
- Main Forge feature summaries
- Application flow, component/module, and data/calculation diagrams
- Screenshots for the dashboard, profile setup, metrics and macros tracker, workout tracker, workout history, cardio tracker, and cardio history
- Code snippets demonstrating major implementation logic
- Final project presentation video link
- Supporting milestone artifacts
- Downloadable Windows executable build
- Instructions for running the project

## Supporting Documentation

The portfolio website links to the following supporting artifacts:

- Implementation Plan, Functional Requirement Mapping, and Source Code Listing
- Forge Test Cases
- Forge Traceability Matrix
- Final project presentation video
- Executable build

These files are included under the portfolio site's `assets/docs/` and `assets/downloads/` folders.

## How to Run Forge

### Option 1: Run the Packaged Windows Executable

1. Open the live portfolio website.
2. Go to the **How to Run Forge** or **Supporting Artifacts** section.
3. Download `Forge_Executable.zip`.
4. Extract the ZIP file.
5. Run the Forge executable from the extracted folder.

Note: The executable is intended for Windows. If Windows displays a security warning, only continue if the file was downloaded from this official project portfolio or the official GitHub repository.

### Option 2: Run From Source

Clone the repository:

```bash
git clone https://github.com/MrSpoopySkeltal/Forge.git
```

Navigate into the project folder and run the application entry point:

```bash
cd Forge/Forge
python app/main.py
```

If your local Python environment requires it, use `python3` instead of `python`.

## GitHub Pages Deployment

The portfolio website is deployed from the `docs/` folder using GitHub Pages.

Deployment settings:

- Source: Deploy from a branch
- Branch: `main`
- Folder: `/docs`

The `docs/` folder includes the static portfolio site files and a `.nojekyll` file to ensure the plain HTML/CSS/JavaScript site is served correctly.

## Senior Project Completion

Forge demonstrates the completed work from the CST-451 and CST-452 senior project sequence. The project includes functional application development, expanded cardio tracking, health and nutrition calculations, persistent data storage, user interface refinement, final testing, project documentation, an executable build, and a public portfolio website suitable for review by instructors and potential employers.

## Author

Yaroslav Morozov  
Grand Canyon University  
Bachelor of Science in Software Development  
CST-451 / CST-452 Senior Project
