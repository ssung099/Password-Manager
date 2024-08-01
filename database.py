MEMBER_TABLE = """
CREATE TABLE MEMBER(
    member_id INTEGER NOT NULL AUTO_INCREMENT,
    email varchar(255) NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    PRIMARY KEY (member_id),
    UNIQUE KEY unique_email (email)
);
"""

PASSWORD_TABLE = """
CREATE TABLE PASSWORD (
    password_id INTEGER NOT NULL AUTO_INCREMENT,
    website TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (password_id)
);
"""