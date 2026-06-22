# KNN Order-Status Classifier | Analytics Pipeline

An end-to-end Machine Learning classification pipeline built as **Project-02** during my data science internship at **Decodelabs**. This project implements a **K-Nearest Neighbors (KNN)** algorithm structured strictly around the classical **IPO (Input-Process-Output) model** to predict e-commerce order fulfillment statuses and automatically generate a 5-panel performance dashboard.

---

## 🎯 Project Objective

The core objective of this project is to clean raw operational e-commerce data, systematically handle missing features and severe class imbalances, engineer optimized numeric representations of categorical indicators, and build a distance-based classifier. The final stage preserves accountability by rendering an evaluation dashboard asset (`knn_dashboard.png`) for model performance auditing.

## 🏗️ Technical Architecture (IPO Framework)

The repository code is clean, modular, and decoupled into three architectural phases:

```text
 ┌──────────────────────────────┐
 │           1. INPUT           │ ──> Load Excel workbook & audit class distributions
 └──────────────┬───────────────┘
                │
 ┌──────────────▼──────────────┐
 │          2. PROCESS          │ ──> Clean ──> Encode ──> Split (Stratified) ──> Scale ──> Fit KNN
 └──────────────┬───────────────┘
                │
 ┌──────────────▼──────────────┐
 │          3. OUTPUT           │ ──> Generate console reports & export evaluation dashboard PNG
 └──────────────────────────────┘