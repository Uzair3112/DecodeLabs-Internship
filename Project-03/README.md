# 🚀 AI Recommendation Logic: Tech Stack Recommender

## 📌 Project Overview
This project is the Capstone for **Project 3: AI Recommendation Logic**, built as part of the DecodeLabs Industrial Training Kit. It serves as a "Digital Matchmaker," shifting algorithmic intent from passive data classification to active prediction to cure "Choice Overload". 

The system maps a user's raw technical skills to specific job roles and toolsets using pure similarity logic and Content-Based Filtering. By bypassing community behavior (Collaborative Filtering), the engine maps user preferences directly to the intrinsic properties of the job profiles[cite: 1].

---

## 🏗️ Architecture & Pipeline
The engine is built on a strict **Input-Process-Output (IPO) model**[cite: 1]:

1. **Ingestion (Input):** Captures the user state by requiring a minimum of three skills (e.g., Python, Cloud, Automation) to bootstrap the baseline vector and bypass the "User Cold Start" problem[cite: 1].
2. **Vector Mapping & Weighting (Process):** Transforms raw text into numerical arrays within a shared vocabulary space[cite: 1]. It applies **Term Frequency-Inverse Document Frequency (TF-IDF)** to penalize high-frequency generic terms and reward highly specific, descriptive tags[cite: 1].
3. **Scoring (Process):** Calculates the mathematical alignment between the user's vector and thousands of available job roles[cite: 1].
4. **Sorting & Filtering (Output):** Sorts the results in descending order and generates a truncated "Top-N" list (Top 3) to prevent information overload[cite: 1].

---

## 🧮 Mathematical Foundation
To avoid the magnitude sensitivity flaws of Euclidean distance, this engine uses **Cosine Similarity**[cite: 1]. This industry-standard metric measures the mathematical angle between two vectors[cite: 1]. 

The calculation relies on the dot product of the vectors divided by the product of their lengths[cite: 1]:

$cos(\theta)=\frac{A\cdot B}{||A||||B||}$

* **Score 1:** Vectors are perfectly aligned (identical orientation)[cite: 1].
* **Score 0:** Vectors are orthogonal (share no common characteristics)[cite: 1].

---

## 🛠️ Tech Stack & Requirements
* **Language:** Python 3.x
* **Core Libraries:** 
  * `pandas` (Data manipulation)
  * `scikit-learn` (TF-IDF Vectorization and Cosine Similarity math)

---

## 🚀 Installation & Usage

### 1. Setup the Environment
Ensure you have the required libraries installed:
```bash
pip install pandas scikit-learn