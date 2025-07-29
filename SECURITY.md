# 🔐 Security Policy

## 🧩 Supported Versions

We currently maintain active security updates for the following versions of the AI Agent Education Platform:

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | ✅ :white_check_mark: |
| 1.1.x   | ❌ :x:                |
| 1.0.x   | ✅ :white_check_mark: |
| < 1.0   | ❌ :x:                |

> To receive security updates and patches, please use version 1.0.0 or higher.

---

## 📣 Reporting a Vulnerability

We take security seriously and welcome reports from the community.

If you discover a vulnerability, please follow the steps below:

### 🔍 How to Report

- **Email**: Send a detailed report to [hendrik.krack@aparavi.com](mailto:hendrik.krack@aparavi.com)
- **GitHub Security Advisories**: You can also report privately via GitHub [Security Advisories](https://github.com/HendrikKrack/ai-agent-education-platform/security/advisories)
- **Required Details**:
  - A clear description of the issue
  - Steps to reproduce the vulnerability
  - Any potential impact or affected components

### 🕒 Response Expectations

- Valid reports will be addressed with a fix or mitigation timeline
- Coordinated disclosure is encouraged; we'll work with you on timing

---

## 🔒 Scope of Protection

We protect against vulnerabilities affecting:

- PDF uploads and parsing (LlamaParse, PyPDF2)
- AI persona injection (OpenAI GPT-4 outputs)
- Chat command misuse (ChatOrchestrator inputs)
- API endpoint abuse (FastAPI backend)
- User data exposure or authentication flaws

---

## 📜 Out of Scope

While important, the following are **not** considered security vulnerabilities:

- Self-hosting misconfigurations
- Use of outdated libraries in forks
- Bugs without security implications

---

## 🙏 Acknowledgments

We thank all security researchers and users who contribute responsibly to the safety of this platform.

