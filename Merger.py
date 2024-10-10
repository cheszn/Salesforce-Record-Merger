import streamlit as st
from simple_salesforce import Salesforce
import pandas as pd
from PIL import Image

# Salesforce connection function
def get_salesforce_connection():
    sf = Salesforce(username='email@domain.com', password='password', security_token='qwertyuiop')
    return sf

# Flatten nested dictionaries in the Salesforce result
def flatten_salesforce_record(record, record_type):
    # Handle Owner fields
    if 'Owner' in record and record['Owner']:
        record['Owner.Id'] = record['Owner'].get('Id')
        record['Owner.Name'] = record['Owner'].get('Name')
    else:
        record['Owner.Id'] = None
        record['Owner.Name'] = None

    # Handle Account fields for Contacts
    if record_type == "Contact" and 'Account' in record and record['Account']:
        record['Account.Id'] = record['Account'].get('Id')
        record['Account.Name'] = record['Account'].get('Name')
    else:
        record['Account.Id'] = None
        record['Account.Name'] = None

    # Handle RecordType.Name for Accounts
    if record_type == "Account" and 'RecordType' in record:
        record['RecordType.Name'] = record['RecordType'].get('Name')
    else:
        record['RecordType.Name'] = None

    # Remove nested fields
    record.pop('Owner', None)
    record.pop('Account', None)
    record.pop('RecordType', None)
    record.pop('attributes', None)

    return record

# Fetch records from Salesforce based on provided IDs and record type
def fetch_salesforce_records(sf, record_ids, record_type):
    records = []
    for record_id in record_ids:
        try:
            if record_type == "Account":
                query = f"""
                SELECT Id, Name, Owner.Id, Owner.Name, Phone, Website, BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry, Type, RecordType.Name
                FROM Account WHERE Id = '{record_id}'"""
            elif record_type == "Lead":
                query = f"""
                SELECT Id, FirstName, LastName, Company, Owner.Id, Owner.Name, Email, Phone, Status, LeadSource
                FROM Lead WHERE Id = '{record_id}'"""
            elif record_type == "Contact":
                query = f"""
                SELECT Id, FirstName, LastName, Account.Id, Account.Name, Email, Phone, Owner.Id, Owner.Name, Title, Department, MailingStreet, MailingCity, MailingState, MailingPostalCode, MailingCountry
                FROM Contact WHERE Id = '{record_id}'"""
            else:
                st.error("Unsupported record type")
                return []
            result = sf.query(query)
            if result['records']:
                record = result['records'][0]
                # Flatten the record
                record = flatten_salesforce_record(record, record_type=record_type)
                records.append(record)
        except Exception as e:
            st.error(f"Error fetching {record_type} {record_id}: {str(e)}")
    return records

# Fetch related records for a specific record ID and flatten Owner fields
def fetch_related_records(sf, record_id, record_type):
    related_records = {}
    try:
        if record_type == "Account":
            # Fetch related contacts
            contact_query = f"SELECT Id, FirstName, LastName, Email, Owner.Id, Owner.Name FROM Contact WHERE AccountId = '{record_id}'"
            contacts = sf.query(contact_query)['records']
            contacts = [flatten_salesforce_record(contact, record_type="Contact") for contact in contacts]
            related_records['Contacts'] = contacts

            # Fetch related opportunities
            opportunity_query = f"SELECT Id, Name, StageName, CloseDate, Owner.Id, Owner.Name FROM Opportunity WHERE AccountId = '{record_id}'"
            opportunities = sf.query(opportunity_query)['records']
            opportunities = [flatten_salesforce_record(opportunity, record_type="Opportunity") for opportunity in opportunities]
            related_records['Opportunities'] = opportunities

            # Fetch related cases
            case_query = f"SELECT Id, CaseNumber, Subject, Status, Owner.Id, Owner.Name FROM Case WHERE AccountId = '{record_id}'"
            cases = sf.query(case_query)['records']
            cases = [flatten_salesforce_record(case, record_type="Case") for case in cases]
            related_records['Cases'] = cases

            # Fetch related tasks
            task_query = f"SELECT Id, Subject, Status, Owner.Id, Owner.Name, WhoId, WhatId FROM Task WHERE WhatId = '{record_id}'"
            tasks = sf.query(task_query)['records']
            tasks = [flatten_salesforce_record(task, record_type="Task") for task in tasks]
            related_records['Tasks'] = tasks

            # Fetch related events
            event_query = f"SELECT Id, Subject, StartDateTime, EndDateTime, Owner.Id, Owner.Name, WhoId, WhatId FROM Event WHERE WhatId = '{record_id}'"
            events = sf.query(event_query)['records']
            events = [flatten_salesforce_record(event, record_type="Event") for event in events]
            related_records['Events'] = events

            # Fetch related notes
            note_query = f"SELECT Id, Title, Owner.Id, Owner.Name FROM Note WHERE ParentId = '{record_id}'"
            notes = sf.query(note_query)['records']
            notes = [flatten_salesforce_record(note, record_type="Note") for note in notes]
            related_records['Notes'] = notes

            # Fetch related attachments
            attachment_query = f"SELECT Id, Name, Owner.Id, Owner.Name FROM Attachment WHERE ParentId = '{record_id}'"
            attachments = sf.query(attachment_query)['records']
            attachments = [flatten_salesforce_record(attachment, record_type="Attachment") for attachment in attachments]
            related_records['Attachments'] = attachments

            # Fetch related files
            file_query = f"SELECT ContentDocumentId, ContentDocument.Title, Id FROM ContentDocumentLink WHERE LinkedEntityId = '{record_id}'"
            files = sf.query(file_query)['records']
            files = [flatten_salesforce_record(file, record_type="File") for file in files]
            related_records['Files'] = files

            # Add any custom object relationships here if applicable

        elif record_type == "Lead":
            # Fetch related tasks
            task_query = f"SELECT Id, Subject, Status, Owner.Id, Owner.Name, WhoId, WhatId FROM Task WHERE WhoId = '{record_id}'"
            tasks = sf.query(task_query)['records']
            tasks = [flatten_salesforce_record(task, record_type="Task") for task in tasks]
            related_records['Tasks'] = tasks

            # Fetch related events
            event_query = f"SELECT Id, Subject, StartDateTime, EndDateTime, Owner.Id, Owner.Name, WhoId, WhatId FROM Event WHERE WhoId = '{record_id}'"
            events = sf.query(event_query)['records']
            events = [flatten_salesforce_record(event, record_type="Event") for event in events]
            related_records['Events'] = events

            # Fetch related notes
            note_query = f"SELECT Id, Title, Owner.Id, Owner.Name FROM Note WHERE ParentId = '{record_id}'"
            notes = sf.query(note_query)['records']
            notes = [flatten_salesforce_record(note, record_type="Note") for note in notes]
            related_records['Notes'] = notes

            # Fetch related attachments
            attachment_query = f"SELECT Id, Name, Owner.Id, Owner.Name FROM Attachment WHERE ParentId = '{record_id}'"
            attachments = sf.query(attachment_query)['records']
            attachments = [flatten_salesforce_record(attachment, record_type="Attachment") for attachment in attachments]
            related_records['Attachments'] = attachments

            # Fetch campaign history
            campaign_member_query = f"SELECT Id, CampaignId, Campaign.Name, Status FROM CampaignMember WHERE LeadId = '{record_id}'"
            campaign_members = sf.query(campaign_member_query)['records']
            campaign_members = [flatten_salesforce_record(cm, record_type="CampaignMember") for cm in campaign_members]
            related_records['CampaignMembers'] = campaign_members

            # Fetch related files
            file_query = f"SELECT ContentDocumentId, ContentDocument.Title, Id FROM ContentDocumentLink WHERE LinkedEntityId = '{record_id}'"
            files = sf.query(file_query)['records']
            files = [flatten_salesforce_record(file, record_type="File") for file in files]
            related_records['Files'] = files

            # Add any custom object relationships here if applicable

        elif record_type == "Contact":
            # Fetch related tasks
            task_query = f"SELECT Id, Subject, Status, Owner.Id, Owner.Name, WhoId, WhatId FROM Task WHERE WhoId = '{record_id}'"
            tasks = sf.query(task_query)['records']
            tasks = [flatten_salesforce_record(task, record_type="Task") for task in tasks]
            related_records['Tasks'] = tasks

            # Fetch related events
            event_query = f"SELECT Id, Subject, StartDateTime, EndDateTime, Owner.Id, Owner.Name, WhoId, WhatId FROM Event WHERE WhoId = '{record_id}'"
            events = sf.query(event_query)['records']
            events = [flatten_salesforce_record(event, record_type="Event") for event in events]
            related_records['Events'] = events

            # Fetch related notes
            note_query = f"SELECT Id, Title, Owner.Id, Owner.Name FROM Note WHERE ParentId = '{record_id}'"
            notes = sf.query(note_query)['records']
            notes = [flatten_salesforce_record(note, record_type="Note") for note in notes]
            related_records['Notes'] = notes

            # Fetch related attachments
            attachment_query = f"SELECT Id, Name, Owner.Id, Owner.Name FROM Attachment WHERE ParentId = '{record_id}'"
            attachments = sf.query(attachment_query)['records']
            attachments = [flatten_salesforce_record(attachment, record_type="Attachment") for attachment in attachments]
            related_records['Attachments'] = attachments

            # Fetch campaign history
            campaign_member_query = f"SELECT Id, CampaignId, Campaign.Name, Status FROM CampaignMember WHERE ContactId = '{record_id}'"
            campaign_members = sf.query(campaign_member_query)['records']
            campaign_members = [flatten_salesforce_record(cm, record_type="CampaignMember") for cm in campaign_members]
            related_records['CampaignMembers'] = campaign_members

            # Fetch related cases
            case_query = f"SELECT Id, CaseNumber, Subject, Status, Owner.Id, Owner.Name FROM Case WHERE ContactId = '{record_id}'"
            cases = sf.query(case_query)['records']
            cases = [flatten_salesforce_record(case, record_type="Case") for case in cases]
            related_records['Cases'] = cases

            # Fetch related files
            file_query = f"SELECT ContentDocumentId, ContentDocument.Title, Id FROM ContentDocumentLink WHERE LinkedEntityId = '{record_id}'"
            files = sf.query(file_query)['records']
            files = [flatten_salesforce_record(file, record_type="File") for file in files]
            related_records['Files'] = files

            # Add any custom object relationships here if applicable

        else:
            st.error("Unsupported record type")
            return {}
    except Exception as e:
        st.error(f"Error fetching related records for {record_type} {record_id}: {str(e)}")
    return related_records

# Function to reassign related records from duplicates to the master record
def reassign_related_records(sf, master_id, related_records, record_type):
    try:
        for related_type, records in related_records.items():
            for record in records:
                # Update the parent reference to point to the master record
                if related_type in ['Tasks', 'Events']:
                    fields_to_update = {}
                    if record.get('WhoId') == record['Id']:
                        fields_to_update['WhoId'] = master_id
                    if record.get('WhatId') == record['Id']:
                        fields_to_update['WhatId'] = master_id
                    if fields_to_update:
                        sf.Task.update(record['Id'], fields_to_update)
                elif related_type in ['Notes', 'Attachments']:
                    sf.Note.update(record['Id'], {'ParentId': master_id})
                elif related_type == 'Contacts' and record_type == 'Account':
                    sf.Contact.update(record['Id'], {'AccountId': master_id})
                elif related_type == 'Opportunities' and record_type == 'Account':
                    sf.Opportunity.update(record['Id'], {'AccountId': master_id})
                elif related_type == 'Cases':
                    if record_type == 'Account':
                        sf.Case.update(record['Id'], {'AccountId': master_id})
                    elif record_type == 'Contact':
                        sf.Case.update(record['Id'], {'ContactId': master_id})
                elif related_type == 'CampaignMembers':
                    if record_type == 'Lead':
                        sf.CampaignMember.update(record['Id'], {'LeadId': master_id})
                    elif record_type == 'Contact':
                        sf.CampaignMember.update(record['Id'], {'ContactId': master_id})
                elif related_type == 'Files':
                    # Update LinkedEntityId in ContentDocumentLink
                    sf.ContentDocumentLink.update(record['Id'], {'LinkedEntityId': master_id})
                else:
                    # Handle other related types if necessary
                    pass
        return True
    except Exception as e:
        st.error(f"Error reassigning related records: {str(e)}")
        return False

# Function to merge Salesforce records
def merge_salesforce_records(sf, master_id, duplicate_ids, record_type):
    try:
        # Fetch master record fields for merging
        if record_type == "Account":
            master_record_query = f"SELECT Id, Name, Owner.Id, Owner.Name, Phone, Website, BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry FROM Account WHERE Id = '{master_id}'"
            master_record = sf.query(master_record_query)['records'][0]
            master_record = flatten_salesforce_record(master_record, record_type=record_type)

            fields_to_update = {}

            # Loop over duplicate records
            for dupe_id in duplicate_ids:
                dupe_record_query = f"SELECT Id, Name, Owner.Id, Owner.Name, Phone, Website, BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry FROM Account WHERE Id = '{dupe_id}'"
                dupe_record = sf.query(dupe_record_query)['records'][0]
                dupe_record = flatten_salesforce_record(dupe_record, record_type=record_type)

                # Fetch related records for the duplicate account
                related_records = fetch_related_records(sf, dupe_id, record_type)

                # Reassign related records to the master account
                if not reassign_related_records(sf, master_id, related_records, record_type):
                    st.error("⚠️ Merge aborted due to errors in reassigning related records. Please fix the issues and try again.")
                    return  # Abort merge if there are errors

                # Only update fields that are empty in the master and not empty in the duplicate
                for field in ['Name', 'Phone', 'Website', 'BillingStreet', 'BillingCity', 'BillingState', 'BillingPostalCode', 'BillingCountry']:
                    if (not master_record.get(field) or not master_record[field]) and dupe_record.get(field):
                        fields_to_update[field] = dupe_record[field]

            # Update the master account with the new data
            if fields_to_update:
                sf.Account.update(master_id, fields_to_update)

            # Delete duplicate accounts
            for dupe_id in duplicate_ids:
                sf.Account.delete(dupe_id)

            st.success("✅ Accounts merged and duplicates deleted.")

        elif record_type == "Lead":
            master_record_query = f"SELECT Id, FirstName, LastName, Company, Owner.Id, Owner.Name, Email, Phone FROM Lead WHERE Id = '{master_id}'"
            master_record = sf.query(master_record_query)['records'][0]
            master_record = flatten_salesforce_record(master_record, record_type=record_type)

            fields_to_update = {}

            # Loop over duplicate records
            for dupe_id in duplicate_ids:
                dupe_record_query = f"SELECT Id, FirstName, LastName, Company, Owner.Id, Owner.Name, Email, Phone FROM Lead WHERE Id = '{dupe_id}'"
                dupe_record = sf.query(dupe_record_query)['records'][0]
                dupe_record = flatten_salesforce_record(dupe_record, record_type=record_type)

                # Fetch related records for the duplicate lead
                related_records = fetch_related_records(sf, dupe_id, record_type)

                # Reassign related records to the master lead
                if not reassign_related_records(sf, master_id, related_records, record_type):
                    st.error("⚠️ Merge aborted due to errors in reassigning related records. Please fix the issues and try again.")
                    return  # Abort merge if there are errors

                # Only update fields that are empty in the master and not empty in the duplicate
                for field in ['FirstName', 'LastName', 'Company', 'Email', 'Phone']:
                    if (not master_record.get(field) or not master_record[field]) and dupe_record.get(field):
                        fields_to_update[field] = dupe_record[field]

            # Update the master lead with the new data
            if fields_to_update:
                sf.Lead.update(master_id, fields_to_update)

            # Delete duplicate leads
            for dupe_id in duplicate_ids:
                sf.Lead.delete(dupe_id)

            st.success("✅ Leads merged and duplicates deleted.")

        elif record_type == "Contact":
            master_record_query = f"SELECT Id, FirstName, LastName, AccountId, Owner.Id, Owner.Name, Email, Phone FROM Contact WHERE Id = '{master_id}'"
            master_record = sf.query(master_record_query)['records'][0]
            master_record = flatten_salesforce_record(master_record, record_type=record_type)

            fields_to_update = {}

            # Loop over duplicate records
            for dupe_id in duplicate_ids:
                dupe_record_query = f"SELECT Id, FirstName, LastName, AccountId, Owner.Id, Owner.Name, Email, Phone FROM Contact WHERE Id = '{dupe_id}'"
                dupe_record = sf.query(dupe_record_query)['records'][0]
                dupe_record = flatten_salesforce_record(dupe_record, record_type=record_type)

                # Fetch related records for the duplicate contact
                related_records = fetch_related_records(sf, dupe_id, record_type)

                # Reassign related records to the master contact
                if not reassign_related_records(sf, master_id, related_records, record_type):
                    st.error("⚠️ Merge aborted due to errors in reassigning related records. Please fix the issues and try again.")
                    return  # Abort merge if there are errors

                # Only update fields that are empty in the master and not empty in the duplicate
                for field in ['FirstName', 'LastName', 'AccountId', 'Email', 'Phone']:
                    if (not master_record.get(field) or not master_record[field]) and dupe_record.get(field):
                        fields_to_update[field] = dupe_record[field]

            # Update the master contact with the new data
            if fields_to_update:
                sf.Contact.update(master_id, fields_to_update)

            # Delete duplicate contacts
            for dupe_id in duplicate_ids:
                sf.Contact.delete(dupe_id)

            st.success("✅ Contacts merged and duplicates deleted.")

        else:
            st.error("Unsupported record type")
            return

    except Exception as e:
        st.error(f"❌ An error occurred during the merge: {str(e)}")

# Streamlit UI components
def main():
    # Set page configuration
    st.set_page_config(page_title="Revenue Magnet - Salesforce Record Merger", layout="wide", page_icon="🔄")

    # Enter Record IDs Section in Sidebar
    st.sidebar.markdown("### Enter Record IDs one per line:")
    records_input = st.sidebar.text_area("Record IDs:", height=150, placeholder="Enter Record IDs here...")
    record_ids = [id.strip() for id in records_input.split('\n') if id.strip()]

    # Select Record Type
    record_type = st.sidebar.selectbox("Select Record Type:", ["Account", "Lead", "Contact"])

    # Buttons: Fetch and Merge in Sidebar
    fetch_records_clicked = st.sidebar.button("📥 Fetch Records")
    merge_records_clicked = st.sidebar.button("🔀 Merge Records")

    # Right panel: Main content area
    st.markdown("""
    <style>
    .main-frame {
        display: flex;
        flex-direction: column;
        background-color: #1c1c1c;
        padding: 20px;
        border-radius: 10px;
    }
    .header {
        text-align: center;
        color: #FF4B4B;
        font-size: 30px;
        font-weight: bold;
    }
    .motto {
        text-align: center;
        color: #ffffff;
        font-size: 18px;
    }
    .right-panel {
        margin-top: 30px;
        background-color: #2c2c2c;
        padding: 20px;
        color: white;
        border-radius: 10px;
    }
    .status-section {
        text-align: center;
        margin-top: 20px;
    }
    .status-check {
        font-size: 20px;
        color: green;
    }
    .status-check.error {
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)

    # Right frame: Header and Motto
    st.markdown('<div class="main-frame">', unsafe_allow_html=True)
    st.markdown('<div class="header">Revenue Magnet - SF Record Merger</div>', unsafe_allow_html=True)
    st.markdown('<div class="motto">Merge Salesforce Records Efficiently</div>', unsafe_allow_html=True)

    # Handle Fetch Records
    if fetch_records_clicked:
        if not record_ids:
            st.error("Please enter at least one Record ID.")
        else:
            sf = get_salesforce_connection()
            with st.spinner(f'🔄 Fetching {record_type}s from Salesforce...'):
                records = fetch_salesforce_records(sf, record_ids, record_type)
                if records:
                    df = pd.DataFrame(records)
                    # Reorder the dataframe to have 'Owner.Name' as the first column
                    columns_order = ['Owner.Name'] + [col for col in df.columns if col != 'Owner.Name']
                    df = df[columns_order]
                    # Show data on the right panel
                    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
                    st.write(f"### Fetched {record_type}s")
                    st.dataframe(df)

                    # Check if names are the same
                    if record_type == 'Account':
                        name_field = 'Name'
                    elif record_type == 'Lead' or record_type == 'Contact':
                        name_field = 'FirstName'
                    else:
                        name_field = 'Name'  # Default

                    names = df[name_field].unique()
                    st.markdown('<div class="status-section">', unsafe_allow_html=True)
                    if len(names) == 1:
                        st.markdown(f'<div class="status-check">✅ {record_type} names are the same</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-check error">❌ {record_type} names are different</div>', unsafe_allow_html=True)

                    # Count total related records
                    total_related_records = {}
                    for record in records:
                        related_records = fetch_related_records(sf, record['Id'], record_type)
                        for key, value in related_records.items():
                            total_related_records[key] = total_related_records.get(key, 0) + len(value)

                    for key, count in total_related_records.items():
                        st.write(f"**Total {key}:** {count}")

                    # Show Record Type if available (only for Accounts)
                    if record_type == 'Account' and 'Type' in df.columns:
                        st.write(f"**{record_type} Type:** {', '.join(df['Type'].unique())}")
                    if record_type == 'Account' and 'RecordType.Name' in df.columns:
                        st.write(f"**{record_type} Record Type:** {', '.join(df['RecordType.Name'].dropna().unique())}")

                    st.markdown('</div>', unsafe_allow_html=True)

    # Handle Merge Records
    if merge_records_clicked:
        if len(record_ids) < 2:
            st.error("Please provide at least one master and one or more duplicate Record IDs.")
        else:
            sf = get_salesforce_connection()
            master_id = record_ids[0]  # The first record is considered the master
            duplicate_ids = record_ids[1:]  # Remaining records are duplicates
            merge_salesforce_records(sf, master_id, duplicate_ids, record_type)

    # Display fetched data for related records
    if 'records' in locals() and records:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.markdown("### Related Records")
        for idx, record in enumerate(records):
            record_name = record.get('Name') or f"{record.get('FirstName', '')} {record.get('LastName', '')}".strip()
            st.markdown(f"#### {record_type} **{record_name}** (ID: {record['Id']})")
            related_records = fetch_related_records(sf, record['Id'], record_type)

            for key, value in related_records.items():
                if value:
                    st.markdown(f"##### {key}:")
                    df_related = pd.DataFrame(value)
                    # Reorder columns to display 'Owner.Name' first
                    if 'Owner.Name' in df_related.columns:
                        columns_order = ['Owner.Name'] + [col for col in df_related.columns if col != 'Owner.Name']
                        df_related = df_related[columns_order]
                    st.dataframe(df_related)

        st.markdown("</div>", unsafe_allow_html=True)  # Close right panel

    st.markdown("</div>", unsafe_allow_html=True)  # Close main frame

if __name__ == "__main__":
    main()
