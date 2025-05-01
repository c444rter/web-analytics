# CMSI 4072: Senior Project II  
# Software Requirements Specification

---

## Table of Contents

1. [5.1 Requirements Introduction](#51-requirements-introduction)  
2. [5.2 Functional Requirements](#52-functional-requirements)  
   - [5.2.1 Graphical User Interface](#521-graphical-user-interface)  
     - [5.2.1.1 GUI Menu System](#5211-gui-menu-system)  
     - [5.2.1.2 GUI Button Widgets](#5212-gui-button-widgets)  
     - [5.2.1.3 GUI Shortcut Keys](#5213-gui-shortcut-keys)  
     - [5.2.1.4 File Open Operation](#5214-file-open-operation)  
3. [5.3 Performance and Non‑Functional Requirements](#53-performance-and-non-functional-requirements)  
   - [5.3.1 Performance Requirements](#531-performance-requirements)  
     - [5.3.1.1 Search Results Return Time](#5311-search-results-return-time)  
     - [5.3.1.2 Bulk Data Ingestion Performance](#5312-bulk-data-ingestion-performance)  
   - [5.3.2 Security, Scalability, and Usability Requirements](#532-security-scalability-and-usability-requirements)
4. [5.4 Environment and Deployment Requirements](#54-environment-and-deployment-requirements)  
   - [5.4.1 Development Environment Requirements](#541-development-environment-requirements)  
   - [5.4.2 Execution Environment Requirements](#542-execution-environment-requirements)  
5. [Appendices](#appendices)  
6. [Acronyms and Abbreviations](#acronyms-and-abbreviations)  
7. [Future Enhancements](#future-enhancements)

---

## 5.1 Requirements Introduction

The purpose of this document is to specify in precise detail the software to be developed for the Shopify Analytics App. This SRS serves as a contract between the customer and the solution provider by ensuring that both parties have a common understanding of the application’s functionality, performance, environment, and non‑functional requirements.

**System Overview:**  
The system provides a backend solution built with FastAPI, PostgreSQL, and Redis to import and process Shopify export files (in CSV, Excel, JSON, or ZIP formats). It optimizes ingestion by using bulk inserts and real‑time progress tracking so that large datasets (e.g., around 13,000 records) can be processed in under 30 seconds. A React/Next.js frontend displays an analytics dashboard featuring customizable KPI widgets, drag‑and‑drop capabilities, and interactive data visualizations. The system also includes machine learning capabilities for sales forecasting, including style-based forecasting that predicts future sales by product style categories. The overall design ensures responsiveness, scalability, and secure handling of sensitive data.

A high-level UML diagram for this system would illustrate:
- **Frontend:** Next.js React app with responsive dashboards, an upload page, and a dynamic menu system.
- **Backend:** FastAPI service with endpoints for uploads, real‑time analytics, status, and historical data retrieval.
- **Data Storage:** PostgreSQL (for orders, uploads, and analytics data) with appropriate indexing.
- **Background Processing:** RQ (Redis Queue) to manage file processing jobs.
- **Cache & PubSub:** Redis for job management and caching, aiding scalability and performance.

---

## 5.2 Functional Requirements

This section documents the functions that the system must perform.

### 5.2.1 Graphical User Interface

The GUI provides users with an intuitive way to interact with the system. The primary functions include file uploads, dashboard views, and historical upload selection.

#### 5.2.1.1 GUI Menu System

- **Requirement:** The GUI **shall** provide a menu system to navigate between the Upload screen, Analytics Dashboard, Historical Uploads, and User Account Management.  
- **Notes:** A common Navbar (e.g., using Material‑UI AppBar) will be implemented to switch between screens.

#### 5.2.1.2 GUI Button Widgets

- **Requirement:** The GUI **shall** contain button widgets for file selection, file upload initiation, and dashboard mode selection.  
- **Notes:** Buttons such as “Upload”, “Load Selected KPIs”, and mode choices (Default vs. Custom KPI) are provided.

#### 5.2.1.3 GUI Shortcut Keys

- **Requirement:** The GUI **shall** support keyboard shortcuts to streamline operations such as file uploads and navigation between dashboard screens.  
- **Notes:** Shortcut keys increase efficiency for power users and will be clearly documented.

#### 5.2.1.4 File Open Operation

- **Requirement:** The File Open operation **shall** display a file chooser dialog that allows the user to select a Shopify export file.  
  - **Accepted Formats:** CSV, XLS, XLSX, JSON, ZIP.  
  - **Interaction:** Single-click for a preview and double-click or “Open” for selection.  
  - **Processing:** Upon file selection, the file is uploaded and queued for background processing.

---

## 5.3 Performance and Non‑Functional Requirements

### 5.3.1 Performance Requirements

#### 5.3.1.1 Search Results Return Time

- **Requirement:** The application **shall** return initial search query results within 10 seconds from submission.  
- **Notes:** This applies to the first batch of returned search results.

#### 5.3.1.2 Bulk Data Ingestion Performance

- **Requirement:** The system **shall** process an export file containing at least 13,000 records in approximately 30 seconds.  
- **Implementation Details:**
  - Use of **bulk inserts** (batch processing) to reduce transaction overhead.
  - CSVs are processed in batches (e.g., 1,000 rows per batch).
  - Orders and line items are processed in two phases: grouping by unique order key, then bulk inserting orders and linking corresponding line items via foreign keys.
  - Real‑time progress tracking is provided via endpoints (e.g., `/uploads/status/{upload_id}`).

### 5.3.2 Security, Scalability, and Usability Requirements

- **Security:**  
  - Authentication/Authorization will be handled by NextAuth, utilizing secure cookies and CSRF tokens.
  - All data transmission will occur over HTTPS.  
  - Endpoints will validate and sanitize incoming data to avoid SQL injection and other exploits.

- **Scalability and Reliability:**  
  - The backend architecture supports scaling through database indexing, potential read replicas for PostgreSQL, and Redis caching for analytics.
  - The system is designed to handle load balancing and container orchestration (Docker, Kubernetes).

- **Usability and Accessibility:**  
  - The GUI adheres to accessibility standards (e.g., WCAG 2.1) ensuring keyboard navigation, clear contrast, and screen reader support.
  - The design includes responsive layouts ensuring usability across desktop and mobile devices.

- **Maintainability and Extensibility:**  
  - The modular design (React components on the frontend, FastAPI on the backend) supports ease of maintenance, testing (including unit and integration testing), and future feature extension.

---

## 5.4 Environment and Deployment Requirements

### 5.4.1 Development Environment Requirements

- **Requirement:** The development environment **shall** include all necessary tools, languages, and libraries specified for the project.  
- **Examples:**  
  - **IDE:** Visual Studio Code, IntelliJ, etc.
  - **Languages:** Python (FastAPI) and JavaScript/TypeScript (Next.js, React).
  - **Libraries:** SQLAlchemy, Pandas, Redis, RQ, Material‑UI, @tanstack/react-query, Axios.
- **Notes:** Dependency management via `pip` for Python and `npm/yarn` for JavaScript.

### 5.4.2 Execution Environment Requirements

- **Hardware Requirements:**
  - **Processor:** Intel i5 or equivalent minimum.
  - **RAM:** Minimum 8 GB.
  - **Storage:** At least 200 MB of free space.
  - **Display:** Minimum resolution of 1024 x 768.
- **Software Requirements:**
  - **Operating System:** Linux for production, macOS/Windows for development.
  - **Database:** PostgreSQL 14 or later.
  - **Task Queue:** Redis.
  - **Web Server:** Uvicorn running FastAPI.
- **Deployment:**  
  - Containerization (Docker) with orchestrated resource allocation.
  - Monitoring, logging, and CI/CD pipelines will be implemented to maintain service reliability.

---

## Appendices

- **Additional Documentation:**  
  Include diagrams (UML, architecture diagrams), API interface details, and extended descriptions of critical processes such as bulk ingestion and progress tracking.
- **Testing and Quality Assurance:**  
  Outline the test plans and CI/CD practices that ensure consistent quality and prompt deployment of updates.

---

## Acronyms and Abbreviations

| Acronym | Definition                                       |
|---------|--------------------------------------------------|
| API     | Application Programming Interface                |
| CSV     | Comma-Separated Values                           |
| DB      | Database                                         |
| GUI     | Graphical User Interface                         |
| KPI     | Key Performance Indicator                        |
| RQ      | Redis Queue                                      |
| SRS     | Software Requirements Specification              |
| UML     | Unified Modeling Language                        |
| SDK     | Software Development Kit                         |
| UI      | User Interface                                   |

---

## Future Enhancements

- **Role-Based Access Control:**  
  Specify additional user roles and permissions for administration versus standard access.
- **Advanced Analytics Integration:**  
  Plan for integration with additional data sources, enhanced export capabilities, and further customization of dashboard widgets. Expand machine learning capabilities to include more sophisticated forecasting models and additional product categorization methods beyond style-based forecasting.
- **Mobile and Cross-Platform Improvements:**  
  Expand on responsive design and dedicated mobile interfaces as user demand increases.
- **Real-Time Collaboration:**  
  Explore features that support collaborative data analysis and multi-user dashboard customization.
- **Enhanced Monitoring:**  
  Integration of advanced monitoring and alerting systems (e.g., Prometheus, Grafana) to ensure uptime and performance.

---
