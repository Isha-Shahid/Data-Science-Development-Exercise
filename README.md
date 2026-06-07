PneumoCare: AI-Powered Pneumonia Triage System

Overview
PneumoCare is a high-fidelity prototype designed to support altruistic medical triage in low-resource regions. By utilizing portable chest X-ray technology and an 
automated machine learning triage system, it allows health workers to identify pneumonia risk indicators in adverse conditions without the need for expensive, heavy 
equipment or numerous on-site expert consultants.

Key Objectives
* Automate Diagnosis: Implement a machine learning-based system to triage patients for pneumonia using X-ray images captured in the field.
* Support Field Work: Empower non-expert health workers to manage patient records, symptoms, and X-ray data via a streamlined web application.
* Remote Collaboration: Facilitate real-time diagnostic review by expert clinicians working remotely, allowing them to provide actionable treatment recommendations
  (e.g., antiviral drugs, antibiotics, or rest).

Technical Stack
* Framework: Flask-based web application.
* AI/ML: CNN (Convolutional Neural Network) for pneumonia classification.
* Architecture: Three-tier triage workflow (Field Capture $\rightarrow$ Automated ML Processing $\rightarrow$ Expert Remote Validation).

Workflow
1. On-Site Capture: Health workers create patient records and upload JPEG X-ray files captured from portable machines.
2. Automated Triage: The web app reports immediate pneumonia suspicions, recording findings to the patient's digital file.
3. Expert Validation: Remote clinicians receive real-time updates of suspected cases to double-check the automated diagnosis and prescribe treatment.
