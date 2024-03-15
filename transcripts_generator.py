from tools_libs import *

def transcripts_generator(csv_file, num_students=50):
    # read the csv file
    df = pd.read_csv(csv_file)

    # extract the available courses
    course_codes = df['Course code'].tolist()
    course_nums  = df['Course number'].tolist()

    # generate transcript for each student
    transcripts = []
    for student in range(num_students):
        # select random courses (5 - 10 courses per student)
        num_courses = random.randint(5, 10)
        courses = random.sample(list(zip(course_codes, course_nums)), num_courses)

        # generate grade(s) for each class
        grades = {}
        for course in courses:
            grade = random.randint(50, 100)
            grades[course] = [grade]

            # check and see if the student needs to retake the class
            if grade < 60:
                retake_grade = random.randint(50, 100)
                grades[course].append(retake_grade)

        transcripts.append({'courses': courses, 'grades': grades})

    # create a dataframe from the transcripts
    transcripts_df = pd.DataFrame(transcripts)

    return transcripts_df