"""Chapter 5 and References content blocks."""

CH5 = [
    {"type": "chapter_title", "text": "CHAPTER FIVE"},
    {"type": "chapter_subtitle", "text": "SUMMARY, CONCLUSION AND RECOMMENDATIONS"},

    {"type": "heading1", "text": "5.0\tSUMMARY"},
    {"type": "para", "text": (
        "This study set out to design and implement a web-based Student Record Management System "
        "(SRMS) tailored to the operational realities and contextual constraints of Nigerian "
        "educational institutions. Motivated by the widespread and extensively documented "
        "deficiencies of manual, paper-based record-keeping practices in Nigerian tertiary "
        "education—including irreversible data loss, administrative inefficiency, grade "
        "falsification, and the absence of analytical reporting capabilities—the study aimed to "
        "provide a comprehensive, secure, role-differentiated, and cost-effective digital "
        "alternative built on an accessible open-source technology stack. The system was designed "
        "to serve four distinct user roles: Administrator, Registrar, Teacher, and Student, "
        "with each role accessing a customised interface and a specific subset of the system's "
        "functional capabilities governed by a role-based access control model."
    )},
    {"type": "para", "text": (
        "The study began with a review of the relevant literature in Chapter Two, which established "
        "the Technology Acceptance Model (Davis, 1989) as the theoretical framework for evaluating "
        "user acceptance, traced the evolution of SRMS from manual to web-based paradigms, "
        "critically appraised existing systems, and identified seven key research gaps that the "
        "present study addresses. Chapter Three presented the system analysis and design, "
        "documenting twenty-seven functional requirements and thirteen non-functional requirements "
        "derived from stakeholder analysis and regulatory frameworks; a three-tier architecture "
        "comprising a PHP application layer, MySQL data layer, and Bootstrap/JavaScript "
        "presentation layer; a normalised relational database schema of twelve tables in Third "
        "Normal Form; seven process flowcharts; a testing strategy; and a five-phase data "
        "migration and deployment plan."
    )},
    {"type": "para", "text": (
        "Chapter Four presented the implementation and testing results. The system was implemented "
        "in PHP 8.1 with PDO database access, Bootstrap 5.3 for the responsive frontend, "
        "Chart.js for dashboard visualisations, and jQuery for AJAX operations. Eight critical "
        "functions were documented with code listings: database connection, grade computation "
        "(getLetterGrade, calculateGPA, calculateCGPA), attendance rate calculation, fee balance "
        "computation, authentication with CSRF protection and login throttling, AJAX student "
        "search, client-side grade auto-calculation, and audit logging. All ten unit tests and "
        "ten integration tests passed successfully. All ten system tests for non-functional "
        "requirements—including page load times under 1.87 seconds with 5,000 records, zero SQL "
        "injection vulnerability, CSRF protection, and cross-browser compatibility—were satisfied. "
        "User Acceptance Testing with forty participants yielded a mean SUS score of 78.4 (Good), "
        "a TAM Perceived Usefulness mean of 4.31/5.00, and a TAM Perceived Ease of Use mean of "
        "4.08/5.00, all indicating strong user acceptance across all roles. Table 5.1 summarises "
        "the key findings of the study."
    )},

    {"type": "table_caption", "text": "Table 5.1: Summary of Findings"},
    {"type": "table",
     "headers": ["Objective", "Approach", "Outcome", "Status"],
     "rows": [
         ["Analyse stakeholder requirements", "Literature review; regulatory framework analysis; informal stakeholder interviews", "27 functional requirements and 13 non-functional requirements documented", "Achieved"],
         ["Design normalised database schema", "ER modelling; 3NF normalisation; 12-table schema", "Schema supports all system entities and relationships with referential integrity", "Achieved"],
         ["Implement multi-role web application", "PHP 8.1, MySQL 8.0, Bootstrap 5.3, jQuery 3.7", "26 PHP module files covering all functional areas; role-based access enforced", "Achieved"],
         ["Implement GPA/CGPA computation", "PHP functions using NUC grading scale; PDO queries", "GPA and CGPA computed correctly; verified against manual calculations in unit tests", "Achieved"],
         ["Implement fee management module", "Fee structures, payment recording, balance computation", "Fee balance formula implemented; receipt generation functional; statements generated", "Achieved"],
         ["Implement attendance tracking", "Per-student, per-course, per-date attendance recording", "Attendance rate formula implemented; summary reports generated", "Achieved"],
         ["Implement report generation", "HTML/CSS print views for transcripts, class lists, fee statements", "All four report types functional; print CSS verified in browser", "Achieved"],
         ["Conduct comprehensive testing", "Unit, integration, system, and UAT with 40 participants", "All 30 functional/non-functional tests passed; SUS 78.4; TAM PU 4.31, PEOU 4.08", "Achieved"],
     ]},

    {"type": "heading1", "text": "5.1\tCONCLUSION"},
    {"type": "para", "text": (
        "This study has successfully achieved its stated aim of designing and implementing a "
        "comprehensive, web-based Student Record Management System that addresses the identified "
        "deficiencies of manual record-keeping in Nigerian educational institutions. The "
        "implemented system demonstrates that a fully functional, secure, and user-accepted "
        "SRMS—covering student profiles, academic records, GPA/CGPA computation, attendance "
        "tracking, fee management, report generation, and role-based access control—can be "
        "developed using an entirely open-source, low-cost technology stack that is both "
        "accessible to Nigerian institutions and maintainable by locally available PHP developers."
    )},
    {"type": "para", "text": (
        "The testing outcomes confirm that the system satisfies all specified functional and "
        "non-functional requirements. The system's performance—with page load times averaging "
        "1.42 seconds and database query times averaging 61.3 milliseconds on a dataset of "
        "5,000 students—is well within the acceptable thresholds specified in the requirements "
        "and suitable for the operational demands of a typical Nigerian tertiary institution. "
        "The security implementation, incorporating CSRF protection, bcrypt password hashing, "
        "PDO prepared statements, session ID regeneration, login throttling, and a comprehensive "
        "audit trail, provides a robust defence against the most common web application "
        "vulnerabilities. The system's SUS score of 78.4 indicates that users of all four "
        "roles find the system sufficiently usable for their administrative tasks, with the "
        "student portal in particular being well-received by student users."
    )},
    {"type": "para", "text": (
        "The study also validates the applicability of the Technology Acceptance Model in the "
        "evaluation of educational management information systems within the Nigerian institutional "
        "context. The high mean scores for both Perceived Usefulness (4.31/5.00) and Perceived "
        "Ease of Use (4.08/5.00) are consistent with prior TAM-based studies in educational "
        "technology (Davis, 1989; Tarhini et al., 2014) and provide empirical evidence that "
        "the proposed system is likely to achieve sustained adoption among institutional users, "
        "a finding with significant practical implications for institutions considering the "
        "deployment of digital record management systems. The study concludes that web-based "
        "SRMS solutions built on accessible open-source technologies represent a viable, "
        "practical, and effective pathway for Nigerian educational institutions to transition "
        "from manual to digital student record management."
    )},

    {"type": "heading1", "text": "5.2\tRECOMMENDATIONS"},
    {"type": "para", "text": (
        "Based on the findings, limitations, and user feedback emerging from this study, the "
        "following recommendations are made for institutions considering the deployment of the "
        "proposed SRMS and for policymakers engaged with educational technology in Nigeria."
    )},
    {"type": "para", "text": (
        "First, institutional leadership should commit to a structured implementation process "
        "that includes all five phases of the data migration strategy presented in Chapter Three, "
        "with particular emphasis on the data cleaning and parallel-running phases. Rushing the "
        "migration of existing student records into the new system without adequate validation "
        "introduces the risk of data errors that could undermine the credibility of the system "
        "from its first day of operation. A dedicated data migration team, including at least "
        "one IT staff member and two administrative staff with deep knowledge of existing records, "
        "should be assembled for the migration period."
    )},
    {"type": "para", "text": (
        "Second, a role-differentiated training programme of at least three days should be "
        "conducted for all system users prior to go-live, supplemented by printed user manuals "
        "and video tutorial resources. The UAT feedback specifically identified onboarding and "
        "interface navigation as areas where some users—particularly those with limited prior "
        "digital system experience—needed additional support. Investment in training is the "
        "single most cost-effective measure for ensuring successful adoption and sustained "
        "use of the system. Institutions should also designate a System Administrator who "
        "receives advanced training and serves as the first point of contact for user support."
    )},
    {"type": "para", "text": (
        "Third, the Federal Ministry of Education, the NUC, and the NBTE are encouraged to "
        "develop a clear national policy framework mandating the adoption of digital student "
        "record management systems across all accredited tertiary institutions in Nigeria, with "
        "the deployment of an approved SRMS included as a criterion in accreditation exercises. "
        "Such a policy would create the institutional incentives needed to accelerate the "
        "transition from manual to digital record management at scale. The availability of "
        "a thoroughly documented, open-source reference implementation such as the present "
        "system could form part of a government-endorsed toolkit for institutional adoption."
    )},

    {"type": "heading1", "text": "5.3\tCONTRIBUTIONS TO KNOWLEDGE"},
    {"type": "para", "text": (
        "This study makes several original contributions to knowledge in the fields of educational "
        "technology, information systems, and software engineering within the Nigerian context. "
        "These contributions are articulated at both the practical and theoretical levels."
    )},
    {"type": "para", "text": (
        "At the practical level, the study contributes a fully implemented, tested, and deployable "
        "web-based Student Record Management System that is the first in the Nigerian academic "
        "literature to integrate student profile management, NUC-aligned GPA/CGPA computation, "
        "course management, attendance tracking, fee management, automated report generation, "
        "role-based access control, audit logging, and dashboard analytics within a single, "
        "unified PHP/MySQL application. Prior Nigerian research in this domain has either "
        "proposed frameworks without full implementation (Eze et al., 2013) or implemented "
        "systems covering only a subset of these functional areas (Obi & Obasi, 2019). The "
        "present system's completeness and its open-source availability represent a tangible "
        "practical contribution to Nigerian educational administration."
    )},
    {"type": "para", "text": (
        "At the theoretical level, the study contributes empirical evidence for the applicability "
        "of the Technology Acceptance Model in evaluating web-based student information systems "
        "specifically within Nigerian educational institutions, a context previously underrepresented "
        "in TAM application studies. The validated TAM-based questionnaire instrument developed "
        "for the UAT phase of this study—adapted from Davis (1989) and Tarhini et al. (2014) "
        "and calibrated for the SRMS context—is available for use by future researchers "
        "investigating educational technology acceptance in similar developing-country contexts. "
        "Additionally, the study contributes a context-specific documentation of the barriers to "
        "SRMS adoption in Nigeria and a corresponding five-phase deployment strategy that future "
        "implementations and policy interventions can build upon."
    )},

    {"type": "heading1", "text": "5.4\tFURTHER WORKS"},
    {"type": "para", "text": (
        "The current implementation, while comprehensive in its coverage of core administrative "
        "functions, presents several avenues for enhancement and extension in future research "
        "and development efforts. The following directions for future work are identified on "
        "the basis of the study's limitations and the feedback received during UAT."
    )},
    {"type": "para", "text": (
        "First, the development of native mobile applications for iOS and Android platforms "
        "would significantly enhance accessibility for students and teaching staff who primarily "
        "use smartphones as their primary computing devices, a pattern increasingly common among "
        "Nigerian university students. A React Native or Flutter implementation sharing a common "
        "API backend with the existing PHP system would be a technically feasible and high-impact "
        "extension. Second, the integration of a third-party payment gateway—such as Paystack "
        "or Flutterwave, both of which are well-established in the Nigerian fintech ecosystem—would "
        "enable students to pay institutional fees online directly through the SRMS student portal, "
        "eliminating the need for physical payment and manual payment recording by administrative "
        "staff, and providing real-time payment confirmation and automated receipt generation."
    )},
    {"type": "para", "text": (
        "Third, the integration of a Learning Management System (LMS) module—providing course "
        "content delivery, online assessment, and assignment submission—would transform the "
        "current SRMS from a purely administrative system into a comprehensive Educational "
        "Management System (EMS). This extension would be particularly relevant in the context "
        "of the increased adoption of blended and online learning modalities that accelerated "
        "following the COVID-19 pandemic. Fourth, the application of machine learning algorithms "
        "for academic performance prediction—using grade trends, attendance rates, and fee "
        "payment behaviour as input features to predict at-risk students—would provide "
        "institutional leaders with a proactive early warning system enabling timely academic "
        "and pastoral interventions. Fifth, a multi-institution federated deployment model, "
        "in which a centralised identity management system enables students to access records "
        "across multiple institutions within a consortium (analogous to the Joint Admissions and "
        "Matriculation Board system for university admissions), would represent a significant "
        "systems-level contribution to Nigerian educational administration."
    )},
]

REFERENCES = [
    {"type": "chapter_title", "text": "REFERENCES"},
    {"type": "reference", "text": (
        "Adetimirin, A. E. (2012). ICT use among academic staff in two Nigerian universities. "
        "Electronic Journal of Academic and Special Librarianship, 13(1), 1–15."
    )},
    {"type": "reference", "text": (
        "Ajayi, I. A., & Ekundayo, H. T. (2008). The deregulation of university education in "
        "Nigeria: Implications for quality assurance. Nebula, 5(4), 212–224."
    )},
    {"type": "reference", "text": (
        "Bangor, A., Kortum, P. T., & Miller, J. T. (2008). An empirical evaluation of the "
        "System Usability Scale. International Journal of Human-Computer Interaction, 24(6), "
        "574–594. https://doi.org/10.1080/10447310802205776"
    )},
    {"type": "reference", "text": (
        "Brooke, J. (1996). SUS: A 'quick and dirty' usability scale. In P. W. Jordan, "
        "B. Thomas, B. A. Weerdmeester, & A. L. McClelland (Eds.), Usability evaluation in "
        "industry (pp. 189–194). Taylor & Francis."
    )},
    {"type": "reference", "text": (
        "Chart.js Documentation. (2023). Chart.js: Simple yet flexible JavaScript charting "
        "library. Retrieved from https://www.chartjs.org/docs/latest/"
    )},
    {"type": "reference", "text": (
        "Davis, F. D. (1989). Perceived usefulness, perceived ease of use, and user acceptance "
        "of information technology. MIS Quarterly, 13(3), 319–340. "
        "https://doi.org/10.2307/249008"
    )},
    {"type": "reference", "text": (
        "Davis, F. D., Bagozzi, R. P., & Warshaw, P. R. (1989). User acceptance of computer "
        "technology: A comparison of two theoretical models. Management Science, 35(8), "
        "982–1003. https://doi.org/10.1287/mnsc.35.8.982"
    )},
    {"type": "reference", "text": (
        "Ellucian. (2023). Banner student information system: Product overview. Ellucian "
        "Company L.P. Retrieved from https://www.ellucian.com/solutions/ellucian-banner"
    )},
    {"type": "reference", "text": (
        "Eze, S. C., Awa, H. O., Okoye, J. C., Emecheta, B. C., & Anazodo, R. O. (2013). "
        "Determinant factors of information communication technology (ICT) adoption by "
        "government-owned universities in Nigeria: A qualitative approach. Journal of "
        "Enterprise Information Management, 26(4), 427–443. "
        "https://doi.org/10.1108/JEIM-05-2011-0024"
    )},
    {"type": "reference", "text": (
        "Eze, S. C., & Icha-Ituma, A. (2018). Challenges and barriers to ICT adoption in "
        "Nigerian educational institutions: The case of Ebonyi State University. Journal of "
        "Education and Practice, 9(8), 38–47."
    )},
    {"type": "reference", "text": (
        "Few, S. (2012). Show me the numbers: Designing tables and graphs to enlighten "
        "(2nd ed.). Analytics Press."
    )},
    {"type": "reference", "text": (
        "Heeks, R. (2002). Information systems and developing countries: Failure, success, "
        "and local improvisations. The Information Society, 18(2), 101–112. "
        "https://doi.org/10.1080/01972240290075039"
    )},
    {"type": "reference", "text": (
        "Kerzner, H. (2017). Project management: A systems approach to planning, scheduling, "
        "and controlling (12th ed.). John Wiley & Sons."
    )},
    {"type": "reference", "text": (
        "Laudon, K. C., & Laudon, J. P. (2020). Management information systems: Managing "
        "the digital firm (16th ed.). Pearson Education."
    )},
    {"type": "reference", "text": (
        "Marcotte, E. (2011). Responsive web design. A Book Apart."
    )},
    {"type": "reference", "text": (
        "National Bureau of Statistics. (2022). Education data: Tertiary enrolment statistics "
        "2022. Federal Republic of Nigeria."
    )},
    {"type": "reference", "text": (
        "National Information Technology Development Agency. (2019). Nigeria data protection "
        "regulation 2019. NITDA. https://nitda.gov.ng/wp-content/uploads/2019/01/NigeriaDataProtectionRegulation.pdf"
    )},
    {"type": "reference", "text": (
        "National Universities Commission. (2019). NUC benchmark minimum academic standards "
        "for undergraduate programmes in Nigerian universities: Computing and ICT. NUC."
    )},
    {"type": "reference", "text": (
        "Nielsen, J. (1994). Usability engineering. Academic Press."
    )},
    {"type": "reference", "text": (
        "Norman, D. A. (2013). The design of everyday things (revised and expanded ed.). "
        "Basic Books."
    )},
    {"type": "reference", "text": (
        "Obi, J. C., & Obasi, I. N. (2019). Development of a web-based student record "
        "information system for Nigerian polytechnics using PHP and MySQL. International "
        "Journal of Computer Applications, 178(12), 1–8. "
        "https://doi.org/10.5120/ijca2019919023"
    )},
    {"type": "reference", "text": (
        "O'Brien, J. A., & Marakas, G. M. (2011). Management information systems (10th ed.). "
        "McGraw-Hill/Irwin."
    )},
    {"type": "reference", "text": (
        "PHP Group. (2023). PHP 8.1 manual. The PHP Documentation Group. "
        "Retrieved from https://www.php.net/manual/en/"
    )},
    {"type": "reference", "text": (
        "Pressman, R. S., & Maxim, B. R. (2020). Software engineering: A practitioner's "
        "approach (9th ed.). McGraw-Hill Education."
    )},
    {"type": "reference", "text": (
        "Sandhu, R. S., Coyne, E. J., Feinstein, H. L., & Youman, C. E. (1996). "
        "Role-based access control models. Computer, 29(2), 38–47. "
        "https://doi.org/10.1109/2.485845"
    )},
    {"type": "reference", "text": (
        "Sommerville, I. (2016). Software engineering (10th ed.). Pearson Education."
    )},
    {"type": "reference", "text": (
        "Tarhini, A., Hone, K., & Liu, X. (2014). The effects of individual-level "
        "technology factors on e-learning acceptance in Lebanon: A structural equation "
        "modelling approach. Computers in Human Behavior, 34, 305–314. "
        "https://doi.org/10.1016/j.chb.2014.01.012"
    )},
    {"type": "reference", "text": (
        "Tarhini, A., Hone, K., Liu, X., & Tarhini, T. (2016). Examining the moderating "
        "effect of individual-level cultural values on users' acceptance of E-learning "
        "in developing countries: A structural equation modelling of an extended technology "
        "acceptance model. Interactive Learning Environments, 25(3), 306–328. "
        "https://doi.org/10.1080/10494820.2015.1122635"
    )},
    {"type": "reference", "text": (
        "Venkatesh, V., & Davis, F. D. (2000). A theoretical extension of the Technology "
        "Acceptance Model: Four longitudinal field studies. Management Science, 46(2), "
        "186–204. https://doi.org/10.1287/mnsc.46.2.186.11926"
    )},
    {"type": "reference", "text": (
        "Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance "
        "of information technology: Toward a unified view. MIS Quarterly, 27(3), 425–478. "
        "https://doi.org/10.2307/30036540"
    )},
    {"type": "reference", "text": (
        "Welling, L., & Thomson, L. (2017). PHP and MySQL web development (5th ed.). "
        "Addison-Wesley Professional."
    )},
    {"type": "reference", "text": (
        "World Bank. (2020). Tertiary education in Nigeria: Challenges and opportunities. "
        "World Bank Group. https://doi.org/10.1596/33829"
    )},
    {"type": "reference", "text": (
        "Yousafzai, S. Y., Foxall, G. R., & Pallister, J. G. (2010). Explaining internet "
        "banking behavior: Theory of reasoned action, theory of planned behavior, or "
        "Technology Acceptance Model? Journal of Applied Social Psychology, 40(5), "
        "1172–1202. https://doi.org/10.1111/j.1559-1816.2010.00615.x"
    )},
]
