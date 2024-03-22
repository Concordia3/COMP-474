from tools_libs import *
import random as rnd

def transcripts_generator(csv_file, num_students=50):
    # Set the random seed
    rnd.seed(42)

    # read the csv file
    df = pd.read_csv(csv_file)

    # extract the available courses
    course_codes = df['Course code'].tolist()
    course_nums  = df['Course number'].tolist()

    # generate transcript for each student
    transcripts = []
    for student in range(num_students):
        # select random courses (5 - 10 courses per student)
        num_courses = rnd.randint(5, 10)

        # probabilities of taking comp472 and comp474
        comp472_prob, comp474_prob = 0.01, 0.01

        courses = []
        random_num = rnd.random()
        for i in range(num_courses):
            if   random_num < comp472_prob: courses.append(('COMP', '472'))                                             # if random number is less than comp472_prob, add comp472 to the list
            elif random_num < comp474_prob: courses.append(('COMP', '474'))                                             # if random number is less than comp474_prob, add comp474 to the list
            else                          : courses.append(rnd.choice(list(zip(course_codes, course_nums))))            # else, add a random course to the list

        courses = list(set(courses))    # remove duplicates

        # generate grade(s) for each class
        grades = {}
        for course in courses:
            grade = rnd.randint(50, 100)
            grades[course] = [grade]

            # check and see if the student needs to retake the class
            if grade < 60:
                retake_grade = rnd.randint(50, 100)
                grades[course].append(retake_grade)

        transcripts.append({'courses': courses, 'grades': grades})

    # create a dataframe from the transcripts
    transcripts_df = pd.DataFrame(transcripts)

    return transcripts_df