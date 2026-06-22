# PyBot 🤖 | Rule-Based AI Chatbot

A highly structured, production-ready terminal chatbot built as **Project-01** during my internship at **Decodelabs**. This project utilizes the classical **IPO (Input-Process-Output) model** combined with efficient data structures to create a responsive, deterministic conversational assistant.

---

## 🎯 Project Overview

The objective of this project was to design a rule-based conversational agent capable of managing user intents efficiently. Moving beyond basic, nested `if-else` chains, this implementation leverages an $O(1)$ dictionary lookup mapping system with dynamic function execution to deliver real-time data handling.

## ✨ Core Features

* **Intent Normalization & Sanitization:** Strips trailing/leading whitespaces and standardizes input to lowercase, ensuring inputs like `"  Hello  "` or `"HELLO"` map gracefully to the same response.
* **Dynamic Content Delivery:** Integrates Python `Callable` objects (lambdas) directly into the knowledge base to serve real-time data such as current times, dates, and randomized jokes or motivational quotes.
* **Fallbacks & Error Trapping:** A robust default mechanism handles unrecognized commands without crashing the execution loop.
* **Optimized State Control:** Utilizes an immutable `frozenset` for exit command execution checks, keeping memory operations highly efficient.

---

## 🏗️ Architecture & Design Pattern

The chatbot is cleanly decoupled into three distinct architectural layers adhering strictly to the **IPO Model**:

```text
 ┌───────────────┐       ┌─────────────────┐       ┌────────────────┐
 │     INPUT     │  ──>  │     PROCESS     │  ──>  │     OUTPUT     │
 │ (User Prompt) │       │ (Sanitize & O(1)│       │ (System Reply) │
 └───────────────┘       │     Lookup)     │       └────────────────┘
                         └─────────────────┘