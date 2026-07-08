"""Chapter 2 content blocks."""

CH2 = [
    {"type": "chapter_title", "text": "CHAPTER TWO"},
    {"type": "chapter_subtitle", "text": "LITERATURE REVIEW"},

    {"type": "heading1", "text": "2.0\tINTRODUCTION"},
    {"type": "para", "text": (
        "This chapter presents a comprehensive review of the existing literature relevant to the design "
        "and implementation of web-based Student Record Management Systems (SRMS). The review is "
        "structured to provide both a theoretical foundation for the study and a critical appraisal of "
        "existing systems, technologies, and research findings. The chapter begins with an examination "
        "of the Technology Acceptance Model (TAM), which serves as the theoretical framework for "
        "evaluating user acceptance of the proposed system. It then traces the conceptual evolution "
        "of student record management systems from manual to digital paradigms, critically reviews "
        "selected existing systems at both national and international levels, evaluates the web "
        "technologies employed in the system's development, discusses user interface and user "
        "experience principles relevant to educational software, identifies the research gaps that the "
        "current study addresses, and examines the specific challenges and barriers to SRMS adoption "
        "in Nigeria. The chapter concludes with a synthesis of the key insights drawn from the "
        "reviewed literature."
    )},

    {"type": "heading1", "text": "2.1\tTHEORETICAL FRAMEWORK: TECHNOLOGY ACCEPTANCE MODEL"},
    {"type": "para", "text": (
        "The Technology Acceptance Model (TAM), originally proposed by Davis (1989) and subsequently "
        "refined by Davis, Bagozzi, and Warshaw (1989), is one of the most widely applied theoretical "
        "frameworks in information systems research for explaining and predicting user acceptance of "
        "new technology. TAM posits that two primary beliefs—Perceived Usefulness (PU) and Perceived "
        "Ease of Use (PEOU)—determine an individual's attitude toward using a technology, which in "
        "turn influences their behavioural intention to use it, ultimately leading to actual system "
        "use. Perceived Usefulness is defined as the degree to which a person believes that using a "
        "particular system would enhance their job performance, while Perceived Ease of Use refers to "
        "the degree to which a person believes that using the system would be free from effort "
        "(Davis, 1989)."
    )},
    {"type": "para", "text": (
        "TAM has been extensively applied in the evaluation of educational information systems, including "
        "learning management systems, e-library platforms, and student information portals. Tarhini, "
        "Hone, and Liu (2014) applied TAM to investigate factors affecting e-learning acceptance among "
        "students in Lebanon and Jordan, finding that Perceived Usefulness and Perceived Ease of Use "
        "significantly predicted intention to use. Similarly, Eze, Awa, Okoye, Emecheta, and Anazodo "
        "(2013) applied TAM to study the acceptance of e-learning systems in Nigerian universities, "
        "confirming the model's applicability in the Nigerian context despite unique socio-technical "
        "challenges such as limited infrastructure and digital literacy variations among staff and "
        "students. The present study adopts TAM as the evaluative framework for the User Acceptance "
        "Testing phase, using a TAM-based questionnaire to measure PU and PEOU among system users."
    )},
    {"type": "para", "text": (
        "TAM has been extended in several directions since its original formulation. Venkatesh and "
        "Davis (2000) proposed TAM2, which incorporated subjective norm and cognitive instrumental "
        "processes as additional antecedents of Perceived Usefulness. Venkatesh, Morris, Davis, and "
        "Davis (2003) later proposed the Unified Theory of Acceptance and Use of Technology (UTAUT), "
        "which unified TAM with several competing models. However, for the purposes of the present "
        "study, the original TAM framework is considered sufficient and appropriate, given its "
        "parsimony, its established validity in educational technology contexts, and the practical "
        "constraints of conducting UAT within a single institutional setting. The TAM constructs "
        "operationalised in this study are defined in Table 2.2."
    )},

    # Figure 2.1
    {"type": "para", "text": (
        "The structural relationships among TAM constructs as applied in the present study are "
        "illustrated in Figure 2.1. The model shows how external variables—including system design "
        "quality, training, and institutional support—influence the two core beliefs, which in turn "
        "determine attitude, behavioural intention, and actual system use."
    )},
    {"type": "mermaid_caption", "text": "Figure 2.1: Technology Acceptance Model (TAM) Framework Adapted for This Study"},
    {"type": "mermaid", "code": """graph LR
    EV[External Variables\\n- System Design Quality\\n- Training Support\\n- Institutional Policy]
    PU[Perceived\\nUsefulness]
    PEOU[Perceived Ease\\nof Use]
    ATT[Attitude Toward\\nUsing System]
    BI[Behavioural\\nIntention to Use]
    AU[Actual\\nSystem Use]

    EV --> PU
    EV --> PEOU
    PEOU --> PU
    PEOU --> ATT
    PU --> ATT
    PU --> BI
    ATT --> BI
    BI --> AU"""},

    # Table 2.2
    {"type": "para", "text": (
        "Table 2.2 presents the operationalised definitions of each TAM construct as employed in the "
        "User Acceptance Testing questionnaire developed for this study. The questionnaire items were "
        "adapted from Davis (1989) and Tarhini et al. (2014) and modified to reflect the specific "
        "features of the SRMS."
    )},
    {"type": "table_caption", "text": "Table 2.2: Technology Acceptance Model (TAM) Constructs and Definitions"},
    {"type": "table", "headers": ["Construct", "Definition", "Sample Survey Item", "Scale"],
     "rows": [
         ["Perceived Usefulness (PU)", "Degree to which the SRMS is believed to enhance job performance", "Using this system improves my ability to manage student records effectively", "5-point Likert (Strongly Disagree to Strongly Agree)"],
         ["Perceived Ease of Use (PEOU)", "Degree to which the SRMS is believed to be free from effort", "Learning to use this system was easy for me", "5-point Likert"],
         ["Attitude Toward Use (ATT)", "User's overall affective evaluation of using the system", "Using this system is a good idea for managing student records", "5-point Likert"],
         ["Behavioural Intention (BI)", "User's stated intention to continue using the system", "I intend to continue using this system in the future", "5-point Likert"],
         ["Actual System Use (AU)", "Observable extent to which the system is used", "Frequency of system login per week", "Frequency count"],
     ]},

    {"type": "heading1", "text": "2.2\tCONCEPT OF STUDENT RECORD MANAGEMENT SYSTEMS"},
    {"type": "para", "text": (
        "A Student Record Management System (SRMS) is broadly defined as an information system "
        "designed to facilitate the collection, storage, retrieval, processing, and reporting of "
        "student-related data across the full lifecycle of a student's engagement with an educational "
        "institution—from initial application and admission through to graduation and alumni management "
        "(Laudon & Laudon, 2020). In its most comprehensive form, an SRMS integrates academic "
        "management (courses, grades, transcripts), administrative management (student profiles, "
        "enrolment, scheduling), financial management (fees, payments, balances), and compliance "
        "management (regulatory reporting, accreditation documentation) within a single, unified "
        "platform. The scope and sophistication of SRMS implementations vary enormously across "
        "institutional contexts, from simple spreadsheet-based grade books to enterprise-grade "
        "Student Information Systems (SIS) deployed by large universities globally."
    )},
    {"type": "para", "text": (
        "The evolution of SRMS can be traced through four broad generations, as illustrated in "
        "Figure 2.2. The first generation, spanning the pre-digital era, relied entirely on manual "
        "paper-based systems with no computational support. The second generation emerged with the "
        "adoption of mainframe computers in university administrative offices during the 1970s and "
        "1980s, enabling batch processing of grade data and the generation of printed reports. The "
        "third generation, beginning in the 1990s, saw the proliferation of client-server database "
        "applications that enabled real-time data entry and retrieval through networked terminals. "
        "The fourth and current generation is characterised by web-based, cloud-enabled platforms "
        "accessible through standard browsers, featuring responsive design, mobile accessibility, "
        "API integrations, and increasingly, artificial intelligence-driven analytics (Heeks, 2002; "
        "O'Brien & Marakas, 2011)."
    )},

    # Figure 2.2
    {"type": "para", "text": (
        "The four-generation evolution of SRMS technologies is depicted in Figure 2.2, illustrating "
        "the progressive shift from entirely manual processes to fully web-based, cloud-accessible systems."
    )},
    {"type": "mermaid_caption", "text": "Figure 2.2: Evolution of Student Record Management Systems"},
    {"type": "mermaid", "code": """timeline
    title Evolution of Student Record Management Systems
    Pre-1970s : Manual Paper Systems
               : Physical registers and ledgers
               : No computation support
    1970s-1980s : Mainframe Era
                : Batch processing of grade data
                : Printed reports
    1990s-2000s : Client-Server Era
                : Networked desktop applications
                : Real-time data entry
                : Early relational databases
    2000s-2010s : Web 1.0 Era
                : Browser-based access
                : Centralised web servers
                : PHP and MySQL systems
    2010s-Present : Cloud and Mobile Era
                  : Responsive mobile-first design
                  : Cloud hosting
                  : API integrations
                  : AI-driven analytics"""},

    # Figure 2.3
    {"type": "para", "text": (
        "Modern SRMS platforms are expected to integrate a comprehensive set of functional modules "
        "that collectively cover the complete spectrum of student data management needs. Figure 2.3 "
        "presents a conceptual map of the key features expected of a modern student record management "
        "system, as synthesised from the reviewed literature."
    )},
    {"type": "mermaid_caption", "text": "Figure 2.3: Key Features of a Modern Student Record Management System"},
    {"type": "mermaid", "code": """mindmap
  root((Modern SRMS))
    Student Management
      Personal Profiles
      Guardian Details
      Admission Records
      Academic History
    Academic Management
      Course Registration
      Grade Entry
      GPA/CGPA Computation
      Transcripts
    Attendance Tracking
      Daily Attendance
      Attendance Reports
      Attendance Rate Calculation
    Financial Management
      Fee Structures
      Payment Recording
      Balance Computation
      Receipts and Statements
    User Access Control
      Role-Based Access
      Authentication
      Audit Logging
    Reporting and Analytics
      Dashboard Visualisations
      Class Lists
      Performance Reports
      Regulatory Reports"""},

    {"type": "heading1", "text": "2.3\tREVIEW OF EXISTING SYSTEMS"},
    {"type": "para", "text": (
        "A number of student record management systems have been developed and deployed at varying "
        "scales, from large commercial enterprise solutions to small open-source projects. This section "
        "critically reviews selected systems from both international and Nigerian contexts, identifying "
        "their strengths and limitations in relation to the requirements of the proposed system. The "
        "review is summarised in Table 2.1, which compares the systems across key functional dimensions."
    )},
    {"type": "para", "text": (
        "Banner Student by Ellucian is one of the most widely deployed commercial Student Information "
        "Systems globally, used by over 1,400 higher education institutions in more than 40 countries "
        "(Ellucian, 2023). It offers comprehensive functionality including admissions, enrolment, "
        "academic records, financial aid, and alumni management. However, its complexity demands "
        "extensive institutional IT infrastructure, dedicated database administrators, and substantial "
        "licensing and implementation costs that typically run into tens of millions of Naira—rendering "
        "it inaccessible to most Nigerian institutions (Adetimirin, 2012). PeopleSoft Campus Solutions "
        "by Oracle presents similar capabilities and similar cost barriers, with additional complexity "
        "in customisation for non-Western academic calendar structures."
    )},
    {"type": "para", "text": (
        "Fedena is an open-source school management system built on Ruby on Rails, initially developed "
        "by Foradian Technologies and later released as open-source software. It has gained adoption "
        "in several developing countries, including some Nigerian private schools, due to its zero "
        "licensing cost. However, Fedena's use of Ruby on Rails—a technology stack less familiar to "
        "Nigerian developers compared to PHP—creates a significant barrier to local customisation, "
        "support, and long-term maintenance (Eze & Icha-Ituma, 2018). OpenSIS is another open-source "
        "alternative built on PHP, which offers a more accessible technology foundation. However, "
        "OpenSIS was not specifically designed for the Nigerian academic calendar structure, credit "
        "unit system, or the letter-grade-to-GPA conversion conventions mandated by the NUC, "
        "requiring extensive customisation for Nigerian deployment."
    )},
    {"type": "para", "text": (
        "Within Nigeria, several research-based systems have been developed and reported in academic "
        "literature. Obi and Obasi (2019) developed a web-based student information system for a "
        "Nigerian polytechnic using PHP and MySQL, demonstrating that the technology stack is "
        "well-suited for the local context. However, their system was limited to basic grade recording "
        "and transcript generation and did not include attendance tracking, fee management, or dashboard "
        "analytics. Eze et al. (2013) proposed a framework for an integrated SRMS for Nigerian "
        "universities but did not provide a full implementation. The present system builds on these "
        "prior efforts by providing a fully implemented, tested, and deployable solution that covers "
        "all the identified functional areas within a single unified platform."
    )},
    {"type": "table_caption", "text": "Table 2.1: Comparison of Existing Student Record Management Systems"},
    {"type": "table",
     "headers": ["System", "Developer", "Technology", "Student Mgmt", "Grade/GPA", "Attendance", "Fee Mgmt", "Reports", "Nigerian Context", "Cost"],
     "rows": [
         ["Banner Student", "Ellucian", "Java/Oracle", "Yes", "Yes", "Yes", "Yes", "Yes", "Not adapted", "Very High"],
         ["PeopleSoft Campus", "Oracle", "Java/Oracle DB", "Yes", "Yes", "Limited", "Yes", "Yes", "Not adapted", "Very High"],
         ["Fedena", "Foradian/OSS", "Ruby on Rails", "Yes", "Yes", "Yes", "Limited", "Yes", "Not adapted", "Free (OSS)"],
         ["OpenSIS", "OS4ED", "PHP/MySQL", "Yes", "Yes", "Yes", "Limited", "Limited", "Partial", "Free (OSS)"],
         ["Obi & Obasi (2019)", "Local Research", "PHP/MySQL", "Basic", "Yes", "No", "No", "Limited", "Yes", "Free"],
         ["Eze et al. (2013)", "Local Research", "Framework only", "Proposed", "Proposed", "Proposed", "Proposed", "Proposed", "Yes", "N/A"],
         ["Proposed SRMS", "This Study", "PHP 8.1/MySQL 8/Bootstrap 5", "Full", "Full + GPA/CGPA", "Full", "Full", "Full", "Fully adapted", "Free (OSS)"],
     ]},

    {"type": "heading1", "text": "2.4\tTECHNOLOGIES FOR STUDENT RECORD MANAGEMENT"},
    {"type": "para", "text": (
        "The selection of appropriate technologies is a critical determinant of a web-based system's "
        "performance, maintainability, security, and scalability. Several technology options exist for "
        "building web-based student record management systems, each with distinct advantages and "
        "trade-offs. The principal technology choices considered during the design phase of this study "
        "are evaluated across key criteria in Table 2.3."
    )},
    {"type": "table_caption", "text": "Table 2.3: Web Technologies Comparison for SRMS Development"},
    {"type": "table",
     "headers": ["Criterion", "PHP 8.1", "Python/Django", "Node.js/Express", "Java/Spring"],
     "rows": [
         ["Learning Curve", "Low — widely taught in Nigerian CS programmes", "Medium", "Medium", "High"],
         ["Nigerian Developer Availability", "Very High", "Medium", "Medium", "Low"],
         ["Hosting Cost (Shared Hosting)", "Very Low — native support", "Medium — requires VPS", "Medium — requires VPS", "High — requires dedicated server"],
         ["Performance", "Good — PHP 8 with JIT", "Good", "Excellent", "Excellent"],
         ["Database Integration", "Excellent (PDO/MySQLi)", "Excellent (ORM)", "Good (query builders)", "Excellent (JPA/Hibernate)"],
         ["Security Features", "Good (with best practices)", "Excellent (built-in CSRF)", "Good", "Excellent"],
         ["Community Support", "Very Large", "Large", "Large", "Very Large"],
         ["Open Source", "Yes", "Yes", "Yes", "Yes (Spring)"],
         ["Suitability for This Project", "Excellent", "Good", "Good", "Overkill"],
     ]},
    {"type": "para", "text": (
        "PHP 8.1 was selected as the server-side language for the proposed system on the basis of "
        "its widespread availability on low-cost shared hosting environments prevalent in Nigeria, "
        "its strong community support, the extensive availability of PHP-skilled developers in the "
        "Nigerian technology market, and the significant improvements in performance introduced in "
        "PHP 8 through the Just-In-Time (JIT) compilation engine. MySQL 8.0 was selected as the "
        "database management system due to its native integration with PHP via the PDO extension, "
        "its robust support for ACID-compliant transactions, its JSON data type support for flexible "
        "metadata storage, and its widespread deployment on standard LAMP (Linux, Apache, MySQL, PHP) "
        "web hosting stacks available to Nigerian educational institutions (Welling & Thomson, 2017)."
    )},
    {"type": "para", "text": (
        "Bootstrap 5.3 was selected as the frontend CSS framework due to its comprehensive grid "
        "system, pre-built responsive components, and minimal dependency on third-party JavaScript "
        "libraries—having dropped jQuery as a hard dependency while remaining compatible with it. "
        "jQuery 3.7 was retained for AJAX operations and DOM manipulation due to its simplicity and "
        "the wide familiarity of Nigerian web developers with its syntax. Chart.js was selected for "
        "dashboard visualisations due to its lightweight footprint, responsive canvas-based rendering, "
        "and straightforward API that requires no build tools—an important consideration for "
        "deployments in environments where build chains may not be reliably available (Chart.js "
        "Documentation, 2023)."
    )},

    {"type": "heading1", "text": "2.5\tUSER INTERFACE AND USER EXPERIENCE IN EDUCATIONAL SYSTEMS"},
    {"type": "para", "text": (
        "The user interface (UI) and user experience (UX) design of an educational management system "
        "are critical determinants of user adoption and effective utilisation. Research has consistently "
        "demonstrated that systems perceived as difficult to use, regardless of their functional "
        "completeness, face significant resistance from end users—particularly in contexts where "
        "digital literacy may be variable and formal system training is limited (Nielsen, 1994; "
        "Brooke, 1996). This finding is particularly salient for Nigerian educational institutions, "
        "where administrative staff span a wide spectrum of digital literacy levels, from digitally "
        "native younger staff to longer-serving employees with limited prior exposure to web-based "
        "applications."
    )},
    {"type": "para", "text": (
        "Nielsen's (1994) ten usability heuristics provide a widely adopted framework for evaluating "
        "and designing usable interfaces. The heuristics most directly relevant to the design of the "
        "proposed SRMS include: visibility of system status (the system should always keep users "
        "informed about what is happening through appropriate feedback), match between system and "
        "the real world (the system should speak the user's language using familiar concepts and "
        "conventions), error prevention (the system should be designed to prevent problems from "
        "occurring in the first place), and consistency and standards (users should not need to "
        "wonder whether different words, situations, or actions mean the same thing). These "
        "heuristics informed specific design decisions in the proposed system, including the use of "
        "flash notification messages, confirmation dialogs before destructive operations, and "
        "consistent navigation patterns across all modules."
    )},
    {"type": "table_caption", "text": "Table 2.5: UI/UX Best Practices for Educational Management Systems"},
    {"type": "table",
     "headers": ["Design Principle", "Application in the Proposed SRMS", "Reference"],
     "rows": [
         ["Consistent Navigation", "Fixed sidebar navigation with active state highlighting on current module", "Nielsen (1994)"],
         ["Role-Appropriate Views", "Each role sees only the modules and data relevant to their function", "Sandhu et al. (1996)"],
         ["Responsive Design", "Bootstrap 5 grid ensures usability on mobile and desktop devices", "Marcotte (2011)"],
         ["Immediate Feedback", "Flash messages confirm successful operations; inline validation flags errors", "Nielsen (1994)"],
         ["Minimal Cognitive Load", "Forms grouped into logical sections; complex calculations automated", "Norman (2013)"],
         ["Data Visualisation", "Dashboard charts provide at-a-glance summary of key institutional metrics", "Few (2012)"],
         ["Printable Reports", "Print CSS media queries ensure clean, professional printouts of transcripts", "Marcotte (2011)"],
         ["Dark Mode Support", "Optional dark mode reduces eye strain during extended administrative sessions", "Norman (2013)"],
         ["Confirmation Dialogs", "Modal confirmation before all delete operations prevents accidental data loss", "Nielsen (1994)"],
         ["Search and Filtering", "AJAX-powered search allows instant retrieval of student records", "Few (2012)"],
     ]},

    {"type": "heading1", "text": "2.6\tIDENTIFIED RESEARCH GAPS"},
    {"type": "para", "text": (
        "The critical review of existing literature and systems reveals a number of significant gaps "
        "that the present study is designed to address. These gaps are summarised in Table 2.6 and "
        "elaborated in the following discussion."
    )},
    {"type": "table_caption", "text": "Table 2.6: Summary of Identified Research Gaps"},
    {"type": "table",
     "headers": ["Gap", "Description", "How This Study Addresses It"],
     "rows": [
         ["Lack of fully integrated local SRMS", "No existing Nigerian study provides a fully implemented system covering all SRMS modules", "Present system implements all modules in one platform"],
         ["NUC grading convention alignment", "Existing open-source systems not aligned with NUC GPA/CGPA computation standards", "Grade computation engine built to NUC specifications"],
         ["Fee management integration", "Most local SRMS research excludes fee management", "Full fee structure, payment recording, and balance computation included"],
         ["Attendance-grade-fee integration", "No existing local study integrates attendance, academic records, and fees in one system", "All three domains integrated in a single relational database"],
         ["TAM-based UAT in Nigerian SRMS", "TAM has rarely been applied to evaluate SRMS specifically in Nigerian universities", "TAM-based UAT instrument designed and administered"],
         ["Dashboard analytics for Nigerian institutions", "No local SRMS study provides real-time dashboard analytics for institutional decision-making", "Chart.js-powered dashboard with department and grade analytics"],
         ["Audit trail and security", "Security and audit logging largely ignored in local SRMS research", "Complete audit log and RBAC implemented"],
     ]},

    {"type": "heading1", "text": "2.7\tCHALLENGES AND BARRIERS TO SRMS ADOPTION IN NIGERIA"},
    {"type": "para", "text": (
        "Despite the well-documented benefits of digital student record management systems, adoption "
        "in Nigerian educational institutions has been slow and uneven. Several interconnected "
        "challenges and barriers contribute to this situation, operating at the levels of "
        "infrastructure, finance, human resources, and institutional culture. Understanding these "
        "barriers is essential for designing a system and deployment strategy that are realistic "
        "within the Nigerian operational context."
    )},
    {"type": "para", "text": (
        "The most fundamental barrier is infrastructural. Reliable electricity supply is a prerequisite "
        "for sustained use of any web-based system, yet Nigeria's power supply remains deeply "
        "unreliable, with many institutions experiencing multiple hours of outages daily. While "
        "generator-based backup power provides a partial solution, the cost of diesel fuel represents "
        "an additional operational burden for institutions already operating under budgetary stress "
        "(Heeks, 2002). Internet connectivity, while improving with the expansion of mobile broadband "
        "networks, remains inconsistent in many geographic areas and prohibitively expensive for "
        "institutions to provision at the bandwidth levels required for concurrent multi-user "
        "web application access."
    )},
    {"type": "para", "text": (
        "Financial constraints constitute a second major barrier. The acquisition cost of commercial "
        "SRMS solutions is far beyond the reach of most government-funded Nigerian institutions "
        "operating under the constraints of annual budgets determined by state or federal government "
        "allocations. Even when free open-source solutions are available, implementation costs—including "
        "server hardware or hosting fees, customisation, data migration, and staff training—present "
        "significant financial hurdles (Ajayi & Ekundayo, 2008). The present study addresses this "
        "barrier by providing a fully documented, open-source solution deployable on widely available "
        "and inexpensive shared web hosting platforms."
    )},
    {"type": "para", "text": (
        "Human resource and capacity challenges represent a third category of barriers. Many Nigerian "
        "educational institutions lack dedicated IT staff with the skills needed to implement, "
        "customise, maintain, and troubleshoot web-based administrative systems. Administrative staff "
        "who are primary users of such systems may resist adoption due to fear of technology, concerns "
        "about job displacement, or simply a preference for established manual routines reinforced "
        "by years of practice (Tarhini et al., 2014). Resistance to change at the organisational "
        "level—particularly among senior administrative staff who have significant influence over "
        "institutional decision-making—can effectively veto technology adoption initiatives even when "
        "institutional leadership is supportive. Addressing these human factors requires not only a "
        "well-designed, easy-to-use system but also a carefully planned change management and "
        "training strategy, as discussed in Section 3.8 of this report."
    )},
    {"type": "para", "text": (
        "Policy and regulatory factors also play a role. The absence of a clear national policy "
        "framework mandating the adoption of digital record management systems in Nigerian educational "
        "institutions means that adoption remains discretionary at the institutional level, leading "
        "to a highly fragmented landscape in which some institutions are digitally advanced while "
        "the majority remain at the manual stage. Regulatory bodies such as the NUC and NBTE have "
        "increasingly emphasised e-governance in their accreditation criteria, but enforcement "
        "remains inconsistent (National Universities Commission, 2019). A stronger policy "
        "environment that creates institutional incentives—or requirements—for SRMS adoption would "
        "significantly accelerate the transition from manual to digital record management across "
        "Nigerian educational institutions."
    )},

    {"type": "heading1", "text": "2.8\tSECURITY REQUIREMENTS FOR STUDENT RECORD SYSTEMS"},
    {"type": "para", "text": (
        "The security of student record systems is a matter of both institutional integrity and "
        "legal compliance. Student data—encompassing personal information, academic performance "
        "records, and financial data—constitutes sensitive personally identifiable information (PII) "
        "that demands robust protection against unauthorised access, modification, and disclosure. "
        "In the Nigerian context, the Nigeria Data Protection Regulation (NDPR) issued by the National "
        "Information Technology Development Agency (NITDA) in 2019 establishes legal obligations for "
        "organisations processing personal data of Nigerian citizens, including educational institutions "
        "(NITDA, 2019). Table 2.4 presents the key security requirements applicable to student "
        "record systems."
    )},
    {"type": "table_caption", "text": "Table 2.4: Security Requirements for Student Record Systems"},
    {"type": "table",
     "headers": ["Security Requirement", "Description", "Implementation Mechanism"],
     "rows": [
         ["Authentication", "Verify the identity of all users before granting access", "Session-based login with password_hash() using bcrypt"],
         ["Authorisation (RBAC)", "Restrict access to functions based on user role", "Role check on every protected page request"],
         ["Input Validation", "Prevent injection and XSS attacks via malicious input", "PDO prepared statements; htmlspecialchars() on all output"],
         ["CSRF Protection", "Prevent cross-site request forgery on all state-changing forms", "Synchroniser token pattern; CSRF token in all POST forms"],
         ["Session Security", "Protect session data from hijacking and fixation", "session_regenerate_id() on login; HttpOnly and Secure cookies"],
         ["Password Security", "Protect stored credentials from compromise", "password_hash() with PASSWORD_BCRYPT; minimum complexity enforced"],
         ["Audit Logging", "Maintain immutable record of all data modifications", "Audit log table recording user, action, timestamp, IP"],
         ["Data Encryption in Transit", "Protect data from interception during transmission", "HTTPS/TLS enforced via .htaccess HSTS header"],
         ["Principle of Least Privilege", "Grant users minimum access needed for their role", "Granular RBAC restricts access beyond role boundary"],
     ]},

    {"type": "heading1", "text": "2.9\tSUMMARY"},
    {"type": "para", "text": (
        "This chapter has presented a comprehensive review of the literature relevant to the design "
        "and implementation of web-based Student Record Management Systems. The Technology Acceptance "
        "Model was established as the theoretical framework for evaluating user acceptance of the "
        "proposed system, with its constructs of Perceived Usefulness and Perceived Ease of Use "
        "identified as the primary predictors of adoption intention. The evolution of SRMS from "
        "manual paper systems through mainframe and client-server eras to the current web-based "
        "paradigm was traced, providing historical context for the current study. A critical review "
        "of existing systems—both international and Nigerian—revealed that while capable commercial "
        "solutions exist, they are inaccessible to most Nigerian institutions due to cost, and that "
        "local research-based systems have not achieved the functional completeness required. The "
        "evaluation of technology options confirmed PHP/MySQL as the most appropriate choice for the "
        "Nigerian institutional context. User interface and user experience principles drawn from "
        "Nielsen's heuristics and established design frameworks were identified as guiding principles "
        "for the system's interface design. The chapter identified seven key research gaps addressed "
        "by the present study and examined the multi-layered barriers to SRMS adoption in Nigeria, "
        "including infrastructural, financial, human resource, and policy-level challenges. The "
        "following chapter translates these insights into a detailed system design and implementation plan."
    )},
]
