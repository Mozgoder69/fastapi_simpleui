# Cleaners Information System

## Overview

### Summary
This repository contains the prototype of the "Cleaners" information system, designed and developed as a coursework project focusing on database and system design. The system is intended to automate processes within cleaning services, enhancing user experience and data security.

### Introduction and Abstract
This project aims to provide a robust solution for automating the workflow of cleaning services, reducing human error, and securing client and operational data. It integrates modern technologies to create a seamless and efficient experience for both customers and staff.

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation and Setup](#installation-and-setup)
- [Functional Overview](#functional-overview)
  - [User Roles](#user-roles)
  - [Core Features](#core-features)
- [System Architecture](#system-architecture)
  - [Technology Stack](#technology-stack)
  - [Database Design](#database-design)
  - [API Endpoints](#api-endpoints)
- [Security Measures](#security-measures)
- [Development Setup](#development-setup)
  - [Environment Setup](#environment-setup)
  - [Running the System](#running-the-system)
- [User Guide](#user-guide)
  - [Accessing the System](#accessing-the-system)
  - [Managing Orders](#managing-orders)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Authors and Acknowledgment](#authors-and-acknowledgment)
- [Appendices](#appendices)
  - [SQL Schema Definitions](#sql-schema-definitions)
  - [Function Definitions](#function-definitions)

## System Requirements
Details of hardware and software requirements to run the system.

## Installation and Setup
Instructions for installing and configuring the system.
## Non-Functional Overview
### Design Philosophy
This document and associated components are developed with a focus on three core principles:
1. **Consistency is Key:** Striving for a coherent and standardized approach in all documented aspects.
2. **Emphasize Relationships:** Prioritizing understanding of the general relationships and structures within the system.
3. **Condense, Don't Oversimplify:** Aiming to be compact yet comprehensive, preserving essential complexity where it matters.
These principles ensure that the documentation is not only effective but also adaptable for future enhancements and understandable by both humans and AI agents, reflecting the project’s intrinsic values.

## Functional Requirements

The system is designed to automate cleaning processes, ensure data security, and improve both customer and employee experiences. Here are some key functionalities:

- **Order Management:** Customers can view, initiate, and track their orders through the user interface.
- **Data Processing:** The system processes input data such as customer and order details to ensure service accuracy.
- **Security:** Data protection measures, including authentication and encryption, are implemented to safeguard user data.

For a detailed overview of all functional requirements, please refer to [the full documentation](link-to-document).
### User Roles
Description of different user roles and their permissions.

### Core Features
Summary of the core features of the system.

## System Architecture
### Technology Stack
**PostgreSQL:** Serves as the primary database.
**Uvicorn:** ASGI server for hosting the application.
**AsyncPG:** Provides asynchronous database operations.
**FastAPI:** Framework for building APIs.
**Alpaca.JS, Alpine.JS, MaterializeCSS, Axios:** Technologies used for the UI and API interactions.

### Database Architecture Overview

System uses multiple schemas to organize and manage data efficiently. Here’s a brief overview of each schema:

- **bss_ops_reg_ext:** Distributed data across different geographical locations.
- **bss_ops_reg_int:** Centralized data that includes sensitive user and operational information.
- **bss_ops_ctg_items:** Contains definitions and classifications related to cleaning processes.
- **bss_ops_ctg_rules:** Stores rules and procedures for the cleaning services.
- **bss_ops_mkg_line:** Marketing data including service summaries and customer interactions.
- **bss_ops_org_line:** Detailed operational data about service execution.
- **bss_ops_activity:** Audit trails and logs of all system actions.


### API Endpoints
List of major API endpoints and their functions.

## Security Measures
Discussion of security protocols and measures in place to protect data and interactions.

## Development Setup
### Environment Setup
Steps to set up the development environment.

### Running the System
Instructions for running the system locally.

## User Guide
### Accessing the System
How users can log in and navigate the system.

### Managing Orders
Guide on how orders are placed, processed, and tracked.

## API Documentation
### Authentication
Methods and protocols for securing access to the API.

### Endpoints
Detailed documentation of API endpoints, including request and response formats.

## Troubleshooting
Common issues and their solutions.

## Contributing
Guidelines for contributing to the project.

## License
Licensing information.

## Authors and Acknowledgment
Credits to the development team and contributors.

## Appendices
### SQL Schema Definitions
Complete SQL schema definitions used in the project.

### Function Definitions
Definitions and descriptions of custom functions used within the database.
