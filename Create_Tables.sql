CREATE DATABASE Python_Quiz;
USE Python_Quiz;

CREATE TABLE Python_Quiz.questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chapter VARCHAR(50),
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT
    
);

CREATE TABLE Python_Quiz.users (
	id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    chapter VARCHAR(50),
    attempts INT DEFAULT 0,
    score INT DEFAULT 0,
    test_status VARCHAR(20) DEFAULT 'Incomplete'
    
);