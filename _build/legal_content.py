# -*- coding: utf-8 -*-
"""
Text for the three legal pages.

DRAFTS. Written to describe what this site actually does - verified against the
code, not assumed: no analytics, no tracking pixels, no cookies set by us, no
browser storage, no accounts and no online ordering. The only personal data the
site handles is what someone types into the Connect form, which Web3Forms
delivers to bd@amps.bio.

They still need a lawyer's eye before anyone relies on them, and each page says
so on its face. Company particulars (registered name, CIN/GST, grievance
officer) are marked TO CONFIRM rather than invented.
"""

COMPANY = "Amplified Biopharma Solutions"
EMAIL = "bd@amps.bio"
PHONE = "+91 96606 45155"
# Pune (Dhanori) was removed on 17 Sep 2026 at the customer's request and may
# come back; add the string here and re-run build_legal.py to restore it.
ADDRESSES = ["Yeshwantpur, Bangalore - 560022, Karnataka, India"]


# Each page: (slug, title, meta description, lead paragraph, [(heading, [blocks])])
# A block is a string (paragraph) or a list of strings (bulleted list).

PRIVACY = (
    "privacy-policy.html",
    "Privacy Policy",
    "How Ampbio - Amplified Biopharma Solutions - handles the information you "
    "share through amps.bio, and how to contact us about it.",
    "This policy explains what happens to information you give us through "
    "amps.bio. In short: we collect only what you type into the enquiry form, "
    "we use it to answer you, and we do not track you around the web.",
    [
        ("Who we are", [
            "%s operates amps.bio. We supply specialised reagents, materials and "
            "scientific support to research organisations, and we are the "
            "exclusive distributor in India for Virongy Biosciences, USA." % COMPANY,
        ]),
        ("What we collect", [
            "Only what you choose to send us through the Connect form:",
            ["Your name", "Your organisation", "Your email address",
             "Your phone number", "The subject and text of your message"],
            "We do not ask for, and the site cannot take, payment details, "
            "identity documents or any special category of personal data. There "
            "are no user accounts and nothing to log in to.",
        ]),
        ("What we do not do", [
            "We think it is worth being specific, because many sites say the "
            "opposite:",
            ["We set no cookies of our own.",
             "We run no analytics - there is no Google Analytics, no advertising "
             "pixel and no visitor tracking on this site.",
             "We store nothing in your browser.",
             "We do not sell, rent or trade your information to anyone.",
             "We do not use your details for marketing unless you ask us to."],
        ]),
        ("Why we use it", [
            "To read your enquiry, reply to it, prepare a quotation if you have "
            "asked for one, and keep a record of our correspondence with you. "
            "That is the whole purpose.",
        ]),
        ("Who else is involved", [
            "Running a website means other companies necessarily see some data. "
            "For amps.bio those are:",
            ["<strong>Web3Forms</strong> - carries your enquiry from the form to "
             "our inbox. Your message passes through their service in transit.",
             "<strong>GitHub Pages</strong> - hosts the site. Like any web host, "
             "its servers record requests, which includes visitor IP addresses.",
             "<strong>Google Fonts</strong> and <strong>cdnfonts</strong> - serve "
             "the typefaces the site uses. Your browser requests those files "
             "directly, so those services can see your IP address.",
             "<strong>Zoho Mail</strong> - hosts our email, so your message rests "
             "in our mailbox there."],
            "We do not pass your enquiry to anyone else without a reason to. If "
            "answering you needs a quotation, lead time or technical detail from "
            "Virongy Biosciences, we may share what is necessary for that - "
            "usually the product and quantity, and your organisation. Tell us if "
            "you would rather we did not.",
        ]),
        ("How long we keep it", [
            "Enquiries stay in our business correspondence for as long as the "
            "commercial relationship or a legal or tax obligation requires, and "
            "are then deleted. Exact retention period: <strong>to confirm</strong>.",
        ]),
        ("Your rights", [
            "You can ask us to show you what we hold about you, correct it, "
            "delete it, or stop using it. Write to %s and we will respond." % EMAIL,
            "If you are in India, the Digital Personal Data Protection Act, 2023 "
            "gives you these rights. If you are in the EU or UK, the GDPR does. "
            "Either way, ask and we will act on it.",
            "Grievance officer for the purposes of the DPDP Act: "
            "<strong>to confirm</strong>.",
        ]),
        ("Children", [
            "This is a business-to-business site for research organisations. It "
            "is not intended for anyone under 18 and we do not knowingly collect "
            "information from children.",
        ]),
        ("Changes", [
            "If we change this policy we will change the date below. Material "
            "changes will be obvious on this page rather than buried.",
        ]),
        ("Contact us", [
            "Email %s or call %s." % (EMAIL, PHONE),
            "<br>".join(ADDRESSES),
        ]),
    ])

TERMS = (
    "terms-of-use.html",
    "Terms of Use",
    "The terms on which Ampbio - Amplified Biopharma Solutions - makes amps.bio "
    "available, including research-use-only conditions.",
    "These terms govern your use of amps.bio. They cover the website itself. "
    "Any actual supply of products is governed by the separate terms in our "
    "quotation and order confirmation.",
    [
        ("Using this site", [
            "By using amps.bio you accept these terms. If you do not accept them, "
            "please do not use the site.",
        ]),
        ("The site is information, not an offer", [
            "Everything here - product descriptions, specifications, options and "
            "availability - is for information. It is an invitation to enquire, "
            "not a binding offer to sell.",
            "There is no online ordering and no checkout. Nothing you do on this "
            "site forms a contract. A sale happens only when we issue a quotation "
            "and you place an order that we confirm in writing.",
        ]),
        ("Research use only", [
            "This matters more than anything else on this page.",
            "The products described on this site are supplied <strong>for "
            "research use only</strong>. They are not for use in diagnostic "
            "procedures, not for therapeutic use, and not for administration to "
            "humans or animals.",
            "Some of them are viral vectors, pseudoviruses and related biological "
            "materials. You are responsible for holding the approvals your "
            "institution and the law require, for the biosafety level at which "
            "they are handled, and for the competence of the people handling them.",
        ]),
        ("Quotations, orders and supply", [
            "Prices are not published on this site. Lead times, availability and "
            "pricing are confirmed in a quotation and are valid only for the "
            "period that quotation states.",
            "Supply is subject to our terms of sale, to the terms of the "
            "manufacturer, and to your organisation holding the permits, import "
            "licences and institutional approvals required.",
        ]),
        ("Intellectual property", [
            "The design, text and arrangement of this site belong to %s or to our "
            "licensors." % COMPANY,
            "Virongy Biosciences product names, descriptions, imagery, "
            "documentation and marks remain the property of Virongy Biosciences "
            "and are reproduced here in our capacity as their distributor. Nothing "
            "on this site transfers any right in them to you.",
            "You may read, print and share these pages for your own evaluation. "
            "You may not republish the content commercially without our written "
            "permission.",
        ]),
        ("Accuracy", [
            "We take care to describe products correctly, but much of the product "
            "information originates from the manufacturer and specifications "
            "change. Nothing here is guaranteed to be current or complete.",
            "Confirm the details that matter to your work with us in writing "
            "before you order.",
        ]),
        ("Links to other sites", [
            "Where we link to another site - a manufacturer, a publication, a "
            "reference - we do not control it and are not responsible for it.",
        ]),
        ("Acceptable use", [
            "Do not use this site unlawfully, do not attempt to interfere with "
            "it or gain access you have not been given, and do not use automated "
            "means to harvest its content.",
        ]),
        ("Liability", [
            "The site is provided as it is. To the extent the law allows, we are "
            "not liable for loss arising from use of the site or from reliance on "
            "information published on it. Nothing here limits liability that "
            "cannot lawfully be limited - including for death or personal injury "
            "caused by negligence, or for fraud.",
        ]),
        ("Governing law", [
            "These terms are governed by the laws of India. Courts at "
            "<strong>to confirm</strong> have exclusive jurisdiction.",
        ]),
        ("Changes", [
            "We may update these terms. The version on this page at the time you "
            "use the site is the one that applies.",
        ]),
        ("Contact us", [
            "Email %s or call %s." % (EMAIL, PHONE),
            "<br>".join(ADDRESSES),
        ]),
    ])

DISCLAIMER = (
    "disclaimer.html",
    "Disclaimer",
    "Research-use-only conditions and the limits of the product information "
    "published on amps.bio by Ampbio - Amplified Biopharma Solutions.",
    "Read this alongside our Terms of Use. It sets out the limits of what the "
    "information on this site can be relied on for.",
    [
        ("Research use only", [
            "All products described on this site are <strong>for research use "
            "only</strong>. They are not for diagnostic or therapeutic use, and "
            "not for administration to humans or animals.",
            "Do not use them in clinical decision-making. Do not use them in or "
            "on people.",
        ]),
        ("Not medical or scientific advice", [
            "Nothing on this site is medical advice, clinical guidance or a "
            "recommendation for a particular experiment. Product descriptions, "
            "applications and background notes are general information.",
            "The suitability of any product for your work is yours to determine, "
            "with your own validation.",
        ]),
        ("Third-party product information", [
            "A substantial part of the product content on this site - including "
            "the Virongy Biosciences catalogue - comes from the manufacturer. We "
            "reproduce it in good faith as their distributor.",
            "Specifications, formats, variants and documentation change without "
            "notice, and manufacturer documentation may contain errors we have "
            "not caught. Confirm anything critical with us in writing.",
        ]),
        ("Safety and compliance are yours", [
            "You are responsible for:",
            ["Obtaining institutional biosafety, ethics and other approvals "
             "before ordering or using these materials",
             "Handling them at the appropriate containment level, by trained "
             "people, under your own risk assessment",
             "Import licences, permits and customs compliance",
             "Disposal in line with applicable regulation"],
            "Where a safety data sheet is available, read it before you handle "
            "the material. Where one is not published here, ask us for it.",
        ]),
        ("Availability and pricing", [
            "Listing a product here does not mean it is in stock or can be "
            "supplied to your location. Many items are made to order. Lead times "
            "and prices are confirmed only in a written quotation.",
        ]),
        ("No warranty", [
            "The information on this site is provided as it is, without warranty "
            "of any kind, express or implied, including as to accuracy, "
            "completeness or fitness for a particular purpose.",
        ]),
        ("Limitation of liability", [
            "To the extent the law allows, %s is not liable for any loss or "
            "damage arising from use of this site or reliance on its content. "
            "Nothing here limits liability that cannot lawfully be limited." % COMPANY,
        ]),
        ("Contact us", [
            "If anything on this site looks wrong, tell us and we will correct "
            "it. Email %s or call %s." % (EMAIL, PHONE),
        ]),
    ])

PAGES = [PRIVACY, TERMS, DISCLAIMER]
