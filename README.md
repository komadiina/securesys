# Secure Communication System

As an university cryptography project, this repository contains a secure storage system implemented in Python. Besides aforementioned, it also includes a Certificate Authority (CA) for managing digital certificates, i.e. a Public Key Infrastructure (PKI).

## Structure

The system is organized into several modules:

- `admin.py`: Contains the Admin class for managing administrative tasks.
- [`ca.py`](command:_github.copilot.openSymbolInFile?%5B%22modules%2Fsystem.py%22%2C%22ca.py%22%5D "modules/system.py"): Implements a Certificate Authority (CA) for signing Certificate Signing Requests (CSR) and managing certificates.
- `cryptoalgorithms.py`: Contains various cryptographic algorithms used throughout the system.
- `entry.py`: Defines the Entry class as an app entry-point.
- [`system.py`](command:_github.copilot.openRelativePath?%5B%22modules%2Fsystem.py%22%5D "modules/system.py"): Contains the System class for managing the overall system.
- [`user.py`](command:_github.copilot.openSymbolInFile?%5B%22modules%2Fsystem.py%22%2C%22user.py%22%5D "modules/system.py"): Defines the User class for creating and managing users.
- `utils.py`: Contains utility functions used throughout the system.

The [`res/`](command:_github.copilot.openRelativePath?%5B%22res%2F%22%5D "res/") directory contains user-specific data, including encryption history and notifications. The [`certs/`](command:_github.copilot.openRelativePath?%5B%22certs%2F%22%5D "certs/") directory stores the digital certificates of users, and the [`requests/`](command:_github.copilot.openRelativePath?%5B%22requests%2F%22%5D "requests/") directory holds the Certificate Signing Requests (CSR) of users.

## Usage

To use the system, run the [`entry.py`](command:_github.copilot.openRelativePath?%5B%22modules%2Fentry.py%22%5D "modules/entry.py") script. This will prompt you for various inputs depending on the operation you want to perform, such as creating a new user, encrypting data, or viewing encryption history.