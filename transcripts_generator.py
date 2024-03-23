import tools_libs

def transcripts_generator(csv_file, num_students=50):
    tools_libs.random.seed(0)    # set the seed for reproducibility
    
    # read the csv file
    df = tools_libs.pd.read_csv(csv_file)

    # extract the available courses
    course_codes = df['Course code'].tolist()
    course_nums  = df['Course number'].tolist()

    # generate transcript for each student
    transcripts = []
    for student in range(num_students):
        # select random courses (5 - 10 courses per student)
        num_courses = tools_libs.random.randint(5, 10)

        # probabilities of taking comp472 and comp474
        comp472_prob, comp474_prob = 0.01, 0.01

        courses = []
        random_num = rnd.random()
        for i in range(num_courses):
            course_prob = tools_libs.random.random()
            if   course_prob < comp472_prob: courses.append(('COMP', '472'))                                                   # if random number is less than comp472_prob, add comp472 to the list
            elif course_prob < comp474_prob: courses.append(('COMP', '474'))                                                   # if random number is less than comp474_prob, add comp474 to the list
            else                           : courses.append(tools_libs.random.choice(list(zip(course_codes, course_nums))))    # else, add a random course to the list

        # remove duplicates while maintaining order
        courses = list(dict.fromkeys(courses))

        # generate grade(s) for each class
        grades = {}
        for course in courses:
            grade = tools_libs.random.randint(50, 100)
            grades[course] = [grade]

            # check and see if the student needs to retake the class
            if grade < 60:
                retake_grade = tools_libs.random.randint(50, 100)
                grades[course].append(retake_grade)

        transcripts.append({'courses': courses, 'grades': grades})

    # create a dataframe from the transcripts
    transcripts_df = tools_libs.pd.DataFrame(transcripts)

    return transcripts_df