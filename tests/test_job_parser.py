from docx import Document

from langgraph_pipeline.nodes.job_parser import JobParser


print("STEP 1")


doc = Document(
    "data/raw/job_description.docx"
)

print("STEP 2")


job_text = "\n".join(

    paragraph.text

    for paragraph in doc.paragraphs

)
print("\n===== RAW JOB TEXT =====\n")

print(job_text)

print("\n=======================\n")

print("STEP 3")


parser = JobParser()

print("STEP 4")


parsed_job = parser.parse(
    job_text
)

print("STEP 5")


print("\n===== PARSED JOB =====\n")

print(parsed_job)

print("\nDONE")