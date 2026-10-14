from backend.app.services import AnswerGenerator


generator = AnswerGenerator()

context = """
The campus library is open from 8:00 AM to 10:00 PM
Monday through Friday.
"""

answer = generator.generate(
    question="What time does the campus library close?",
    context=context,
)

print("Answer:")
print(answer)

print("---")

unknown_answer = generator.generate(
    question="Who is the current university chancellor?",
    context=context,
)

print("Unknown answer:")
print(unknown_answer)