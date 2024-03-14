from tools_libs import *

# load the csv files
df_info = pd.read_csv('data/courses/raw_course_info_2024.csv')
df_web  = pd.read_csv('data/courses/raw_course_websites_2024.csv')

# Rename column in df_info to match the column name in df_web
df_info.rename(columns={'Subject': 'Course code', 'Catalog': 'Course number'}, inplace=True)

# merge the dataframes
merged_df = pd.merge(df_info, df_web, on=['Course code', 'Course number'], how='inner')

# save the merged dataframe
merged_df.to_csv('data/courses/processed_course_info_2024.csv', index=False)

# create RDF graph
g = Graph()

# define RDF schema
g.add((ex.Course, RDF.type, RDFS.Class))                # course class
g.add((ex.hasCourseCode, RDF.type, RDF.Property))       # subject property
g.add((ex.hasCourseNumber, RDF.type, RDF.Property))     # catalog property
g.add((ex.hasTitle, RDF.type, RDF.Property))            # title property
g.add((ex.hasCredits, RDF.type, RDF.Property))          # credits property
g.add((ex.hasDescription, RDF.type, RDF.Property))      # description property

# define relationships between classes
g.add((ex.courseAt, RDFS.domain, ex.Course))            # course is at a university
g.add((ex.courseAt, RDFS.range, UNIVERSITY))

# Convert selected data to RDF
for index, row in merged_df.iterrows():
    subject = URIRef(ex + row['Course code'] + '/' + row['Course number'])

    # current subject is of course class
    g.add((subject, RDF.type, ex.Course))

    # add properties
    g.add((subject, ex.courseAt, UNIVERSITY))
    g.add((subject, ex.hasCourseCode, Literal(row['Course code'])))
    g.add((subject, ex.hasCourseNumber, Literal(row['Course number'])))
    g.add((subject, ex.hasTitle, Literal(row['Long Title'])))
    g.add((subject, ex.hasCredits, Literal(row['Class Units'], datatype=XSD.float)))
    g.add((subject, ex.hasDescription, Literal(row['Description'])))
    g.add((subject, RDFS.seeAlso, Literal(row['Website'])))

# save the graph
g.serialize(destination="graphs/courses.ttl", format="turtle") 