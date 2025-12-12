import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',              
        database='research_lab'
    )
    return conn

# ==========================================
# 2. ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

# --- MENU 1: MEMBERS MANAGEMENT ---
@app.route('/members', methods=('GET', 'POST'))
def members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    members_by_grant = None
    
    
    if request.method == 'POST' and 'add_member' in request.form:
        mid = request.form['mid']
        name = request.form['name']
        join_date = request.form['join_date']
        member_type = request.form['member_type']
        
        # Project Assignment Fields
        pid = request.form.get('pid')
        hours = request.form.get('hours')
        role = "Member" 

        # Extended Attributes
        dept = request.form.get('department')
        major = request.form.get('major')
        level = request.form.get('level')
        affiliation = request.form.get('affiliation')
        biography = request.form.get('biography')

        try:
            # 1. Insert into Main Table
            cursor.execute("INSERT INTO Lab_Member (MID, Name, Join_Date, Member_Type) VALUES (%s, %s, %s, %s)",
                         (mid, name, join_date, member_type))
            
            # 2. Insert into Sub-Table based on Type
            if member_type == 'Faculty':
                final_dept = dept if dept else 'Unassigned'
                cursor.execute("INSERT INTO Faculty (MID, Department) VALUES (%s, %s)", (mid, final_dept))
            elif member_type == 'Student':
                sid = f"S{mid}" 
                final_major = major if major else 'Undeclared'
                final_level = level if level else 'Undergrad'
                cursor.execute("INSERT INTO Student (MID, SID, Major, Level) VALUES (%s, %s, %s, %s)", 
                             (mid, sid, final_major, final_level))
            elif member_type == 'Collaborator':
                final_aff = affiliation if affiliation else 'Unknown'
                final_bio = biography if biography else ''
                cursor.execute("INSERT INTO Collaborator (MID, Affiliation, Biography) VALUES (%s, %s, %s)", 
                             (mid, final_aff, final_bio))
            
            # 3. Insert into Works Table
            if pid and hours:
                cursor.execute("INSERT INTO Works (MID, PID, Role, Hours) VALUES (%s, %s, %s, %s)",
                             (mid, pid, role, hours))

            conn.commit()
        except Exception as e:
            print(f"Error adding member: {e}")

    # B. UPDATE MEMBER
    if request.method == 'POST' and 'update_member' in request.form:
        mid = request.form['mid']
        name = request.form['name']
        join_date = request.form['join_date']
        member_type = request.form['member_type']
        try:
            cursor.execute("""
                UPDATE Lab_Member 
                SET Name=%s, Join_Date=%s, Member_Type=%s 
                WHERE MID=%s
            """, (name, join_date, member_type, mid))
            conn.commit()
        except Exception as e:
            print(f"Error updating member: {e}")

    # C. DELETE MEMBER
    if request.method == 'POST' and 'delete_member' in request.form:
        mid_to_delete = request.form['mid_to_delete']
        try:
            cursor.execute("DELETE FROM Works WHERE MID = %s", (mid_to_delete,))
            cursor.execute("DELETE FROM Mentorship WHERE Mentor_ID = %s OR Mentee_ID = %s", (mid_to_delete, mid_to_delete))
            cursor.execute("DELETE FROM Is_Used WHERE MID = %s", (mid_to_delete,))
            cursor.execute("UPDATE Project SET Lead_MID = NULL WHERE Lead_MID = %s", (mid_to_delete,))
            
            cursor.execute("DELETE FROM Faculty WHERE MID = %s", (mid_to_delete,))
            cursor.execute("DELETE FROM Student WHERE MID = %s", (mid_to_delete,))
            cursor.execute("DELETE FROM Collaborator WHERE MID = %s", (mid_to_delete,))
            
            cursor.execute("DELETE FROM Lab_Member WHERE MID = %s", (mid_to_delete,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting member: {e}")

    # D. SEARCH BY GRANT
    if request.method == 'POST' and 'grant_search' in request.form:
        gid = request.form['grant_id_search']
        cursor.execute('''
            SELECT DISTINCT L.Name, L.Member_Type
            FROM Lab_Member L
            JOIN Works W ON L.MID = W.MID
            JOIN Funds F ON W.PID = F.PID
            WHERE F.GID = %s
        ''', (gid,))
        members_by_grant = cursor.fetchall()

    # E. LOAD ALL DATA
    cursor.execute('SELECT * FROM Lab_Member')
    members = cursor.fetchall()
    
    cursor.execute('SELECT PID, Title FROM Project')
    project_list = cursor.fetchall()
    
    cursor.execute('''
        SELECT P.Title, M1.Name as Mentor, M2.Name as Mentee
        FROM Mentorship Ment
        JOIN Lab_Member M1 ON Ment.Mentor_ID = M1.MID
        JOIN Lab_Member M2 ON Ment.Mentee_ID = M2.MID
        JOIN Works W1 ON W1.MID = Ment.Mentor_ID
        JOIN Works W2 ON W2.MID = Ment.Mentee_ID
        JOIN Project P ON W1.PID = P.PID
        WHERE W1.PID = W2.PID
    ''')
    mentorships = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('members.html', 
                           members=members, 
                           mentorships=mentorships, 
                           members_by_grant=members_by_grant,
                           project_list=project_list)

# --- MENU 2: PROJECTS MANAGEMENT ---
@app.route('/projects', methods=('GET', 'POST'))
def projects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    project_status = None
    grant_search_results = None
    grant_mentorships = None
    project_search_details = None
    project_search_members = None

    # A. ADD PROJECT
    if request.method == 'POST' and 'add_project' in request.form:
        pid = request.form['pid']
        title = request.form['title']
        status = request.form['status']
        lead_mid = request.form.get('lead_mid')
        try:
            if not lead_mid: lead_mid = None
            cursor.execute("INSERT INTO Project (PID, Title, Status, Lead_MID) VALUES (%s, %s, %s, %s)", 
                           (pid, title, status, lead_mid))
            conn.commit()
        except Exception as e:
            print(f"Error adding project: {e}")

    # B. UPDATE PROJECT
    if request.method == 'POST' and 'update_project' in request.form:
        pid = request.form['pid']
        title = request.form['title']
        status = request.form['status']
        lead_mid = request.form.get('lead_mid')
        try:
            if not lead_mid: lead_mid = None
            cursor.execute("""
                UPDATE Project 
                SET Title=%s, Status=%s, Lead_MID=%s 
                WHERE PID=%s
            """, (title, status, lead_mid, pid))
            conn.commit()
        except Exception as e:
            print(f"Error updating project: {e}")

    # C. DELETE PROJECT
    if request.method == 'POST' and 'delete_project' in request.form:
        pid_to_delete = request.form['pid_to_delete']
        try:
            cursor.execute("DELETE FROM Works WHERE PID = %s", (pid_to_delete,))
            cursor.execute("DELETE FROM Funds WHERE PID = %s", (pid_to_delete,))
            cursor.execute("DELETE FROM Project WHERE PID = %s", (pid_to_delete,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting project: {e}")

    # D. SEARCH PROJECT DETAILS
    if request.method == 'POST' and 'search_project_details' in request.form:
        search_pid = request.form['search_pid']
        cursor.execute('''
            SELECT P.PID, P.Title, P.Status, P.Start_Date, P.End_Date, 
                   L.Name as LeaderName, L.MID as LeaderID
            FROM Project P
            LEFT JOIN Lab_Member L ON P.Lead_MID = L.MID
            WHERE P.PID = %s
        ''', (search_pid,))
        project_search_details = cursor.fetchone()
        
        if project_search_details:
            cursor.execute('''
                SELECT L.Name, L.MID, L.Member_Type, W.Role, W.Hours
                FROM Works W
                JOIN Lab_Member L ON W.MID = L.MID
                WHERE W.PID = %s
            ''', (search_pid,))
            project_search_members = cursor.fetchall()

    # E. SEARCH MEMBERS BY GRANT
    if request.method == 'POST' and 'grant_member_search' in request.form:
        search_gid = request.form['search_gid']
        cursor.execute('''
            SELECT L.Name, L.MID, L.Member_Type, P.Title AS Project_Title, P.PID AS Project_ID
            FROM Lab_Member L
            JOIN Works W ON L.MID = W.MID
            JOIN Project P ON W.PID = P.PID
            JOIN Funds F ON P.PID = F.PID
            WHERE F.GID = %s
            ORDER BY P.PID, L.Name
        ''', (search_gid,))
        grant_search_results = cursor.fetchall()
        
        cursor.execute('''
            SELECT P.Title AS Project_Title, M1.Name AS Mentor_Name, M2.Name AS Mentee_Name
            FROM Mentorship Ment
            JOIN Lab_Member M1 ON Ment.Mentor_ID = M1.MID
            JOIN Lab_Member M2 ON Ment.Mentee_ID = M2.MID
            JOIN Works W1 ON W1.MID = Ment.Mentor_ID
            JOIN Works W2 ON W2.MID = Ment.Mentee_ID
            JOIN Project P ON W1.PID = P.PID
            JOIN Funds F ON P.PID = F.PID
            WHERE W1.PID = W2.PID AND F.GID = %s
        ''', (search_gid,))
        grant_mentorships = cursor.fetchall()

    # F. LOAD DATA
    cursor.execute('''
        SELECT P.*, L.Name AS Leader_Name
        FROM Project P
        LEFT JOIN Lab_Member L ON P.Lead_MID = L.MID
        ORDER BY P.Status, P.Title
    ''')
    all_projects = cursor.fetchall()

    cursor.execute('''
        SELECT L.MID, L.Name 
        FROM Lab_Member L 
        JOIN Faculty F ON L.MID = F.MID
    ''')
    faculty_list = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('projects.html', 
                           all_projects=all_projects, 
                           project_status=project_status,
                           faculty_list=faculty_list,
                           grant_search_results=grant_search_results,
                           grant_mentorships=grant_mentorships,
                           project_search_details=project_search_details,
                           project_search_members=project_search_members)

# --- MENU 3: EQUIPMENT ---
@app.route('/equipment', methods=('GET', 'POST'))
def equipment():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    search_result = None
    
    if request.method == 'POST' and 'add_equipment' in request.form:
        eid = request.form['eid']
        name = request.form['name']
        eq_type = request.form['type']
        pur_date = request.form['pur_date']
        status = request.form['status']
        try:
            cursor.execute("INSERT INTO Equipment (EID, Name, Type, Pur_Date, Status) VALUES (%s, %s, %s, %s, %s)",
                         (eid, name, eq_type, pur_date, status))
            conn.commit()
        except Exception as e:
            print(f"Error adding equipment: {e}")

    if request.method == 'POST' and 'update_equipment' in request.form:
        eid = request.form['eid']
        name = request.form['name']
        eq_type = request.form['type']
        pur_date = request.form['pur_date']
        status = request.form['status']
        
        assign_mid = request.form.get('assign_mid')
        assign_purpose = request.form.get('assign_purpose')

        try:
            cursor.execute("""
                UPDATE Equipment 
                SET Name=%s, Type=%s, Pur_Date=%s, Status=%s 
                WHERE EID=%s
            """, (name, eq_type, pur_date, status, eid))

            if status == 'In Use' and assign_mid:
                cursor.execute("SELECT COUNT(*) as cnt FROM Is_Used WHERE EID = %s AND End_Date IS NULL", (eid,))
                active_users = cursor.fetchone()['cnt']
                
                if active_users >= 3:
                    print("ERROR: Equipment cannot be used by more than 3 members simultaneously.")
                else:
                    cursor.execute("INSERT INTO Is_Used (EID, MID, Start_Date, Purpose) VALUES (%s, %s, CURDATE(), %s)",
                                 (eid, assign_mid, assign_purpose))
            
            if status == 'Available' or status == 'Retired':
                cursor.execute("UPDATE Is_Used SET End_Date = CURDATE() WHERE EID = %s AND End_Date IS NULL", (eid,))

            conn.commit()
        except Exception as e:
            print(f"Error updating equipment: {e}")

    if request.method == 'POST' and 'delete_equipment' in request.form:
        eid_to_delete = request.form['eid_to_delete']
        try:
            cursor.execute("DELETE FROM Is_Used WHERE EID = %s", (eid_to_delete,))
            cursor.execute("DELETE FROM Equipment WHERE EID = %s", (eid_to_delete,))
            conn.commit()
        except Exception as e:
            print(f"Error deleting equipment: {e}")

    if request.method == 'POST' and 'eid_search' in request.form:
        eid = request.form['eid_search']
        cursor.execute('SELECT * FROM Equipment WHERE EID = %s', (eid,))
        search_result = cursor.fetchone()

    filter_status = 'All'
    if request.method == 'POST' and 'filter_status' in request.form:
        filter_status = request.form['filter_status']

    base_query = '''
        SELECT E.EID, E.Name as EquipName, E.Status, 
               L.Name as MemberName, IU.Purpose as ProjectName
        FROM Equipment E
        LEFT JOIN Is_Used IU ON E.EID = IU.EID AND (IU.End_Date IS NULL OR IU.End_Date > CURDATE())
        LEFT JOIN Lab_Member L ON IU.MID = L.MID
    '''

    if filter_status == 'In Use':
        cursor.execute(base_query + " WHERE E.Status = 'In Use' ORDER BY E.EID")
    elif filter_status == 'Available':
        cursor.execute(base_query + " WHERE E.Status = 'Available' ORDER BY E.EID")
    elif filter_status == 'Retired':
        cursor.execute(base_query + " WHERE E.Status = 'Retired' ORDER BY E.EID")
    else:
        cursor.execute(base_query + " ORDER BY E.EID")
        
    filtered_list = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Equipment ORDER BY EID")
    all_equipment = cursor.fetchall()

    cursor.execute("SELECT MID, Name FROM Lab_Member")
    member_list = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('equipment.html', 
                           search_result=search_result, 
                           filtered_list=filtered_list, 
                           filter_status=filter_status, 
                           all_equipment=all_equipment,
                           member_list=member_list)

@app.route('/reports', methods=('GET', 'POST'))
def reports():
    conn = get_db_connection()
    conn.commit() 
    cursor = conn.cursor(dictionary=True)
    
    grant_proj_count = None
    prolific_members = None

    if request.method == 'POST':
        if request.form.get('report_type') == 'grant_projects':
            gid = request.form['grant_id']
            s_date = request.form['start_date']
            e_date = request.form['end_date']
            
            cursor.execute('''
                SELECT COUNT(DISTINCT P.PID) as Cnt
                FROM Project P
                JOIN Funds F ON P.PID = F.PID
                WHERE F.GID = %s
                  AND P.Start_Date <= %s 
                  AND (P.End_Date >= %s OR P.End_Date IS NULL)
            ''', (gid, e_date, s_date))
            row = cursor.fetchone()
            if row:
                grant_proj_count = row['Cnt']

        elif request.form.get('report_type') == 'prolific':
            gid = request.form['grant_id_prolific']
            
            
            cursor.execute('''
                SELECT 
                    L.Name, 
                    P.Title AS Project_Title,
                    COUNT(IP.Publication_ID) AS Total_Pubs,
                    GROUP_CONCAT(Pub.Publication_ID SEPARATOR ', ') as Pub_IDs,
                    GROUP_CONCAT(Pub.Title SEPARATOR ' | ') as Pub_Titles
                FROM Lab_Member L
                JOIN Works W ON L.MID = W.MID
                JOIN Project P ON W.PID = P.PID
                JOIN Funds F ON P.PID = F.PID
                JOIN Is_Published IP ON L.MID = IP.MID
                JOIN Publication Pub ON IP.Publication_ID = Pub.Publication_ID
                WHERE F.GID = %s
                GROUP BY L.MID, L.Name, P.Title
                ORDER BY Total_Pubs DESC
                LIMIT 3
            ''', (gid,))
            prolific_members = cursor.fetchall()

    cursor.execute('''
        SELECT L.Name, COUNT(IP.Publication_ID) as Pub_Count
        FROM Lab_Member L
        JOIN Is_Published IP ON L.MID = IP.MID
        GROUP BY L.MID, L.Name
        ORDER BY Pub_Count DESC LIMIT 1
    ''')
    top_pub = cursor.fetchone()
    
    cursor.execute('''
        SELECT S.Major, COUNT(IP.Publication_ID) * 1.0 / COUNT(DISTINCT S.MID) as Avg_Val
        FROM Student S
        LEFT JOIN Is_Published IP ON S.MID = IP.MID
        GROUP BY S.Major
    ''')
    avg_pubs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('reports.html', 
                           top_pub=top_pub, 
                           avg_pubs=avg_pubs,
                           grant_proj_count=grant_proj_count,
                           prolific_members=prolific_members)

if __name__ == '__main__':
    app.run(debug=True)