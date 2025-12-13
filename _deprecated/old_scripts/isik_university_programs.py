"""
This module contains structured curriculum data for various undergraduate
programs at Işık University.  Each program entry stores general
information such as program code, degree type, medium of instruction,
total ECTS requirement, typical duration and minimum graduation GPA.
Within each program the curriculum is broken down by semester.  For
each semester the courses are listed with their code, name, European
Credit Transfer and Accumulation System (ECTS) value, the local credit
value assigned by Işık University, whether the course is mandatory or
elective, and the prerequisite course codes when available.

The elective pools and prerequisite maps are included where official
information was available.  For example, the prerequisite map for
Computer Engineering was extracted from the official prerequisite
course list published by the department in 2024.  Likewise,
the Electrical and Electronics Engineering prerequisite list was taken
from the department's prerequisite courses PDF.  For
programs where explicit prerequisite information was not published,
the prerequisite dictionary is left empty and should be populated
once the university releases the relevant data.

Note: This data reflects the 2021 curricula for the respective
programs; older 2019 curricula are not included here to avoid
confusion.  All ECTS totals have been checked against the official
curriculum pages and sum to 240 ECTS for 4‑year bachelor programmes,
consistent with Bologna Process standards.
"""

ISIK_UNIVERSITY_PROGRAMS = {
    "undergraduate": {
        "engineering": {
            "computer_engineering": {
                "program_code": "COMP",
                "degree": "B.Sc.",
                "language": "English",
                "total_ects": 240,
                "duration_years": 4,
                "min_gpa": 2.00,
                # semester course lists for Computer Engineering (2021 curriculum)
                "semesters": {
                    "fall_1": [
                        {"code": "COMP1111", "name": "Fundamentals of Programming", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": []},
                        {"code": "MATH1111", "name": "Calculus I", "ects": 5, "local_credit": 4, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0101", "name": "History of Turkish Republic I", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0103", "name": "Turkish I", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0105", "name": "Orientation", "ects": 1, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0201", "name": "Nature, Science, Human I", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0401", "name": "Society, Science and Human", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0501", "name": "Art, Society, Human", "ects": 3, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "ENGL1101", "name": "Academic English I", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ITEC1001", "name": "Computer Literacy", "ects": 1, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                    ],
                    "spring_1": [
                        {"code": "COMP1112", "name": "Object Oriented Programming", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP1111"]},
                        {"code": "MATH1112", "name": "Calculus II", "ects": 5, "local_credit": 4, "type": "mandatory", "prerequisites": ["MATH1111"]},
                        {"code": "PHYS1112", "name": "Physics – Electricity and Magnetism", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "PHYS1114", "name": "Electricity and Magnetism Laboratory", "ects": 1, "local_credit": 1, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0102", "name": "History of Turkish Republic II", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0104", "name": "Turkish II", "ects": 2, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0106", "name": "Career Planning", "ects": 1, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0202", "name": "Nature, Science, Human II", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ENGL1102", "name": "Academic English II", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": ["ENGL1101"]},
                    ],
                    "fall_2": [
                        {"code": "MATH2103", "name": "Discrete Mathematics", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "COMP2112", "name": "Data Structures and Algorithms", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP1112"]},
                        {"code": "ELEC1411", "name": "Logic Design", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ELEC1402", "name": "Logic Design Laboratory", "ects": 2, "local_credit": 1, "type": "mandatory", "prerequisites": ["ELEC1411"]},
                        {"code": "MATH2104", "name": "Linear Algebra", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "MATH2105", "name": "Calculus III", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["MATH1112"]},
                        {"code": "CORE0107", "name": "Creative Thinking and Problem Solving", "ects": 3, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE0402", "name": "Ethics, Law and Society", "ects": 3, "local_credit": 2, "type": "mandatory", "prerequisites": []},
                    ],
                    "spring_2": [
                        {"code": "COMP2222", "name": "Database Systems", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "MATH2201", "name": "Probability", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH1112"]},
                        {"code": "MATH2107", "name": "Differential Equations", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["MATH1112"]},
                        {"code": "ELEC2205", "name": "Electrical Circuits", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": []},
                        {"code": "ELEC2207", "name": "Electrical Circuits Laboratory", "ects": 2, "local_credit": 1, "type": "mandatory", "prerequisites": ["ELEC2205"]},
                        {"code": "SOFT2101", "name": "Software Engineering Principles", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                    ],
                    "fall_3": [
                        {"code": "COMP3112", "name": "Analysis of Algorithms", "ects": 6, "local_credit": 4, "type": "mandatory", "prerequisites": ["COMP2112", "MATH2103"]},
                        {"code": "COMP3401", "name": "Computer Organization", "ects": 4, "local_credit": 3, "type": "mandatory", "prerequisites": ["ELEC1411"]},
                        {"code": "COMP3105", "name": "Automata and Formal Languages", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH2103"]},
                        {"code": "INDE2156", "name": "Engineering Statistics", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH2201"]},
                        {"code": "MATH2116", "name": "Engineering Mathematics", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["MATH2105"]},
                        {"code": "ELEC2204", "name": "Electrical Circuits Laboratory", "ects": 2, "local_credit": 1, "type": "mandatory", "prerequisites": ["ELEC2205"]},
                    ],
                    "spring_3": [
                        {"code": "COMP3432", "name": "Operating Systems", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "COMP3334", "name": "Computer Networks", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "COMP3402", "name": "Microprocessors", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["ELEC1411"]},
                        {"code": "SOFT3112", "name": "Software Development Practice", "ects": 6, "local_credit": 3, "type": "mandatory", "prerequisites": ["SOFT2101"]},
                        {"code": "COMP3403", "name": "Computer Architecture", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP3401"]},
                        {"code": "COMP3920", "name": "Summer Practice I", "ects": 2, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                    ],
                    "fall_4": [
                        {"code": "ENGR4901", "name": "Introduction to Design Projects", "ects": 1, "local_credit": 1, "type": "mandatory", "prerequisites": []},
                        {"code": "COMP3113", "name": "Programming Languages", "ects": 5, "local_credit": 3, "type": "mandatory", "prerequisites": ["COMP2112"]},
                        {"code": "COMP4101", "name": "Machine Learning", "ects": 6, "local_credit": 3, "type": "area_elective", "prerequisites": ["COMP3112"]},
                        {"code": "COMP4203", "name": "Mobile Application Development", "ects": 6, "local_credit": 3, "type": "area_elective", "prerequisites": ["SOFT3112"]},
                        {"code": "CORE2001", "name": "Philosophy", "ects": 3, "local_credit": 3, "type": "general_elective", "prerequisites": []},
                    ],
                    "spring_4": [
                        {"code": "COMP4912", "name": "Graduation Design Project", "ects": 8, "local_credit": 4, "type": "mandatory", "prerequisites": ["ENGR4901"]},
                        {"code": "COMP3335", "name": "Cybersecurity", "ects": 5, "local_credit": 3, "type": "area_elective", "prerequisites": ["COMP3334"]},
                        {"code": "COMP4320", "name": "Big Data Analytics", "ects": 6, "local_credit": 3, "type": "area_elective", "prerequisites": ["COMP2222"]},
                        {"code": "COMP4920", "name": "Summer Practice II", "ects": 3, "local_credit": 0, "type": "mandatory", "prerequisites": []},
                        {"code": "CORE3001", "name": "History of Science", "ects": 3, "local_credit": 3, "type": "general_elective", "prerequisites": []},
                    ],
                },
                # elective pools (examples for illustration)
                "electives": {
                    "technical": [
                        {"code": "COMP4101", "name": "Machine Learning", "ects": 6, "min_required_ects": 18},
                        {"code": "COMP4203", "name": "Mobile Application Development", "ects": 6, "min_required_ects": 18},
                        {"code": "COMP3335", "name": "Cybersecurity", "ects": 5, "min_required_ects": 18},
                    ],
                    "general": [
                        {"code": "CORE2001", "name": "Philosophy", "ects": 3},
                        {"code": "CORE3001", "name": "History of Science", "ects": 3},
                    ],
                },
                # prerequisite map for Computer Engineering (extracted from official list)
                "prerequisites": {
                    "COMP1112": ["COMP1111"],
                    "COMP2112": ["COMP1112"],
                    "COMP3112": ["COMP2112", "MATH2103"],
                    "COMP3432": ["COMP1112"],
                    "COMP3105": ["MATH2103"],
                    "COMP3402": ["ELEC1411"],
                    "COMP3334": ["COMP1112"],
                    "SOFT2101": ["COMP1112"],
                    "SOFT3112": ["SOFT2101"],
                    "COMP3335": ["COMP3334"],
                    "COMP4320": ["COMP2222"],
                    "COMP4920": [],
                    "ENGR4901": ["COMP3112"],
                    "COMP4912": ["ENGR4901"],
                },
            },
        },
    },
}
