"""
MISIC Subtest Definitions
=========================
Complete definitions for all MISIC subtests including questions,
scoring criteria, time limits, and administration rules.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from models import SubtestType


@dataclass
class SubtestItem:
    """Definition of a single test item."""
    number: int
    question: str
    time_limit: Optional[int] = None  # seconds, None for untimed
    max_score: int = 1
    score_criteria: Dict[int, str] = field(default_factory=dict)
    correct_answers: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class SubtestDefinition:
    """Complete definition of a subtest."""
    subtest_type: SubtestType
    name: str
    description: str
    instructions: str
    items: List[SubtestItem]
    discontinue_after: int = 5  # consecutive failures
    start_item: int = 1  # default start item
    reverse_rule: bool = False  # whether reverse scoring applies
    auto_credit_rule: Optional[Dict] = None  # age-based auto-credit
    timing_per_item: bool = False  # whether each item is timed separately
    global_time_limit: Optional[int] = None  # overall time limit


# ==========================================
# VERBAL SUBTESTS
# ==========================================

INFORMATION_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.INFORMATION,
    name="Information",
    description="Tests general knowledge and information acquired from environment and formal education.",
    instructions="""Ask each question clearly. 
For children aged 8+, start with Item 6. 
If Items 6, 7, and 8 are all passed, give full credit for Items 1-5.
If any of Items 6-8 fail, administer Items 1-5 in reverse order until 2 consecutive passes.""",
    discontinue_after=5,
    auto_credit_rule={
        "min_age": 8,
        "credit_items": [1, 2, 3, 4, 5],
        "condition_items": [6, 7, 8],
        "condition": "all_pass"
    },
    items=[
        SubtestItem(1, "How many ears do you have?", max_score=1, 
                   score_criteria={0: "Wrong or no response", 1: "Two/2"},
                   correct_answers=["two", "2"]),
        SubtestItem(2, "What do we do with our eyes?", max_score=1,
                   score_criteria={0: "Wrong or no response", 1: "See/Look/Watch"},
                   correct_answers=["see", "look", "watch", "read"]),
        SubtestItem(3, "How many legs does a dog have?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Four/4"},
                   correct_answers=["four", "4"]),
        SubtestItem(4, "What is water made of?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Hydrogen and oxygen / H2O"},
                   correct_answers=["hydrogen and oxygen", "h2o"]),
        SubtestItem(5, "What are the colors of the Indian flag?", max_score=1,
                   score_criteria={0: "Incomplete or wrong", 1: "Saffron, white, green (all three)"},
                   correct_answers=["saffron white green", "orange white green"]),
        SubtestItem(6, "How many days are there in a week?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Seven/7"},
                   correct_answers=["seven", "7"]),
        SubtestItem(7, "What is the capital of India?", max_score=1,
                   score_criteria={0: "Wrong", 1: "New Delhi"},
                   correct_answers=["new delhi", "delhi"]),
        SubtestItem(8, "In which direction does the sun rise?", max_score=1,
                   score_criteria={0: "Wrong", 1: "East"},
                   correct_answers=["east"]),
        SubtestItem(9, "How many months are in a year?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Twelve/12"},
                   correct_answers=["twelve", "12"]),
        SubtestItem(10, "Who was Mahatma Gandhi?", max_score=1,
                   score_criteria={0: "Wrong or vague", 1: "Father of Nation / Freedom fighter / Led independence movement"},
                   correct_answers=["father of nation", "freedom fighter", "independence leader"]),
        SubtestItem(11, "What is the largest state of India by area?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Rajasthan"},
                   correct_answers=["rajasthan"]),
        SubtestItem(12, "What is the boiling point of water?", max_score=1,
                   score_criteria={0: "Wrong", 1: "100 degrees Celsius"},
                   correct_answers=["100", "100 degrees", "100 celsius"]),
        SubtestItem(13, "Who wrote the National Anthem of India?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Rabindranath Tagore"},
                   correct_answers=["rabindranath tagore", "tagore"]),
        SubtestItem(14, "What is the currency of Japan?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Yen"},
                   correct_answers=["yen"]),
        SubtestItem(15, "What causes day and night?", max_score=1,
                   score_criteria={0: "Wrong", 1: "Earth's rotation on its axis"},
                   correct_answers=["earth rotation", "rotation"]),
    ]
)


COMPREHENSION_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.COMPREHENSION,
    name="Comprehension",
    description="Tests practical reasoning, social judgment, and common sense understanding.",
    instructions="""Read each question clearly and allow the child to respond.
Prompt for elaboration if response is unclear: 'Tell me more about that.'
Score based on quality of reasoning demonstrated.""",
    discontinue_after=4,
    items=[
        SubtestItem(1, "What should you do if you cut your finger?", max_score=2,
                   score_criteria={
                       0: "No response or irrelevant",
                       1: "Partial (e.g., tell someone)",
                       2: "Complete (e.g., wash it, apply bandage, tell adult)"
                   }),
        SubtestItem(2, "Why do we wear clothes?", max_score=2,
                   score_criteria={
                       0: "No response or irrelevant",
                       1: "One reason (protection OR modesty)",
                       2: "Two or more reasons"
                   }),
        SubtestItem(3, "What should you do if you find someone's wallet on the road?", max_score=2,
                   score_criteria={
                       0: "Keep it / Wrong response",
                       1: "Give to police OR try to return",
                       2: "Comprehensive - check for ID, try to contact owner, give to authority"
                   }),
        SubtestItem(4, "Why do we have schools?", max_score=2,
                   score_criteria={
                       0: "No response or irrelevant",
                       1: "One reason (to learn / get education)",
                       2: "Multiple purposes (learn, socialize, prepare for life)"
                   }),
        SubtestItem(5, "What should you do before crossing a busy road?", max_score=2,
                   score_criteria={
                       0: "No response or dangerous suggestion",
                       1: "Look for vehicles OR use crossing",
                       2: "Look both ways, wait for traffic to clear, use zebra crossing"
                   }),
        SubtestItem(6, "Why is it important to brush your teeth?", max_score=2,
                   score_criteria={
                       0: "No response or wrong",
                       1: "One reason (cleanliness OR prevent decay)",
                       2: "Multiple reasons (hygiene, prevent cavities, fresh breath)"
                   }),
        SubtestItem(7, "Why do we have traffic rules?", max_score=2,
                   score_criteria={
                       0: "No response or wrong",
                       1: "Safety OR order",
                       2: "Both safety and order, prevent accidents"
                   }),
        SubtestItem(8, "What would you do if a younger child takes your toy?", max_score=2,
                   score_criteria={
                       0: "Hit them / Aggressive response",
                       1: "Ask for it back OR tell adult",
                       2: "Gentle approach, share, explain"
                   }),
        SubtestItem(9, "Why is saving money important?", max_score=2,
                   score_criteria={
                       0: "No response or wrong",
                       1: "For future OR emergencies",
                       2: "Multiple reasons (security, future needs, emergencies)"
                   }),
        SubtestItem(10, "Why do houses have windows?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Light OR air",
                        2: "Both light and ventilation"
                    }),
    ]
)


ARITHMETIC_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.ARITHMETIC,
    name="Arithmetic",
    description="Tests numerical reasoning and mental arithmetic ability.",
    instructions="""Read each problem clearly at a moderate pace.
Do not repeat the problem (unless child did not hear).
Time each problem - discontinue if time limit exceeded.
No paper or pencil allowed.""",
    discontinue_after=4,
    timing_per_item=True,
    items=[
        SubtestItem(1, "If you have 2 apples and I give you 1 more, how many do you have?", 
                   time_limit=30, score_criteria={0: "Wrong", 1: "3"}),
        SubtestItem(2, "What is 3 + 4?", time_limit=30,
                   score_criteria={0: "Wrong", 1: "7"}),
        SubtestItem(3, "If you have 5 candies and eat 2, how many are left?", 
                   time_limit=30, score_criteria={0: "Wrong", 1: "3"}),
        SubtestItem(4, "What is 8 - 3?", time_limit=30,
                   score_criteria={0: "Wrong", 1: "5"}),
        SubtestItem(5, "If one pencil costs 2 rupees, how much do 3 pencils cost?", 
                   time_limit=45, score_criteria={0: "Wrong", 1: "6 rupees"}),
        SubtestItem(6, "What is 9 + 7?", time_limit=30,
                   score_criteria={0: "Wrong", 1: "16"}),
        SubtestItem(7, "A boy had 12 marbles. He lost 5. How many does he have now?", 
                   time_limit=45, score_criteria={0: "Wrong", 1: "7"}),
        SubtestItem(8, "What is 15 - 8?", time_limit=30,
                   score_criteria={0: "Wrong", 1: "7"}),
        SubtestItem(9, "If 4 children share 20 sweets equally, how many does each get?", 
                   time_limit=60, score_criteria={0: "Wrong", 1: "5"}),
        SubtestItem(10, "What is 6 × 7?", time_limit=30,
                    score_criteria={0: "Wrong", 1: "42"}),
        SubtestItem(11, "A dozen eggs cost 60 rupees. What is the cost of one egg?", 
                    time_limit=60, score_criteria={0: "Wrong", 1: "5 rupees"}),
        SubtestItem(12, "What is 144 ÷ 12?", time_limit=45,
                    score_criteria={0: "Wrong", 1: "12"}),
        SubtestItem(13, "If a train travels 60 km in one hour, how far in 2.5 hours?", 
                    time_limit=90, score_criteria={0: "Wrong", 1: "150 km"}),
        SubtestItem(14, "What is 25% of 80?", time_limit=60,
                    score_criteria={0: "Wrong", 1: "20"}),
        SubtestItem(15, "A shopkeeper sells an item for Rs. 450 with 10% profit. What was his cost?", 
                    time_limit=120, score_criteria={0: "Wrong", 1: "Rs. 409 or approximately 409"}),
    ]
)


SIMILARITIES_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.SIMILARITIES,
    name="Similarities",
    description="Tests verbal concept formation and abstract thinking.",
    instructions="""Say: 'I am going to name two things that are alike in some way. 
Tell me how they are alike.'
Prompt only for the first item if needed.""",
    discontinue_after=4,
    items=[
        SubtestItem(1, "How are a CAT and a DOG alike?", max_score=2,
                   score_criteria={
                       0: "Wrong or difference",
                       1: "Concrete similarity (have four legs, have fur)",
                       2: "Abstract category (both are animals/pets)"
                   }),
        SubtestItem(2, "How are a BALL and an ORANGE alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (both are round)",
                       2: "Abstract (both are spherical objects)"
                   }),
        SubtestItem(3, "How are a SHIRT and a PANT alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (we wear them)",
                       2: "Abstract (both are clothing/garments)"
                   }),
        SubtestItem(4, "How are MILK and WATER alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (we drink them)",
                       2: "Abstract (both are liquids/fluids)"
                   }),
        SubtestItem(5, "How are a PIANO and a GUITAR alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (make music/sound)",
                       2: "Abstract (musical instruments)"
                   }),
        SubtestItem(6, "How are ANGER and JOY alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (feelings we have)",
                       2: "Abstract (emotions/psychological states)"
                   }),
        SubtestItem(7, "How are a KNIFE and a SAW alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Concrete (can cut things)",
                       2: "Abstract (cutting tools/implements)"
                   }),
        SubtestItem(8, "How are LIBERTY and JUSTICE alike?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Vague (good things, rights)",
                       2: "Abstract (fundamental values/ideals/concepts)"
                   }),
        SubtestItem(9, "How are FIRST and LAST alike?", max_score=2,
                   score_criteria={
                       0: "Wrong (opposites)",
                       1: "Concrete (positions)",
                       2: "Abstract (ordinal positions/extremes)"
                   }),
        SubtestItem(10, "How are a POEM and a STATUE alike?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Concrete (created by people)",
                        2: "Abstract (forms of art/artistic expressions)"
                    }),
    ]
)


VOCABULARY_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.VOCABULARY,
    name="Vocabulary",
    description="Tests word knowledge and verbal concept formation.",
    instructions="""Say: 'I want to see how many words you know. 
Tell me what [word] means.'
For children 8+, start at Item 10. If 0 on Items 10 or 11, go back to Item 1.
Query vague responses once: 'Tell me more about that.'""",
    discontinue_after=5,
    start_item=10,  # For age 8+
    reverse_rule=True,
    items=[
        SubtestItem(1, "What does APPLE mean?", max_score=2,
                   score_criteria={
                       0: "Wrong/No response",
                       1: "Vague (fruit, red thing)",
                       2: "Clear definition (a fruit that grows on trees)"
                   }),
        SubtestItem(2, "What does BICYCLE mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Partial (has wheels, we ride it)",
                       2: "Complete (two-wheeled vehicle for riding)"
                   }),
        SubtestItem(3, "What does BRAVE mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Example only (a soldier)",
                       2: "Definition (not afraid, courageous)"
                   }),
        SubtestItem(4, "What does ALPHABET mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Example (A, B, C)",
                       2: "Definition (letters of a language)"
                   }),
        SubtestItem(5, "What does UMBRELLA mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Use only (keeps rain off)",
                       2: "Complete (device to protect from rain/sun)"
                   }),
        SubtestItem(6, "What does ANCIENT mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Partial (old)",
                       2: "Complete (very old, from long ago)"
                   }),
        SubtestItem(7, "What does HAZARDOUS mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Partial (bad, not good)",
                       2: "Complete (dangerous, risky)"
                   }),
        SubtestItem(8, "What does MIGRATE mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Partial (move, go somewhere)",
                       2: "Complete (move from one place to another, especially seasonally)"
                   }),
        SubtestItem(9, "What does COMPASSION mean?", max_score=2,
                   score_criteria={
                       0: "Wrong",
                       1: "Partial (being nice)",
                       2: "Complete (sympathy, caring for others' suffering)"
                   }),
        SubtestItem(10, "What does ABSORB mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Partial (take in)",
                        2: "Complete (soak up, take in liquid or knowledge)"
                    }),
        SubtestItem(11, "What does OBSTRUCT mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Partial (stop)",
                        2: "Complete (block, hinder, get in the way)"
                    }),
        SubtestItem(12, "What does TRANSPARENT mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Example (like glass)",
                        2: "Complete (see-through, clear)"
                    }),
        SubtestItem(13, "What does UNANIMOUS mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Partial (everyone)",
                        2: "Complete (everyone agrees, complete agreement)"
                    }),
        SubtestItem(14, "What does PLAGIARIZE mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Partial (copy)",
                        2: "Complete (copy someone's work and claim as own)"
                    }),
        SubtestItem(15, "What does DILATORY mean?", max_score=2,
                    score_criteria={
                        0: "Wrong",
                        1: "Partial (slow)",
                        2: "Complete (causing delay, intentionally slow)"
                    }),
    ]
)


DIGIT_SPAN_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.DIGIT_SPAN,
    name="Digit Span",
    description="Tests auditory short-term memory and attention.",
    instructions="""Say: 'I am going to say some numbers. Listen carefully and repeat them after me.'
For Digits Backward: 'Now I am going to say more numbers. This time say them backwards.'
Say digits at rate of 1 per second. Two trials per item.
Score 1 if either trial is correct.""",
    discontinue_after=2,  # Two consecutive items failed (both trials)
    items=[
        # Digits Forward
        SubtestItem(1, "Digits Forward: 3-8-6", max_score=1,
                   notes="Trial 2: 6-1-2"),
        SubtestItem(2, "Digits Forward: 3-4-1-7", max_score=1,
                   notes="Trial 2: 6-1-5-8"),
        SubtestItem(3, "Digits Forward: 8-4-2-3-9", max_score=1,
                   notes="Trial 2: 5-2-1-8-6"),
        SubtestItem(4, "Digits Forward: 3-8-9-1-7-4", max_score=1,
                   notes="Trial 2: 7-9-6-4-8-3"),
        SubtestItem(5, "Digits Forward: 5-1-7-4-2-3-8", max_score=1,
                   notes="Trial 2: 9-8-5-2-1-6-3"),
        SubtestItem(6, "Digits Forward: 1-6-4-5-9-7-6-3", max_score=1,
                   notes="Trial 2: 2-9-7-6-3-1-5-4"),
        SubtestItem(7, "Digits Forward: 5-3-8-7-1-2-4-6-9", max_score=1,
                   notes="Trial 2: 4-2-6-9-1-7-8-3-5"),
        # Digits Backward
        SubtestItem(8, "Digits Backward: 2-5", max_score=1,
                   notes="Trial 2: 6-3. Answer: 5-2 or 3-6"),
        SubtestItem(9, "Digits Backward: 5-7-4", max_score=1,
                   notes="Trial 2: 2-5-9. Answer: 4-7-5 or 9-5-2"),
        SubtestItem(10, "Digits Backward: 7-2-9-6", max_score=1,
                    notes="Trial 2: 8-4-9-3"),
        SubtestItem(11, "Digits Backward: 4-1-3-5-7", max_score=1,
                    notes="Trial 2: 9-7-8-5-2"),
        SubtestItem(12, "Digits Backward: 1-6-5-2-9-8", max_score=1,
                    notes="Trial 2: 3-6-7-1-9-4"),
        SubtestItem(13, "Digits Backward: 8-5-9-2-3-4-2", max_score=1,
                    notes="Trial 2: 4-5-7-9-2-8-1"),
        SubtestItem(14, "Digits Backward: 6-9-1-6-3-2-5-8", max_score=1,
                    notes="Trial 2: 3-1-7-9-5-4-8-2"),
    ]
)


# ==========================================
# PERFORMANCE SUBTESTS
# ==========================================

PICTURE_COMPLETION_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.PICTURE_COMPLETION,
    name="Picture Completion",
    description="Tests visual perception and ability to identify missing parts.",
    instructions="""Show each picture and ask: 'What important part is missing from this picture?'
Allow 20 seconds per item.
Score 1 for correct identification of missing part.""",
    discontinue_after=4,
    timing_per_item=True,
    items=[
        SubtestItem(1, "A comb with missing teeth", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Teeth/Bristles"},
                   correct_answers=["teeth", "bristles"],
                   notes="Picture: Comb missing some teeth"),
        SubtestItem(2, "A door without a handle", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Handle/Knob"},
                   correct_answers=["handle", "knob", "doorknob"],
                   notes="Picture: Door missing handle"),
        SubtestItem(3, "A face without eyebrows", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Eyebrows"},
                   correct_answers=["eyebrows", "eyebrow"],
                   notes="Picture: Human face missing eyebrows"),
        SubtestItem(4, "A table with one leg missing", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Leg"},
                   correct_answers=["leg"],
                   notes="Picture: Table with 3 legs instead of 4"),
        SubtestItem(5, "A rabbit without ears", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Ears"},
                   correct_answers=["ears", "ear"],
                   notes="Picture: Rabbit missing ears"),
        SubtestItem(6, "A clock without hands", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Hands/Needles"},
                   correct_answers=["hands", "needles", "hand"],
                   notes="Picture: Clock face missing hands"),
        SubtestItem(7, "A scissors with one blade missing", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Blade"},
                   correct_answers=["blade"],
                   notes="Picture: Scissors with only one blade"),
        SubtestItem(8, "A girl without nose", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Nose"},
                   correct_answers=["nose"],
                   notes="Picture: Girl's face missing nose"),
        SubtestItem(9, "A shoe without laces", time_limit=20, max_score=1,
                   score_criteria={0: "Wrong/Timeout", 1: "Laces/Shoelaces"},
                   correct_answers=["laces", "shoelaces", "lace"],
                   notes="Picture: Shoe missing laces"),
        SubtestItem(10, "A cat without whiskers", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Whiskers"},
                    correct_answers=["whiskers"],
                    notes="Picture: Cat face missing whiskers"),
        SubtestItem(11, "An umbrella without handle", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Handle"},
                    correct_answers=["handle"],
                    notes="Picture: Umbrella missing handle"),
        SubtestItem(12, "A bicycle without pedals", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Pedals"},
                    correct_answers=["pedals", "pedal"],
                    notes="Picture: Bicycle missing pedals"),
        SubtestItem(13, "A peacock without tail feathers", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Tail/Feathers"},
                    correct_answers=["tail", "feathers", "tail feathers"],
                    notes="Picture: Peacock missing its decorative tail"),
        SubtestItem(14, "A telephone without buttons/dial", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Buttons/Keys/Dial"},
                    correct_answers=["buttons", "keys", "dial", "keypad"],
                    notes="Picture: Phone missing buttons"),
        SubtestItem(15, "A leaf without veins", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Veins"},
                    correct_answers=["veins"],
                    notes="Picture: Leaf without visible veins"),
        SubtestItem(16, "A fish without fins", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Fins"},
                    correct_answers=["fins", "fin"],
                    notes="Picture: Fish missing fins"),
        SubtestItem(17, "A staircase without railing", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Railing/Handrail"},
                    correct_answers=["railing", "handrail", "banister"],
                    notes="Picture: Stairs without railing"),
        SubtestItem(18, "An elephant without tusks", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Tusks"},
                    correct_answers=["tusks", "tusk"],
                    notes="Picture: Elephant missing tusks"),
        SubtestItem(19, "A car without headlights", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Headlights/Lights"},
                    correct_answers=["headlights", "lights", "headlight"],
                    notes="Picture: Car front missing headlights"),
        SubtestItem(20, "A thermometer without scale markings", time_limit=20, max_score=1,
                    score_criteria={0: "Wrong/Timeout", 1: "Scale/Markings/Numbers"},
                    correct_answers=["scale", "markings", "numbers"],
                    notes="Picture: Thermometer without temperature markings"),
    ]
)


BLOCK_DESIGN_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.BLOCK_DESIGN,
    name="Block Design",
    description="Tests spatial visualization and constructional ability.",
    instructions="""Present blocks and design card.
Say: 'Make one just like this using these blocks.'
Time each design. Award bonus points for speed on more difficult designs.""",
    discontinue_after=3,
    timing_per_item=True,
    items=[
        SubtestItem(1, "Design 1 (4 blocks)", time_limit=60, max_score=4,
                   notes="Bonus: <10s=2pts, 10-15s=1pt"),
        SubtestItem(2, "Design 2 (4 blocks)", time_limit=60, max_score=4,
                   notes="Bonus: <10s=2pts, 10-15s=1pt"),
        SubtestItem(3, "Design 3 (4 blocks)", time_limit=60, max_score=4,
                   notes="Bonus: <15s=2pts, 15-20s=1pt"),
        SubtestItem(4, "Design 4 (4 blocks)", time_limit=60, max_score=4,
                   notes="Bonus: <20s=2pts, 20-30s=1pt"),
        SubtestItem(5, "Design 5 (9 blocks)", time_limit=120, max_score=4,
                   notes="Bonus: <35s=2pts, 35-50s=1pt"),
        SubtestItem(6, "Design 6 (9 blocks)", time_limit=120, max_score=4,
                   notes="Bonus: <55s=2pts, 55-75s=1pt"),
        SubtestItem(7, "Design 7 (9 blocks)", time_limit=120, max_score=4,
                   notes="Bonus: <55s=2pts, 55-75s=1pt"),
        SubtestItem(8, "Design 8 (9 blocks)", time_limit=120, max_score=4,
                   notes="Bonus: <75s=2pts, 75-90s=1pt"),
        SubtestItem(9, "Design 9 (9 blocks)", time_limit=120, max_score=4,
                   notes="Bonus: <90s=2pts, 90-120s=1pt"),
        SubtestItem(10, "Design 10 (9 blocks)", time_limit=120, max_score=4,
                    notes="Bonus: <90s=2pts, 90-120s=1pt"),
    ]
)


OBJECT_ASSEMBLY_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.OBJECT_ASSEMBLY,
    name="Object Assembly",
    description="Tests part-whole relationships and visual-motor coordination.",
    instructions="""Present puzzle pieces arranged in standard position.
Say: 'Put these pieces together to make something. Work as fast as you can.'
Time each puzzle. Award points based on correct junctures and bonus for speed.""",
    discontinue_after=0,  # Administer all items
    timing_per_item=True,
    items=[
        SubtestItem(1, "Girl (4 pieces)", time_limit=120, max_score=8,
                   notes="Score by junctures. Bonus for speed."),
        SubtestItem(2, "Horse (6 pieces)", time_limit=150, max_score=10,
                   notes="Score by junctures. Bonus for speed."),
        SubtestItem(3, "Face (8 pieces)", time_limit=150, max_score=12,
                   notes="Score by junctures. Bonus for speed."),
        SubtestItem(4, "Car (7 pieces)", time_limit=180, max_score=10,
                   notes="Score by junctures. Bonus for speed."),
    ]
)


CODING_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.CODING,
    name="Coding",
    description="Tests visual-motor speed, accuracy, and short-term memory.",
    instructions="""For children under 8: Use Coding A (symbols).
For children 8 and above: Use Coding B (digit-symbol).
Allow 120 seconds. Score = number of correct symbols.""",
    global_time_limit=120,
    discontinue_after=0,  # Timed test
    items=[
        SubtestItem(1, "Coding A/B - 120 second test", time_limit=120, max_score=100,
                   notes="Age <8: Coding A (Symbols). Age ≥8: Coding B (Digit Symbol)")
    ]
)


MAZES_SUBTEST = SubtestDefinition(
    subtest_type=SubtestType.MAZES,
    name="Mazes",
    description="Tests planning ability and visual-motor control.",
    instructions="""Present maze and pencil without eraser.
Say: 'Start here and find your way out without crossing any lines.'
Time each maze. Score based on errors (crossing lines or entering blind alleys).""",
    discontinue_after=2,
    timing_per_item=True,
    items=[
        SubtestItem(1, "Maze 1", time_limit=30, max_score=2,
                   score_criteria={0: ">2 errors", 1: "1-2 errors", 2: "0 errors"}),
        SubtestItem(2, "Maze 2", time_limit=30, max_score=2,
                   score_criteria={0: ">2 errors", 1: "1-2 errors", 2: "0 errors"}),
        SubtestItem(3, "Maze 3", time_limit=45, max_score=3,
                   score_criteria={0: ">3 errors", 1: "2-3 errors", 2: "1 error", 3: "0 errors"}),
        SubtestItem(4, "Maze 4", time_limit=45, max_score=3,
                   score_criteria={0: ">3 errors", 1: "2-3 errors", 2: "1 error", 3: "0 errors"}),
        SubtestItem(5, "Maze 5", time_limit=60, max_score=3,
                   score_criteria={0: ">3 errors", 1: "2-3 errors", 2: "1 error", 3: "0 errors"}),
        SubtestItem(6, "Maze 6", time_limit=60, max_score=4,
                   score_criteria={0: ">4 errors", 1: "3-4 errors", 2: "2 errors", 3: "1 error", 4: "0 errors"}),
        SubtestItem(7, "Maze 7", time_limit=90, max_score=4,
                   score_criteria={0: ">4 errors", 1: "3-4 errors", 2: "2 errors", 3: "1 error", 4: "0 errors"}),
        SubtestItem(8, "Maze 8", time_limit=90, max_score=5,
                   score_criteria={0: ">5 errors", 1: "4-5 errors", 2: "2-3 errors", 3: "1 error", 4: "0 errors"}),
    ]
)


# ==========================================
# Subtest Registry
# ==========================================

SUBTEST_DEFINITIONS: Dict[SubtestType, SubtestDefinition] = {
    # Verbal
    SubtestType.INFORMATION: INFORMATION_SUBTEST,
    SubtestType.COMPREHENSION: COMPREHENSION_SUBTEST,
    SubtestType.ARITHMETIC: ARITHMETIC_SUBTEST,
    SubtestType.SIMILARITIES: SIMILARITIES_SUBTEST,
    SubtestType.VOCABULARY: VOCABULARY_SUBTEST,
    SubtestType.DIGIT_SPAN: DIGIT_SPAN_SUBTEST,
    # Performance
    SubtestType.PICTURE_COMPLETION: PICTURE_COMPLETION_SUBTEST,
    SubtestType.BLOCK_DESIGN: BLOCK_DESIGN_SUBTEST,
    SubtestType.OBJECT_ASSEMBLY: OBJECT_ASSEMBLY_SUBTEST,
    SubtestType.CODING: CODING_SUBTEST,
    SubtestType.MAZES: MAZES_SUBTEST,
}


def get_subtest_definition(subtest_type: SubtestType) -> SubtestDefinition:
    """Get the definition for a subtest."""
    return SUBTEST_DEFINITIONS[subtest_type]


def get_verbal_subtests() -> List[SubtestDefinition]:
    """Get all verbal subtest definitions in order."""
    from models import VERBAL_SUBTESTS
    return [SUBTEST_DEFINITIONS[st] for st in VERBAL_SUBTESTS]


def get_performance_subtests() -> List[SubtestDefinition]:
    """Get all performance subtest definitions in order."""
    from models import PERFORMANCE_SUBTESTS
    return [SUBTEST_DEFINITIONS[st] for st in PERFORMANCE_SUBTESTS]
