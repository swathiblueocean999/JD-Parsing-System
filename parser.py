
import pdfplumber
import re
import json
import os

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return [page.extract_text() for page in pdf.pages if page.extract_text()]

def parse_job_details(text):
    # 1. skill list
    skill_keywords = [
        "Tally", "GST", "TDS", "Taxation", "Ledger Accounts", "Invoicing", 
        "Audit", "Accounts Payable", "AP processes", "Accounts Receivable", 
        "AR reporting", "Transfer pricing", "Benchmarking", "Fund accounting", 
        "Valuation", "Excel", "Data accuracy", "Communication", "Coordination","ERP systems", "itc", "Financial reporting", "Reconciliation", "Budgeting", "Forecasting", "dtaa", "erm", "sox", "Payroll software", "labor laws", "hr", "bi tools", "quickbooks", "zohobooks", "cloud based accounting software"
    ]
    # 2. pages divided into profiles based on numbering pattern (e.g., "1. ", "2. ", etc.)
    raw_profiles = re.split(r'(?=\d+\.\s)', text)
    raw_profiles = [p.strip() for p in raw_profiles if len(p.strip()) > 50]
    
    parsed_in_page = []

    for profile in raw_profiles:
        # skills
        found_skills = []
        for skill in skill_keywords:
            if re.search(rf"\b{re.escape(skill)}\b", profile, re.IGNORECASE):
                found_skills.append(skill.title() if len(skill) > 3 else skill.upper())

        # 3. experience
        exp_pattern = r'(\d+[\s-]*to[\s-]*\d+|\d+\+?)\s*(?:years|yrs|year)'
        exp_match = re.search(exp_pattern, profile, re.IGNORECASE)
        experience = exp_match.group(0) if exp_match else "Not Mentioned"

        # 4. role list
        role_list = ["Finance Assistant", "Accounts Payable Assistant", "Accounts Receivable Assistant", "GST Consultant"]
        found_role = "General Accountant" 
        for role in role_list:
            if role.lower() in profile.lower():
                found_role = role
                break
        #4a. Responsibilities extraction
        # We capture everything between "Key Responsibilities:" and "Required Skills & Qualifications:"
        # using a non-greedy, multiline, case-insensitive regex pattern.
        
        responsibilities_pattern = r'(?i)Key Responsibilities:[\s:]*([\s\S]*?)(?=(?i:Required Skills & Qualifications:|$))'
        resp_match = re.search(responsibilities_pattern, profile)
        
        found_responsibilities = []
        
        if resp_match:
            # Capture the entire raw text block of responsibilities
            raw_resp_text = resp_match.group(1).strip()
            
            # Use regex to find and extract the individual bullet points.
            # We look for a newline, a delimiter (- or •), optional space, followed by non-newline characters.
            # Your PDF uses '•', so we explicitly include it.
            bullet_pattern = r'(?:^|[\r\n])[ \t]*[-•][ \t]*(.+?)(?=[\r\n]|$)'
            
            # Find all matches, which will be the individual responsibility lines.
            bullet_matches = re.findall(bullet_pattern, raw_resp_text)
            
            # Double check to remove any leading/trailing spaces from each line.
            found_responsibilities = [item.strip() for item in bullet_matches if item.strip()]
        
        # 5. Education list regex pattern 
        education = "Not Mentioned"
        edu_pattern = r'B\.Com|M\.Com|MBA|CA|ICWA|Bachelor|Degree'
        if re.search(edu_pattern, profile, re.IGNORECASE):
            education = "Degree/Professional Qualification"

        parsed_in_page.append({
            "Role_Name": found_role,
            "Education": education,
            "Experience_Required": experience,
            "Required_Skills": list(set(found_skills)),
            "Key_Responsibilities": found_responsibilities
        })
    
    return parsed_in_page


file_path = r"C:\Users\LENOVO\OneDrive\Desktop\JD_Parser_Project\profiles\Accountant Model.pdf"
output_data = []

if os.path.exists(file_path):
    pages_content = extract_text_from_pdf(file_path)
    for i, page_text in enumerate(pages_content):
        results = parse_job_details(page_text)
        for res in results:
            res["Source_File"] = f"Accountant Model.pdf (Page {i+1})"
            output_data.append(res)

    with open("final_parsed_profiles.json", "w", encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

    print(f"Success! Total profiles found: {len(output_data)}")