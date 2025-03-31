SYSTEM_PROMPT = """
You are a team assistant and support the team with its daily work.
"""

INSTRUCTIONS_CREATE_MEETING_MINUTES = """
Your task is to generate structured meeting minutes from the provided transcript. Follow these steps:

1. **Meeting Information**:
   - Extract the date, time, and location if available.

2. **Attendees**:
   - List the participants.

3. **Goals**:
   - Identify and summarize the main objectives.

4. **Discussion Topics**:
   - Outline key points discussed.

5. **Decisions**:
   - Document important decisions made.

6. **Assigned Tasks**:
   - List tasks assigned to specific individuals, including deadlines.

7. **Additional Notes**:
   - Include important points that do not fit other categories.

Return the final meeting minutes in markdown format for Word (docx).
"""

SELECT_LANGUAGE = "Always respond in English."

EXAMPLE_OUTPUT = """
# Meeting Minutes

## Meeting Information
- **Date:** [Extracted Date]
- **Time:** [Extracted Time]
- **Location:** [Extracted Location]

## Attendees
- [List of Participants]

## Goals
- Organize a surprise party for Adam.

## Discussion Topics
- Planning for the surprise.
- Party logistics.

## Decisions
- Surprise Adam when he comes back home.
- Everyone hides in the kitchen until Adam enters the flat.
- When Adam enters, everyone sings Happy Birthday.
- The party will have music, cake, and soft drinks.
- The party should not last beyond 11 o'clock since everyone has work the next day.

## Assigned Tasks
- **SPEAKER_02:** Organizes the key to Adam's apartment.
- **SPEAKER_01:** Buys drinks.
- **SPEAKER_00:** Buys snacks.
- **SPEAKER_03:** Organizes music.

## Additional Notes
- The idea of hiring a clown for the party was dismissed due to cost.
"""