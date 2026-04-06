# MedLinka - Software Architecture Documentation

---

## 1. Scope
MedLinka addresses the difficulty many people face in accessing affordable healthcare or visiting hospitals due to physical and financial limitations. Our software provides a simplified platform that bridges the gap between patients and medical resources by centralizing consultations and pharmacy services. The system enables users to check symptoms via AI, book doctor appointments, order medications, and set dosage reminders. To maintain a lightweight design within a limited academic timeframe, the project does not include real-time hardware sensor integration or external health device synchronization.

## 2. References
* Course lecture slides from SWE332 Software Architecture.
* The 4+1 Architectural View Model by Philippe Kruchten.
* GitHub Markdown Guide.
* Project Part 2 Requirements and Submission Guidelines.

## 3. Software Architecture
The MedLinka system follows the 4+1 Architectural View Model. The system is designed as a modular web application that separates the user interface, backend logic, and external service integrations into distinct architectural views.

The architecture focuses on a Modular Strategy, allowing the AI, Pharmacy, and Consultation components to be developed and maintained independently. This approach ensures that the system is scalable for future improvements while remaining lightweight enough for a student-led project.

## 4. Architectural Goals & Constraints
### **Goals**
* **User-Friendly Interface:** Ensure the system is simple enough for users of all ages.
* **Security:** Protect sensitive health-related information and user privacy.
* **High Performance:** Maintain a responsive system for real-time consultations and reminders.
* **Trustworthiness:** Provide reliable AI-driven guidance and verified doctor connections.

### **Constraints**
* **Time Limitation:** Must be completed within one academic semester.
* **Budget:** Reliance on free or open-source technologies and APIs.
* **Language:** Python is the mandatory language for backend development.
* **Team Size:** Developed by five students, necessitating clear task distribution.

## 5. Logical Architecture
The MedLinka system is organized into functional components, each serving a specific healthcare role:

1.  **User Management Module:** Handles secure registration, login, and profile management for patients, doctors, and pharmacies.
2.  **Healthcare Service Modules:**
    * **AI Chat:** Analyzes symptoms and provides basic health advice via external APIs.
    * **Doctor Consultation:** Manages the scheduling and execution of video or chat meetings.
    * **Medicine Ordering:** Connects users to pharmacies for browsing and placing orders.
3.  **Data Layer:** A relational database that stores user profiles, medical prescriptions, doctor schedules, and order histories.

## 6. Process Architecture
The system follows a sequential and clear process flow for user actions:

1.  **User Request:** The user logs in and either describes symptoms to the AI or searches for a specific medication.
2.  **Data Retrieval:** The system retrieves doctor availability or medicine data from the relational database.
3.  **Transaction Processing:** The system processes the consultation booking or the medicine order and stores the transaction.
4.  **Response & Scheduling:** The system displays a confirmation to the user and automatically schedules reminders for medication intake.

## 7. Development Architecture
The system is built with a modular package structure to ensure clean code organization:

* **Frontend:** Built with a responsive design for mobile and desktop access. Includes Login/Register, Dashboard, AI Chat UI, Pharmacy Store, and Reminders page.
* **Backend:** Developed using Python frameworks (Flask/Django) to handle user authentication, AI API integration, and order processing logic.
* **External Interfaces:** Includes the AI API for symptom analysis, a Notification Service for medicine reminders, and a Video API for real-time consultations.

## 8. Physical Architecture
The physical architecture describes the hardware and hosting environment:

* **Client Side:** Users access MedLinka via web browsers on smartphones, tablets, or laptops.
* **Server Side:** A Python-based application server handles all logic and API communications.
* **Data Side:** A dedicated database server manages structured medical and user records.
* **Cloud Infrastructure:** The system is hosted on cloud platforms (such as Heroku or AWS) to ensure 24/7 accessibility.

## 9. Scenarios
* **Symptom to Consultation:** A user enters symptoms into the AI Chat, receives a suggestion, and is immediately directed to book a meeting with a relevant doctor.
* **Pharmacy to Reminder:** A user completes a medicine order, and the system instantly generates a daily notification schedule based on the prescription details.

## 10. Size and Performance
* **Optimized Loading:** By using Python's efficient frameworks and modular CSS, the application is designed to load key healthcare features in under 2 seconds.
* **Efficiency:** AI and symptom processing are handled via API calls to ensure the local server remains lightweight.
* **Scalability:** The use of a relational database and cloud hosting allows the system to scale as the number of patient records increases.

## 11. Quality
* **Security & Privacy:** The system implements basic encryption and authentication to protect sensitive health data.
* **Reliability:** Validations are placed on medicine orders and doctor bookings to prevent empty or incorrect data entries.
* **Code Organization:** The project separates the UI (HTML/CSS) from the logic (Python), making it easy to fix bugs or update medical modules.
* **Accessibility:** High-contrast designs and simple navigation ensure the platform is "PG friendly" and accessible to elderly users.

---

## **Appendices**

### **Acronyms and Abbreviations**
* **API:** Application Programming Interface.
* **AI:** Artificial Intelligence.
* **RTL:** Right-to-Left (for Arabic language support).

### **Definitions (Glossary)**
* **Backend:** The server-side part of the application that processes data.
* **Telemedicine:** Providing medical services remotely through technology.
* **Database:** A structured storage system for application data.
