-- 1. Create the database
CREATE DATABASE IF NOT EXISTS research_lab;
USE research_lab;

-- Disable checks so we can reload data easily
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- 2. DROP TABLES
-- -----------------------------------------------------
DROP TABLE IF EXISTS Is_Published;
DROP TABLE IF EXISTS Is_Used;
DROP TABLE IF EXISTS Mentorship;
DROP TABLE IF EXISTS Works;
DROP TABLE IF EXISTS Funds;
DROP TABLE IF EXISTS Project;
DROP TABLE IF EXISTS Grants;
DROP TABLE IF EXISTS Publication;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Collaborator;
DROP TABLE IF EXISTS Student;
DROP TABLE IF EXISTS Faculty;
DROP TABLE IF EXISTS Lab_Member;

-- -----------------------------------------------------
-- 3. CREATE TABLES
-- -----------------------------------------------------

CREATE TABLE Lab_Member (
    MID INT PRIMARY KEY,
    Name VARCHAR(100),
    Join_Date DATE,
    Member_Type VARCHAR(20)
);

CREATE TABLE Faculty (
    MID INT PRIMARY KEY,
    Department VARCHAR(50),
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID) ON DELETE CASCADE
);

CREATE TABLE Student (
    MID INT PRIMARY KEY,
    SID VARCHAR(20),
    Major VARCHAR(50),
    Level VARCHAR(20),
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID) ON DELETE CASCADE
);

CREATE TABLE Collaborator (
    MID INT PRIMARY KEY,
    Affiliation VARCHAR(100),
    Biography TEXT,
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID) ON DELETE CASCADE
);

CREATE TABLE Grants (
    GID INT PRIMARY KEY,
    Source VARCHAR(100),
    Budget DECIMAL(15, 2),
    Start_Date DATE,
    Duration INT
);

CREATE TABLE Project (
    PID INT PRIMARY KEY,
    Lead_MID INT,
    Exp_Duration INT,
    Start_Date DATE,
    End_Date DATE,
    Title VARCHAR(200),
    Status VARCHAR(20),
    FOREIGN KEY (Lead_MID) REFERENCES Faculty(MID)
);

CREATE TABLE Funds (
    GID INT,
    PID INT,
    PRIMARY KEY (GID, PID),
    FOREIGN KEY (GID) REFERENCES Grants(GID),
    FOREIGN KEY (PID) REFERENCES Project(PID)
);

CREATE TABLE Equipment (
    EID INT PRIMARY KEY,
    Pur_Date DATE,
    Status VARCHAR(20),
    Name VARCHAR(100),
    Type VARCHAR(50)
);

CREATE TABLE Publication (
    Publication_ID INT PRIMARY KEY,
    Venue VARCHAR(100),
    Title VARCHAR(200),
    Date DATE,
    DOI VARCHAR(100)
);

CREATE TABLE Works (
    MID INT,
    PID INT,
    Role VARCHAR(50),
    Hours INT,
    PRIMARY KEY (MID, PID),
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID),
    FOREIGN KEY (PID) REFERENCES Project(PID)
);

CREATE TABLE Mentorship (
    Mentor_ID INT,
    Mentee_ID INT,
    Start_Date DATE,
    End_Date DATE,
    PRIMARY KEY (Mentor_ID, Mentee_ID),
    FOREIGN KEY (Mentor_ID) REFERENCES Lab_Member(MID),
    FOREIGN KEY (Mentee_ID) REFERENCES Lab_Member(MID)
);

CREATE TABLE Is_Used (
    EID INT,
    MID INT,
    Start_Date DATE,
    End_Date DATE,
    Purpose VARCHAR(200),
    PRIMARY KEY (EID, MID),
    FOREIGN KEY (EID) REFERENCES Equipment(EID),
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID)
);

CREATE TABLE Is_Published (
    MID INT,
    Publication_ID INT,
    PRIMARY KEY (MID, Publication_ID),
    FOREIGN KEY (MID) REFERENCES Lab_Member(MID),
    FOREIGN KEY (Publication_ID) REFERENCES Publication(Publication_ID)
);

-- Re-enable checks
SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------
-- 4. INSERTING SAMPLE DATA
-- -----------------------------------------------------

-- Members
INSERT INTO Lab_Member VALUES (101, 'Dr. Smith', '2020-01-01', 'Faculty');
INSERT INTO Faculty VALUES (101, 'Computer Science');

INSERT INTO Lab_Member VALUES (102, 'Alice Doe', '2021-06-01', 'Student');
INSERT INTO Student VALUES (102, 'S001', 'Computer Science', 'PhD');

INSERT INTO Lab_Member VALUES (103, 'Bob Lee', '2022-01-15', 'Student');
INSERT INTO Student VALUES (103, 'S002', 'Biology', 'Masters');

INSERT INTO Lab_Member VALUES (104, 'Dr. External', '2021-01-01', 'Collaborator');
INSERT INTO Collaborator VALUES (104, 'NASA', 'Expert in propulsion');

INSERT INTO Lab_Member VALUES (201, 'Dr. Gregory House', '2019-05-10', 'Faculty');
INSERT INTO Faculty VALUES (201, 'Medicine');

INSERT INTO Lab_Member VALUES (202, 'Dr. Sheldon Cooper', '2018-01-01', 'Faculty');
INSERT INTO Faculty VALUES (202, 'Theoretical Physics');

-- New Students (PhD and Undergrad)
INSERT INTO Lab_Member VALUES (203, 'Harry Potter', '2021-09-01', 'Student');
INSERT INTO Student VALUES (203, 'S003', 'Chemistry', 'PhD');

INSERT INTO Lab_Member VALUES (204, 'Hermione Granger', '2021-09-01', 'Student');
INSERT INTO Student VALUES (204, 'S004', 'Chemistry', 'PhD');

INSERT INTO Lab_Member VALUES (205, 'Ron Weasley', '2022-01-15', 'Student');
INSERT INTO Student VALUES (205, 'S005', 'Chemistry', 'Undergrad');

INSERT INTO Lab_Member VALUES (206, 'Peter Parker', '2023-01-10', 'Student');
INSERT INTO Student VALUES (206, 'S006', 'Physics', 'Masters');

-- New Collaborator
INSERT INTO Lab_Member VALUES (207, 'Tony Stark', '2020-03-15', 'Collaborator');
INSERT INTO Collaborator VALUES (207, 'Stark Industries', 'Expert in clean energy');

-- Grants
INSERT INTO Grants VALUES (500, 'NSF', 1000000.00, '2020-01-01', 36);
INSERT INTO Grants VALUES (600, 'National Institutes of Health (NIH)', 2500000.00, '2019-06-01', 60);
INSERT INTO Grants VALUES (700, 'Dept of Energy (DOE)', 500000.00, '2022-01-01', 24);

-- Projects
INSERT INTO Project VALUES (1, 101, 24, '2020-02-01', '2022-02-01', 'AI for Biology', 'Active');
INSERT INTO Project VALUES (2, 101, 12, '2023-01-01', NULL, 'Database Optimization', 'Active');
-- Project 10: Funded by NIH, Led by Dr. House, Active
INSERT INTO Project VALUES (10, 201, 48, '2019-07-01', NULL, 'Diagnostic Medicine AI', 'Active');

-- Project 11: Funded by DOE, Led by Dr. Cooper, Active
INSERT INTO Project VALUES (11, 202, 24, '2022-02-01', NULL, 'String Theory Simulation', 'Active');

-- Project 12: No Grant (Internal), Led by Dr. House, Paused
INSERT INTO Project VALUES (12, 201, 12, '2023-01-01', '2023-06-01', 'Lupus Research', 'Paused');

-- Funds
INSERT INTO Funds VALUES (500, 1);
INSERT INTO Funds VALUES (600, 10); -- NIH funds Diagnostic AI
INSERT INTO Funds VALUES (700, 11); -- DOE funds String Theory

-- Works
INSERT INTO Works VALUES (101, 1, 'PI', 10);
INSERT INTO Works VALUES (102, 1, 'Research Assistant', 20);
INSERT INTO Works VALUES (103, 1, 'Data Analyst', 15);
INSERT INTO Works VALUES (102, 2, 'Lead Dev', 20);
INSERT INTO Works VALUES (201, 10, 'PI', 10);              -- Dr. House
INSERT INTO Works VALUES (203, 10, 'Lead Researcher', 40); -- Harry
INSERT INTO Works VALUES (204, 10, 'Data Scientist', 40);  -- Hermione
INSERT INTO Works VALUES (205, 10, 'Lab Assistant', 20);   -- Ron

-- Team Cooper (Project 11)
INSERT INTO Works VALUES (202, 11, 'PI', 10);              -- Dr. Cooper
INSERT INTO Works VALUES (206, 11, 'Intern', 15);          -- Peter Parker
INSERT INTO Works VALUES (207, 11, 'Consultant', 5);       -- Tony Stark

-- Mentorship
INSERT INTO Mentorship VALUES (101, 102, '2021-06-01', NULL);
INSERT INTO Mentorship VALUES (102, 103, '2022-02-01', NULL);

INSERT INTO Mentorship VALUES (201, 203, '2021-09-01', NULL);


INSERT INTO Mentorship VALUES (203, 205, '2022-01-15', NULL);


INSERT INTO Mentorship VALUES (207, 206, '2023-02-01', NULL);


INSERT INTO Mentorship VALUES (202, 204, '2021-09-01', NULL);

-- Equipment
INSERT INTO Equipment VALUES (10, '2019-01-01', 'In Use', 'Supercomputer', 'Server');
INSERT INTO Equipment VALUES (11, '2020-05-01', 'Available', 'Microscope', 'Optical');
INSERT INTO Equipment VALUES (20, '2020-01-01', 'In Use', 'Electron Microscope', 'Microscopy');
INSERT INTO Equipment VALUES (21, '2021-06-15', 'Available', 'Centrifuge 9000', 'Lab Tool');
INSERT INTO Equipment VALUES (22, '2018-05-20', 'Retired', 'Old Server Rack', 'Computing');

-- Is_Used
INSERT INTO Is_Used VALUES (10, 102, '2023-11-01', NULL, 'Running Simulations');

INSERT INTO Is_Used VALUES (20, 204, '2023-12-01', NULL, 'Cell Analysis');


INSERT INTO Is_Used VALUES (21, 205, '2023-11-01', '2023-11-05', 'Mixing Chemicals');

-- Publications
INSERT INTO Publication VALUES (901, 'IEEE Trans', 'AI in Bio', '2021-12-01', 'DOI/111');
INSERT INTO Publication VALUES (902, 'Nature', 'Bio Data', '2022-05-01', 'DOI/222');
INSERT INTO Publication VALUES (903, 'ACM SIGMOD', 'Fast SQL', '2023-01-01', 'DOI/333');
INSERT INTO Publication VALUES (910, 'Nature', 'Magic of Chemistry', '2022-01-01', 'DOI/HERM1');
INSERT INTO Publication VALUES (911, 'Science', 'Polyjuice Potions', '2022-06-01', 'DOI/HERM2');
INSERT INTO Publication VALUES (912, 'IEEE', 'Alchemy Algorithms', '2023-01-01', 'DOI/HERM3');
INSERT INTO Publication VALUES (913, 'Journal of Magic', 'Defense Arts', '2022-03-15', 'DOI/HARRY1');


INSERT INTO Is_Published VALUES (101, 901);
INSERT INTO Is_Published VALUES (102, 901);
INSERT INTO Is_Published VALUES (103, 902);
INSERT INTO Is_Published VALUES (102, 903);

INSERT INTO Is_Published VALUES (204, 910);
INSERT INTO Is_Published VALUES (204, 911);
INSERT INTO Is_Published VALUES (204, 912);

INSERT INTO Is_Published VALUES (203, 913);


INSERT INTO Is_Published VALUES (201, 910);
