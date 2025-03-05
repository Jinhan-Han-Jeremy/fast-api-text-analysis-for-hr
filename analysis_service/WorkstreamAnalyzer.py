

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class WorkstreamAnalyzer:
    def __init__(self, tasks_info):
        self.tasks_info = tasks_info

    def match_workstream_to_task(self, workstream_text):
        vectorizer = TfidfVectorizer()

        task_names = self.tasks_info['name']

        print(workstream_text)
        task_vectors = vectorizer.fit_transform(task_names)

        print("match_workstream 진행중~ ")
        if task_vectors.shape[0] == 0 or task_vectors.shape[1] == 0:
            raise ValueError("Task vectors are empty. Check the input task names.")

        workstream_vector = vectorizer.transform([workstream_text])

        # 코사인 유사도 계산
        try:
            similarities = cosine_similarity(workstream_vector, task_vectors).flatten()
        except Exception as e:
            print(f"Error calculating cosine similarity: {e}")
            raise

        matched_indices = similarities.argsort()[-6:][::-1]
        print("matched indices", matched_indices)
        return matched_indices

    def analyzed_texts(self, input_text):
        matched_indices = self.match_workstream_to_task(input_text)

        # 임시 리스트 생성
        result_list = []

        # 인덱스 유효성 검사 및 데이터 추가
        for index in matched_indices:
            if index < 0 or index >= len(self.tasks_info):
                print(f"Index {index} is out of bounds for tasks_info.")
                continue
                # 아래에서 name, difficulty, requirements 중 name만 뽑는다
            result_list.append(self.tasks_info.iloc[index]['name'])

        print("matched_indices=== ", result_list)

        return result_list

    def task_names_from_analyzed_texts(self, input_text):
        results = self.analyzed_texts(input_text)
        print("Task names--:\n", results)

        if results is None or results.empty:
            print("Results are empty or None.")
            return []

        # 'name' 컬럼이 존재하는지 확인
        if 'name' not in results.columns:
            print("Results DataFrame does not contain 'name' column.")
            return []


        print("Task names:\n", results)
        return results