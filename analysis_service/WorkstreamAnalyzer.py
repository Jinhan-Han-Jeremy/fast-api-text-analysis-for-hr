import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class WorkstreamAnalyzer:
    def __init__(self, tasks_info):
        self.tasks_info = tasks_info

    def match_workstream_to_task(self, workstream_text):
        vectorizer = TfidfVectorizer()
        task_names = self.tasks_info['name']
        task_vectors = vectorizer.fit_transform(task_names)
        workstream_vector = vectorizer.transform([workstream_text])

        similarities = cosine_similarity(workstream_vector, task_vectors).flatten()
        matched_indices = similarities.argsort()[-3:][::-1]
        return matched_indices

    def analyzed_texts(self, input_text):
        matched_indices = self.match_workstream_to_task(input_text)
        results = pd.DataFrame(columns=['name', 'difficulty', 'requirements'])

        for index in matched_indices:
            results = results.append(self.tasks_info.iloc[index], ignore_index=True)

        return results

    def task_names_from_analyzed_texts(self, input_text):
        results = self.analyzed_texts(input_text)
        return results['name'].tolist()