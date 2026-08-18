\# Research Review



\## 1. Background



With the rapid development of large language models (LLMs) for HTML generation, 

a large amount of generated web code needs automatic quality verification.



Traditional human evaluation is expensive and difficult to scale.



Therefore, an automatic HTML verifier is required to evaluate generated web pages 

from multiple perspectives.



The target of this project is building an HTML quality verifier that takes HTML 

as input and outputs quality scores.





\## 2. Related Work



\## Code Aesthetics with Agentic Reward Feedback



The main reference of this project is:



Code Aesthetics with Agentic Reward Feedback





The project introduces:



\- AesCode-358K training dataset

\- AesCoder-4B model

\- OpenDesign evaluation benchmark





The research focuses on improving code generation models through aesthetic 

reward feedback.





\## 3. Evaluation Dimensions



Following the OpenDesign evaluation idea, HTML quality can be divided into 

three dimensions:





\### 3.1 Usability



Question:



Can the generated HTML page run correctly?





Evaluation includes:



\- HTML loading success

\- CSS rendering

\- JavaScript execution

\- Runtime errors





\### 3.2 Functionality



Question:



Does the generated page satisfy the user's requirements?





Evaluation includes:



\- Task completion

\- Interaction logic

\- Required components

\- User intention matching





\### 3.3 Aesthetics



Question:



Does the webpage have good visual quality?





Evaluation includes:



\- Layout

\- Color harmony

\- Typography

\- Visual hierarchy

\- Modern design style





\## 4. Current Implementation



This project implements a lightweight verifier:





HTML



↓



Browser Rendering



↓



LLM Evaluation



↓



Quality Score







Compared with a trained reward model, this implementation uses 

LLM-as-a-Judge technology.





\## 5. Future Improvement



Future directions:



1\. Build human annotated evaluation dataset



2\. Calculate human-AI agreement



3\. Train reward model



4\. Add interactive agent evaluation



