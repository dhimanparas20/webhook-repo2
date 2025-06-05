subject_fullname = {        
    'M': 'Math',
    'S': 'Science',
    'E': 'English',
    'H': 'History',
    'G': 'Geography'
}
# TODO
# 1 : add doc strings
# 2 : only fetch the the data that happened in last 15 secs
# 3 : Use env
# 4 : Learn multi threading
# 5 : make the code professional 
# 6: celery and message queing

def decrypt_records(encrypted_records: dict) -> dict:
    final_dict = {}
    for name, scores  in encrypted_records.items():
      decrypteed_scores = []
      full_subject = []
      final_scores_with_subjects = {}
      score_list = scores['scores']
      map_code = scores['map']
      
      for code in map_code:
        subject = subject_fullname[code]
        full_subject.append(subject)

      for i,score in enumerate(score_list):
        decrypted_score = score - ord(map_code[i])
        decrypteed_scores.append(decrypted_score)

      for i, subject in enumerate(full_subject):
          final_scores_with_subjects[subject] = decrypteed_scores[i]

      schema = {name: final_scores_with_subjects}
      final_dict.update(schema)
    return final_dict
         

solution = decrypt_records({

    "Alice": {

        "scores": [183, 214, 172],

        "map": "MSE"

    },

    "Bob": {

        "scores": [180, 208],

        "map": "GH"

    }

})        
print(solution)