import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

def load_data(filepath):
    """Loads the job roles and skills dataset."""
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'. Make sure it is in the same directory.")
        sys.exit()

def recommend_roles(user_skills_list, df, top_n=3):
    """
    Applies TF-IDF vectorization and Cosine Similarity to match 
    user skills with the most relevant job roles.
    """
    # 1. Combine user skills into a single space-separated string
    user_skills_str = " ".join(user_skills_list)
    
    # 2. Append the user profile to the dataset temporarily for vectorization
    all_skills = df['Required_Skills'].tolist()
    all_skills.append(user_skills_str)
    
    # 3. Vectorization (Process phase)
    # TfidfVectorizer converts text to a matrix of TF-IDF features, 
    # rewarding specific skills and penalizing generic terms.
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_skills)
    
    # 4. Calculate Cosine Similarity
    # The user profile is the last item in the matrix (-1)
    user_vector = tfidf_matrix[-1]
    job_vectors = tfidf_matrix[:-1] # Everything except the last item
    
    # Calculate how close the user vector is to every job vector
    similarity_scores = cosine_similarity(user_vector, job_vectors).flatten()
    
    # 5. Output phase: Sort and Filter
    df['Similarity_Score'] = similarity_scores
    recommended_jobs = df.sort_values(by='Similarity_Score', ascending=False).head(top_n)
    
    return recommended_jobs

if __name__ == "__main__":
    print("="*50)
    print(" DecodeLabs Project 3: AI Recommendation Engine")
    print("="*50)
    
    # Load the dataset
    df = load_data('raw_skills.csv')
    
    # Input phase: Handle the User Cold Start problem
    print("\n[SYSTEM] Initializing Digital Matchmaker...")
    print("To bootstrap your profile, please provide your technical foundation.")
    print("Type 'exit' or 'quit' to stop.\n")

    try:
        while True:
            user_input = input("Enter at least 3 skills separated by commas\n(e.g., C#, React, PyTorch): ")
            if user_input.strip().lower() in ('exit', 'quit'):
                print("\n[SYSTEM] Exiting. Goodbye!")
                break

            # Clean the input
            user_skills = [skill.strip() for skill in user_input.split(',') if skill.strip()]

            # Validation constraint from requirements
            if len(user_skills) < 3:
                print("\n[ERROR] Minimum 3 skills required to ensure accurate mathematical mapping. Try again or type 'exit' to quit.\n")
                continue

            print("\n[SYSTEM] Analyzing vector space and calculating Cosine Similarity...")

            # Execute Recommendation Logic
            top_matches = recommend_roles(user_skills, df)

            # Display Results
            print("\n" + "-"*40)
            print(" TOP 3 RECOMMENDED CAREER PATHS")
            print("-" * 40)

            for index, row in top_matches.iterrows():
                score_percentage = round(row['Similarity_Score'] * 100, 1)
                # Only show results if there is an actual mathematical overlap (> 0%)
                if score_percentage > 0:
                    print(f"➜ Role: {row['Job_Role']}")
                    print(f"  Match Alignment: {score_percentage}%")
                    print(f"  Core Attributes: {row['Required_Skills']}\n")
                else:
                    print(f"➜ No further matching patterns found in the database.")
                    break

            print("Type more skills to get new recommendations, or 'exit' to quit.\n")

    except (KeyboardInterrupt, EOFError):
        print("\n\n[SYSTEM] Interrupted by user. Exiting.")