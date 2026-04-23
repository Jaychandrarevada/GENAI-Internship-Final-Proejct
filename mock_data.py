from fpdf import FPDF

def create_mock_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    content = """Acme Corp Customer Support Policy

1. Returns and Refunds
Customers may return products within 30 days of purchase for a full refund. The item must be in its original packaging and undamaged.
For damaged goods upon arrival, please take a photo and upload it to our claims portal. Refunds for damaged goods are processed within 2-3 business days.

2. Shipping Policies
Standard shipping takes 5-7 business days. Expedited shipping takes 1-2 business days.
Once a package is shipped, the shipping address cannot be changed. If a package is lost, Acme Corp requires 14 days from the estimated delivery date to open an investigation.

3. Account Management
To delete an account, users must navigate to settings and request deletion. Deletion takes 30 days to process.
Passwords can be reset using the "Forgot Password" link on the login page.

4. Warranty
All electronic products come with a 1-year limited warranty covering manufacturing defects. It does not cover water damage or accidental drops.

5. Escalation Rules
If a customer is irate, explicitly angry, threatens legal action, or disputes a charge over $500, the automated system MUST NOT attempt to resolve the issue directly and MUST escalate to a human agent immediately.
"""
    
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line.encode('latin-1', 'replace').decode('latin-1'), ln=True)

    pdf.output("support_policy.pdf")
    print("Created mock PDF: support_policy.pdf")

if __name__ == "__main__":
    create_mock_pdf()
