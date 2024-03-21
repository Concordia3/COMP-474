import PyPDF2

def PDFReader(file_path):
    # provide the file path to the syllabus
    file_path = "data/courses/comp472_data/syllabus.pdf"

    # Open the PDF file in binary mode
    with open(file_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)

        # Get the total number of pages in the PDF
        num_pages = len(pdf_reader.pages)

        # Iterate through each page and extract text
        text = ""
        for page_num in range(num_pages):
            # Get the page object
            page = pdf_reader.pages[page_num]

            # Extract text from the page
            text = text + (page.extract_text())

        return text