#python 1_ingest.py

Loaded 6 documents
Split into 27 chunks (chunk_size=300, overlap=50)
Example chunk -> '## Contact\nQueries about the training can be sent to the Training & Placement Cell office, Room 104, Main Block.' {'source': 'ai_fluency_training.md'}
Stored 27 vectors in ./chroma_db using EMBED_PROVIDER=fastembed
Vector length: 384


#python 2_search.py

Q: How much is the late fee for paying fees after the due date?
  0.197  [fee_policy.md]  '## Late fee\nA late fee of Rs. 100 per day is charged after the due dat'
  0.299  [fee_policy.md]  '## Tuition fee\nThe annual tuition fee must be paid before 15 July for '
  0.333  [exam_regulations.md]  '## Revaluation\nRevaluation can be applied for within 5 working days of'

Q: What time should hostel students return?
  0.130  [hostel_rules.md]  '## In-time\nAll hostel residents must return to the hostel by 9.00 PM. '
  0.295  [hostel_rules.md]  '## Leave\nTo go home, a student must submit a leave form to the warden '
  0.300  [hostel_rules.md]  '# Hostel Rules (Greenfield College of Engineering - sample document)'

Q: Can I write the exam with 70% attendance?
  0.247  [exam_regulations.md]  '## Attendance requirement\nA student needs a minimum of 75% attendance '
  0.332  [exam_regulations.md]  'Students below 65% attendance are not permitted to write the examinati'
  0.338  [placement_policy.md]  '## Pre-placement training\nA minimum of 90% attendance in pre-placement'

Q: What CGPA do I need to be eligible for placements?
  0.185  [placement_policy.md]  '# Placement Policy (Greenfield College of Engineering - sample documen'
  0.236  [fee_policy.md]  '## Scholarships\nStudents with a CGPA of 9.0 or above in the previous y'
  0.284  [placement_policy.md]  '## Pre-placement training\nA minimum of 90% attendance in pre-placement'

Filtered to library.md:
   library.md -> ## Fines A fine of Rs. 2 per day per book is charged for late return. Lost books
   library.md -> # Library Rules (Greenfield College of Engineering - sample document)  ## Borrow

# Relevance guard score evidence

Embedding provider: FastEmbed (`BAAI/bge-small-en-v1.5`)

Query: What CGPA do I need to be eligible for placements?
  0.185  [placement_policy.md]
  0.236  [fee_policy.md]
  0.284  [placement_policy.md]

Query: What is the capital of France?
  0.573  [hostel_rules.md]
  0.573  [hostel_rules.md]
  0.577  [library.md]

Chosen MAX_DISTANCE: 0.4. This keeps all three placement-query results and drops all three France-query results.

# Part D - Test and report

Run: `python task_agent.py`, using thread ID `task-run` for all five questions.

| # | Tools called (in order) | Agent's answer (short) | Correct? (Y/N) | If N, why? |
|---|---|---|---|---|
| 1 | `search_handbook` | CGPA 6.5 or above and no standing arrears for placements. | Y | |
| 2 | `check_exam_eligibility` | Condonation with certificate; Rs. 500 per course. | Y | |
| 3 | `get_course_fee` x2, `search_handbook`, `calculator` | Rs. 32,000 total. | Y | |
| 4 | `calculator` | Rs. 30,500 total after a Rs. 500 five-day late fee. | Y | |
| 5 | `search_handbook` | I don't know; not covered in the college handbook. | Y | |

Model used: `qwen/qwen3.8-27b` (Groq)

Embedding model: `BAAI/bge-small-en-v1.5` (FastEmbed)

MAX_DISTANCE: `0.4`

Scores - placements question: `0.185, 0.236, 0.284`

Scores - France question: `0.573, 0.573, 0.577`
